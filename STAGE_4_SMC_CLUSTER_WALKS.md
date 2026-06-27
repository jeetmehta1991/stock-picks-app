# Stage 4 SMC (Smart Money Concepts) Pure Price-Action Cluster Walks — Per-Strategy Deep-Dive Audit

> **B1029 STATUS BANNER 2026-06-27 doc-sync:** ALL WALKS 1-5 41-of-41 RESOLVED B984-B993 per CLAUDE.md banner. Cluster walks across 220 strategies CLOSED (B722 -3 + B874 -2 + B1010 +1 = 220 / 217 active). R5 LAUNCHED 2026-06-27 B1028 on AWS i-0940a53c75d049381 (Master 1929 ops x 4y window 2022-05-05 to 2026-05-05). Banners below indicating PENDING/RUNNING/DEFER status from B691-B750-era are HISTORICAL.


> **B719 STATUS BANNER (2026-06-12) — 6TH ADVERSARIAL REVIEW + LINE-BY-LINE METHOD APPLIED PROSPECTIVELY.** Output: [STAGE_4_SMC_CLUSTER_B719_ADVERSARIAL_REVIEW.md](STAGE_4_SMC_CLUSTER_B719_ADVERSARIAL_REVIEW.md). First cluster review where I applied `feedback_line_by_line_ticket_extraction_before_synthesis` (memory rule codified B715 after owner correction) PROSPECTIVELY -- extracted 18 actionable reviewer sentences to discrete tickets BEFORE writing the synthesis doc. **Four reviewer claims source-verified at line-number level**: `event_recency_bars=90` ([smc_ict.py:81](backtest/signals/smc_ict.py#L81)), `liquidity_range_pct=0.01` ([smc_ict.py:79](backtest/signals/smc_ict.py#L79)), `dealing_range_lookback=50` + `ohlc.tail(50)` ([smc_ict.py:80, 407-414](backtest/signals/smc_ict.py#L80)), B555 OPT-C SMC panel-cache layer exists with EXPLICITLY DOCUMENTED PIT-risk caveat ([smc_panel_cache.py:24-30](backtest/signals/smc_panel_cache.py)).
>
> **THREE HEADLINE FINDINGS (re-ranked per reviewer; doc currently treats as mid-priority among 7 patterns):**
>
> **(1) Pattern I detection lag = existence-of-edge problem, not staleness tradeoff.** 11 of 18 strategies are entry-timing-bound by the library's swing-confirmation 20-80 bar detection lag + 90-bar recency window. Entry timing is 20-170 bars after the structural event by construction. No parameter sweep fixes this. These strategies should be RECLASSIFIED AS POSITIONAL, not entry-timed (queued).
>
> **(2) Pattern K dealing-range lookahead = most likely fake-edge vector.** smc_panel_cache.py explicitly documents *"The library's OB function has forward-mutating state... When precomputed on the full series, an OB at bar 100 may show different final state than when computed on a truncated slice at bar 300"*. Cache is opt-in pending B554 parity test resolution. **Producer-audit harness (B699/B700 template) MUST be run on the dealing-range path and B555 panel-cache layer.**
>
> **(3) Pattern M 61% Quantum-Algo backtest = anti-evidence, not weak evidence.** 61% WR on 2,600 trades across 90 cells by the library author on 10 cherry-pickable assets is textbook over-parameterization signature. Honest prior is ~50% coinflip minus costs. **"DO NOT OPTIMIZE FROM THIS BASELINE" caveat queued.**
>
> **The one genuinely-optimizable sub-cluster**: SMC-12/13/18 liquidity-sweep family -- stop-run/failed-breakout effect with real microstructure mechanism. Same as ICT Turtle Soup. Highest-value tuning change: tight 1-5 bar recency for SMC-18 (parallel to B705 ICT Turtle Soup fix; should ship TOGETHER as single producer-additive batch). Flagship cross-cluster action: consolidate SMC-12/13/18 + ICT-7/8/9/10 to single liquidity-sweep-reversal family.
>
> **Architectural new finding**: vendored-library SPOF (Pattern L) needs loud-failure sentinel test -- the one ticket this cluster surfaces that prior tools don't cover. Engine-startup test asserts smartmoneyconcepts library imports + key functions present; fails pyramid loudly. Cheap fix.
>
> **18 B719 tickets queued across 6 phases.** Top priority: `S4-B719-SMC-PRODUCER-AUDIT-DEALING-RANGE-PATH-PIT-CHECK` (PHASE-0 fake-edge gate).
>
> ---
>
> **B693 BANNER ADDENDUM (2026-06-11) — selective-reading correction.** External reviewer of [STAGE_4_BREAKOUT_CLUSTER_WALKS.md](STAGE_4_BREAKOUT_CLUSTER_WALKS.md) caught a methodology problem in B691's blanket "false negative" labels: when favorable B660 numbers are LOCKED and unfavorable ones are PENDING-RERUN without a positive test, measurement can no longer disconfirm. **Each SMC strategy's zero now requires the positive two-part test** ((a) confirm gate signal literally absent from precompute signals dict, (b) confirm with signal present, other gates leave non-empty surviving set). Diagnostic tool: [`scripts/diagnose_zero_fires.py`](scripts/diagnose_zero_fires.py). The PENDING-B689-RERUN label below stays but is now provisional on that diagnostic. SMC's case is the strongest for harness-gap explanation (smc_ict producer literally absent from pre-B689 precompute, verified by source-read at [scripts/measure_fire_count.py:265 pre-B689](scripts/measure_fire_count.py#L265)) — but "strongest case" still requires the positive test, not assumption.
>
> ---
>
> **B691 STATUS BANNER (2026-06-11) — 🔴 FALSE-NEGATIVE — PENDING-B689-RERUN.** B660 measurement landed [2026-06-11 02:30 UTC](output_audit/fire_count_measured_b660_full_universe.json) showing **18 of 18 SMC strategies = 0 fires (100% FAIL_FIRE_STARVED).** **This is a measurement harness gap, NOT real verdicts.** The `smc_ict.compute_smc_signals(ohlc, ticker=ticker)` producer (which emits `smc_bos_*`, `smc_choch_*`, `smc_fvg_*`, `smc_order_block_*`, `smc_liquidity_swept_*`, `smc_breaker_block_*`, `smc_mitigation_block_*`, `smc_premium_*`, `smc_discount_*`, `smc_inverse_fvg_*`, `smc_equal_*_swept`, `smc_ote_*`, `smc_dealing_range_*`) was NOT invoked in the pre-B689 precompute path. Verification via gate_marginals audit: the marginals dict for `smc_bos_continuation` contained only the OHLCV-derived gates (e.g. `price_above_ema_200`) — the `smc_bos_bullish_active` / `_bearish_active` keys were ABSENT from the marginals, not present-at-False.
>
> **B689 (commit `8e8c258dd`) shipped the wire-in** — smoke test confirmed `smc_fvg_retest_long` fires 1× on AAPL Jun-Aug 2024 (vs B660's 0). The in-flight re-run (task `bzja19ugq`, started 09:30:39 2026-06-11, ETA ~2026-06-12 12:30) will produce trustworthy fire counts for ALL 18 SMC strategies. **All `PENDING-B660` and "100% FAIL_FIRE_STARVED" labels in this doc are now PENDING-B660-RERUN-B689 until then.**
>
> **What does NOT change in this batch:** the SMC walks' Pattern I (90-bar staleness) + Pattern J (FVG/OB/BOS overlap) + Pattern K (dealing_range PIT lookahead concern at lookback=50) + Pattern L (vendored library SPOF for `smc_liquidity_swept`) + Pattern M (Quantum Algo Mar 2026 unaudited methodology) + Pattern N (intra-cluster collinearity ablation candidate) + Pattern O (hardcoded tolerances) findings remain VALID regardless of fire-count revision. The B687 reviewer methodology fix (conditional-information diagnostic) applies to ANY cluster whose strategies' fire counts ultimately land in PASS_CUBE; until cube replay (B668) emits per-cell forward returns, SMC redundancy verdicts on overlapping primitives remain pending.
>
> **B673 status banner (2026-06-10, owner-approved cluster-walk launch):** owner directive *"create comprehensive walk doc for the next cluster"* + AskUserQuestion answer **"SMC pure price-action (12)"**. This is the FOURTH per-cluster Stage 4 walk doc following the pivot + trend + smart-money cluster doc precedents. The owner explicitly distinguished SMC pure price-action from the data-source smart-money cluster just completed in B672 (B672j commit `ad72c1e6a`).
>
> **Scope correction:** the AskUserQuestion option labeled "SMC pure price-action (12)" actually maps to **18 strategies** in the `smc` category per `STRATEGY_ROSTER.md` lines 169-186 + `len([f for f in dir(screener) if f.startswith("strat_smc_")]) = 18`. The "12" was a stale count derived from incomplete grep. This doc covers all 18 SMC strategies + structural reference to 2 Layer 2D ICT strategies (`strat_turtle_soup_long` + `strat_turtle_soup_short`) that share producer semantics with SMC but live in a separate category. **Total in-scope: 18 SMC + 2 ICT-Turtle-Soup = 20 strategies referenced; 18 with full walks.**
>
> **No prior cluster walk on these strategies.** Roster shows 5 with `Y (B570)` reviewed status — but B570 was the "Stage 4 owner-decision tool + first 7 Class-6 Defer flips" batch (commit `5444bb815`), which applied owner-decision tooling to set status flags (Deferred / Approved / etc.) WITHOUT running the per-strategy 7-step deep-dive walk per CHECKLIST #105. All 18 SMC strategies receive their FIRST CHECKLIST #105 walk in this doc.
>
> **Source of truth.** Code references reflect current state at commit `780e7b150` (post-B672 EXECUTION_QUEUE update). Producer: [backtest/signals/smc_ict.py](backtest/signals/smc_ict.py); strategies: [backtest/signals/screener.py:3208-3543](backtest/signals/screener.py#L3208-L3543).

> **Foundational sequence (carried from B665 commitment + reaffirmed B672):** B660 measured-fire-count run still in flight on laptop (PID 9988; ~25% complete; ETA ~5hr); B668 cube replay with `cube_compose_verdict.csv` populated awaiting B660 land; B669 survivorship execution awaiting B660 land. **All fires/yr projections in this doc are PENDING B660** per the same discipline applied to smart-money cluster doc — projections from independence-product math are diagnostic-only NOT measured. Per `feedback_no_rushing_per_strategy_tweak`: each walk surfaces options + WAITS for owner direction; no auto-action.

---

## Audience

Two:

1. **External reviewer** who issued the adversarial audits on the pivot + smart-money clusters. For you: the SMC cluster is materially different from both prior clusters because (a) signals are **PURE PRICE-ACTION** computed from OHLCV alone (no alt-data dependency), (b) the producer is a **VENDORED THIRD-PARTY LIBRARY** (joshyattridge/smartmoneyconcepts under DEC-508 Phase A) — single-point-of-failure for all 18 strategies, (c) most SMC primitives have a structural **DETECTION LAG of 20-80 bars** due to swing-confirmation requirement (Batch 273 fix); the `event_recency_bars=90` parameter controls fire-frequency-vs-staleness tradeoff and is a hidden tunable, (d) the underlying ICT methodology has **NO PEER-REVIEWED LITERATURE** — it's a YouTube-era trading framework with one unaudited Quantum Algo Mar 2026 backtest (61% WR / 2.17 PF / +2.27R on 10-asset 2,600-trade 26-month sample), (e) most strategies have **inherent multi-test exposure**: BOS continuation + BOS retest + CHOCH reversal + OB bounce + FVG retest all measure overlapping "institutional re-entry to recently-imbalanced zone" semantics. The walk methodology adapts to these differences — see [Methodology adaptations for SMC cluster](#methodology-adaptations-for-smc-cluster) section.

2. **Future readers** (owner, Claude in later sessions, new collaborators). The [Cluster scope inventory](#cluster-scope-inventory) is your orientation; per-strategy walks below.

---

## Methodology adaptations for SMC cluster

### 1. Vendored library dependency — `joshyattridge/smartmoneyconcepts` under DEC-508 Phase A

All 18 strategies depend on a single vendored library (`vendored/smartmoneyconcepts/smartmoneyconcepts.py`) imported into [backtest/signals/smc_ict.py:39-48](backtest/signals/smc_ict.py#L39-L48):

```python
with contextlib.redirect_stdout(io.StringIO()):
    try:
        from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc
        _SMC_AVAILABLE = True
    except Exception as _e:
        log_silent_failure("smc_ict.import_smartmoneyconcepts", _e)
        _smc = None
        _SMC_AVAILABLE = False
```

**Failure mode:** if the library import fails (version bump, environment delta, dependency conflict), `_SMC_AVAILABLE=False` and `compute_smc_signals` returns `{}`. All 18 strategies degrade together to "no signal → no fire." Step 5 OPEN_INVESTIGATIONS grep must check that B458 silent-failure logging is wired (✅ confirmed at line 46).

**Cross-strategy implication:** unlike the smart-money cluster where 41 strategies span 5 producers (13F + 13D + insider Form 4 + congressional + classification), SMC has 18 strategies sharing ONE producer. A library bug affects all 18 simultaneously. Per `feedback_walk_step3_must_read_producer_source`: the library source itself must be in scope for the walk; not just `smc_ict.py`'s wrapper.

### 2. Detection-lag dependency — `event_recency_bars=90` hidden tunable

Per Batch 273 fix documented at [smc_ict.py:51-72](backtest/signals/smc_ict.py#L51-L72):

> *"SMC library has intrinsic detection lag from swing-confirmation requirement. Using tail(N) for 'recently active' base signals (BOS/CHOCH/OB/liquidity) misses events because detection happens 20-80 bars after the event itself. This helper finds the last non-zero event by index and checks recency relative to current_idx instead of relative to the tail. Per empirical sweep on AAPL (1255 bars, swing_length=20): a 90-bar recency window catches the most-recent BOS in ~30% of days (vs ~0% with a 5-bar tail)."*

**The 90-bar `event_recency_bars` parameter is a free tuning knob with material alpha impact.** Increase → more fires + more staleness; decrease → fewer fires + fresher events but lower min_trades risk. Currently HARDCODED in [smc_ict.py:81](backtest/signals/smc_ict.py#L81) as the default `event_recency_bars=90`. Affects:
- `smc_bos_bullish` / `smc_bos_bearish`
- `smc_choch_bullish` / `smc_choch_bearish`
- `smc_ob_bullish_active` / `smc_ob_bearish_active`
- `smc_liquidity_swept_up` / `smc_liquidity_swept_dn`

NOT affected (use a different recency window or no decay):
- `smc_fvg_bullish_active` / `smc_fvg_bearish_active` — use `fvg_lookback=5` tail (FVG events are denser per producer comment line 168-171)
- `smc_*_retest_*_zone` — point-in-time price-in-zone check; no decay
- `smc_inverse_fvg_*` — point-in-time mitigated-and-flipped check; no decay
- `smc_dealing_range_pct` + `smc_in_discount_zone` + `smc_in_premium_zone` — uses `dealing_range_lookback=50`

**Step 7 should ALWAYS flag whether the strategy consumes `event_recency_bars`-bearing signals.** If yes, fire-count sensitivity to the 90-bar default is non-trivial.

### 3. PIT integrity — multiple producer-side fixes (B273 + B390 + B555 + B556)

The SMC producer has been bug-fixed multiple times for sparse-event slicing failures:
- **B273**: `_most_recent_event_within` helper added (BOS/CHOCH/OB/liquidity sparse-event lag)
- **B390**: `liquidity` events filter-then-tail (was missing 100% of sweeps pre-fix)
- **B555**: OPT-C SMC panel cache layer (must produce identical results to per-call compute; PIT integrity verified via separate test)
- **B556**: FVG + OB filter-then-tail consistency with B390 liquidity fix

Each walk's Step 3 must confirm the producer code path is the post-fix version + Step 5 grep OPEN_INVESTIGATIONS for any active producer-side concerns.

### 4. Bar-of-fire EVENT vs continuous STATE — SMC-specific temporality

Unlike the smart-money cluster where Pattern B (STATE-as-EVENT) was the dominant concern, SMC signals span the EVENT/STATE spectrum on a different axis:

| Signal class | Temporality | Lag profile | Step 7 concern |
|---|---|---|---|
| **Point-in-time zone-active** (FVG retest, OB mitigation, dealing range, OTE) | EVENT-shaped boundary | 0-day | Lookahead risk in zone-definition (see §5 dealing_range_lookback) |
| **Recency-windowed event** (BOS, CHOCH, OB active, liquidity sweep) | **STATE**-as-EVENT-with-90-bar-decay | 20-80 bar detection lag + up to 90-bar recency window | Pattern I detection-lag dependency |
| **Confluence composition** (CHOCH + FVG, BOS + retest near, liquidity-sweep + CHOCH/BOS) | Variable | Depends on the most-lagging component | Pattern N internal overlap |

Per CHECKLIST (s): the recency-windowed events ARE EVENT-class for purposes of "did something happen at bar of fire" but DEGRADE on the staleness axis as the window approaches its 90-bar tail. Strategies using these as the primary trigger must accept this degradation OR add a fresher confirmation gate (vol_spike_2x + RSI direction, B262/B278 pattern).

### 5. Lookahead risk class — `dealing_range_lookback=50` shares the S4-FIB-ANCHOR-LOOKAHEAD-AUDIT pattern

Per [smc_ict.py:406-418](backtest/signals/smc_ict.py#L406-L418):

```python
if len(ohlc) >= dealing_range_lookback:
    window = ohlc.tail(dealing_range_lookback)
    hi = float(window["high"].max())
    lo = float(window["low"].min())
```

The `dealing_range_lookback=50` parameter selects the high/low anchors over the trailing 50 bars. **If `ohlc` is ever passed with bars beyond `as_of`, the dealing-range anchors peek into the future** — identical lookahead-vector class as `compute_fibonacci` per `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` (EXECUTION_QUEUE.md ticket). Engine slicing convention is `df[df.index.date <= as_of]` BUT no explicit test asserts the SMC variant. Step 7 of `strat_smc_discount_long` + `strat_smc_premium_short` MUST surface this.

### 6. ICT methodology has no peer-reviewed academic support

Unlike the smart-money cluster which had Cohen-Malloy-Pomorski 2012, Cohen-Frazzini-Malloy 2008, Yan-Zhang 2009, Akbas-Jiang-Koch 2024 RFS citations (all peer-reviewed JF/JFE/RFS), the ICT/SMC framework is a **YouTube-era trading methodology** with no peer-reviewed publications:
- **Inner Circle Trader** = Michael J. Huddleston (pseudonym) — 2007+ trading-room methodology; no journal publications
- **Smart Money Concepts** = community-coined umbrella for ICT-derived concepts
- **Joshyattridge/smartmoneyconcepts library** = open-source community implementation; not peer-validated
- **Quantum Algo Mar 2026 backtest** = unaudited YouTube channel backtest (10 assets / 2,600 trades / 26 months); cited in `compute_smc_signals` docstring lines 19-22 as empirical backing BUT (i) NOT independent of the library author's frame, (ii) NOT validated against survivorship (left-tail likely deleted), (iii) NOT validated against multi-testing correction (the 18 strategies + 5 exits = 90 cells over 26 months is heavily over-fitted in a 2,600-trade sample).

**Step 4 doc-vs-thesis MUST flag the citation void.** Honest framing per `feedback_signal_temporality_event_vs_state` + `feedback_avwap_redundant_with_ema_trend_filter` distinct-failure-mode tests: SMC strategies are *plausible* per the methodology's internal logic but lack the academic-evidence anchor that the smart-money cluster's CMP / CFM citations supplied. Cube replay + Bailey-LdP deflated Sharpe + Hansen SPA + BH-FDR (per `backtest/engine/multiple_testing_correction.py` B667 + B668) is the ONLY path to empirical adjudication.

### 7. Internal multi-test exposure — 18 strategies on ~7 primitives

The 18 SMC strategies consume only 6 primitive boolean signals from the producer (FVG / OB / BOS / CHOCH / liquidity / dealing-range) + 2 derived (retest zone, mitigated-flip). **Combinatorially, the 18 strategies are dense compositions of those 7-ish primitives** — the joint information set is meaningfully smaller than 18 × independent signal stacks would suggest. This creates internal multi-test inflation EVEN BEFORE adding the cluster's cells to the broader 222-strategy family. Specifically:

- **6 dual strategies via `_strat3()`** (inverse_fvg, bos_continuation, choch_reversal, bos_retest_entry, order_block_bounce, liquidity_sweep_reversal) → 12 (strategy × direction) cells from 6 functions
- **12 single-direction strategies** (smc_fvg_retest_long, smc_fvg_retest_short, smc_breaker_block_long, smc_breaker_block_short, smc_mitigation_block_long, smc_mitigation_block_short, smc_discount_long, smc_premium_short, smc_ote_long, smc_ote_short, smc_equal_highs_sweep_short, smc_equal_lows_sweep_long)

→ **24 (strategy × direction) cells from 18 functions ON 7 primitives = ~3.4× density per primitive.** Step 7 of every walk must surface the Pattern N (internal multi-test) concern + the post-cube branch-stratified ablation that would settle which compositions earn independent registry slots.

---

## Reviewer findings response matrix

> Pre-emptive matrix awaiting external reviewer critique. After this doc's first read by the reviewer, findings will be tabulated here following the smart-money cluster precedent.

| # | Finding | Severity | Status | Action |
|---|---|---|---|---|
| _F-pending_ | Awaiting external reviewer pass on the SMC walk | — | OPEN | Will be tabulated post-review |

---

## Cluster scope inventory

**18 SMC strategies + 2 referenced ICT-Turtle-Soup (`turtle_soup_long` + `turtle_soup_short` in `chart_pattern` category, not walked here).** The 18 SMC strategies group into 6 sub-clusters by underlying ICT/SMC primitive:

| Sub-cluster | # strategies | Strategies |
|---|---|---|
| **A — Fair Value Gap (FVG) family** | 3 | SMC-1 `smc_fvg_retest_long` / SMC-2 `smc_fvg_retest_short` / SMC-3 `smc_inverse_fvg` (dual) |
| **B — Order Block (OB) family** | 4 | SMC-4 `smc_breaker_block_short` / SMC-5 `smc_breaker_block_long` / SMC-6 `smc_mitigation_block_long` / SMC-7 `smc_mitigation_block_short` |
| **C — Dealing range (premium/discount) family** | 2 | SMC-8 `smc_discount_long` / SMC-9 `smc_premium_short` |
| **D — Optimal Trade Entry (OTE) family** | 2 | SMC-10 `smc_ote_long` / SMC-11 `smc_ote_short` |
| **E — Liquidity sweep family** | 3 | SMC-12 `smc_equal_highs_sweep_short` / SMC-13 `smc_equal_lows_sweep_long` / SMC-18 `smc_liquidity_sweep_reversal` (dual) |
| **F — BOS / CHOCH structural family** | 4 | SMC-14 `smc_bos_retest_entry` (dual) / SMC-15 `smc_bos_continuation` (dual) / SMC-16 `smc_choch_reversal` (dual) / SMC-17 `smc_order_block_bounce` (dual) |

**Note on numbering:** SMC-N numbers run 1-18 in the order strategies are defined in screener.py for consistency with code-reading order. Sub-cluster grouping above is logical; not strictly contiguous.

**Cross-cluster overlap:** none with smart-money cluster (which is data-source-derived); 2 referenced strategies share PRODUCER (`strat_turtle_soup_long` / `_short` in chart_pattern category use the same `smc_liquidity_swept_*` signals but live in a separate category per B580 Layer 2D ICT inline-spec wiring). Per `feedback_strategy_roster_doc_maintenance`: STRATEGY_ROSTER.md is the single source of truth; this doc cross-refs but doesn't re-declare counts.

---

## Cross-strategy patterns (Pattern I-Q new for SMC cluster + Patterns A/F/G carried from prior clusters)

### Pattern I — Detection-LAG dependency on `event_recency_bars=90` hidden tunable (NEW for SMC)

**Affects:** 12 of 18 strategies that consume recency-windowed events (BOS, CHOCH, OB-active, liquidity-sweep). Specifically: SMC-3 (inverse_fvg) ✘ (uses point-in-time mitigated check, not recency), SMC-4/5 (breaker_block; uses point-in-time mitigated-flip), SMC-6/7 (mitigation_block; uses point-in-time in-zone), SMC-12/13 (equal_*_swept; uses `Swept` flag with 50-bar recency), SMC-14 (bos_retest_entry; uses 0.5% near-test on BOS Level over last 20 BOS events), SMC-15 (bos_continuation; consumes `smc_bos_bullish` from 90-bar recency), SMC-16 (choch_reversal; consumes `smc_choch_bullish` from 90-bar recency), SMC-17 (order_block_bounce; consumes `smc_ob_bullish_active` from 90-bar recency), SMC-18 (liquidity_sweep_reversal; consumes `smc_liquidity_swept_*` from 90-bar recency).

**Concern:** 90-bar window = ~4 months. A "BOS bullish" signal can fire 4 months after the actual structural break — by which time the structural backdrop may have changed entirely. Strategies that AND a "fresh" confirmation (B262 inverse_fvg + B278 bos_continuation pattern: `vol_spike_2x OR force_index_breakout`) mitigate the staleness; strategies without a freshness gate carry full staleness exposure.

**Step 7 disposition:** every walk consuming recency-windowed events must surface (a) which freshness gate (if any) mitigates staleness; (b) post-B660 sensitivity test of fire-count vs. tighter recency windows (e.g., 30 / 45 / 90 sweep); (c) candidate Class 2 LOOSEN/TIGHTEN of `event_recency_bars` as a free parameter cube can adjudicate.

### Pattern J — FVG / OB / BOS / CHOCH semantic overlap (NEW for SMC)

**Affects:** all 18 strategies. The 6 primitive signals (FVG, OB, BOS, CHOCH, liquidity, dealing-range) all measure variations of **"institutional re-entry to a recently-imbalanced zone"**:

- FVG = 3-bar imbalance (price gap)
- OB = last opposing candle before impulse (institutional accumulation/distribution zone)
- BOS = break of prior structural high/low (continuation event)
- CHOCH = first break of structure against prior trend (reversal event)
- Liquidity sweep = price takes out stops above/below equal-highs/lows (stop-hunt event)

These are NOT independent signals — they are different angular projections of the same underlying "where did institutions act" question. Cube replay must apply marginal-contribution scoring per `S5-MARGINAL-CONTRIBUTION-SCORING` C3 ticket: scoring each strategy as `book_with_X.sharpe - book_without_X.sharpe` rather than standalone Sharpe.

**Step 7 disposition:** every walk consuming 2+ primitives must surface Pattern J marginal-contribution concern. Cross-ref `S5-MARGINAL-CONTRIBUTION-SCORING` + this cluster as the highest-leverage application beyond the smart-money 13F sleeve test (`S5-13F-SLEEVE-MARGINAL-CONTRIBUTION-TEST`).

### Pattern K — `dealing_range_lookback=50` lookahead-vector class (NEW for SMC)

**Affects:** 2 strategies — SMC-8 `smc_discount_long` + SMC-9 `smc_premium_short` (both consume `smc_in_discount_zone` / `smc_in_premium_zone`).

**Concern:** identical lookahead-vector class as `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` for `compute_fibonacci`. The 50-bar trailing dealing-range max/min selects high/low anchors from a window that MUST be PIT-sliced before passing to the producer. Engine convention is `df[df.index.date <= as_of]` but no explicit test pins SMC-8/9 against future-data peeking.

**Step 7 disposition:** SMC-8 + SMC-9 walks queue a producer-PIT test ticket symmetric with `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT`. Low-confidence-but-no-test class; producer is most likely correct given engine convention but verification is cheap.

### Pattern L — Vendored library single-point-of-failure (NEW for SMC)

**Affects:** all 18 strategies.

**Concern:** library import failure → `_SMC_AVAILABLE=False` → all 18 strategies degrade to no-fire simultaneously. B458 silent-failure logging is wired (✅ confirmed at `smc_ict.py:46`) but the silent-fail mode produces a "no-signal → no-fire" pattern that mimics "no opportunity" in cube outputs. Distinguishable from genuine no-opportunity only via the silent_failure log + sentinel-test runs.

**Step 5 OPEN_INVESTIGATIONS** must confirm B458 logging is still active + the library version is pinned. Step 7 disposition: queue a periodic library-version-sentinel check (low-priority but cheap).

### Pattern M — Backtest provenance unaudited (NEW for SMC)

**Affects:** all 18 strategies (cited in producer docstring lines 19-22).

**Concern:** Quantum Algo Mar 2026 backtest cited as empirical backing (61% WR / 2.17 PF / +2.27R on 10 assets / 2,600 trades / 26 months) is (i) NOT independent of the library author's frame, (ii) NOT survivorship-validated (left-tail likely deleted), (iii) NOT multi-testing-corrected (18 strategies × ~5 exits = 90 cells on 2,600 trades = severely under-powered), (iv) NOT cited in any peer-reviewed publication, (v) sample is a 10-asset universe (vs our T1a 503 names). Treating this as evidence of expected alpha is overclaim per `feedback_signal_temporality_event_vs_state` doc-vs-thesis discipline.

**Step 4 doc-vs-thesis** of every walk should flag the Quantum Algo citation when present. Honest reframe: "Quantum Algo Mar 2026 reports 61% WR / 2.17 PF on a 10-asset sample; our cube replay against T1a 503 names + multi-testing correction is the ONLY adjudication path."

### Pattern N — Internal multi-test inflation (NEW for SMC; carry-over from §7 methodology adaptation)

**Affects:** all 18 strategies. 24 (strategy × direction) cells on ~7 primitives.

**Concern:** Cluster-internal Bonferroni / FDR inflation is materially higher than the per-strategy walk's Pattern F (cross-cluster) concern. The SMC cluster alone is a 24-cell × 26-exit ~624-cell subset of the broader cube; if all 18 strategies share 7 primitives, the effective independent test count is closer to 7-14 than 18.

**Step 7 disposition:** cube replay with multi-testing correction (B667 + B668 already shipped) handles this at the program level via `cube_select_with_multiple_testing()`. But intra-cluster collinearity ablation (which compositions earn registry slots after correction) is a CLUSTER-SCOPED test beyond C2 — queued as new ticket post-walk.

### Pattern O — Hardcoded tolerance constants (NEW for SMC)

**Affects:** 3 strategies depending on hardcoded thresholds in producer:
- SMC-14 `smc_bos_retest_entry` consumes `smc_bos_retest_*` produced with `tol = 0.005` (0.5%) hard-coded at [smc_ict.py:310](backtest/signals/smc_ict.py#L310)
- SMC-12 / SMC-13 `smc_equal_*_swept` consume `liquidity_range_pct=0.01` (1%) hard-coded as the equal-level cluster tolerance
- SMC-8 / SMC-9 / SMC-3 / SMC-15 / SMC-16 / SMC-17 / SMC-18 consume `event_recency_bars=90` (Pattern I) and `dealing_range_lookback=50` (Pattern K)

**Concern:** these tolerances are free parameters with no empirical basis cited; they should be either (a) config-driven (in `backtest/config.py`) so cube can sweep, (b) documented as DELIBERATE methodology choice with cited rationale, or (c) sensitivity-tested post-B660 to confirm they're not artifacts.

**Step 7 disposition:** queue a producer-side config-parameterization ticket post-B660 measured-fire-count baselines.

### Pattern A (carried from prior clusters) — `price_above_ema_200` / `below_ema_200` default handling

**Status:** ✅ already SWEPT per B663 + B630. All 18 strategies use either `s.get("price_above_ema_200", False)` (B663 fixed default-True → False) or `s.get("below_ema_200", False)` (B630 producer-additive positive symmetric). Verified via grep of screener.py SMC functions: 0 remaining default-True instances.

**Step 1 confirmation:** each walk should note "Pattern A confirmed FIXED" + commit reference.

### Pattern F (cross-cluster, carried from smart-money) — marginal-contribution audit

**Status:** Pattern J above (FVG/OB/BOS overlap) is the SMC-specific specialization of cross-cluster Pattern F. Cross-ref `S5-MARGINAL-CONTRIBUTION-SCORING` + `S5-13F-SLEEVE-MARGINAL-CONTRIBUTION-TEST` (smart-money) + this cluster's intra-cluster collinearity test (Pattern N) as 3 applications of the same methodology.

### Pattern G (cross-cluster, carried from smart-money) — low-fire-combo EXPLORATORY

**Status:** several SMC strategies project low fires/yr due to Pattern I detection-LAG + Pattern J overlapping primitives (specifically SMC-12 + SMC-13 equal-highs/lows sweep family + the BOS+FVG/OB+RSI confluence strategies). Cross-ref `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660` for the active ticket; SMC candidates added per walks below.

---

## Cluster current state table

| SMC # | Function name | Direction | Sub-cluster | Primary signal(s) | Confluence gates | B663/B630 ✓ | Pattern flags | Walk status |
|---|---|---|---|---|---|---|---|---|
| SMC-1 | `strat_smc_fvg_retest_long` | long | A FVG | `smc_fvg_retest_long_zone` | `price_above_ema_200` | ✅ | J | ⏳ Walked B673 |
| SMC-2 | `strat_smc_fvg_retest_short` | short | A FVG | `smc_fvg_retest_short_zone` | `below_ema_200` | ✅ | J | ⏳ Walked B673 |
| SMC-3 | `strat_smc_inverse_fvg` | dual | A FVG | `smc_inverse_fvg_bullish` / `_bearish` | `vol_confirms` (vol_spike_2x OR force_index_breakout) + 200-EMA | ✅ | B262 forensic-fixed; J + M | ⏳ Walked B673 |
| SMC-4 | `strat_smc_breaker_block_short` | short | B OB | `smc_breaker_block_bearish` | `below_ema_200` | ✅ | I + J | ⏳ Walked B673 |
| SMC-5 | `strat_smc_breaker_block_long` | long | B OB | `smc_breaker_block_bullish` | `price_above_ema_200` | ✅ | I + J | ⏳ Walked B673 |
| SMC-6 | `strat_smc_mitigation_block_long` | long | B OB | `smc_mitigation_block_long` | `price_above_ema_200` + `rsi_14<50` | ✅ | I + J | ⏳ Walked B673 |
| SMC-7 | `strat_smc_mitigation_block_short` | short | B OB | `smc_mitigation_block_short` | `below_ema_200` + `rsi_14>50` | ✅ | I + J | ⏳ Walked B673 |
| SMC-8 | `strat_smc_discount_long` | long | C dealing range | `smc_in_discount_zone` + (`smc_bos_bullish` OR `smc_choch_bullish`) | `price_above_ema_200` | ✅ | I + J + K | ⏳ Walked B673 |
| SMC-9 | `strat_smc_premium_short` | short | C dealing range | `smc_in_premium_zone` + (`smc_bos_bearish` OR `smc_choch_bearish`) | `below_ema_200` | ✅ | I + J + K | ⏳ Walked B673 |
| SMC-10 | `strat_smc_ote_long` | long | D OTE | `smc_ote_long_zone` + (`smc_bos_bullish` OR `smc_choch_bullish`) | (none — no EMA gate) | ✅ N/A | I + J + missing-trend-filter | ⏳ Walked B673 |
| SMC-11 | `strat_smc_ote_short` | short | D OTE | `smc_ote_short_zone` + (`smc_bos_bearish` OR `smc_choch_bearish`) | (none — no EMA gate) | ✅ N/A | I + J + missing-trend-filter | ⏳ Walked B673 |
| SMC-12 | `strat_smc_equal_highs_sweep_short` | short | E liquidity | `smc_equal_highs_swept` + `smc_fvg_bearish_active` | (none — no EMA gate) | ✅ N/A | I + J + missing-trend-filter + G fire-starve | ⏳ Walked B673 |
| SMC-13 | `strat_smc_equal_lows_sweep_long` | long | E liquidity | `smc_equal_lows_swept` + `smc_fvg_bullish_active` | (none — no EMA gate) | ✅ N/A | I + J + missing-trend-filter + G fire-starve | ⏳ Walked B673 |
| SMC-14 | `strat_smc_bos_retest_entry` | dual | F structural | `smc_bos_retest_long` / `smc_bos_retest_short` | EMA-200 | ✅ | I + J + O | ⏳ Walked B673 |
| SMC-15 | `strat_smc_bos_continuation` | dual | F structural | `smc_bos_bullish` / `smc_bos_bearish` | `vol_confirms` + RSI direction + EMA-200 | ✅ | B278 post-forensic gates; I + J | ⏳ Walked B673 |
| SMC-16 | `strat_smc_choch_reversal` | dual | F structural | `smc_choch_bullish` + `smc_fvg_bullish_active` (LONG); symmetric SHORT | (no EMA gate; FVG-confluence only) | ✅ N/A | I + J + missing-trend-filter | ⏳ Walked B673 |
| SMC-17 | `strat_smc_order_block_bounce` | dual | F structural | `smc_ob_bullish_active` + `rsi_14<45`; symmetric SHORT | EMA-200 | ✅ | I + J | ⏳ Walked B673 |
| SMC-18 | `strat_smc_liquidity_sweep_reversal` | dual | E liquidity | `smc_liquidity_swept_*` + (`smc_choch_*` OR `smc_bos_*`) | (no EMA gate; CHOCH/BOS confluence only) | ✅ N/A | I + J + missing-trend-filter | ⏳ Walked B673 |

**Net cluster state:**
- 18 functions / 24 (strategy × direction) cells
- 12 with EMA-200 trend gate; 6 without (SMC-10, SMC-11, SMC-12, SMC-13, SMC-16, SMC-18 — all use BOS/CHOCH/FVG structural-confluence as the trend proxy)
- Pattern A (B663/B630): ✅ all 12 EMA-consumers verified post-sweep
- Pattern I (90-bar recency): 11 strategies affected
- Pattern J (primitive overlap): all 18 affected
- Pattern K (dealing_range lookahead): SMC-8 + SMC-9
- Pattern O (hard-coded tolerances): SMC-12, SMC-13, SMC-14 directly + producer-wide implicit

---

## Per-strategy walks

### SMC-1. `strat_smc_fvg_retest_long` (Batch 216, FVG family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate LONG; canonical ICT FVG-retest continuation entry.

#### Step 1 — Read the code

[screener.py:3208-3220](backtest/signals/screener.py#L3208-L3220):

```python
def strat_smc_fvg_retest_long(s):
    """Batch 216 (SMC expansion 2026-05-18 owner-approved): price returned
    to an unmitigated bullish Fair Value Gap zone -> long entry.
    FVG = institutional 3-bar imbalance; retests of bullish FVGs are
    canonical ICT continuation entries."""
    fires = (
        s.get("smc_fvg_retest_long_zone", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "smc",
        ["smc_fvg_retest_long_zone", "price_above_ema_200"],
        ["Price inside unmitigated bullish Fair Value Gap zone",
         "Above 200 EMA (regime gate)"])
```

**2-gate LONG strategy.** Simplest SMC walk in the cluster.

| Gate | Meaning |
|---|---|
| `smc_fvg_retest_long_zone` | EVENT-shaped boundary: today's close is INSIDE an unmitigated bullish FVG zone (3-bar imbalance where bar -2's high < bar 0's low); `MitigatedIndex` from library is 0/NaN/non-current |
| `price_above_ema_200` | Long-term uptrend; B663-fixed default False |

#### Step 2 — Classify

- Category: `smc`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663 (Pattern A WAVE 1 family sweep — confirmed `price_above_ema_200` default is False post-sweep per smc_ict.py grep)

#### Step 3 — Producer source-read + temporality

- `smc_fvg_retest_long_zone` is computed at [smc_ict.py:174-205](backtest/signals/smc_ict.py#L174-L205) via FVG primitive's `Top`/`Bottom`/`MitigatedIndex` columns. Logic: iterate last 20 ACTUAL FVG events (B556 filter-then-tail fix); for each, check `is_mitigated = (MitigatedIndex set AND < current_idx)` AND `in_zone = (close >= bot AND close <= top)`; if `not is_mitigated AND in_zone AND fvg_val == 1` → `retest_long = True`.
- Lag: 0-day (point-in-time zone-active check at bar of fire)
- `price_above_ema_200` STATE

**EVENT/STATE composition:** 1 EVENT-shaped (zone-active) + 1 STATE. ✅ Canonical cross-EVENT/STATE structure where the EVENT IS the timing trigger. NOT a Pattern B candidate.

**Pattern J concern:** the FVG primitive is correlated with OB primitive (both measure "institutional imbalance zone"); strategies SMC-1 + SMC-6 may surface high correlation in cube replay.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "FVG = institutional 3-bar imbalance" | ✅ Producer implementation matches — `_smc.fvg(ohlc)` returns Top/Bottom of the 3-bar gap |
| "retests of bullish FVGs are canonical ICT continuation entries" | ⚠ **Pattern M** — canonical per ICT methodology BUT no peer-reviewed validation; cube-replay is the only adjudication path |
| Implicit "unmitigated FVG retest is high-probability entry" | ⚠ Quantum Algo Mar 2026 backtest cited cluster-wide but not specifically for FVG retest; per-component breakdown not in producer citation |

#### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations on SMC-1 specifically
- Producer-level: B556 filter-then-tail fix is the current state (no successor bug)
- Library-level: Pattern L vendored library SPOF concern applies generically

#### Step 6 — Missing-inverse + economic-symmetry

- **Inverse EXISTS** — SMC-2 `strat_smc_fvg_retest_short` is the symmetric mirror
- Economic symmetry: ✅ price-action signal; both directions equally valid per FVG semantics

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-J primitive overlap** | FVG retest + OB mitigation + OB bounce + breaker block all measure overlapping "institutional zone re-entry"; SMC-1 marginal contribution test needed | MEDIUM | Pattern J / S5-MARGINAL-CONTRIBUTION-SCORING |
| **F-pattern-M unaudited backtest** | Quantum Algo Mar 2026 cited cluster-wide; per-strategy contribution unknown until cube replay | MEDIUM | Pattern M |
| F-pattern-A | `price_above_ema_200` default False ✅ confirmed | ✅ SHIPPED B663 | — |
| F-fire-count | FVG retests are dense (~ every 5-15 bars per ticker per producer comment); projected fire count moderate-high; Step 7 expects PASS on min_trades=30 | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Add freshness gate symmetric with SMC-3 B262 fix — `vol_spike_2x OR force_index_breakout` to reduce stale-retest false positives |
| (c) Branch-stratified cube replay surfacing Pattern J overlap with SMC-6 (mitigation_block_long) + SMC-17 LONG (order_block_bounce) |
| **(d) RECOMMENDED — (c). Pattern J adjudication is the highest-leverage SMC ablation. Pre-cube no code change; the strategy is simple + structurally sound + already EMA-gated. (b) is a Class 2 LOOSEN/TIGHTEN candidate AFTER cube data settles whether SMC-1 carries distinct alpha from the OB family.** |

**My recommendation: (d).**

**Awaiting owner direction on SMC-1:**
1. (a)/(b)/(c)/(d) — recommendation (d)
2. Confirm Pattern J cube-replay ablation scope (which strategies to compare; SMC-1 vs SMC-6 + SMC-17 LONG is the minimum test)

---

### SMC-2. `strat_smc_fvg_retest_short` (Batch 216, FVG family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate SHORT; symmetric mirror of SMC-1.

#### Step 1 — Read the code

[screener.py:3223-3232](backtest/signals/screener.py#L3223-L3232):

```python
def strat_smc_fvg_retest_short(s):
    """Batch 216: bearish FVG retest -> short entry. Symmetric to long."""
    fires = (
        s.get("smc_fvg_retest_short_zone", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat(fires, "short", "smc",
        ["smc_fvg_retest_short_zone", "price_below_ema_200"],
        ["Price inside unmitigated bearish Fair Value Gap zone",
         "Below 200 EMA (bear regime)"])
```

**2-gate SHORT strategy.** Symmetric mirror of SMC-1.

| Gate | Meaning |
|---|---|
| `smc_fvg_retest_short_zone` | EVENT-shaped boundary: close inside unmitigated bearish FVG (3-bar imbalance where bar -2's low > bar 0's high) |
| `below_ema_200` | Long-term downtrend; B630 producer-additive positive symmetric (NOT default-True NOT-pattern) |

#### Step 2-6 (compact — symmetric with SMC-1)

- Category `smc`; SHORT direction; B291 default; last touched B630/B663
- Producer: [smc_ict.py:174-205](backtest/signals/smc_ict.py#L174-L205) symmetric branch (`fvg_val == -1`)
- EVENT/STATE: 1 EVENT-shaped + 1 STATE; canonical structure
- Pattern A B630 producer-additive ✅
- Pattern J primitive-overlap same as SMC-1
- Inverse: SMC-1 (long mirror); economic-symmetry ✅ price-action
- **B671 centralized borrow-trap gate applies** via `_strat()` inspect-frame consult (added B671): when `direction == "short"` AND `_short_borrow_trap_active(s)`, fires forced to False

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-J primitive overlap (SHORT-side)** | Symmetric mirror's marginal contribution vs SMC-7 (mitigation_block_short) + SMC-17 SHORT (order_block_bounce_short) | MEDIUM | Pattern J |
| **F-borrow-cost asymmetry** | SHORT side carries borrow-cost burden that SMC-1 LONG doesn't; B671 centralized DTC > 8 gate applies pre-fire | LOW | F5 carryover |
| F-pattern-A | `below_ema_200` B630 producer-additive ✅ | ✅ SHIPPED B630 | — |
| F-fire-count | Bearish-FVG retests rarer than bullish (equity upward drift); projected ~60-70% of SMC-1 fire count; should still PASS min_trades=30 | INFO | F4 |

**Options:** (a) status quo / (b) freshness gate symmetric with SMC-3 / (c) cube-replay Pattern J + branch-stratify SHORT vs LONG asymmetry / **(d) RECOMMENDED — (c)**

**My recommendation: (d) bundled with SMC-1 disposition.**

**Awaiting owner direction on SMC-2:** same as SMC-1; bundled.

---

### SMC-3. `strat_smc_inverse_fvg` (Batch 216 + B262 forensic-fixed, FVG family, walked B673 — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **B262 FORENSIC-FIXED CASE** — original signal fired 478 trades (40% of all flow) with 24.7% WR = -1659pp = ~95% of aggregate loss in Phase 1A-alpha. B262 added regime gate + volume confirmation gates. Walk surfaces (a) is the post-fix design empirically validated, (b) does the cube vindicate the fix?

#### Step 1 — Read the code

[screener.py:3235-3269](backtest/signals/screener.py#L3235-L3269):

```python
def strat_smc_inverse_fvg(s):
    """Batch 216: Inverse FVG - bullish FVG was invalidated (price closed
    below) -> the zone flips role and acts as resistance (short).
    Symmetric for bearish FVG invalidated upward (long).
    ICT 'IFVG' concept: a failed institutional imbalance becomes the new
    opposing reference.

    Batch 262 fix (Pass 53 Day 9+ 2026-05-20 post-1A-alpha forensic):
    Original signal fired 478 trades (40% of all flow) with 24.7% WR /
    -3.47% mean PnL = -1659pp total contribution = ~95% of aggregate loss.
    Root cause: no regime gate, no volume confirmation, no momentum filter.
    Fired on every IFVG flag indiscriminately.

    Added confluence gates:
    - 200-EMA regime alignment (long above, short below)
    - vol_spike OR price_acceleration confirms institutional follow-through
      (IFVG breakdown without volume = false signal per ICT canon)
    """
    fl_base = s.get("smc_inverse_fvg_bullish", False)
    fs_base = s.get("smc_inverse_fvg_bearish", False)
    above_200 = s.get("price_above_ema_200", False)
    below_200 = s.get("below_ema_200", False)
    vol_confirms = s.get("vol_spike_2x", False) or s.get("force_index_breakout", False)
    fl = fl_base and above_200 and vol_confirms
    fs = fs_base and below_200 and vol_confirms
    return _strat3(fl, fs, "smc",
        ["smc_inverse_fvg_bullish", "price_above_ema_200", "vol_confirms"],
        ["smc_inverse_fvg_bearish", "price_below_ema_200", "vol_confirms"],
        ["Inverse FVG bullish + 200-EMA gate + volume confirms",
         "ICT IFVG role-flip with institutional follow-through"],
        ["Inverse FVG bearish + 200-EMA gate + volume confirms",
         "ICT IFVG role-flip with institutional follow-through"])
```

**3-gate dual strategy.** Most heavily-gated SMC strategy due to B262 forensic-fix.

**Each direction fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `smc_inverse_fvg_bullish` (LONG) / `_bearish` (SHORT) | EVENT-shaped point-in-time: FVG was mitigated AND price now opposite side (bullish FVG below price after invalidation → LONG; bearish FVG above price after invalidation → SHORT) |
| `price_above_ema_200` (LONG) / `below_ema_200` (SHORT) | Regime gate added B262 |
| `vol_confirms` = `vol_spike_2x OR force_index_breakout` | Volume confirmation added B262 |

#### Step 2 — Classify

- Category: `smc`
- Direction: dual via `_strat3`
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 dual default
- Last touched: B262 (forensic fix); B630/B663 verified

#### Step 3 — Producer source-read + temporality

- `smc_inverse_fvg_bullish` / `_bearish` computed at [smc_ict.py:194-206](backtest/signals/smc_ict.py#L194-L206) — checks last 20 ACTUAL FVG events for `is_mitigated` AND price now opposite side of zone (close < Bottom for bearish flip; close > Top for bullish flip)
- Lag: 0-day point-in-time check
- `price_above_ema_200` / `below_ema_200` STATE
- `vol_spike_2x` is genuine EVENT (today's volume >= 2x trailing 20-bar mean); `force_index_breakout` is EVENT (today's force index crosses breakout threshold)

**EVENT/STATE composition:** 2 EVENT (inverse_fvg + vol_confirms) + 1 STATE (200-EMA) per direction. **Strongest EVENT-anchored structure in the cluster** after the B262 fix.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Original signal fired 478 trades (40% of all flow) with 24.7% WR = -1659pp" | ✅ **B262 forensic confirmed empirically** in Phase 1A-alpha. The fix is evidence-based, not theoretical. |
| "Inverse FVG = failed institutional imbalance becomes the new opposing reference" | ✅ Canonical ICT IFVG concept; implementation matches |
| "vol_spike OR price_acceleration confirms institutional follow-through" | ✅ Defensible — without volume, an IFVG break is a stop-hunt; with volume, it's institutional follow-through |
| Implicit "post-B262 fix the strategy is sound" | ⚠ **Pattern M** — B262 fixed the empirical disaster but the fix has not been re-validated against a full-universe cube replay; pre-B660 the fix is plausible but unproven |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B262 forensic precedent IS the active concern; post-B660 cube replay must surface whether the post-fix design is empirically sound on the full T1a universe
- Cross-ref: B262 is the canonical "kill the loser by gating not deleting" precedent — a model for Pattern E confluence wraps + W5 / W5m EXPLORATORY markers + low-fire-combo dispositions

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual (`_strat3`); both directions fire under B262 fix
- Economic symmetry: ✅ price-action; both IFVG bullish AND bearish are valid per ICT semantics

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-B262 fix re-validation** | The 95%-aggregate-loss fix must be re-validated under post-B660 cube replay on T1a 503 names. If the fix is empirically sound, the strategy is the cluster's most-forensic-evidence-anchored design | HIGH | F1 |
| **F-pattern-J FVG overlap** | Inverse_fvg + FVG retest (SMC-1/SMC-2) both consume FVG primitive at different stages; marginal contribution audit | MEDIUM | Pattern J |
| **F-pattern-M unaudited Quantum Algo** | Quantum Algo backtest cited cluster-wide does NOT include the post-B262-fix design; verdict is from the broken pre-fix version | HIGH | Pattern M |
| F-fire-count | Post-fix gates triple-AND reduce fires materially; projected ~30-80/yr universe-wide per direction; borderline PASS min_trades=30 | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo (post-B262-fix) |
| (b) Tighter regime gate — `price_above_ema_50 AND price_above_ema_200` (multi-timeframe regime confluence) |
| (c) Looser regime gate — drop 200-EMA + keep volume; pure EVENT-anchored design |
| **(d) RECOMMENDED — (a) + post-B660 cube replay re-validation of B262 fix is the empirical adjudication path. If cube vindicates the fix, the strategy is the cluster's design-template; if it doesn't, the strategy should be DELETED per B262's own precedent of evidence-based intervention.** |
| (e) EXPLORATORY marker pre-cube (analogous to W5/W5m) — exclude from selection budget while keeping for cube-replay coverage |

**My recommendation: (d).** B262 represents the gold standard for SMC-strategy disposition methodology — gate-add fix based on empirical disaster. The post-fix design deserves a clean post-B660 cube test to settle whether the fix landed.

**Awaiting owner direction on SMC-3:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (d)
2. Confirm post-B660 cube-replay re-validation scope on B262 fix
3. Whether to surface B262 forensic precedent as a cluster-wide methodology citation (canonical model for gate-add-instead-of-delete dispositions)

---

### SMC-4. `strat_smc_breaker_block_short` (Batch 216, OB family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate SHORT — bullish OB mitigated downward becomes resistance.

#### Step 1 — Read the code

[screener.py:3272-3283](backtest/signals/screener.py#L3272-L3283):

```python
def strat_smc_breaker_block_short(s):
    """Batch 216: Breaker block short - bullish OB that was mitigated +
    price now below bottom -> the OB flips role and becomes resistance.
    Classic ICT 'breaker block' reversal setup."""
    fires = (
        s.get("smc_breaker_block_bearish", False)
        and s.get("below_ema_200", False)  # B630 sweep
    )
    return _strat(fires, "short", "smc",
        ["smc_breaker_block_bearish", "price_below_ema_200"],
        ["Bullish Order Block mitigated + price below - role flipped to resistance",
         "Below 200 EMA (bear regime)"])
```

**2-gate SHORT strategy.** Variant of inverse-FVG concept applied to Order Blocks.

| Gate | Meaning |
|---|---|
| `smc_breaker_block_bearish` | EVENT-shaped point-in-time: bullish OB was mitigated AND price now below OB Bottom (role flip to resistance) |
| `below_ema_200` | Bear regime |

#### Step 2-3 — Producer + temporality

- `smc_breaker_block_bearish` at [smc_ict.py:258-265](backtest/signals/smc_ict.py#L258-L265) — checks last 20 ACTUAL OB events (B556 filter-then-tail) for `is_mitigated AND ob_val == 1 AND close < float(bot)` → True
- OB primitive uses `event_recency_bars=90` via `_most_recent_event_within` (Pattern I applies indirectly through `smc_ob_bullish_active` STATE; but `smc_breaker_block_*` reads OB events directly via filter-then-tail of last 20 events — NOT recency-windowed)
- Lag: 0-day point-in-time check (mitigated-and-flipped)
- 1 EVENT-shaped + 1 STATE

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Bullish OB that was mitigated + price now below bottom → resistance flip" | ✅ Implementation matches ICT canon |
| "Classic ICT breaker block reversal setup" | ⚠ Pattern M — canonical per ICT methodology BUT no peer-reviewed validation |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B556 producer fix is current state
- No active investigations specific to SMC-4

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — SMC-5 `strat_smc_breaker_block_long`
- Economic symmetry: ✅ price-action

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-J OB-family overlap** | Breaker block + mitigation block + order block bounce all consume OB primitive at different stages; marginal contribution audit | MEDIUM | Pattern J |
| **F-borrow-cost** | B671 centralized DTC>8 gate applies | LOW | F5 carryover |
| **F-no-freshness-gate** | Unlike SMC-3 (B262 fix added vol_confirms), SMC-4 has no volume confirmation. The B262 forensic precedent may apply — pre-cube speculation that breaker-block-without-volume is high false-positive risk symmetric with B262 inverse_fvg-without-volume | MEDIUM | F1 + B262 precedent |
| F-pattern-A | `below_ema_200` B630 producer-additive ✅ | ✅ SHIPPED B630 | — |
| F-fire-count | Breaker block events rare (mitigated OBs are rare); projected ~10-30/yr universe-wide per direction; borderline FAIL min_trades=30 | MEDIUM | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Add `vol_confirms` gate symmetric with SMC-3 B262 fix — guards against breaker block being a stop-hunt without follow-through |
| (c) Branch-stratified cube replay surfacing OB-family overlap with SMC-7 (mitigation_block_short) + SMC-17 SHORT |
| **(d) RECOMMENDED — (b) + (c). The B262 precedent argues a freshness gate is the canonical SMC-strategy hardening pattern; SMC-4 lacks it. Post-B660 cube replay settles whether the gate-add improves vs status quo.** |
| (e) EXPLORATORY marker pre-cube — low-fire-combo class |

**My recommendation: (d).** The B262 forensic-fix precedent strongly suggests volume confirmation is a near-universal SMC-strategy hardening per ICT methodology itself ("IFVG breakdown without volume = false signal per ICT canon"); applying it symmetrically to breaker-block is the consistent design choice.

**Awaiting owner direction on SMC-4:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (d)
2. Whether (b) freshness-gate addition is a global SMC-cluster pattern (apply to SMC-5, SMC-6, SMC-7, SMC-10, SMC-11, SMC-12, SMC-13, SMC-14, SMC-16, SMC-17, SMC-18) or per-strategy decision
3. Pattern N (intra-cluster collinearity ablation) cube-replay scope

---

### SMC-5. `strat_smc_breaker_block_long` (Batch 216, OB family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate LONG; symmetric mirror of SMC-4.

#### Step 1 — Read the code

[screener.py:3286-3296](backtest/signals/screener.py#L3286-L3296):

```python
def strat_smc_breaker_block_long(s):
    """Batch 216: Breaker block long - bearish OB that was mitigated +
    price now above top -> flips to support."""
    fires = (
        s.get("smc_breaker_block_bullish", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "smc",
        ["smc_breaker_block_bullish", "price_above_ema_200"],
        ["Bearish Order Block mitigated + price above - role flipped to support",
         "Above 200 EMA (regime gate)"])
```

**2-gate LONG strategy.** Symmetric mirror of SMC-4.

#### Step 2-7 (compact — symmetric with SMC-4)

- Category `smc`; LONG; B291 default; last touched B663
- Producer: [smc_ict.py:258-265](backtest/signals/smc_ict.py#L258-L265) symmetric branch
- Same Pattern J + no-freshness-gate concern as SMC-4
- Same fire-count concern (rare mitigated OB events)
- Pattern A B663 ✅

**Options:** same as SMC-4; bundled. **My recommendation: (d) bundled with SMC-4.**

**Awaiting owner direction on SMC-5:** bundled with SMC-4.

---

### SMC-6. `strat_smc_mitigation_block_long` (Batch 216, OB family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate LONG — price entering unmitigated bullish OB zone.

#### Step 1 — Read the code

[screener.py:3299-3313](backtest/signals/screener.py#L3299-L3313):

```python
def strat_smc_mitigation_block_long(s):
    """Batch 216: Price entering an UN-mitigated bullish Order Block
    zone - the institutional zone is being mitigated NOW. Lower-risk
    entry than waiting for the OB to fully play out; pairs naturally
    with subsequent CHoCH/BOS confirmation."""
    fires = (
        s.get("smc_mitigation_block_long", False)
        and s.get("price_above_ema_200", False)
        and s.get("rsi_14", 50) < 50
    )
    return _strat(fires, "long", "smc",
        ["smc_mitigation_block_long", "price_above_ema_200", "rsi_14<50"],
        ["Price inside bullish Order Block zone - mitigation underway",
         "Above 200 EMA (regime gate)",
         "RSI pullback context (not overbought)"])
```

**3-gate LONG strategy.** Mitigation_block is the "early entry" variant of order-block trading — enter as the OB is being mitigated NOW (lower-risk than waiting).

| Gate | Meaning |
|---|---|
| `smc_mitigation_block_long` | EVENT-shaped: price inside UN-mitigated bullish OB (`is_mitigated == False AND in_zone == True AND ob_val == 1`) |
| `price_above_ema_200` | Long-term uptrend |
| `rsi_14 < 50` | Pullback context — not overbought |

#### Step 2-3 — Classify + producer

- Category `smc`; LONG; B291 default; last touched B663
- Producer: [smc_ict.py:268-272](backtest/signals/smc_ict.py#L268-L272); `mitigation_long = True` when `not is_mitigated AND in_zone AND ob_val == 1`
- 1 EVENT-shaped + 2 STATE
- Pattern I applies indirectly — the OB primitive itself uses 90-bar recency for the "active" STATE but breaker/mitigation reads OB events from filter-then-tail of last 20 directly. Different staleness profile than SMC-17 order_block_bounce which DOES consume `smc_ob_bullish_active` STATE.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Price entering an UN-mitigated bullish OB zone" | ✅ Implementation matches |
| "Lower-risk entry than waiting for the OB to fully play out" | ⚠ Pattern M — canonical per ICT but no peer-reviewed validation. The "lower-risk" claim is unverified outside the ICT framework. |
| "RSI pullback context (not overbought)" | ⚠ **F-rsi-default-50 hazard** per `S5-RSI-DEFAULT-50-FAMILY` ticket — `s.get("rsi_14", 50) < 50` with default=50 means missing data fails the gate (50 < 50 is False). Fail-safe ✅. But: default=50 also means an RSI exactly at 50 fails the gate. **Strict-inequality on default-value-AT-threshold = the canonical S5-RSI-DEFAULT-50 family member.** B654 W8 fix precedent (drop the gate) may apply if cube shows the gate is near-no-op. |

#### Step 5 — OPEN_INVESTIGATIONS grep

- **`S5-RSI-DEFAULT-50-FAMILY`** ticket directly applies — SMC-6 + SMC-7 are family members
- B556 producer fix is current state

#### Step 6 — Missing-inverse

- ✅ Inverse EXISTS — SMC-7 `strat_smc_mitigation_block_short` (symmetric with `rsi_14 > 50` rally context)

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-J OB-family overlap** | SMC-6 + SMC-4/SMC-5 + SMC-17 LONG share OB primitive; marginal contribution audit | MEDIUM | Pattern J |
| **F-rsi-default-50 hazard** | `rsi_14 < 50` strict-inequality on default-50; family member of `S5-RSI-DEFAULT-50-FAMILY`. B654 W8 precedent (drop the gate) may apply post-cube | MEDIUM | F-rsi-50 |
| F-pattern-A | `price_above_ema_200` ✅ | ✅ SHIPPED B663 | — |
| F-fire-count | Mitigation events more common than breaker-block (unmitigated OBs are common); projected ~30-90/yr universe-wide; PASS likely | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Drop `rsi_14<50` gate per B654 W8 precedent (S5-RSI-DEFAULT-50-FAMILY resolution option a) — would raise fire count slightly + remove near-no-op gate |
| (c) Tighten `rsi_14<50` to `rsi_14<45` (canonical pullback band; per `feedback_minimum_fire_count_gate_before_cube`) — actual pullback rather than coin-flip midpoint |
| (d) Branch-stratified cube replay — keep status quo + cube settles RSI-gate marginal contribution |
| **(e) RECOMMENDED — (d). RSI-gate is the candidate Class 2 LOOSEN/TIGHTEN; cube empirical settles whether to drop (b) or tighten (c). Pre-cube no code change.** |

**My recommendation: (e).**

**Awaiting owner direction on SMC-6:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. Whether RSI-default-50 family-bug sweep should bundle SMC-6 + SMC-7 with broader screener.py grep (per `S5-RSI-DEFAULT-50-FAMILY` ticket scope)

---

### SMC-7. `strat_smc_mitigation_block_short` (Batch 216, OB family, walked B673)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate SHORT; symmetric mirror of SMC-6.

#### Step 1 — Read the code

[screener.py:3316-3327](backtest/signals/screener.py#L3316-L3327):

```python
def strat_smc_mitigation_block_short(s):
    """Batch 216: Symmetric mitigation block short."""
    fires = (
        s.get("smc_mitigation_block_short", False)
        and s.get("below_ema_200", False)  # B630 sweep
        and s.get("rsi_14", 50) > 50
    )
    return _strat(fires, "short", "smc",
        ["smc_mitigation_block_short", "price_below_ema_200", "rsi_14>50"],
        ["Price inside bearish Order Block zone - mitigation underway",
         "Below 200 EMA (bear regime)",
         "RSI rally context (not oversold)"])
```

**3-gate SHORT strategy.** Symmetric with SMC-6 with `rsi_14 > 50` rally context. Same `S5-RSI-DEFAULT-50-FAMILY` hazard symmetric direction.

#### Step 2-7 (compact — symmetric with SMC-6)

- Same Pattern J + same RSI-default-50 family hazard
- B671 centralized DTC>8 gate applies
- Fire-count slightly lower than SMC-6 (bearish OBs less common than bullish in upward-drift equity)
- Pattern A B630 ✅

**Options:** same as SMC-6; bundled. **My recommendation: (e) bundled.**

**Awaiting owner direction on SMC-7:** bundled with SMC-6.

---

### SMC-8. `strat_smc_discount_long` (Batch 216, dealing-range family, walked B673b)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate LONG; ICT premium/discount filter — "buy low" inside dealing range.

#### Step 1 — Read the code

[screener.py:3330-3346](backtest/signals/screener.py#L3330-L3346):

```python
def strat_smc_discount_long(s):
    """Batch 216: Premium/Discount filter - long only when price is in
    DISCOUNT zone (below 50% of recent dealing range) AND there is
    bullish structure (BOS bullish OR CHoCH bullish). ICT discipline:
    'buy low, sell high' inside the dealing range. Mitigates against
    chasing tops in an uptrend."""
    fires = (
        s.get("smc_in_discount_zone", False)
        and (s.get("smc_bos_bullish", False) or s.get("smc_choch_bullish", False))
        and s.get("price_above_ema_200", False)
    )
```

**3-gate LONG.** Combines dealing-range price-location with structural-confirmation OR-disjunct with EMA-200 regime.

| Gate | Meaning |
|---|---|
| `smc_in_discount_zone` | EVENT-shaped boundary: close in BOTTOM 50% of 50-bar dealing range (dealing_range_pct < 0.5) |
| (`smc_bos_bullish` OR `smc_choch_bullish`) | OR-disjunct: bullish BOS event within 90-bar recency OR bullish CHOCH event within 90-bar recency |
| `price_above_ema_200` | Long-term uptrend; B663-fixed |

#### Step 2 — Classify

- Category: `smc`; LONG; B291 default; last touched B663

#### Step 3 — Producer source-read + temporality

- `smc_in_discount_zone` at [smc_ict.py:406-418](backtest/signals/smc_ict.py#L406-L418) — `pct = (close - lo) / (hi - lo)` over trailing 50 bars; `pct < 0.5` → True
- `smc_bos_bullish` / `smc_choch_bullish` via `_most_recent_event_within(..., event_recency_bars=90)` — recency-windowed events (Pattern I applies)
- `price_above_ema_200` STATE
- EVENT/STATE: 1 EVENT-shaped (zone) + 1 recency-windowed-EVENT (BOS or CHOCH) + 1 STATE

**Pattern K LOOKAHEAD CONCERN:** `dealing_range_lookback=50` selects the high/low anchors over the trailing 50 bars. Identical lookahead-vector class as `compute_fibonacci` per `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT`. Producer correctly slices `ohlc.tail(50)` from a pre-filtered (engine-side `as_of`-sliced) DataFrame, but no explicit test pins this.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Premium/Discount filter ... ICT discipline 'buy low, sell high'" | ⚠ Pattern M — canonical ICT methodology; no peer-reviewed validation |
| "Mitigates against chasing tops in an uptrend" | ✅ Mechanically true — discount zone gate by construction prevents top-chasing; defensible |
| Implicit "BOS or CHOCH provides structural backing" | ⚠ **Pattern I** — 90-bar recency means the "structural backing" event could be up to 4 months stale by the time the discount-zone bar fires |

#### Step 5 — OPEN_INVESTIGATIONS grep

- **`S4-SMC-PATTERN-K-PIT-AUDIT`** (NEW B673) — `dealing_range_lookback=50` PIT verification; producer most likely correct but no explicit test
- Cross-ref `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` (active) — same lookahead-vector class

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — SMC-9 `strat_smc_premium_short`
- Economic symmetry: ✅ price-action

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-K lookahead** | dealing_range_lookback=50 needs PIT pin (symmetric with FIB-ANCHOR) | LOW-MEDIUM | Pattern K |
| **F-pattern-I 90-bar BOS/CHOCH recency** | Structural-backing event can be stale by up to 4 months; freshness gate (vol_confirms) would mitigate per B278/B262 precedent | MEDIUM | Pattern I |
| **F-pattern-J BOS/CHOCH overlap** | OR-disjunct with BOS or CHOCH primitives; SMC-8 shares structural primitives with SMC-14/15 (BOS) + SMC-16 (CHOCH) | MEDIUM | Pattern J |
| F-pattern-A | `price_above_ema_200` ✅ | ✅ SHIPPED B663 | — |
| F-fire-count | Discount zone is common (~50% of bars); BOS/CHOCH co-occurrence reduces; projected ~40-100/yr universe-wide; PASS likely | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Add `vol_confirms` (vol_spike_2x OR force_index_breakout) freshness gate per B262/B278 precedent — mitigates Pattern I stale-event concern |
| (c) Tighten dealing-range threshold to 0.4 (deep discount) — would reduce fire count, may improve signal quality |
| (d) Tighten BOS/CHOCH recency window from 90 → 30 bars (Pattern O config sweep candidate) |
| **(e) RECOMMENDED — (a) + queue PIT pin per Pattern K + cube-replay Pattern I sensitivity sweep on event_recency_bars. (b) freshness gate is a candidate Class 2 if cube shows status quo fires-many-but-low-WR.** |

**My recommendation: (e).** No code change pre-cube; queue 2 tickets (PIT pin + recency sensitivity) for post-B660 adjudication.

**Awaiting owner direction on SMC-8:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. PIT pin scope — bundle SMC-8 + SMC-9 + cross-ref `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` into a single pyramid-test batch?
3. event_recency_bars sensitivity sweep scope (Pattern O config-parameterization)

---

### SMC-9. `strat_smc_premium_short` (Batch 216, dealing-range family, walked B673b)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate SHORT; symmetric mirror of SMC-8.

#### Step 1 — Read the code

[screener.py:3349-3362](backtest/signals/screener.py#L3349-L3362):

```python
def strat_smc_premium_short(s):
    """Batch 216: Premium short - symmetric inverse of discount long.
    Price in top 50% of dealing range + bearish structure."""
    fires = (
        s.get("smc_in_premium_zone", False)
        and (s.get("smc_bos_bearish", False) or s.get("smc_choch_bearish", False))
        and s.get("below_ema_200", False)  # B630 sweep
    )
```

**3-gate SHORT.** Symmetric mirror of SMC-8.

#### Step 2-7 (compact — symmetric with SMC-8)

- Category `smc`; SHORT; B291 default; last touched B630/B663
- Producer: same dealing_range_lookback=50 (Pattern K applies)
- 1 EVENT-shaped (premium zone) + 1 recency-windowed (BOS bearish or CHOCH bearish) + 1 STATE
- **B671 centralized DTC>8 borrow-trap gate applies**
- Same Pattern I + Pattern J + Pattern K concerns as SMC-8
- Fire-count: premium zone less common in upward-drift equity than discount zone; projected ~25-70/yr universe-wide

**Options:** same as SMC-8; bundled. **My recommendation: (e) bundled with SMC-8.**

**Awaiting owner direction on SMC-9:** bundled with SMC-8.

---

### SMC-10. `strat_smc_ote_long` (Batch 216, OTE family, walked B673b)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate LONG; **NO EMA TREND FILTER** — relies on BOS/CHOCH structural-confluence as trend proxy. Optimal Trade Entry = Fib 62-79% retracement zone (ICT canonical "sweet spot").

#### Step 1 — Read the code

[screener.py:3365-3377](backtest/signals/screener.py#L3365-L3377):

```python
def strat_smc_ote_long(s):
    """Batch 216: Optimal Trade Entry long - Fibonacci 62-79%
    retracement zone after bullish CHoCH/BOS. ICT canonical 'sweet
    spot' for high-conviction trend continuation entries."""
    fires = (
        s.get("smc_ote_long_zone", False)
        and (s.get("smc_bos_bullish", False) or s.get("smc_choch_bullish", False))
    )
```

**2-gate LONG.** Most heavily-trusted "ICT sweet spot" pattern in the cluster; no explicit trend filter (relies on structural-event OR-disjunct).

| Gate | Meaning |
|---|---|
| `smc_ote_long_zone` | EVENT-shaped boundary: current retracement % in 62-79% range AND direction > 0 (bullish leg context) |
| (`smc_bos_bullish` OR `smc_choch_bullish`) | OR-disjunct: structural backdrop |

#### Step 2 — Classify

- Category: `smc`; LONG; B291 default; last touched B216

#### Step 3 — Producer source-read + temporality

- `smc_ote_long_zone` at [smc_ict.py:382-401](backtest/signals/smc_ict.py#L382-L401) — uses `_smc.retracements(ohlc, swings)` library primitive; reads last row's `Direction` (>0 = bullish leg) and `CurrentRetracement%`; True when `62 <= pct <= 79 AND direction > 0`
- Lag: 0-day point-in-time check
- BOS/CHOCH via 90-bar recency window (Pattern I applies)
- EVENT/STATE: 1 EVENT-shaped (OTE zone) + 1 recency-windowed-EVENT (BOS or CHOCH)

**Lookahead concern (Pattern K-adjacent):** `retracements` primitive reads from `_smc.swing_highs_lows(ohlc, swing_length=20)` — swing identification is point-in-time but depends on PIT-correct `ohlc` slicing.

**NO EMA REGIME GATE.** Departure from SMC-1/2/4/5/6/7/8/9/14/15/17 pattern. Justification: BOS/CHOCH OR-disjunct serves as structural trend proxy. **But** 90-bar recency means the "structural backdrop" can be 4 months stale — by which time absolute trend (EMA-200) may have flipped.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Optimal Trade Entry ... ICT canonical 'sweet spot' for high-conviction trend continuation entries" | ⚠ **Pattern M** — canonical per ICT YouTube methodology; no peer-reviewed validation. The "high-conviction" framing is overclaim per CHECKLIST (s) docstring honesty discipline. |
| Implicit "BOS/CHOCH confluence substitutes for EMA trend filter" | ⚠ **Pattern I + missing-trend-filter** — 90-bar-old BOS/CHOCH does NOT confirm CURRENT trend regime. The strategy could fire in a trend-flipped regime when the structural event is stale |
| "Fibonacci 62-79% retracement zone" | ✅ Implementation matches; 62-79% is the Murray/canonical OTE range per ICT methodology |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Cross-ref `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` (active) — OTE uses `_smc.retracements()` which internally uses swing-anchors; same lookahead-vector class
- No active investigations specific to SMC-10

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — SMC-11 `strat_smc_ote_short`
- Economic symmetry: ✅ price-action

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-missing-trend-filter** | No EMA-200 gate; BOS/CHOCH 90-bar recency may not reflect CURRENT trend; trade fires in flipped-trend regime when structural event is stale | HIGH | F1-trend |
| **F-pattern-I 90-bar staleness** | Same Pattern I as SMC-8 | MEDIUM | Pattern I |
| **F-pattern-M "high-conviction" overclaim** | ICT docstring framing not supported by peer-reviewed evidence | MEDIUM | Pattern M |
| **F-pattern-J retracements-primitive overlap** | OTE uses retracements primitive which uses swing_highs_lows; overlaps with BOS/CHOCH primitives | MEDIUM | Pattern J |
| F-fire-count | OTE zone (62-79% Fib retracement) AND BOS/CHOCH co-occurrence narrow; projected ~20-50/yr universe-wide; borderline FAIL min_trades=30 per regime | MEDIUM | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Add EMA-200 trend gate (`price_above_ema_200` LONG) — would catch the stale-BOS/CHOCH case where absolute trend has flipped. Symmetric with how most other SMC strategies handle the no-EMA case (SMC-12/13/16/18 also lack EMA gate; same critique applies; cluster-wide pattern reframe candidate) |
| (c) Tighten BOS/CHOCH recency to 30 bars (Pattern O config sweep) |
| (d) Add `vol_confirms` (vol_spike_2x OR force_index_breakout) freshness gate per B262/B278 precedent |
| (e) Cube replay branch-stratified (with/without EMA gate; with/without recency tighten) |
| **(f) RECOMMENDED — (b) + (e). The no-EMA-gate pattern is a CLUSTER-WIDE concern (SMC-10, SMC-11, SMC-12, SMC-13, SMC-16, SMC-18 all share it); proposing EMA-200 addition as a cluster-wide reframe candidate alongside cube validation is the consistent design choice. Pre-cube no code change; B673b-d remaining walks surface the same finding so the disposition can bundle.** |

**My recommendation: (f).**

**Awaiting owner direction on SMC-10:**
1. (a)/(b)/(c)/(d)/(e)/(f) — recommendation (f)
2. Whether to surface CLUSTER-WIDE EMA-gate proposal as a separate B-N batch (SMC-10/11/12/13/16/18 bundled)
3. Pattern O `event_recency_bars` config-parameterization scope

---

### SMC-11. `strat_smc_ote_short` (Batch 216, OTE family, walked B673b)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate SHORT; symmetric mirror of SMC-10.

#### Step 1 — Read the code

[screener.py:3380-3390](backtest/signals/screener.py#L3380-L3390):

```python
def strat_smc_ote_short(s):
    """Batch 216: Symmetric OTE short."""
    fires = (
        s.get("smc_ote_short_zone", False)
        and (s.get("smc_bos_bearish", False) or s.get("smc_choch_bearish", False))
    )
```

**2-gate SHORT.** Symmetric mirror of SMC-10.

#### Step 2-7 (compact — symmetric with SMC-10)

- Category `smc`; SHORT; B291 default; last touched B216
- Same NO-EMA-GATE issue as SMC-10
- Same Pattern I + Pattern J + Pattern M concerns
- **B671 centralized DTC>8 borrow-trap gate applies**
- Fire-count: ~15-40/yr universe-wide (bearish OTE less common than bullish in upward-drift equity); borderline FAIL min_trades=30

**Options:** same as SMC-10; bundled. **My recommendation: (f) bundled with SMC-10.**

**Awaiting owner direction on SMC-11:** bundled with SMC-10.

---

### SMC-12. `strat_smc_equal_highs_sweep_short` (Batch 216, liquidity-sweep family, walked B673c)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate SHORT; **NO EMA GATE**; classic ICT stop-hunt-then-reverse pattern. Pattern G low-fire-combo candidate per `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660`.

#### Step 1 — Read the code

[screener.py:3393-3404](backtest/signals/screener.py#L3393-L3404):

```python
def strat_smc_equal_highs_sweep_short(s):
    """Batch 216: Equal-highs cluster swept (taking out stops above
    cluster) + bearish FVG below = high-conviction reversal short.
    Classic ICT stop-hunt-then-reverse pattern."""
    fires = (
        s.get("smc_equal_highs_swept", False)
        and s.get("smc_fvg_bearish_active", False)
    )
```

**2-gate SHORT.** Liquidity-sweep + FVG-confluence; no EMA trend filter.

| Gate | Meaning |
|---|---|
| `smc_equal_highs_swept` | EVENT-shaped: equal-highs cluster was swept (Swept flag set; producer recency 50-bar; per B390 producer fix) |
| `smc_fvg_bearish_active` | STATE: any bearish FVG active in last 5 bars |

#### Step 2 — Classify

- Category: `smc`; SHORT; B291 default; last touched B390 (producer fix); no strategy-level changes since B216

#### Step 3 — Producer source-read + temporality

- `smc_equal_highs_swept` at [smc_ict.py:344-379](backtest/signals/smc_ict.py#L344-L379) — B390 producer fix: filter liquidity events to non-zero THEN tail(20) THEN check `Swept` flag (bar-index float; non-null = swept) AND `(current_idx - swept_val) <= 50` recency. Pre-B390 the strategy fired 0/1542 ticker-days on AAPL sample.
- `smc_fvg_bearish_active` at [smc_ict.py:157-159](backtest/signals/smc_ict.py#L157-L159) — `(recent == -1).any()` over `fvg_lookback=5` tail
- Lag: 0-day point-in-time on sweep event; FVG_active 0-5 bar tail
- EVENT/STATE: 1 recency-windowed EVENT (sweep within 50 bars) + 1 short-window STATE (FVG within 5 bars)

**Pattern O hardcoded:** `liquidity_range_pct=0.01` (1%) tolerance for equal-level cluster identification at [smc_ict.py:79](backtest/signals/smc_ict.py#L79). Hardcoded in producer; not config-driven; no empirical basis cited.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Equal-highs cluster swept + bearish FVG below = high-conviction reversal short" | ⚠ **Pattern M** — canonical per ICT YouTube methodology; no peer-reviewed validation |
| "Classic ICT stop-hunt-then-reverse pattern" | ⚠ Same Pattern M; "high-conviction" framing is overclaim per docstring honesty discipline |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B390 producer fix is current state; no successor bug
- Cross-ref `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660` — SMC-12 candidate for the existing low-fire-combo list per fire-count concern

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — SMC-13 `strat_smc_equal_lows_sweep_long`
- Economic symmetry: ✅ price-action

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-missing-trend-filter** | No EMA-200 gate; same as SMC-10/11/16/18 | HIGH | F1-trend |
| **F-low-fire-combo** | Equal-highs sweep + bearish FVG co-occurrence is RARE; B390 fix established producer correctness but fire-count projection ~5-20/yr universe-wide; HIGH RISK FAIL min_trades=30 per regime | HIGH | F4 + Pattern G |
| **F-pattern-O hardcoded** | `liquidity_range_pct=0.01` and 50-bar recency on Swept hardcoded; should be config-driven | MEDIUM | Pattern O |
| **F-pattern-J FVG overlap** | Bearish FVG active overlaps with SMC-2 FVG retest short + SMC-3 inverse FVG | MEDIUM | Pattern J |
| F-pattern-A | NO EMA gate — N/A | ✅ N/A | — |
| **F-borrow-cost** | B671 centralized DTC>8 gate applies | LOW | F5 carryover |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Add `below_ema_200` regime gate (per cluster-wide CLUSTER-WIDE EMA proposal) |
| (c) Loosen — drop the FVG-active confluence; pure liquidity-sweep SHORT |
| (d) EXPLORATORY marker pre-cube — analogous to W5/W5m; exclude from selection budget while keeping registered for cube-replay coverage |
| (e) Loosen Pattern O — increase `liquidity_range_pct` from 1% → 2% to raise equal-cluster detection rate (would raise fires; producer-side change) |
| **(f) RECOMMENDED — (a) + queue (d) EXPLORATORY marker decision for post-B660 measurement. SMC-12 is a clean Pattern G candidate per low-fire projection. Cube replay settles whether to keep as standalone or fold under (b) cluster-wide EMA proposal.** |

**My recommendation: (f).**

**Awaiting owner direction on SMC-12:**
1. (a)/(b)/(c)/(d)/(e)/(f) — recommendation (f)
2. Add SMC-12 to existing `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660` ticket as candidate
3. Pattern O `liquidity_range_pct` config-parameterization scope

---

### SMC-13. `strat_smc_equal_lows_sweep_long` (Batch 216, liquidity-sweep family, walked B673c)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate LONG; symmetric mirror of SMC-12.

#### Step 1 — Read the code

[screener.py:3407-3417](backtest/signals/screener.py#L3407-L3417):

```python
def strat_smc_equal_lows_sweep_long(s):
    """Batch 216: Equal-lows cluster swept + bullish FVG above =
    high-conviction reversal long."""
    fires = (
        s.get("smc_equal_lows_swept", False)
        and s.get("smc_fvg_bullish_active", False)
    )
```

**2-gate LONG.** Symmetric mirror of SMC-12.

#### Step 2-7 (compact — symmetric with SMC-12)

- Category `smc`; LONG; B291 default
- Same producer source (B390 fix); same Pattern O hardcoded constants
- Same missing-trend-filter + low-fire-combo + Pattern J + Pattern M concerns
- Fire-count: equal-lows sweeps slightly more common than equal-highs in upward-drift equity (selling-climax pattern); projected ~10-30/yr universe-wide; still HIGH RISK FAIL min_trades=30 per regime

**Options:** same as SMC-12; bundled. **My recommendation: (f) bundled with SMC-12.**

**Awaiting owner direction on SMC-13:** bundled with SMC-12.

---

### SMC-14. `strat_smc_bos_retest_entry` (Batch 216, structural family, walked B673c — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate dual; ICT "allow the broken level to confirm-as-support before adding risk" discipline.

#### Step 1 — Read the code

[screener.py:3420-3439](backtest/signals/screener.py#L3420-L3439):

```python
def strat_smc_bos_retest_entry(s):
    """Batch 216: BOS retest - price returns to within 0.5pct of a
    recently-broken structure level. Empirically higher hit rate than
    naive BOS continuation per ICT discipline (allow the broken level
    to confirm-as-support before adding risk)."""
    fl = (
        s.get("smc_bos_retest_long", False)
        and s.get("price_above_ema_200", False)
    )
    fs = (
        s.get("smc_bos_retest_short", False)
        and s.get("below_ema_200", False)
    )
```

**2-gate dual strategy.** Most explicit "wait-for-retest" SMC pattern.

| Direction | Gate 1 | Gate 2 |
|---|---|---|
| LONG | `smc_bos_retest_long` | `price_above_ema_200` |
| SHORT | `smc_bos_retest_short` | `below_ema_200` |

#### Step 2 — Classify

- Category: `smc`; dual via `_strat3`; B291 default; last touched B556 (producer filter-then-tail fix)

#### Step 3 — Producer source-read + temporality

- `smc_bos_retest_long` / `_short` at [smc_ict.py:299-326](backtest/signals/smc_ict.py#L299-L326) — B556 producer fix: filter `bos_events` to non-zero THEN tail(20) THEN check `abs(close - Level) / Level < 0.005` (0.5% near-test); iterate last 20 actual BOS events
- Lag: 0-day point-in-time near-test
- EVENT/STATE: 1 EVENT-shaped near-test + 1 STATE
- **Pattern O hardcoded `tol = 0.005` (0.5%)** at [smc_ict.py:310](backtest/signals/smc_ict.py#L310) — narrow tolerance; if loosened to 1% or 2%, fire-rate would materially increase

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Empirically higher hit rate than naive BOS continuation per ICT discipline" | ⚠ **Pattern M overclaim** — "empirically higher" framing implies validation; no peer-reviewed evidence cited. ICT methodology argues this internally; cube-replay against SMC-15 (BOS continuation) is the only adjudication |
| "allow the broken level to confirm-as-support before adding risk" | ✅ Defensible — retest waiting reduces breakout-failure exposure (classic price-action discipline beyond ICT) |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B556 producer fix current state
- Cross-ref `S4-SMC-PATTERN-O-CONFIG-PARAMETERIZATION` (NEW B673) — `tol = 0.005` config-driven candidate

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual
- Economic symmetry: ✅ price-action

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-O hardcoded tolerance** | `tol = 0.005` (0.5%) — narrow; sensitivity to 0.5% vs 1% vs 2% unknown; cube-replay-eligible | MEDIUM | Pattern O |
| **F-pattern-M empirical overclaim** | "higher hit rate" framing not validated; cube vs SMC-15 settles | MEDIUM | Pattern M |
| **F-pattern-J BOS overlap with SMC-15** | SMC-14 + SMC-15 both consume `smc_bos_*`; marginal contribution audit | MEDIUM | Pattern J |
| F-pattern-A | EMA-200 ✅ | ✅ SHIPPED B663 | — |
| F-fire-count | Narrow 0.5% near-test + BOS event co-occurrence; projected ~20-50/yr universe-wide per direction; borderline | MEDIUM | F4 |
| F-borrow-cost | B671 SHORT-side DTC>8 gate applies | LOW | F5 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Loosen `tol = 0.005` → `0.01` (1%) at producer — raises fires + reduces miss-rate; risk: false-retest noise |
| (c) Cube-replay Pattern O sensitivity sweep (0.5% / 1% / 2%) post-B660 |
| (d) Branch-stratified cube replay SMC-14 vs SMC-15 (BOS-retest vs BOS-continuation) — settles "higher hit rate" claim |
| **(e) RECOMMENDED — (c) + (d). No pre-cube code change; cube settles both Pattern O sensitivity AND Pattern M empirical claim simultaneously.** |

**My recommendation: (e).**

**Awaiting owner direction on SMC-14:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. Bundle SMC-14 + SMC-15 cube ablation as Pattern J flagship test for the SMC cluster (symmetric with SM-41 vs SM-6 for smart-money cluster)
3. Pattern O `tol` config-parameterization scope

---

### SMC-15. `strat_smc_bos_continuation` (Batch 210 + B278 forensic-fixed, structural family, walked B673c — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **B278 FORENSIC-FIXED CASE** — pre-B278 Tier 2 v2 showed 13 trades / 15.4% WR / -6.60% mean / -86 pp due to stale-90-bar BOS events. B278 added `vol_confirms` + RSI-direction-aligned gates symmetric with B262 SMC-3 fix.

#### Step 1 — Read the code

[screener.py:3442-3477](backtest/signals/screener.py#L3442-L3477):

```python
def strat_smc_bos_continuation(s):
    """Batch 210 ... Batch 278 (Tier 2 gate tightening 2026-05-20 owner-approved option B):
    Stage B v2 showed 13 trades / 15.4% WR / -6.60% mean / -86 pp. Root
    cause: Batch 273's event_recency_bars=90 means BOS signal stays True
    for up to 90 bars, so entries fire on stale structural breaks where
    trend may have already reversed. Added: vol_confirms (vol_spike_2x OR
    force_index_breakout) + momentum confirm (RSI direction-aligned) to
    require institutional follow-through on the BOS bar.
    """
    vol_confirms = s.get("vol_spike_2x", False) or s.get("force_index_breakout", False)
    rsi = s.get("rsi_14", 50)
    fl = (
        s.get("smc_bos_bullish", False)
        and s.get("price_above_ema_200", False)
        and vol_confirms
        and rsi > 50
    )
    fs = (
        s.get("smc_bos_bearish", False)
        and s.get("below_ema_200", False)
        and vol_confirms
        and rsi < 50
    )
```

**4-gate dual strategy.** Most heavily-gated SMC strategy post-B278 fix (4 gates per direction, same gate density as SMC-3 after its B262 fix).

| Direction | Gates |
|---|---|
| LONG | `smc_bos_bullish` + `price_above_ema_200` + `vol_confirms` + `rsi_14 > 50` |
| SHORT | `smc_bos_bearish` + `below_ema_200` + `vol_confirms` + `rsi_14 < 50` |

#### Step 2 — Classify

- Category: `smc`; dual; B291 default; last touched B278 (forensic fix); B630/B663 verified

#### Step 3 — Producer source-read + temporality

- `smc_bos_bullish` / `_bearish` via 90-bar recency window (Pattern I)
- `vol_spike_2x` + `force_index_breakout` are bar-of-fire EVENTs
- `rsi_14` STATE (today's RSI)
- EVENT/STATE: 1 recency-windowed EVENT (BOS) + 1 EVENT (vol_confirms OR) + 2 STATE (EMA + RSI)
- **F-rsi-default-50 hazard** per `S5-RSI-DEFAULT-50-FAMILY` — `rsi > 50` (LONG) / `rsi < 50` (SHORT) with default=50 means missing-data fails the gate (50 > 50 is False; 50 < 50 is False). Fail-safe ✅. Strict-inequality on default-value-AT-threshold = family member.

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Stage B v2 showed 13 trades / 15.4% WR / -6.60% mean / -86 pp" | ✅ **B278 forensic confirmed empirically** in Stage B v2 backtest. Fix is evidence-based |
| "Batch 273's event_recency_bars=90 means BOS signal stays True for up to 90 bars" | ✅ Mechanically correct per producer code |
| "vol_confirms + momentum confirm require institutional follow-through on the BOS bar" | ✅ Defensible — addresses the stale-event problem directly |
| Implicit "post-B278 fix the strategy is sound" | ⚠ **Pattern M** — B278 fixed the empirical disaster but post-fix design has not been re-validated against full-universe cube (same as SMC-3 B262); pre-B660 the fix is plausible but unproven |

#### Step 5 — OPEN_INVESTIGATIONS grep

- B278 forensic precedent IS the active concern (symmetric with B262 SMC-3); post-B660 cube replay must surface whether the post-fix design is empirically sound
- Cross-ref `S5-RSI-DEFAULT-50-FAMILY` — SMC-15 family member

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual; both directions fire under B278 fix
- Economic symmetry: ✅ price-action

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-B278 fix re-validation** | Same class as SMC-3 B262 — gate-add fix needs full-universe cube replay validation | HIGH | F1 |
| **F-rsi-default-50 family hazard** | Strict-inequality on default-50 boundary; B654 W8 precedent may apply post-cube | MEDIUM | S5-RSI-DEFAULT-50-FAMILY |
| **F-pattern-I 90-bar BOS recency** | Even post-B278 fix, the BOS event could be up to 90 bars old at fire bar; the 4-gate vol+momentum confluence partially mitigates but doesn't eliminate | MEDIUM | Pattern I |
| **F-pattern-J BOS overlap with SMC-14** | SMC-15 vs SMC-14 — BOS-continuation vs BOS-retest on same primitive | MEDIUM | Pattern J |
| F-pattern-A | EMA-200 ✅ | ✅ SHIPPED B663 | — |
| F-fire-count | Quadruple-AND gates reduce fires; post-B278 projected ~25-60/yr universe-wide per direction; borderline | MEDIUM | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo (post-B278-fix) |
| (b) Tighten BOS recency from 90 → 30 bars (producer-side; Pattern O config sweep candidate) — would address Pattern I more directly than the B278 vol_confirms workaround |
| (c) Drop RSI gate per B654 W8 precedent (S5-RSI-DEFAULT-50-FAMILY resolution option a) — would raise fires |
| (d) Cube-replay re-validation of B278 fix on full T1a universe |
| **(e) RECOMMENDED — (d) + (b) post-cube. B278 fix is the gold standard for SMC-strategy disposition; cube validates whether fix landed. Pattern O recency-tighten is the upstream fix that B278 papers-over with vol_confirms — cube-evaluate both designs.** |

**My recommendation: (e).**

**Awaiting owner direction on SMC-15:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. Pattern O `event_recency_bars` config-parameterization priority
3. Whether B278 forensic precedent should be cited cluster-wide alongside B262 as canonical gate-add disposition pattern

---

### SMC-16. `strat_smc_choch_reversal` (Batch 210, structural family, walked B673d — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate dual; **NO EMA TREND FILTER** — CHOCH + FVG-active confluence only.

#### Step 1 — Read the code

[screener.py:3480-3498](backtest/signals/screener.py#L3480-L3498):

```python
def strat_smc_choch_reversal(s):
    """Batch 210: Change of Character reversal. CHoCH marks the FIRST
    structural shift opposing the prior trend; high-conviction reversal
    setup per ICT/SMC discipline. Pairs with FVG-aligned entry."""
    fl = (
        s.get("smc_choch_bullish", False)
        and s.get("smc_fvg_bullish_active", False)
    )
    fs = (
        s.get("smc_choch_bearish", False)
        and s.get("smc_fvg_bearish_active", False)
    )
```

**2-gate dual.** CHOCH + FVG-confluence; no EMA gate.

#### Step 2 — Classify

- Category: `smc`; dual; B291 default; last touched B210/B273 (90-bar recency)

#### Step 3 — Producer source-read + temporality

- `smc_choch_bullish` / `_bearish` via 90-bar recency (Pattern I)
- `smc_fvg_bullish_active` / `_bearish_active` over 5-bar tail (`fvg_lookback=5`)
- EVENT/STATE: 2 recency-windowed events (CHOCH 90-bar + FVG 5-bar tail)
- **NO EMA REGIME GATE** — same cluster-wide concern as SMC-10/11/12/13/18

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "CHoCH marks the FIRST structural shift opposing the prior trend" | ✅ Implementation matches ICT canon |
| "high-conviction reversal setup per ICT/SMC discipline" | ⚠ **Pattern M overclaim** — "high-conviction" framing not peer-reviewed; cube-replay is only adjudication |
| Implicit "FVG confluence substitutes for EMA trend filter" | ⚠ Same missing-trend-filter concern as SMC-10/11/12/13/18 |

#### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations specific to SMC-16
- Cross-ref CLUSTER-WIDE EMA-gate proposal (Pattern carried from SMC-10)

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual
- Economic symmetry: ✅ price-action; CHOCH is a defined reversal event in both directions

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-missing-trend-filter** | No EMA-200 gate; cluster-wide pattern (SMC-10/11/12/13/16/18) | HIGH | F1-trend |
| **F-pattern-I 90-bar CHOCH staleness** | A 4-month-old CHOCH is materially less reliable than a fresh one; vol-confirmation gate would mitigate per B262/B278 precedent | MEDIUM | Pattern I |
| **F-pattern-J CHOCH + FVG overlap** | CHOCH + FVG-active confluence with SMC-3 + SMC-10 + SMC-11 + SMC-18 (all consume CHOCH or FVG primitives) | MEDIUM | Pattern J |
| **F-pattern-M "high-conviction" overclaim** | ICT framing not peer-reviewed | MEDIUM | Pattern M |
| F-fire-count | CHOCH + FVG co-occurrence narrow; projected ~15-40/yr per direction; borderline FAIL min_trades=30 per regime | MEDIUM | F4 |
| F-borrow-cost | B671 SHORT-side DTC>8 gate applies | LOW | F5 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Add EMA-200 trend gate per CLUSTER-WIDE proposal (bundled with SMC-10/11/12/13/18) |
| (c) Add `vol_confirms` freshness gate per B262/B278 precedent |
| (d) Cube-replay branch-stratified Pattern J (CHOCH-FVG overlap with SMC-3/SMC-10/SMC-11/SMC-18) |
| **(e) RECOMMENDED — (b) + (d) bundled with cluster-wide EMA proposal. SMC-16 is one of 6 no-EMA-gate SMC strategies; bundled B-N batch is the consistent design choice.** |

**My recommendation: (e).**

**Awaiting owner direction on SMC-16:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. Bundle SMC-10 + SMC-11 + SMC-12 + SMC-13 + SMC-16 + SMC-18 cluster-wide EMA proposal as single B-N batch
3. Pattern J flagship cube ablation (SMC-3 + SMC-10 + SMC-11 + SMC-16 + SMC-18 all consume CHOCH or FVG)

---

### SMC-17. `strat_smc_order_block_bounce` (Batch 210, structural family, walked B673d — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate dual; OB-active + RSI confirmation + EMA-200. **Asymmetric RSI thresholds** (45 LONG / 55 SHORT) — escapes `S5-RSI-DEFAULT-50-FAMILY` hazard.

#### Step 1 — Read the code

[screener.py:3501-3522](backtest/signals/screener.py#L3501-L3522):

```python
def strat_smc_order_block_bounce(s):
    """Batch 210: Order block bounce. Bullish OB = last opposing
    (bearish) candle before an impulse up; price returning to this zone
    acts as institutional support. Symmetric for bearish OB."""
    fl = (
        s.get("smc_ob_bullish_active", False)
        and s.get("rsi_14", 50) < 45  # pullback context
        and s.get("price_above_ema_200", False)
    )
    fs = (
        s.get("smc_ob_bearish_active", False)
        and s.get("rsi_14", 50) > 55
        and s.get("below_ema_200", False)
    )
```

**3-gate dual.** OB-active recency-windowed + asymmetric RSI + EMA-200.

| Direction | Gates |
|---|---|
| LONG | `smc_ob_bullish_active` + `rsi_14 < 45` + `price_above_ema_200` |
| SHORT | `smc_ob_bearish_active` + `rsi_14 > 55` + `below_ema_200` |

#### Step 2 — Classify

- Category: `smc`; dual; B291 default; last touched B273/B556

#### Step 3 — Producer source-read + temporality

- `smc_ob_bullish_active` / `_bearish_active` via 90-bar recency on OB primitive (Pattern I directly applies — this is the strategy that MOST consumes the recency-windowed STATE)
- `rsi_14` STATE
- EVENT/STATE: 1 recency-windowed (OB 90-bar) + 2 STATE

**Asymmetric RSI thresholds (45 / 55) ESCAPE S5-RSI-DEFAULT-50-FAMILY hazard:**
- LONG `rsi_14 < 45`: default-50 → False (50 < 45 is False) → fail-safe ✅
- SHORT `rsi_14 > 55`: default-50 → False (50 > 55 is False) → fail-safe ✅
- Both thresholds OUTSIDE the default-50 value → strict-inequality safety ✅
- Bands are tighter than canonical Wilder oversold/overbought 30/70 but defensible as "pullback context" per docstring

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Bullish OB = last opposing (bearish) candle before an impulse up" | ✅ Implementation matches ICT/SMC canon |
| "price returning to this zone acts as institutional support" | ⚠ **Pattern M** — canonical per ICT methodology; no peer-reviewed validation. Defensible at the structural-mechanic level (institutional zones DO act as support/resistance in price-action methodology generally — beyond ICT) |

#### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations specific to SMC-17
- ESCAPES `S5-RSI-DEFAULT-50-FAMILY` (asymmetric thresholds well clear of default-50)

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual
- Economic symmetry: ✅ price-action

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-I DIRECT 90-bar OB STATE** | SMC-17 is the strategy that MOST consumes the recency-windowed STATE (`smc_ob_*_active` directly); staleness exposure highest in cluster | HIGH | Pattern I |
| **F-pattern-J OB-family overlap** | SMC-17 + SMC-4/SMC-5 (breaker_block) + SMC-6/SMC-7 (mitigation_block) all consume OB primitive at different stages; marginal contribution audit | MEDIUM | Pattern J |
| **F-asymmetric RSI thresholds — POSITIVE NOTE** | 45/55 thresholds escape S5-RSI-DEFAULT-50 family hazard ✅; pullback context defensible | INFO / ✅ POSITIVE | F-rsi |
| **F-pattern-M "institutional support" framing** | Defensible at structural-mechanic level; not as overclaim-heavy as "high-conviction" framing | LOW | Pattern M |
| F-pattern-A | EMA-200 LONG ✅ + below_ema_200 SHORT ✅ | ✅ SHIPPED B663 + B630 | — |
| F-fire-count | OB-active 90-bar STATE is common; RSI band + EMA narrows; projected ~30-80/yr per direction; PASS likely | INFO | F4 |
| F-borrow-cost | B671 SHORT-side DTC>8 gate applies | LOW | F5 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Tighten BOS-active recency window from 90 → 30 bars (Pattern O config sweep) — would address direct Pattern I exposure |
| (c) Add `vol_confirms` freshness gate per B262/B278 precedent |
| (d) Cube-replay Pattern J ablation (SMC-17 vs SMC-4/SMC-5/SMC-6/SMC-7) — settles OB-family marginal contribution |
| **(e) RECOMMENDED — (a) + (b) post-cube + (d) flagship OB-family ablation. SMC-17's direct 90-bar STATE consumption makes it the cleanest specimen for Pattern I sensitivity test. (b) is the cluster-wide producer-side fix; (d) is the Pattern J adjudication.** |

**My recommendation: (e).**

**Awaiting owner direction on SMC-17:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. Pattern I 90-bar `event_recency_bars` sensitivity sweep priority
3. OB-family Pattern J flagship cube ablation (SMC-4 + SMC-5 + SMC-6 + SMC-7 + SMC-17)

---

### SMC-18. `strat_smc_liquidity_sweep_reversal` (Batch 210, liquidity-sweep family, walked B673d — DUAL)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate dual; **NO EMA TREND FILTER**; liquidity-sweep + CHOCH-or-BOS confluence. Pattern N internal multi-test concern (combinatorial overlap with SMC-12/SMC-13 sweeps + SMC-16 CHOCH + SMC-14/SMC-15 BOS).

#### Step 1 — Read the code

[screener.py:3524-3543](backtest/signals/screener.py#L3524-L3543):

```python
def strat_smc_liquidity_sweep_reversal(s):
    """Batch 210: Liquidity sweep reversal. Price sweeps a cluster of
    equal highs/lows (taking out stops), then reverses. Classic ICT
    'stop hunt' pattern. Pairs with CHoCH for additional reversal
    confirmation."""
    fl = (
        s.get("smc_liquidity_swept_dn", False)  # lows swept -> bullish reversal
        and (s.get("smc_choch_bullish", False) or s.get("smc_bos_bullish", False))
    )
    fs = (
        s.get("smc_liquidity_swept_up", False)
        and (s.get("smc_choch_bearish", False) or s.get("smc_bos_bearish", False))
    )
```

**2-gate dual.** Liquidity-sweep + CHOCH-OR-BOS structural confluence; no EMA gate.

| Direction | Gates |
|---|---|
| LONG | `smc_liquidity_swept_dn` (lows swept) + (`smc_choch_bullish` OR `smc_bos_bullish`) |
| SHORT | `smc_liquidity_swept_up` (highs swept) + (`smc_choch_bearish` OR `smc_bos_bearish`) |

#### Step 2 — Classify

- Category: `smc`; dual; B291 default; last touched B273 (recency fix) / B390 (liquidity producer fix)

#### Step 3 — Producer source-read + temporality

- `smc_liquidity_swept_dn` / `_up` via 90-bar recency on liquidity primitive (Pattern I — sweep event windowed)
- `smc_choch_*` and `smc_bos_*` via 90-bar recency (Pattern I)
- EVENT/STATE: 3 recency-windowed events (sweep 90-bar + CHOCH 90-bar OR BOS 90-bar) + 0 STATE
- **NO EMA REGIME GATE** — cluster-wide concern

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Price sweeps a cluster of equal highs/lows (taking out stops), then reverses" | ✅ Mechanically matches; defensible at price-action level beyond ICT |
| "Classic ICT 'stop hunt' pattern" | ⚠ **Pattern M** — canonical per ICT YouTube methodology; no peer-reviewed validation |
| "Pairs with CHoCH for additional reversal confirmation" | ⚠ Pattern N — CHOCH-OR-BOS confluence overlaps with SMC-16 (CHOCH+FVG) + SMC-14/15 (BOS); marginal contribution unknown pre-cube |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Cross-ref `S4-SMC-CLUSTER-PATTERN-N-INTRA-CLUSTER-COLLINEARITY` (NEW B673) — SMC-18 is the cluster's MOST overlap-heavy strategy (liquidity + CHOCH + BOS = 3 of 7 primitives)
- B390 producer fix is current state

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Already dual
- Economic symmetry: ✅ price-action; both upside + downside stop-hunts are valid

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-missing-trend-filter** | No EMA-200 gate; cluster-wide pattern | HIGH | F1-trend |
| **F-pattern-I TRIPLE 90-bar exposure** | Liquidity sweep + CHOCH OR BOS — ALL THREE primitives use 90-bar recency; SMC-18 has the highest staleness exposure in the cluster | HIGH | Pattern I |
| **F-pattern-N MAXIMUM OVERLAP** | SMC-18 consumes liquidity + CHOCH + BOS primitives — 3 of 7 primitives → cluster's most overlap-heavy strategy | HIGH | Pattern N |
| **F-pattern-J cross-strategy overlap** | SMC-18 + SMC-12/13 (liquidity sweeps) + SMC-16 (CHOCH+FVG) + SMC-14/15 (BOS) — quad-strategy overlap | HIGH | Pattern J |
| **F-pattern-M ICT framing** | Stop-hunt mechanic defensible at price-action level | LOW-MEDIUM | Pattern M |
| F-fire-count | Liquidity-sweep + CHOCH/BOS triple-event recency-windowed; projected ~25-60/yr per direction; modest PASS likely | INFO | F4 |
| F-borrow-cost | B671 SHORT-side DTC>8 gate applies | LOW | F5 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Add EMA-200 trend gate per CLUSTER-WIDE proposal |
| (c) Add `vol_confirms` freshness gate per B262/B278 precedent |
| (d) Pattern I recency tighten (90 → 30 bars on producer) — most direct staleness fix |
| (e) Cube-replay branch-stratified Pattern N + Pattern J ablation — SMC-18 vs SMC-12/13 vs SMC-16 vs SMC-14/15 |
| **(f) RECOMMENDED — (b) + (e). SMC-18 is the cluster's flagship Pattern N specimen; cube ablation against the 5 overlapping strategies is the highest-leverage SMC cluster test. EMA gate addition is the cluster-wide proposal. Pre-cube no producer change; post-cube the recency tighten (d) is the cleanest Pattern I fix if cube shows staleness damage.** |

**My recommendation: (f).**

**Awaiting owner direction on SMC-18:**
1. (a)/(b)/(c)/(d)/(e)/(f) — recommendation (f)
2. SMC-18 as Pattern N + Pattern J flagship ablation specimen — confirm scope
3. Cluster-wide EMA proposal bundle priority

---

## Outstanding queue tickets surfaced (SMC cluster)

| Ticket slug | Status | Source |
|---|---|---|
| `S4-SMC-CLUSTER-PATTERN-J-CUBE-ABLATION` (NEW) | DEFERRED-POST-B660-CUBE | Pattern J primitive overlap across all 18 strategies — needs cube-replay marginal-contribution audit symmetric with `S5-13F-SLEEVE-MARGINAL-CONTRIBUTION-TEST` |
| `S4-SMC-CLUSTER-PATTERN-N-INTRA-CLUSTER-COLLINEARITY` (NEW) | DEFERRED-POST-B660-CUBE | 24 cells on 7 primitives; intra-cluster effective-test-count audit |
| `S4-SMC-PATTERN-K-PIT-AUDIT` (NEW) | PENDING-PIT-AUDIT | SMC-8/9 dealing_range_lookback=50 lookahead-vector class; symmetric with S4-FIB-ANCHOR-LOOKAHEAD-AUDIT |
| `S4-SMC-PATTERN-O-CONFIG-PARAMETERIZATION` (NEW) | DEFERRED-NEAR-TERM | event_recency_bars=90 + dealing_range_lookback=50 + tol=0.005 + liquidity_range_pct=0.01 hardcoded; move to config.py for cube sensitivity sweeps |
| `S4-SMC-B262-FIX-CUBE-REVALIDATION` (NEW) | DEFERRED-POST-B660-CUBE | SMC-3 post-B262-fix design has not been validated against full-universe cube; gate of B262 forensic precedent's empirical claim |
| `S4-SMC-PATTERN-M-QUANTUM-ALGO-AUDIT` (NEW) | DEFERRED-POST-B660-CUBE | Per-strategy contribution to Quantum Algo Mar 2026 61% WR / 2.17 PF claim is unknown; cube replay against T1a 503 names is the only adjudication |
| `S5-RSI-DEFAULT-50-FAMILY` (EXISTING) | DEFERRED-STAGE-5 | SMC-6 + SMC-7 are family members |
| `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660` (EXISTING) | DEFERRED-POST-B660-MEASUREMENT-EXPLICIT-OWNER-ROUND-2-HOLD | SMC-12 + SMC-13 (equal-highs/lows sweep) candidates for the existing low-fire-combo list |
| `S5-MARGINAL-CONTRIBUTION-SCORING` (EXISTING) | DEFERRED-STAGE-5 | SMC cluster is the second-highest-leverage application of C3 methodology after the smart-money 13F sleeve test |

---

## Cluster-wide methodology references

- **Producer:** [backtest/signals/smc_ict.py](backtest/signals/smc_ict.py) — wraps `vendored/smartmoneyconcepts/smartmoneyconcepts.py` (joshyattridge/smart-money-concepts under DEC-508 Phase A)
- **Strategies:** [backtest/signals/screener.py:3208-3543](backtest/signals/screener.py#L3208-L3543) — 18 functions
- **Forensic precedents:** B262 (inverse_fvg gate-add post-1A-alpha forensic; 95%-loss fix), B278 (bos_continuation gate-add); B273 (event_recency window fix); B390 (liquidity producer filter-then-tail fix); B556 (FVG + OB producer filter-then-tail fix); B555 (OPT-C panel cache); B458 (silent-failure logging); B630 (below_ema_200 producer-additive sweep); B663 (Pattern A WAVE 1 ema_200 default-True → False sweep); B671 (centralized SHORT borrow-trap gate via inspect-frame consult)
- **Owner-decision tooling reference:** B570 (Stage 4 owner-decision tool — set 5 SMC strategies to "Deferred" status via tool, NOT via per-strategy 7-step walk per CHECKLIST #105)
- **Vendored library:** [vendored/smartmoneyconcepts/smartmoneyconcepts.py](vendored/smartmoneyconcepts/smartmoneyconcepts.py) — single-point-of-failure for all 18 strategies (Pattern L)
- **Unaudited empirical citation:** Quantum Algo Mar 2026 backtest (61% WR / 2.17 PF / +2.27R; 10 assets; 2,600 trades; 26 months) — see Pattern M
- **Cluster status sequencing:** PENDING B660 measured-fire-count + B668 cube replay + B669 survivorship execution. No empirical disposition pre-B660 per `feedback_no_rushing_per_strategy_tweak` + B665 foundational re-prioritization commitment.

---

## B673 cluster walk status

| Item | Status |
|---|---|
| Doc infrastructure (header + adaptations + inventory + patterns + state table) | ✅ B673 |
| Per-strategy walks SMC-1 + SMC-2 + SMC-3 + SMC-4 + SMC-5 + SMC-6 + SMC-7 (7 walks at full template density) | ✅ B673 |
| Per-strategy walks SMC-8 + SMC-9 + SMC-10 + SMC-11 (sub-clusters C + D) | ✅ B673b |
| Per-strategy walks SMC-12 + SMC-13 + SMC-14 (sub-cluster E + structural F lead-in) | ✅ B673c |
| Per-strategy walks SMC-15 + SMC-16 + SMC-17 + SMC-18 (sub-cluster F completion) | ✅ B673d |
| External reviewer pass | ⏳ post-walk-completion |
| Cluster-wide post-walk findings synthesis | ⏳ post-reviewer |

**Cumulative B673: 18 of 18 walks fully expanded. CLUSTER WALK COMPLETE.**

## B673 cluster walk completion wrap-up

> All 18 SMC pure price-action cluster strategies now have full pivot-doc-template per-walk coverage:
>
> - **Sub-cluster A — FVG family (3):** SMC-1 ✅ + SMC-2 ✅ + SMC-3 ✅ (B262 forensic-fixed)
> - **Sub-cluster B — OB family (4):** SMC-4 ✅ + SMC-5 ✅ + SMC-6 ✅ + SMC-7 ✅
> - **Sub-cluster C — dealing range (2):** SMC-8 ✅ + SMC-9 ✅ (Pattern K lookahead)
> - **Sub-cluster D — OTE family (2):** SMC-10 ✅ + SMC-11 ✅ (no EMA gate)
> - **Sub-cluster E — liquidity sweep (3):** SMC-12 ✅ + SMC-13 ✅ + SMC-18 ✅
> - **Sub-cluster F — BOS/CHOCH structural (4):** SMC-14 ✅ + SMC-15 ✅ (B278 forensic-fixed) + SMC-16 ✅ + SMC-17 ✅
>
> **Total fully-expanded: 18 of 18.**

### Bundled disposition recommendations summary

| Pattern | Strategies | Disposition |
|---|---|---|
| **A (default-True silent-gap)** | All 18 (12 EMA-consumers) | ✅ B663/B630 sweep verified clean for all consumers |
| **I (90-bar recency staleness)** | SMC-3 (B262 vol_confirms mitigates), SMC-4/5 (filter-then-tail direct), SMC-6/7 (filter-then-tail direct), SMC-8/9 (90-bar BOS/CHOCH), SMC-10/11 (90-bar BOS/CHOCH), SMC-12/13/18 (90-bar sweep + CHOCH/BOS), SMC-14 (BOS Level near-test), SMC-15 (B278 vol_confirms mitigates), SMC-16 (90-bar CHOCH), SMC-17 (DIRECT 90-bar OB STATE) | Cube replay sensitivity sweep on `event_recency_bars=90` post-B660; Pattern O config-parameterization for empirical sensitivity test |
| **J (primitive overlap)** | All 18; flagship ablations: SMC-1/2 vs SMC-6/7 vs SMC-17 (FVG vs OB) + SMC-14 vs SMC-15 (BOS-retest vs BOS-continuation) + SMC-3 vs SMC-10/11 vs SMC-16 vs SMC-18 (CHOCH+FVG vs OTE vs CHOCH+FVG vs liquidity-sweep) | Cube replay marginal-contribution scoring per `S5-MARGINAL-CONTRIBUTION-SCORING` C3 |
| **K (dealing_range lookahead)** | SMC-8 + SMC-9 | PIT pin queued symmetric with `S4-FIB-ANCHOR-LOOKAHEAD-AUDIT` |
| **L (vendored library SPOF)** | All 18 | Monitor B458 silent-failure logging; library version pin |
| **M (Quantum Algo unaudited)** | All 18 | Cube replay against T1a 503 names + multi-testing correction (B667+B668 already shipped) is the only adjudication |
| **N (intra-cluster collinearity)** | 24 cells on 7 primitives; SMC-18 is max-overlap specimen (3 of 7 primitives) | Cube ablation post-B660 |
| **O (hardcoded tolerances)** | event_recency_bars=90 (12 strategies); dealing_range_lookback=50 (SMC-8/9); tol=0.005 (SMC-14); liquidity_range_pct=0.01 (SMC-12/13) | Config-parameterization for sensitivity sweep |
| **Missing-trend-filter (cluster-wide)** | SMC-10, SMC-11, SMC-12, SMC-13, SMC-16, SMC-18 (6 of 18) | CLUSTER-WIDE EMA-gate addition proposal as bundled B-N batch |
| **B262/B278 forensic-fix re-validation** | SMC-3 + SMC-15 | Post-B660 cube replay validates whether gate-add fixes landed empirically |
| **RSI-default-50 family** | SMC-6 + SMC-7 (strict-inequality on default-50 boundary) | Cross-ref existing `S5-RSI-DEFAULT-50-FAMILY` ticket; B654 W8 precedent (drop gate) candidate post-cube |

### Queue tickets surfaced (recap)

- `S4-SMC-CLUSTER-PATTERN-J-CUBE-ABLATION` (NEW B673)
- `S4-SMC-CLUSTER-PATTERN-N-INTRA-CLUSTER-COLLINEARITY` (NEW B673)
- `S4-SMC-PATTERN-K-PIT-AUDIT` (NEW B673)
- `S4-SMC-PATTERN-O-CONFIG-PARAMETERIZATION` (NEW B673)
- `S4-SMC-B262-FIX-CUBE-REVALIDATION` (NEW B673; extend to SMC-15 B278 fix)
- `S4-SMC-PATTERN-M-QUANTUM-ALGO-AUDIT` (NEW B673)
- `S4-SMC-CLUSTER-WIDE-EMA-GATE-PROPOSAL` (NEW B673d — 6 strategies bundled)
- `S5-RSI-DEFAULT-50-FAMILY` (EXISTING; SMC-6 + SMC-7 family members)
- `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660` (EXISTING; SMC-12 + SMC-13 candidates)
- `S5-MARGINAL-CONTRIBUTION-SCORING` (EXISTING; SMC = 2nd-highest application)

---

## B680 Self-Critique Iteration 2 — Cross-Cutting Feasibility Findings

> **Status (B680 self-critique iteration 2026-06-10):** owner directive *"Just update all docs"* — proceed with adversarial self-critique in lieu of external reviewer pass. Findings below are produced by Claude doing a 2nd-pass adversarial read of the cluster doc against the same critique-axis framework that the external reviewer applied to smart-money cluster (B673 CC1-CC7). Findings are severity-ordered + producer-code-grounded where applicable.

### Cross-cutting feasibility findings (Claude self-critique 2026-06-10)

| # | Finding | Verification | Severity | Status |
|---|---|---|---|---|
| **CC-A** | **Engine entry mechanism mismatched to recency-windowed signals.** Pattern I 90-bar staleness means a sweep / BOS / CHOCH / OB-active signal can be 4 months old at the bar of fire. Engine enters next-day-open AFTER the signal-bar — adding another 1-day lag. **Total worst-case entry lag = ~91 trading days = ~4.4 calendar months from the actual market-structure event.** The thesis that "institutional zones act as support/resistance" loses force at this lag; institutions that placed an OB 4 months ago have either been filled, repositioned, or been overwritten by newer flow. SMC-17 (`strat_smc_order_block_bounce`) is the cleanest specimen — it consumes `smc_ob_*_active` STATE directly with no freshness gate. **Realized return per cube replay will almost certainly UNDERSHOOT the Quantum Algo Mar 2026 sample's reported +2.27R because that sample likely had tighter recency parameters or non-realistic entry timing.** | ✅ Confirmed by reading [smc_ict.py:81](backtest/signals/smc_ict.py#L81) `event_recency_bars=90` + producer comment lines 51-72 acknowledging detection lag | **HIGH** | NEW (carry to existing `S4-SMC-PATTERN-O-CONFIG-PARAMETERIZATION` ticket as cube-sensitivity-sweep priority) |
| **CC-B** | **B262 forensic-fix re-validation gates the entire cluster.** SMC-3 `strat_smc_inverse_fvg` original design fired 478 trades = 40% of all flow with 24.7% WR = **−1659pp = ~95% of aggregate loss in Phase 1A-alpha** before B262 added regime + volume gates. If this single strategy could cause 95% of aggregate loss undetected in a Phase 1A-alpha run, **how many of the 17 unwalked-by-cube SMC strategies have similar latent failure modes that the gating + walk discipline hasn't caught?** The walks surfaced Pattern R / Q / N / etc. but the B262 disaster was caught by FORENSIC observation, not by walk methodology. The walk methodology improved post-B262 (B273/B390/B556/B663) but the cluster still hasn't had a full-universe cube re-validation pass — the SMC-3 post-fix design itself is unproven on T1a 503 names. | ✅ Confirmed by reading [screener.py:strat_smc_inverse_fvg docstring](backtest/signals/screener.py) | **HIGH** | NEW — cross-ref `S4-SMC-B262-FIX-CUBE-REVALIDATION` ticket EXTENDED |
| **CC-C** | **Quantum Algo Mar 2026 backtest is fundamentally under-powered as cluster validation.** Cited as collective methodology evidence in producer docstring lines 19-22: 10 assets / 2,600 trades / 26 months / 61% WR / 2.17 PF / +2.27R. **Statistical power analysis:** 2,600 trades / 18 SMC strategies = ~144 trades per strategy on average; with 6 of 18 strategies having NO EMA gate (likely lower fire count) and 5 of 18 being Pattern G fire-starve risks (SMC-12/13/14/15/16), the per-strategy sample is likely 50-200 trades. **At ~150 trades per strategy, the 95% CI on win rate is ±8 percentage points; the cited 61% WR could be anywhere from 53% to 69% — overlapping coin-flip.** Sample is 10 assets — likely the most liquid / longest-history / most-followed names where ICT patterns are most retail-popularized + therefore most arbitraged. Sample is 26 months ~ 2-2.5 years — captures one bull-cycle / one minor pullback, NOT a full regime cycle. **Methodology citation is statistically meaningless for our purposes.** Cube replay on T1a 503 / 6 years / multi-regime is the only adjudication. | ✅ Backtest claims in producer docstring lines 19-22; statistical inference straightforward | **HIGH** | NEW `S4-SMC-PATTERN-M-QUANTUM-ALGO-CITATION-RETRACT` |
| **CC-D** | **Effective hypothesis count ≈ 7, not 18 — the cluster massively inflates multi-testing budget.** 18 SMC strategies on 7 primitives (FVG / OB / BOS / CHOCH / liquidity-sweep / dealing-range / OTE-retracement). C2 multi-testing correction at B667/B668 ships with `len(EXPLORATORY_STRATEGIES) = 2` excluded but NO grouping for SMC-cluster reskins. **Net effect: SMC cluster consumes 18 hypothesis-test slots in the family-wise correction when it should consume ~7.** This inflates the deflated-Sharpe haircut for EVERY OTHER strategy in the system. Cross-cluster Pattern N with ICT (Turtle Soup + Judas Swing × 4 also consume liquidity_swept_* and CHOCH/BOS primitives) makes this WORSE: combined ICT + SMC effective N for shared primitives ≈ 7, but registry shows 30 strategies. **C2 correction needs hierarchical grouping per `S4-B673-CC7-EFFECTIVE-HYPOTHESIS-COUNT-WITHIN-CLUSTER` ticket EXTENDED.** | ✅ Inherent to cluster's structure | **HIGH** | NEW — extend existing CC7 ticket |
| **CC-E** | **SMC-1/2 (FVG retest) and SMC-4/5 (breaker block) have identical structure: zone-active + EMA — but FVG zone and OB zone are correlated.** FVG (3-bar imbalance) and OB (last opposing candle before impulse) detect different EVENTS but at the SAME structural inflection points — both fire when price has made a strong move + then retraces into the prior-imbalance region. **Pattern J primitive overlap is even tighter than the walk doc admits.** Cube ablation will likely show SMC-1 + SMC-4 are 70-80% correlated on fire events. The walk doc's Pattern J framing is correct but understates the magnitude. | Inferred from producer logic at smc_ict.py lines 174-205 + 244-272 | MEDIUM-HIGH | NEW — `S4-SMC-FVG-OB-FIRE-CORRELATION-PRE-CUBE-AUDIT` |
| **CC-F** | **The "no peer-reviewed literature" framing applies to ICT methodology — but the SMC PATTERNS THEMSELVES (FVG / OB / liquidity sweep / order flow) have been observed independently in market microstructure literature.** This is a partial defense: while Inner Circle Trader has no peer-reviewed publications, the underlying market-microstructure phenomena have been documented by Easley + O'Hara (information-based microstructure), Madhavan (market-making models), Hasbrouck (order-flow imbalance). The ICT/SMC framework is a TRADER-FACING wrapper around real microstructure phenomena. **Pattern Q applies to ICT METHODOLOGY but not to the SIGNAL CLASSES.** This nuance is missing from the walks. | Microstructure literature; partial cluster-positive note | INFO / partial defense | NEW — `S4-SMC-MICROSTRUCTURE-LITERATURE-NUANCE-DOCSTRING` |
| **CC-G** | **6 of 18 strategies lacking EMA-200 trend gate is a STRUCTURAL design pattern, not an oversight — the walks surfaced this but didn't engage with WHY.** SMC-10/11 (OTE) + SMC-12/13 (equal-sweep) + SMC-16 (CHOCH+FVG) + SMC-18 (liquidity+CHOCH/BOS) all rely on BOS/CHOCH/FVG structural-confluence as the "trend proxy" — the ICT methodology's INTERNAL claim is that structural breaks + flow events ARE the trend signal; EMA is a lagging confirmation. **Adding EMA-200 gate would either (a) violate ICT methodology consistency or (b) implicitly admit ICT methodology is insufficient.** Cluster-wide EMA proposal (existing ticket) is a methodology-conflict that needs explicit framing. | Inferred from walk methodology adaptations + ICT literature | MEDIUM | NEW — `S4-SMC-CLUSTER-WIDE-EMA-PROPOSAL-METHODOLOGY-CONFLICT-FRAMING` |

### Per-strategy reframings (Claude self-critique)

| Strategy | Walk disposition | Self-critique reframing | Action |
|---|---|---|---|
| **SMC-3** `strat_smc_inverse_fvg` | RECOMMENDED (d) — B262 fix cube re-validation | **B262 fix's empirical validation is the CLUSTER'S GATE not just SMC-3's.** If post-B660 cube shows the B262 fix landed, it sets a positive precedent for forensic-driven gating across SMC strategies. If it didn't land, the cluster's "gating not deleting" methodology is brittle. Promote SMC-3 cube re-validation from per-strategy ticket to CLUSTER-CRITICAL gate. | Elevate ticket priority |
| **SMC-17** `strat_smc_order_block_bounce` | RECOMMENDED (e) — flagship Pattern I sensitivity sweep | **DIRECT 90-bar OB STATE consumption + 3-gate composition makes SMC-17 the cluster's worst Pattern I exposure case.** Walk noted this but understates: SMC-17's structural failure mode is "buy because of an OB from 4 months ago" — empirically untenable in fast-moving markets. **Pre-B660 fire-count projection of ~30-80/yr is likely WRONG-HIGH** because the 90-bar window is so loose; cube will reveal high fire count + low WR. | Promote to PATTERN-I FLAGSHIP TEST |
| **SMC-8/SMC-9** `strat_smc_discount/premium_*` | RECOMMENDED (e) — PIT pin + recency sensitivity | **dealing_range_lookback=50 PIT integrity is the ONLY structural lookahead vector in the cluster.** Walk identified Pattern K but didn't propose immediate PIT test. **Should ship pyramid test BEFORE cube** to avoid contaminating cube data with possible lookahead. | Bring PIT pin in-batch (pre-cube) |
| **SMC-12/SMC-13** equal-sweep | RECOMMENDED (f) — Pattern G EXPLORATORY | **B390 producer fix established empirical correctness; pre-B390 fired 0/1542 ticker-days on AAPL.** The post-fix design is unvalidated; combined with low fire count (~5-20/yr) this is the cluster's worst statistical-power case. Strong candidate for EXPLORATORY-or-DELETE per `project_no_apriori_strategy_pruning` override + W5/W5m precedent. | Priority for Pattern G review |

### Net effect on B673 walk dispositions

- **Pattern F audit (existing ticket)** SCOPE EXPANDED: must include FVG-OB fire-correlation test per CC-E
- **Pattern M unaudited-Quantum-Algo (existing ticket)** ELEVATED to citation-retraction action; not just "audit later"
- **Cluster-wide EMA proposal (existing ticket)** REFRAMED: it's a methodology-conflict not a simple oversight per CC-G
- **C2 multi-testing correction (existing ticket S5-MULTIPLE-TESTING-CORRECTION B667/B668)** must add SMC-cluster hierarchical grouping per CC-D
- **PIT integrity audit (Pattern K)** PROMOTED to pre-cube ship-required per per-strategy reframing on SMC-8/9
- **SMC-3 B262 fix re-validation** ELEVATED from per-strategy to CLUSTER-CRITICAL gate

### Queue tickets surfaced by self-critique (B680)

- `S4-SMC-PATTERN-M-QUANTUM-ALGO-CITATION-RETRACT` (HIGH; CC-C)
- `S4-SMC-FVG-OB-FIRE-CORRELATION-PRE-CUBE-AUDIT` (MEDIUM-HIGH; CC-E)
- `S4-SMC-MICROSTRUCTURE-LITERATURE-NUANCE-DOCSTRING` (INFO; CC-F partial defense)
- `S4-SMC-CLUSTER-WIDE-EMA-PROPOSAL-METHODOLOGY-CONFLICT-FRAMING` (MEDIUM; CC-G)
- `S4-SMC-PATTERN-K-PIT-PIN-PRE-CUBE-REQUIRED` (MEDIUM-HIGH; per-strategy reframing on SMC-8/9)
- `S4-SMC-3-B262-CUBE-REVALIDATION-CLUSTER-CRITICAL-GATE` (HIGH; per-strategy reframing on SMC-3)
- `S4-SMC-17-PATTERN-I-FLAGSHIP-TEST` (HIGH; per-strategy reframing on SMC-17)

---

## B679 Iteration 2 Preparation — Review Solicitation Guide

> **Status (post-B679 format alignment):** this doc is READY FOR EXTERNAL REVIEWER + OWNER FEEDBACK on Iteration 2. The smart-money cluster doc received 2 review rounds and was substantially improved by each (B669 cluster-walk critique → 7 findings → B669 docstring fix + Pattern F + B670 deletions; B673 cross-cutting feasibility CC1-CC7 → B674 incorporation with 12 NEW EXECUTION_QUEUE tickets). The SMC cluster doc is at the same maturity stage as smart-money was post-B669 — READY FOR YOUR 2ND-WAVE FEASIBILITY CRITIQUE.
>
> **Recommended review structure (parallel to B673 smart-money review):**
>
> | Review axis | What to look for in SMC | Smart-money parallel (B673 CC-class) |
> |---|---|---|
> | **CC-A: Engine entry mechanism feasibility** | Daily-bar next-open after `event_recency_bars=90` staleness; SMC primitives detect 20-80 bars late then can fire up to 90 bars later — total lag could be 4-5 months. What's the capturable fraction of any "institutional re-entry" alpha when the engine enters next-bar-open after a multi-month-old signal? | CC1 (M&A target gap) |
> | **CC-B: Vendored library / producer integrity** | joshyattridge/smartmoneyconcepts library has no peer-review; multiple producer-side fixes (B273/B390/B555/B556) suggest known bug rate; what's the SMC equivalent of Quiver PIT integrity audit? | CC4 (Quiver PIT) |
> | **CC-C: ICT methodology academic standing** | Quantum Algo Mar 2026 cited as collective methodology evidence is unaudited 10-asset / 2,600-trade / 26-month sample — sample size is severely under-powered for 18-strategy backtest; the methodology has NO peer-reviewed publications. Magnitude overclaim analog to CC6 | CC6 (pre-crowding magnitude decay) |
> | **CC-D: Effective hypothesis count** | 18 strategies on 7 primitives (FVG / OB / BOS / CHOCH / liquidity / dealing-range / OTE-retracement) — effective N ≈ 7 not 18. C2 multi-testing correction must treat reskins as near-duplicates | CC7 (effective N ≈ 4) |
> | **CC-E: Per-strategy feasibility reframings** | SMC-3 inverse_fvg post-B262-fix has NOT been re-validated under full-universe cube; the original disaster (95% aggregate loss) means the fix is empirically critical; SMC-8/9 dealing_range_lookback=50 PIT integrity unverified; SMC-12/13 equal_*_swept rare-event fire-count concern (Pattern G) | SM-4 / SM-5 / SM-18+19 reframings |
> | **CC-F: Cross-cluster registry concerns** | 4 of 12 ICT strategies (Turtle Soup + Judas Swing) cross-cluster-consume SMC primitives — Pattern L SPOF + Pattern I 90-bar staleness transmit. Pattern N cross-cluster ablation should include both clusters | Pattern H carry from smart-money |
>
> Provide feedback in the format of B673 review (severity-ranked) and B679 will incorporate as B679-incorporation batch symmetric with B674 smart-money pattern. Status fields to update post-review: "Reviewer findings response matrix" + add "B679 Cross-Cutting Feasibility Findings (External Reviewer 2nd-Wave)" section.

---

## Cross-cluster status snapshot (post-B679 — index at [STAGE_4_CLUSTER_WALKS_INDEX.md](STAGE_4_CLUSTER_WALKS_INDEX.md))

8 cluster docs / ~138 strategies covered across the cluster-walk initiative. Review status:

| Cluster | Strategies | Owner review | Iteration 2 ready |
|---|---|---|---|
| Pivot | ~10 | ✅ 2 rounds | (already iterated) |
| Trend | ~12 | ✅ Companion | (already iterated) |
| Smart-money | 41 | ✅ 2 rounds (B669 + B673 → B674) | (already iterated) |
| **SMC** | **18** | **❌ AWAITING — this doc** | **READY for B673 2nd-wave-style critique** |
| ICT | 12 | ❌ AWAITING | READY |
| Breakout | 19 | ❌ AWAITING | READY |
| Event-driven | 10 | ❌ AWAITING | READY |
| Chart+Candle | 16 | ❌ AWAITING | READY |
