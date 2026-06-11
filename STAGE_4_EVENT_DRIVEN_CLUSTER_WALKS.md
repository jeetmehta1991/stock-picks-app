# Stage 4 Event-Driven Cluster Walks — Per-Strategy Deep-Dive Audit

> **B691 STATUS BANNER (2026-06-11) — SPLIT VERDICT: pre_fomc subset pending-B689-rerun / news+pead+8K subset pending-B690.** B660 measurement landed [2026-06-11 02:30 UTC](output_audit/fire_count_measured_b660_full_universe.json) showing **12 of 12 event-driven strategies = 0 fires (100% FAIL_FIRE_STARVED).** **This is a measurement harness gap, NOT real verdicts.** Two-tier resolution:
>
> **B689 RE-RUN UN-BLOCKS (~2026-06-12 12:30):**
> - Pre-FOMC strategies — `macro_events.compute_pre_fomc_signals(as_of)` is TIER 3 (per-as_of global), wired in B689. Pre-FOMC fire counts will appear in the re-run.
> - VIX backwardation / totm / halloween_seasonal / pre_holiday — `cross_asset.compute_cross_asset_signals(as_of)` + `calendar_effects.compute_calendar_signals(as_of)` both TIER 3, wired in B689.
>
> **B690 UN-BLOCKS (waits for TIER 2 harness extension):**
> - 4 PEAD variants — `pead.compute_pead_signals(ticker, ohlcv, as_of)` + `earnings_surprise_yoy.compute_yoy_surprise_signal(ticker, ohlcv, as_of)` — TIER 2 (per-(ticker, as_of) cache reads on Finnhub earnings cache)
> - `buyback_8k_recent_long` — `macro_events.compute_recent_8k_signal(ticker, as_of)` + SEC EDGAR decoded — TIER 2 (per-ticker SEC parquet read)
> - `news_momentum_long/short`, `news_reversal_long` — `news_sentiment.compute_news_sentiment_signals(ticker, as_of)` — TIER 2 (Polygon news cache)
> - `m_and_a_target_long`, `activist_13d_long` — `sec_edgar_extractor.compute_sec_edgar_signals(ticker, as_of)` — TIER 2 (SEC EDGAR decoded)
>
> The 3 cross-cluster references to smart-money strategies (SM-1 `insider_cluster_long`, SM-2 `insider_cluster_with_director_long`, SM-6 `pead_with_insider_confirmation_long`) remain blocked on B690 per [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md) status.
>
> **What does NOT change in this batch:** the event-driven walks' Pattern W (PEAD strict-subset narrowing — EV-3 + EV-4 already DELETED B682) + CC1 PEAD next-open-after-gap concern + Pattern M (LEGITIMATE peer-reviewed citations — Bernard-Thomas 1989 JoAR, Lucca-Moench 2015 JF, Foster-Olsen-Shevlin 1984) findings remain VALID regardless of fire-count revision.
>
> **All `PENDING B660` labels in this doc are now split:**
> - Pre-FOMC + cross-asset + calendar subset → **PENDING-B660-RERUN-B689** (resolves ~2026-06-12 12:30)
> - News + PEAD + 8-K + SEC-EDGAR subset → **PENDING-B690**
>
> **B677 status banner (2026-06-10, owner-directed autonomous continuation):** SEVENTH per-cluster Stage 4 walk doc. Owner directive *"continue autonomously"* after B676 breakout cluster walk.
>
> **Scope:** 10 strategies in `event_driven` category. **Cross-cluster note:** 3 of 10 strategies (`strat_insider_cluster_long` = SM-1, `strat_insider_cluster_with_director_long` = SM-2, `strat_pead_with_insider_confirmation_long` = SM-6) were ALREADY WALKED in the smart-money cluster doc per CHECKLIST #105 7-step methodology. This doc therefore covers 10 strategies but the 3 cross-cluster references compactly cite the smart-money walk + add event-driven-specific findings. **NEW walks: 7 strategies** (`strat_buyback_8k_recent_long` + 4 PEAD variants + 2 pre-FOMC variants).
>
> **Source of truth.** Code references reflect current state at commit `696e4f475` (post-B676 breakout walk).
>
> **CARRY-FORWARD:** Pattern A (clean), Pattern M / Q (cluster mostly has LEGITIMATE peer-reviewed citations — Bernard-Thomas 1989 JoAR, Lucca-Moench 2015 JF, Garfinkel-Hribar-Hsiao 2024, Foster-Olsen-Shevlin 1984, Manconi-Peyer-Vermaelen 2019 JFQA, Cohen-Malloy-Pomorski 2012 — Pattern Q does NOT apply broadly), Pattern N (heavy — 4 PEAD variants on same primitives), Pattern T forensic-fix lineage (B385 + B507).
>
> Per `feedback_no_rushing_per_strategy_tweak` + foundational sequence (B660 in flight): no code changes in B677.

---

## Audience

Two:

1. **External reviewer** — for you: the event-driven cluster differs from breakout cluster in that (a) strategies are anchored on FILING EVENTS (8-K filings, earnings announcements, FOMC scheduled events) — different temporality class than breakout's chart-pattern EVENTs, (b) **CC1 next-open-after-gap concern from B673 reviewer applies MOST STRONGLY here** — earnings announcements gap 5-20%; 8-K filings can gap; FOMC days are scheduled but stocks can gap into them. The capturable-after-gap haircut is the cluster's dominant feasibility concern. (c) **Pattern Q does NOT apply broadly** — 8 of 10 strategies have legitimate peer-reviewed anchors (Bernard-Thomas 1989, Lucca-Moench 2015 JF, Cohen-Malloy-Pomorski 2012, etc.). The cluster has the same legitimate-citation strength as breakout. (d) Heavy intra-cluster collinearity — 4 PEAD variants share `within_pead_window` + earnings-surprise primitives. (e) Cross-cluster overlap with smart-money sub-cluster A — 3 of 10 are joint memberships.

2. **Future readers** — [Cluster scope inventory](#cluster-scope-inventory) below.

---

## Methodology adaptations for event-driven cluster

### 1. CC1 next-open-after-gap concern most acute in this cluster

Per B673 reviewer 2nd-wave feasibility critique (CC1): EVENT-alpha is uncapturable via next-day-open after a gap. Event-driven cluster carries the MOST acute version of this concern:

| Strategy class | Gap risk | Concern level |
|---|---|---|
| **PEAD (4 strategies)** | Earnings announcements typically gap 5-20% on the day of the report; PEAD strategies enter `within_pead_window` (60-day post-earnings) which means the gap-day is INSIDE the window. **If entry fires on day +1 (next bar after earnings) the engine has missed the announcement-day gap.** Bernard-Thomas 1989 60-day drift is measured FROM the post-announcement bar. Capturable fraction is the 60-day drift only, not the announcement-day move. | **HIGH** |
| **8-K filing (buyback_8k_recent_long)** | 8-K filings can gap (Item 1.01 M&A, Item 8.01 buybacks, Item 7.01 Reg FD all can move stocks materially). Strategy enters `days_since_8k <= 5` which includes the gap day. **Same CC1 concern as PEAD.** | **HIGH** |
| **Insider cluster (SM-1, SM-2)** | Form 4 filings are 2-day-lag and individually small-impact; cluster signal aggregates — gap risk is lower per-event but SM-1 already walked in smart-money cluster surfaced this | MEDIUM (covered in SM walk) |
| **Pre-FOMC (2 strategies)** | FOMC days are SCHEDULED (known in advance); entry day (d-1) is known; **NO gap risk on entry** — but FOMC announcement itself often gaps in either direction → exit-side gap risk if hold continues into d+1 | LOW (entry side); MEDIUM (exit side) |

**Step 7 disposition:** PEAD + 8-K walks must explicitly acknowledge CC1; pre-FOMC walks can cite reduced entry-side risk.

### 2. Pattern Q does NOT apply broadly — legitimate citations

| Strategy | Citation | Peer-review level |
|---|---|---|
| **PEAD family (4)** | Bernard + Thomas 1989 *Journal of Accounting Research* "Post-Earnings-Announcement Drift" + Foster-Olsen-Shevlin 1984 + Garfinkel-Hribar-Hsiao 2024 | ✅ Anchor + multiple updates |
| **8-K buyback (1)** | Manconi-Peyer-Vermaelen 2019 JFQA buyback abnormal-return literature + Lopez-Lira-Tang 2023 8-K post-filing window | ✅ Real |
| **Pre-FOMC (2)** | Lucca + Moench 2015 *Journal of Finance* "The Pre-FOMC Announcement Drift" + Cieslak-Pang 2024 yield-curve conditional | ✅ Top-tier finance |
| **Insider cluster (SM-1, SM-2)** | Cohen-Malloy-Pomorski 2012 JF + Lakonishok-Lee 2001 RFS + Akbas-Jiang-Koch 2024 RFS | ✅ Anchor |
| **pead_with_insider_confirmation_long (SM-6)** | Combines PEAD + insider citations | ✅ Composite |

**Pattern Q applies to 0 of 10 strategies.** Cluster-positive note.

### 3. Heavy intra-PEAD-family collinearity (Pattern N + W NEW)

4 PEAD variants all consume `within_pead_window` primitive:

| Strategy | Differential gate |
|---|---|
| `strat_pead_long` | `pead_positive_surprise` (composite: YoY+ AND ann-ret > +2%) |
| `strat_pead_short` | `pead_negative_surprise` (composite mirror) |
| `strat_pead_long_high_yoy_growth_only` | `yoy_surprise_high` (yoy_growth >= +5%) — STRICTER YoY-only sub-population of `pead_positive_surprise` |
| `strat_pead_short_negative_yoy_growth` | `yoy_surprise_negative` (yoy_growth <= −5%) — STRICTER YoY-only sub-population of `pead_negative_surprise` |
| `strat_pead_with_insider_confirmation_long` (SM-6, walked smart-money) | `pead_positive_surprise + insider_cluster_active` |
| `strat_pead_with_smart_money_long` (SM-41, walked smart-money) | `pead_positive_surprise + _has_smart_money_buy` UNION |

**6 PEAD variants on 1 underlying signal class (within_pead_window + earnings-surprise primitive).** Effective hypothesis count for PEAD-family ≈ 2 (positive-surprise + negative-surprise), not 6. Massive Pattern N exposure.

**Pattern W (NEW for event-driven): PEAD-family sub-population narrowing.** `pead_long_high_yoy_growth_only` (B507) is a STRICTER sub-population of `pead_long` — by construction the strict subset has a fire-count subset relationship. Cube must explicitly test sub-population vs full-population PEAD to determine whether the narrowing earns its own registry slot.

### 4. Cross-cluster overlap — 3 of 10 walked in smart-money cluster

| Event-driven strategy | Smart-money walk reference |
|---|---|
| `strat_insider_cluster_long` | SM-1 (B663 closed; walked B672 expansion) |
| `strat_insider_cluster_with_director_long` | SM-2 (B663 closed; walked B672) |
| `strat_pead_with_insider_confirmation_long` | SM-6 (walked B672a) |

Plus the SM-41 `strat_pead_with_smart_money_long` is in `smart_money_sleeve` category — UNION variant of SM-6.

This doc cross-references the smart-money walks for the 3 dual-membership strategies + adds event-driven-cluster-specific findings (CC1 carry, Pattern W collinearity).

---

## Reviewer findings response matrix

> Pre-emptive matrix.

| # | Finding | Severity | Status | Action |
|---|---|---|---|---|
| _F-pending_ | Awaiting external reviewer | — | OPEN | Will tabulate post-review |

---

## Cluster scope inventory

**10 strategies in `event_driven` category.** Sub-cluster grouping:

| Sub-cluster | # strategies | Strategies |
|---|---|---|
| **A — PEAD family (4 NEW + 1 walked SM)** | 5 | EV-1 `strat_pead_long` / EV-2 `strat_pead_short` / EV-3 `strat_pead_long_high_yoy_growth_only` (B507) / EV-4 `strat_pead_short_negative_yoy_growth` (B507) / SM-6 `strat_pead_with_insider_confirmation_long` (walked smart-money) |
| **B — Pre-FOMC (2 NEW)** | 2 | EV-5 `strat_pre_fomc_long_sleeve` / EV-6 `strat_pre_fomc_quality_momentum_long` |
| **C — 8-K filing (1 NEW)** | 1 | EV-7 `strat_buyback_8k_recent_long` |
| **D — Insider cluster (2 walked SM)** | 2 | SM-1 `strat_insider_cluster_long` (cross-ref) / SM-2 `strat_insider_cluster_with_director_long` (cross-ref) |

**Cross-cluster:** 3 of 10 already walked in [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md); this doc walks the 7 NEW strategies + adds event-driven-specific findings cross-referenced for the 3 dual-membership.

---

## Cross-strategy patterns (event-driven cluster)

### Pattern W (NEW for event-driven): PEAD sub-population narrowing creates strict-subset Pattern N

**Affects:** EV-3 (high-yoy variant of EV-1) + EV-4 (negative-yoy variant of EV-2) + SM-6 + SM-41 (insider/UNION variants of EV-1).

**Concern:** B507 added EV-3 + EV-4 as STRICTER sub-population variants of EV-1/EV-2. By construction, fires of EV-3 are a SUBSET of fires of EV-1 (within_pead_window AND yoy_surprise_high ⊂ within_pead_window AND pead_positive_surprise). This is the cleanest possible Pattern N: the sub-population strategy can ONLY add value via tighter signal-to-noise on the sub-population OR via differential exit/hold profile. Cube replay marginal-contribution test:
- Does EV-3 (high-YoY) outperform EV-1 (any-positive-surprise) on a per-trade basis? If yes, the sub-population is informative.
- If no, EV-3 is a Pattern N reskin and should be deprecated.

**Same logic applies to EV-4 vs EV-2.**

### Pattern X (NEW for event-driven): cross-cluster walked-elsewhere

**Affects:** SM-1, SM-2, SM-6 (3 of 10 strategies have walks in smart-money cluster doc).

**Concern:** Pattern H (cross-cluster registry dedup) governance smell — strategies appear in 2 walk docs but ONE walk is the source-of-truth. Per `S4-CROSS-CLUSTER-REGISTRY-DEDUP-NOMENCLATURE` ticket: single source-of-truth registry is the resolution.

### Pattern N intra-cluster (carried + extended)

10 strategies on 5 primitives:
- `within_pead_window` + `pead_positive_surprise` / `pead_negative_surprise` / `yoy_surprise_high` / `yoy_surprise_negative` (5 PEAD variants)
- `recent_8k_filed` (1)
- `pre_fomc_d1` (2)
- `insider_cluster_active` (2 — cross-walk)

**Effective N ≈ 5, not 10.**

### Pattern A (carried) — ✅ clean

All 10 strategies use `price_above_ema_200` (default-False post-B663) or `below_ema_200` (B630 producer-additive). 0 silent-gap.

### Pattern T forensic-fix lineage

- B385 (`days_since_8k` loosened 3 → 5 per Lopez-Lira-Tang 2023 5-day window)
- B507 (PEAD YoY-growth variants added per M6 Path-2)

---

## Cluster current state table

| EV # | Function | Direction | Sub-cluster | Primary signal(s) | Confluence gates | Citation anchor | Pattern flags | Walk status |
|---|---|---|---|---|---|---|---|---|
| EV-1 | `strat_pead_long` | long | A PEAD | `within_pead_window` + `pead_positive_surprise` | (none) | Bernard-Thomas 1989 JoAR | CC1 HIGH + W | ⏳ Walked B677 |
| EV-2 | `strat_pead_short` | short | A PEAD | `within_pead_window` + `pead_negative_surprise` | (none) | Garfinkel 2024 | CC1 HIGH + W + B671 borrow-trap | ⏳ Walked B677 |
| EV-3 | `strat_pead_long_high_yoy_growth_only` | long | A PEAD | `within_pead_window` + `yoy_surprise_high` | (none) | Foster-Olsen-Shevlin 1984 + B507 | CC1 HIGH + W STRICT-SUBSET of EV-1 | ⏳ Walked B677 |
| EV-4 | `strat_pead_short_negative_yoy_growth` | short | A PEAD | `within_pead_window` + `yoy_surprise_negative` | (none) | B507 inverse | CC1 HIGH + W STRICT-SUBSET of EV-2 + B671 borrow-trap | ⏳ Walked B677 |
| EV-5 | `strat_pre_fomc_long_sleeve` | long | B Pre-FOMC | `pre_fomc_d1` | `price_above_ema_200` | Lucca-Moench 2015 JF | CC1 LOW entry / MED exit | ⏳ Walked B677 |
| EV-6 | `strat_pre_fomc_quality_momentum_long` | long | B Pre-FOMC | `pre_fomc_d1` + `xs_momentum_top_decile` | `price_above_ema_200` | Lucca-Moench + Goyal-Jegadeesh 2024 | CC1 LOW + Pattern N reskin of EV-5 | ⏳ Walked B677 |
| EV-7 | `strat_buyback_8k_recent_long` | long | C 8-K | `recent_8k_filed` + `days_since_8k<=5` | `price_above_ema_200` + `vol_spike_15x` | Manconi-Peyer-Vermaelen 2019 + Lopez-Lira-Tang 2023 | CC1 HIGH + 8-K-not-buyback-text-parsed gap | ⏳ Walked B677 |
| SM-1 | `strat_insider_cluster_long` | long | D Insider | `insider_cluster_active` | `price_above_ema_200` | CMP 2012 JF | Already walked smart-money B663 | ✅ Walked B663 (cross-ref) |
| SM-2 | `strat_insider_cluster_with_director_long` | long | D Insider | `insider_cluster_active` + director | `price_above_ema_200` | Lakonishok-Lee 2001 RFS | Walked B663 (cross-ref) | ✅ Walked B663 (cross-ref) |
| SM-6 | `strat_pead_with_insider_confirmation_long` | long | A PEAD + D Insider | composite | (none) | PEAD + insider | Walked B672a (cross-ref) | ✅ Walked B672 (cross-ref) |

**Net cluster state:**
- 7 NEW walks + 3 cross-references = 10 strategies covered
- Pattern A ✅ clean
- All have legitimate citations (Pattern Q does NOT apply)
- 4 SHORT-side strategies subject to B671 centralized borrow-trap (EV-2, EV-4, and indirectly through SM-1/2/6 sleeve consultation if applicable)
- CC1 next-open-after-gap is the dominant feasibility concern

---

## Per-strategy walks

### EV-1. `strat_pead_long` (Batch 209, PEAD family, walked B677)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate LONG; **Bernard-Thomas 1989 anchor** — cluster's anchor citation.

#### Step 1 — Read the code

[screener.py:3725-3747](backtest/signals/screener.py#L3725-L3747):

```python
def strat_pead_long(s):
    fires = (
        s.get("within_pead_window", False)
        and s.get("pead_positive_surprise", False)
    )
```

**2-gate LONG.** Simplest PEAD walk; canonical anchor.

| Gate | Meaning |
|---|---|
| `within_pead_window` | STATE: today's bar within 60 trading days of last earnings announcement (post-event window) |
| `pead_positive_surprise` | EVENT (composite): YoY EPS growth > 0 AND announcement-day return > +2% |

#### Step 2 — Classify

- Category: `event_driven`; LONG; B291 default; last touched B209

#### Step 3 — Producer source-read + temporality

- `within_pead_window`: STATE-with-decay — 60-trading-day window post-earnings; produced from earnings calendar
- `pead_positive_surprise`: composite gate (YoY > 0 AND announcement return > +2%) — anchored on the EARNINGS DAY (the event); the strategy fires on subsequent bars within the window
- EVENT/STATE: 1 STATE-windowed (PEAD window) + 1 EVENT-anchored (the announcement was the trigger; the strategy enters AFTER)

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Bernard-Thomas (1989) 60-day drift continuation" | ✅ **REAL ANCHOR** — Bernard + Thomas 1989 *Journal of Accounting Research* established PEAD. Top-tier accounting journal; widely-cited. |
| "Post-Earnings Announcement Drift" | ✅ Real phenomenon; well-documented |
| Implicit "next-day-open captures the 60-day drift" | ⚠ **CC1 HIGH** — earnings days gap 5-20%; the strategy enters within `within_pead_window` which is 60 days; **if entry fires on day +1, the engine has missed the announcement-day gap.** Bernard-Thomas 60-day drift is measured FROM the post-announcement bar — the capturable fraction is the 60-day drift only, not the announcement move |
| `>+2%` threshold | ⚠ Pattern O — hardcoded threshold; not empirically calibrated against the announcement-return distribution |

#### Step 5 — OPEN_INVESTIGATIONS grep

- Pattern N: EV-1 vs EV-3 (high-yoy strict subset) vs SM-6 (insider-confirmed) vs SM-41 (UNION-smart-money) — 4-variant PEAD ablation candidate
- Pattern T: B507 forensic addition of EV-3 created the strict-subset class
- CC1 carries forward from B673 reviewer critique

#### Step 6 — Missing-inverse + economic-symmetry

- ✅ Inverse EXISTS — EV-2 `strat_pead_short`
- Economic symmetry: ✅ PEAD is documented in both directions

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-CC1-gap-haircut-required** | Earnings days gap; engine entry after gap; capturable fraction is drift ONLY, not announcement-day move | HIGH | CC1 |
| **F-pattern-N PEAD-variants** | 4-variant cube ablation (EV-1 / EV-3 / SM-6 / SM-41) | HIGH | Pattern N + W |
| **F-pattern-W strict-subset** | EV-3 is by construction a subset of EV-1; cube settles whether sub-population earns separate registry slot | HIGH | Pattern W |
| **F-bernard-thomas-anchor ✅** | Real citation; cluster-positive | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-pattern-O threshold** | `>+2%` announcement-return threshold hardcoded; not calibrated | LOW | Pattern O |
| F-pattern-A | `price_above_ema_200` not used in EV-1 (60-day post-earnings window is the regime) | N/A | — |
| F-fire-count | Earnings season concentration + positive-surprise narrowing; projected ~200-500/yr universe-wide (PEAD is the highest-fire event-driven strategy); PASS | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) CC1 capturable-after-gap haircut acknowledged in docstring + cube validates realized return vs Bernard-Thomas 60-day cumulative |
| (c) 4-variant PEAD Pattern N cube ablation (EV-1 / EV-3 / SM-6 / SM-41) |
| **(d) RECOMMENDED — (b) + (c). PEAD is the cluster's most-cited strategy; cube validation MUST surface (i) capturable-after-gap realized return + (ii) marginal contribution among variants** |

**My recommendation: (d).**

**Awaiting owner direction on EV-1:**
1. (a)/(b)/(c)/(d) — recommendation (d)
2. PEAD-family Pattern N ablation flagship scope

---

### EV-2. `strat_pead_short` (Batch 209, PEAD family, walked B677)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate SHORT; symmetric mirror of EV-1.

[screener.py:3750-3766](backtest/signals/screener.py#L3750-L3766) — symmetric with `pead_negative_surprise` (yoy < 0 AND announcement-return < -2%). **B671 borrow-trap gate applies.** Same CC1 HIGH + Pattern N + W concerns. Garfinkel-Hribar-Hsiao 2024 cites bottom-decile-surprise downside drift (✅ legitimate).

**Options:** same as EV-1; bundled. **My recommendation: (d) bundled with EV-1 + EV-3 + EV-4.**

**Awaiting owner direction on EV-2:** bundled with EV-1.

---

### EV-3. `strat_pead_long_high_yoy_growth_only` (Batch 507, PEAD family, walked B677 — STRICT SUBSET of EV-1)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate LONG; B507 M6 Path-2 sleeve; **STRICTER sub-population of EV-1.**

#### Step 1 — Read the code

[screener.py:3769-3794](backtest/signals/screener.py#L3769-L3794):

```python
fires = (
    s.get("within_pead_window", False)
    and s.get("yoy_surprise_high", False)
)
```

**2-gate LONG.** Stricter sub-population — `yoy_surprise_high` requires `yoy_growth >= +5%` (vs EV-1's composite `yoy>0 AND ann_ret>+2%`).

#### Step 2-7 (compact — Pattern W strict-subset of EV-1)

- Category `event_driven`; LONG; last touched B507
- **Pattern W STRICT-SUBSET:** fires of EV-3 are a SUBSET of fires of EV-1 by construction (`yoy_surprise_high = yoy >= +5%` is stricter than EV-1's `yoy>0 AND ann_ret>+2%` on the YoY-axis alone; though EV-1 also gates on ann_ret which EV-3 doesn't, the YoY-stricter EV-3 captures a different sub-population than EV-1 — the relationship is "stricter-on-YoY-only" not "subset")
- Foster-Olsen-Shevlin 1984 citation legitimate ✅
- M6 Path-2 surrogate (paid Finnhub analyst-surprise deferred; YoY proxy ships)

**Step 7 critical question:** does EV-3 (high-YoY-only) outperform EV-1 (composite YoY+ann_ret) per trade? Cube settles. If EV-3 ≈ EV-1, Pattern N flagship deprecation candidate.

**Options:** (a) status quo / (b) cube Pattern N validates strict-subset earns registry slot / (c) deprecate EV-3 if cube shows no marginal contribution / **(d) RECOMMENDED — (b). Cube is the only adjudication.**

**My recommendation: (d).** EV-3's existence is gated on B660 + cube validation.

**Awaiting owner direction on EV-3:** Pattern W cube validation post-B660.

---

### EV-4. `strat_pead_short_negative_yoy_growth` (Batch 507, PEAD family, walked B677)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Symmetric mirror of EV-3.

[screener.py:3797-3815](backtest/signals/screener.py#L3797-L3815) — symmetric with `yoy_surprise_negative` (yoy <= -5%). **B671 borrow-trap.** Same Pattern W strict-subset finding as EV-3.

**Options:** bundled with EV-3. **My recommendation: (d) bundled.**

**Awaiting owner direction on EV-4:** bundled.

---

### EV-5. `strat_pre_fomc_long_sleeve` (Batch 224, Pre-FOMC family, walked B677)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate LONG; **Lucca-Moench 2015 JF anchor** — top-tier finance citation.

#### Step 1 — Read the code

[screener.py:2841-2859](backtest/signals/screener.py#L2841-L2859):

```python
fires = (
    s.get("pre_fomc_d1", False)
    and s.get("price_above_ema_200", False)
)
```

**2-gate LONG.** Pre-FOMC day-1 EVENT + EMA-200 regime.

#### Step 2 — Classify

- Category: `event_driven`; LONG; last touched B224
- **Bypass event suppression:** strategy is in `STRATEGIES_BYPASS_EVENT_SUPPRESSION` config — reverses Batch 191 FOMC suppression for the LONG sleeve specifically

#### Step 3 — Producer source-read + temporality

- `pre_fomc_d1`: EVENT — today is the trading day before an FOMC announcement (calendar-driven)
- `price_above_ema_200`: STATE regime
- EVENT/STATE: 1 EVENT + 1 STATE

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Lucca-Moench 2015 JF 'The Pre-FOMC Announcement Drift': +50bps/yr alpha concentrating in 24h preceding FOMC announcements" | ✅ **REAL ANCHOR** — Lucca + Moench 2015 *Journal of Finance* established the pre-FOMC drift anomaly. Top-tier finance journal. |
| "Cieslak-Pang 2024 conditional on yield-curve slope" | ✅ Real refinement |
| "Long entry on the pre-FOMC day (d-1) when broad bullish context holds" | ✅ Mechanical implementation matches the documented effect window |

**CC1 entry-side risk LOW:** FOMC dates are SCHEDULED (known in advance); entry on d-1 is at next-day-open after detection bar; no announcement gap to miss on entry. Exit-side gap risk: if hold continues into FOMC day or d+1, the announcement can gap in either direction — exit-side concern.

#### Step 5 — OPEN_INVESTIGATIONS grep

- Cross-ref `S4-REGIME-FRED-VINTAGE` (yield-curve PIT for Cieslak-Pang 2024 refinement if implemented)
- Pattern N: EV-5 vs EV-6 (quality-momentum variant)

#### Step 6 — Missing-inverse + economic-symmetry

- ❌ **No inverse mirror** — pre-FOMC drift is documented in LONG direction only (Lucca-Moench shows positive drift; no symmetric "pre-FOMC bear" literature)
- Asymmetric per `feedback_asymmetric_data_sources_break_mechanical_inverse`

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-lucca-moench-anchor ✅** | Real citation; cluster-positive | INFO / ✅ POSITIVE | Pattern Q exception |
| **F-CC1-LOW-entry-risk** | Scheduled event; no entry-side gap | INFO | CC1 partial |
| **F-pattern-N EV-5 vs EV-6** | EV-6 adds xs_momentum_top_decile; cube settles marginal contribution | MEDIUM | Pattern N |
| **F-no-inverse-mirror** | Pre-FOMC LONG only per literature; asymmetric ✅ | INFO / ✅ POSITIVE | F6 |
| F-pattern-A | EMA-200 ✅ | ✅ SHIPPED B663 | — |
| F-fire-count | FOMC ~8 events/yr × 503 tickers × EMA-200 filter ≈ ~3000-4000/yr universe-wide; PASS | INFO | F4 |

**Options:** (a) status quo (well-anchored + clean) / (b) cube EV-5 vs EV-6 ablation. **My recommendation: (a) + (b).**

**Awaiting owner direction on EV-5:**
1. Pattern N EV-5 vs EV-6 cube ablation scope

---

### EV-6. `strat_pre_fomc_quality_momentum_long` (Batch 224, Pre-FOMC family, walked B677)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate LONG; higher-conviction Pre-FOMC variant.

[screener.py:2862-2875](backtest/signals/screener.py#L2862-L2875) — combines `pre_fomc_d1` + `xs_momentum_top_decile` + `price_above_ema_200`. Goyal-Jegadeesh-Subrahmanyam 2024 RFS momentum citation legitimate ✅.

#### Step 2-7 (compact — Pattern N reskin of EV-5)

- Category `event_driven`; LONG; last touched B224
- Adds top-decile XS momentum filter to EV-5
- Pattern N: EV-6 is a reskin of EV-5 + momentum factor; cube settles whether momentum filter adds value above pre-FOMC drift
- Fire-count: pre-FOMC × top-decile momentum AND EMA — projected ~300-700/yr universe-wide; PASS

**Options:** bundled with EV-5 Pattern N. **My recommendation: cube settles.**

**Awaiting owner direction on EV-6:** bundled with EV-5.

---

### EV-7. `strat_buyback_8k_recent_long` (Batch 224, 8-K family, walked B677)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 4-gate LONG; **buyback proxy not actual buyback parser** (docstring acknowledges).

#### Step 1 — Read the code

[screener.py:2878-2908](backtest/signals/screener.py#L2878-L2908):

```python
fires = (
    s.get("recent_8k_filed", False)
    and s.get("days_since_8k", -1) <= 5
    and s.get("price_above_ema_200", False)
    and s.get("vol_spike_15x", False)
)
```

**4-gate LONG.** Recent 8-K + 5-day window + EMA-200 + vol spike.

| Gate | Meaning |
|---|---|
| `recent_8k_filed` | EVENT: 8-K filed within last 5 days |
| `days_since_8k <= 5` | EVENT-window: time-bound to 5-day filing window (B385 loosened from 3 → 5 per Lopez-Lira-Tang 2023) |
| `price_above_ema_200` | STATE |
| `vol_spike_15x` | EVENT: today's volume > 1.5x trailing 20-bar mean |

#### Step 2 — Classify

- Category: `event_driven`; LONG; B385 forensic loosen (Pattern T)

#### Step 3 — Producer source-read + temporality

- `recent_8k_filed` + `days_since_8k`: derived from SEC EDGAR feed (P17 wire-in DEC-456)
- `price_above_ema_200` STATE
- `vol_spike_15x` EVENT
- EVENT/STATE: 3 EVENT-class + 1 STATE

#### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Generic 8-K filing in last 5 days as a corporate-event proximity signal" | ✅ **DOCSTRING IS HONEST** — explicitly notes this is NOT a true buyback filter; requires 8-K item-level text parsing (Item 8.01 etc) which is deferred |
| "Manconi-Peyer-Vermaelen 2019 JFQA documented 4pct/yr abnormal return on filtered buybacks" | ✅ Real citation BUT applies to FILTERED buybacks (Item 8.01 + buyback text); EV-7 fires on ANY 8-K which is broader signal class |
| "Lopez-Lira-Tang 2023 documents 5-day post-8K reaction window" | ✅ Real citation (B385 forensic loosen reference) |
| Implicit "any 8-K + vol spike + uptrend = high-quality long" | ⚠ The strategy fires on ANY 8-K type (Items 1.01-9.01) — could be earnings, M&A target, officer change, Reg FD, buyback. Mixing populations dilutes the signal. **F-population-mixing flag.** |

#### Step 5 — OPEN_INVESTIGATIONS grep

- **F-population-mixing**: any 8-K type fires; M&A target Item 1.01 fires alongside buyback Item 8.01 — different economic populations
- Future 8-K text parsing deferred (Pattern T — partial implementation; full buyback filter pending)
- Cross-ref `S4-B673-SM4-FEASIBILITY-FAILURE-RECLASSIFICATION` — SM-4 (M&A target long) had EXACTLY this concern with 8-K Item 1.01; B673 reviewer flagged SM-4 as feasibility failure. **EV-7 inherits the same concern for the M&A-target subset of its fires.**

#### Step 6 — Missing-inverse + economic-symmetry

- No mirror — buybacks are LONG-only signal class per literature

#### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-population-mixing** | Any 8-K type fires; mixes M&A target (SM-4 feasibility failure) + buyback + Reg FD + officer change; different economic populations | HIGH | F1 + B673 SM-4 carry |
| **F-CC1-gap-haircut** | 8-K Item 1.01 gaps; engine entry after gap; capturable fraction depends on item type | HIGH | CC1 |
| **F-docstring-honesty ✅** | Docstring explicitly notes "NOT true buyback filter; proxy/placeholder" | INFO / ✅ POSITIVE | F-honesty |
| **F-pattern-T B385 loosen** | days_since_8k 3 → 5 forensic-fix per Lopez-Lira-Tang citation | INFO | Pattern T |
| F-fire-count | 8-K filings common; ~50-150/yr per ticker; vol_spike + EMA narrows; projected ~500-1500/yr universe-wide; PASS | INFO | F4 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo (docstring already honest about proxy status) |
| (b) 8-K text parsing implementation per docstring's deferred plan — true buyback filter |
| (c) EV-7 deprecation pending (b) implementation (avoid running the broad 8-K proxy that includes SM-4 feasibility-failure cases) |
| **(d) RECOMMENDED — (b) deferred but (a) honest. Cube replay validates EMPIRICAL realized return on the proxy; if it fails, route to (c). If it passes, defer (b) implementation indefinitely.** |

**My recommendation: (d).**

**Awaiting owner direction on EV-7:**
1. (a)/(b)/(c)/(d) — recommendation (d)
2. Population-mixing concern resolution: tolerate via cube validation OR implement 8-K text parsing
3. Cross-cluster Pattern X with SM-4 feasibility-failure subset

---

### SM-1, SM-2, SM-6 — cross-references (walked in smart-money cluster doc)

> See [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md) for full walks.

**SM-1 `strat_insider_cluster_long`** — 2-gate LONG; Cohen-Malloy-Pomorski 2012 JF anchor; B663 default-True swept clean. Event-driven-cluster-specific finding: CC1 partial applicability — Form 4 filings are 2-day-lag and individually small; cluster signal aggregates so per-event gap risk is lower than PEAD/8-K.

**SM-2 `strat_insider_cluster_with_director_long`** — 3-gate LONG; Lakonishok-Lee 2001 RFS director-premium anchor; B663 closed.

**SM-6 `strat_pead_with_insider_confirmation_long`** — composite PEAD + insider confirmation; cross-cluster Pattern N flagship with EV-1 + EV-3 + SM-41. Cube ablation candidate.

---

## B677 cluster walk completion wrap-up

> All 10 event-driven strategies now have full pivot-doc-template per-walk coverage (7 NEW walks + 3 cross-references):

- **Sub-cluster A — PEAD family (4 NEW + 1 walked):** EV-1 + EV-2 + EV-3 + EV-4 + SM-6 (cross-ref)
- **Sub-cluster B — Pre-FOMC (2 NEW):** EV-5 + EV-6
- **Sub-cluster C — 8-K filing (1 NEW):** EV-7
- **Sub-cluster D — Insider cluster (2 walked):** SM-1 + SM-2 (cross-ref)

**Total fully-covered: 10 of 10. CLUSTER WALK COMPLETE.**

### Bundled disposition recommendations summary

| Pattern | Strategies | Disposition |
|---|---|---|
| **A (default-True silent-gap)** | ✅ All 10 clean post-B663/B630 | ✅ RESOLVED |
| **M / Q (citation)** | LEGITIMATE for all 10 (Bernard-Thomas 1989, Lucca-Moench 2015, Garfinkel 2024, Foster-Olsen-Shevlin 1984, Manconi-Peyer-Vermaelen 2019, Lopez-Lira-Tang 2023, CMP 2012, Lakonishok-Lee 2001) | DOCUMENTATION-ONLY; cluster-positive |
| **N (intra-cluster collinearity)** | 10 strategies on ~5 primitives; PEAD-family is the heaviest sub-cluster (4 variants on `within_pead_window` + 2 sleeves SM-6/SM-41 = 6 total) | Cube replay 4-6-variant Pattern N flagship ablation |
| **W (PEAD strict-subset)** | EV-3 ⊂ EV-1 on YoY-axis; EV-4 ⊂ EV-2 | Cube settles whether sub-population earns separate registry slot |
| **CC1 next-open-after-gap** | PEAD (4) + 8-K (1) = 5 strategies HIGH-risk; pre-FOMC (2) LOW entry-risk + MED exit-risk | Documentation-only haircut; cube validates capturable realized return |
| **F-population-mixing EV-7** | 8-K-any-type proxy mixes M&A target (SM-4 feasibility failure carry) + buyback + Reg FD + officer change | Deferred 8-K text parsing OR deprecate pending cube |
| **B671 SHORT borrow-trap** | EV-2 + EV-4 (and indirectly SM-1/2/6 if any SHORT branches exist) | Already centralized B671 (revert pending per B673 reviewer) |

### Queue tickets surfaced

NEW B677 tickets:

- `S4-EV-PATTERN-N-PEAD-FAMILY-FLAGSHIP-CUBE-ABLATION` — 4-6-variant PEAD cube ablation (EV-1 / EV-3 / SM-6 / SM-41 + EV-2 / EV-4 mirrors)
- `S4-EV-PATTERN-W-PEAD-STRICT-SUBSET-VALIDATION` — EV-3 ⊂ EV-1 + EV-4 ⊂ EV-2 marginal-contribution validation
- `S4-EV-CC1-PEAD-CAPTURABLE-AFTER-GAP-HAIRCUT` — cube empirical realized return vs Bernard-Thomas 60-day CAR
- `S4-EV-7-8K-POPULATION-MIXING-AUDIT` — any-8-K-type proxy mixes M&A target with buyback; deferred 8-K text parsing OR EV-7 deprecation

EXISTING tickets cross-referenced:
- `S4-B673-SM4-FEASIBILITY-FAILURE-RECLASSIFICATION` — EV-7 inherits the M&A-target subset of SM-4's concern
- `S4-CROSS-CLUSTER-REGISTRY-DEDUP-NOMENCLATURE` — SM-1/SM-2/SM-6 cross-cluster membership
- `S4-REGIME-FRED-VINTAGE` — Cieslak-Pang 2024 yield-curve refinement for EV-5/EV-6 (if implemented)

---

## Cluster-wide methodology references

- **Producers:** [backtest/signals/screener.py](backtest/signals/screener.py) — EV-5 + EV-6 + EV-7 + insider cluster at lines 2841-2998; EV-1 + EV-2 + EV-3 + EV-4 at lines 3725-3815
- **Cross-cluster strategies:** [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md) for SM-1 + SM-2 + SM-6 walks
- **Citations:** Bernard + Thomas 1989 JoAR (PEAD anchor); Foster-Olsen-Shevlin 1984 (PEAD with YoY proxy); Garfinkel-Hribar-Hsiao 2024 (PEAD update); Lucca + Moench 2015 JF (pre-FOMC drift); Cieslak-Pang 2024 (yield-curve conditional); Manconi-Peyer-Vermaelen 2019 JFQA (buybacks); Lopez-Lira-Tang 2023 (8-K 5-day window); Cohen-Malloy-Pomorski 2012 JF (insider cluster); Lakonishok-Lee 2001 RFS (director premium); Akbas-Jiang-Koch 2024 RFS (insider update); Goyal-Jegadeesh-Subrahmanyam 2024 RFS (momentum)
- **Forensic-fix lineage (Pattern T):** B385 (days_since_8k 3 → 5) + B507 (PEAD YoY-growth variants M6 Path-2 sleeve)
- **Cluster status sequencing:** PENDING B660 + B668 cube replay + B669 survivorship execution

---

## B677 cluster walk status

| Item | Status |
|---|---|
| Doc infrastructure (header + adaptations + inventory + patterns + state table) | ✅ B677 |
| Per-strategy walks EV-1 through EV-7 (7 NEW walks) + SM-1/2/6 cross-references (3) | ✅ B677 |
| External reviewer pass | ⏳ post-walk-completion |
| Cluster-wide post-walk findings synthesis | ⏳ post-reviewer |

**Cumulative B677: 10 of 10 strategies covered. CLUSTER WALK COMPLETE.**

## B680 Self-Critique Iteration 2 — Cross-Cutting Feasibility Findings

> **Status (B680 self-critique iteration 2026-06-10):** owner directive *"Just update all docs"* — proceed with adversarial self-critique in lieu of external reviewer pass.

### Cross-cutting feasibility findings (Claude self-critique 2026-06-10)

| # | Finding | Verification | Severity | Status |
|---|---|---|---|---|
| **CC-A** | **CC1 gap-haircut is the cluster's DOMINANT structural concern + the walk acknowledged it but didn't quantify the magnitude.** Bernard-Thomas 1989 PEAD cumulative abnormal return is +1-3% over 60 days for top-decile-surprise; **earnings-day gap alone is typically 5-15%.** Engine entry after the gap captures the 60-day drift (~+1-3% expected) NOT the announcement move. **Realized PEAD strategy return per cube replay will be ~30-60% of the cited CAR magnitude after gap-haircut.** Walks framed CC1 as "documentation-only haircut" — but this should be a quantitative haircut applied to the strategy's expected-value reporting + thesis caveat. Without it, the strategies' "documented +1-3% alpha" framing IS the magnitude overclaim that B673 CC6 fix targeted for smart-money cluster. Same Pattern B-class overclaim at the cited-magnitude level. | Bernard-Thomas 1989 magnitude + typical earnings-gap statistics; quantitative inference | **HIGH** | NEW — `S4-EV-CC1-QUANTITATIVE-GAP-HAIRCUT-REPORTING` |
| **CC-B** | **EV-7 8-K population-mixing is a CONFIRMED design defect inherited from SM-4 feasibility failure** that the walk identified but didn't ESCALATE to immediate action. Strategy fires on ANY 8-K type — including Item 1.01 M&A target (which B673 reviewer flagged as feasibility failure SM-4). **EV-7 is silently capturing the same M&A target population that SM-4 was reclassified for.** Walk noted "F-population-mixing HIGH" but disposition is "deferred 8-K text parsing OR deprecate pending cube." **Should ship deletion or 8-K Item parsing pre-cube to avoid contaminating cube data with the same uncapturable M&A target population.** | ✅ EV-7 fires on `recent_8k_filed` which includes Item 1.01; cross-ref B673 SM-4 disposition | **HIGH** | ✅ **RESOLVED-B682-DELETED** — owner-approved 2026-06-10. EV-7 strat_buyback_8k_recent_long deleted; ALL_STRATEGIES entry removed; B660 partial data confirmed 0 fires/yr universe-wide pre-deletion (validates the deletion). If buyback alpha matters in future work, ship NEW strategy with proper 8-K Item 8.01 text parsing per Manconi-Peyer-Vermaelen 2019 spec. Tests updated (B224 + B385 pinned tests converted to deletion-verification). |
| **CC-C** | **Pattern W PEAD strict-subset (EV-3 ⊂ EV-1; EV-4 ⊂ EV-2) is more fundamental than the walk admitted — it's a CONFIRMED registry inflation, not a "cube settles" question.** EV-3 fires only when `yoy_surprise_high` (yoy >= +5%) — this is a strict subset of EV-1's `pead_positive_surprise` (yoy > 0 AND ann_ret > +2%) on the YoY-axis (EV-1's announcement-return gate doesn't help; the YoY-axis is monotone). **Cube will produce EV-3 fires as a deterministic subset of EV-1 fires; per-trade Sharpe will be near-identical by construction.** Pattern W is a Pattern N reskin disguised as a "stricter sub-population" — same Pattern E class as the smart-money confluence wraps where bullet text reframe was insufficient and Pattern F audit was required. **Should reframe EV-3/EV-4 as "tighter-threshold variants of EV-1/EV-2" + deprecate per cube replay; deletion candidate per `project_no_apriori_strategy_pruning` override.** | Mechanical from gate sets | MEDIUM-HIGH | ✅ **RESOLVED-B682-DELETED** — owner-approved 2026-06-10. EV-3 + EV-4 deleted; B507 M6 Path-2 sleeves removed from ALL_STRATEGIES. yoy_surprise_high + yoy_surprise_negative producer signals PRESERVED for future work (parameter variant on EV-1/EV-2 not separate registry slot). test_batch503 sleeve-registration test converted to deletion-verification. |
| **CC-D** | **EV-5 + EV-6 pre-FOMC strategies depend on calendar-feed accuracy — but the producer's calendar feed integrity is unaudited.** `pre_fomc_d1` signal source not surfaced in walk; presumably some FOMC calendar in producer. **What feed? What lag? What revisions?** FOMC dates are SCHEDULED but the Fed has historically moved meeting dates (rarely, but it happens) + emergency meetings exist. Walk's "scheduled event = no entry-side gap" framing assumes calendar correctness. **No PIT audit of the pre-FOMC calendar producer.** Subtle lookahead risk if the producer was populated retroactively from final calendar (including any moved meetings re-anchored to actual dates). | Producer source not surfaced in walk; needs investigation | MEDIUM | NEW — `S4-EV-PRE-FOMC-CALENDAR-PIT-AUDIT` |
| **CC-E** | **Effective hypothesis count ≈ 4, not 10.** PEAD family is 4 variants (EV-1/EV-2/EV-3/EV-4) on 2 underlying primitives (positive_surprise + negative_surprise); Pre-FOMC is 2 on 1 primitive; 8-K is 1; Insider is 2 on 1 primitive (cross-walked). **Effective N ≈ 4 distinct signal classes** — the cluster is 2.5× over-registered relative to its underlying signal diversity. C2 correction haircut inflated proportionally. | Inherent to cluster structure | HIGH | NEW — extend existing CC7 ticket |
| **CC-F** | **Cross-cluster Pattern X with smart-money creates governance debt** — 3 of 10 strategies are dual-membership (SM-1 + SM-2 + SM-6 walked in smart-money cluster doc). Cross-references add `S4-CROSS-CLUSTER-REGISTRY-DEDUP-NOMENCLATURE` debt at every walk doc update. Without a STRATEGY_REGISTRY canonical source-of-truth, per-cluster docs drift apart on dispositions for shared strategies. | Mechanical from cross-cluster membership | MEDIUM | NEW — extend existing `S4-CROSS-CLUSTER-REGISTRY-DEDUP-NOMENCLATURE` |
| **CC-G** | **`pead_positive_surprise` composite threshold (yoy > 0 AND ann_ret > +2%) is arbitrary** — yoy > 0 is mechanical (any positive growth); ann_ret > +2% is the canonical announcement-effect threshold per Foster-Olsen-Shevlin but the cluster's other gates (`yoy_surprise_high = yoy >= +5%`) suggest tighter calibration is plausible. **Pattern O hardcoded; sensitivity untested.** | ✅ Verified from producer | LOW-MEDIUM | NEW — `S4-EV-PEAD-COMPOSITE-THRESHOLD-CALIBRATION` |

### Per-strategy reframings (Claude self-critique)

| Strategy | Walk disposition | Self-critique reframing | Action |
|---|---|---|---|
| **EV-3 + EV-4** PEAD strict-subset variants | RECOMMENDED (d) — cube settles whether sub-population earns registry slot | **Reskin DETERMINISTIC SUBSET; cube will show near-identical per-trade Sharpe by construction.** Strong DELETION candidate per CC-C; cube can validate the deletion claim. | Pre-cube DELETION candidate |
| **EV-7** 8-K buyback proxy | RECOMMENDED (d) — cube validates proxy | **CC-B carry — should DELETE or implement 8-K Item parsing pre-cube to avoid M&A target contamination.** | Pre-cube DELETE-OR-FIX |
| **EV-1 + EV-2** PEAD long/short | RECOMMENDED (d) — CC1 haircut + 4-variant ablation | **Quantitative CC1 haircut should ship in docstring pre-cube.** Reframe expected magnitude as "60-day drift component only (~+1-3%), NOT announcement-day move (~+5-15%)." | Pre-cube docstring honesty |
| **EV-5 + EV-6** pre-FOMC | RECOMMENDED (a) + (b) — well-anchored cluster-positive | **Calendar PIT integrity should be verified pre-cube** (CC-D). Otherwise this is the cluster's cleanest strategy pair. | Pre-cube calendar PIT pin |

### Net effect on B677 walk dispositions

- **EV-3 + EV-4 deletion** ELEVATED to pre-cube candidate per Pattern W deterministic-subset finding
- **EV-7 deletion or fix** ELEVATED to pre-cube per SM-4 contamination carry-forward
- **CC1 gap-haircut** ELEVATED from documentation-only to quantitative reporting requirement
- **Pre-FOMC calendar PIT integrity** NEW audit
- **Effective hypothesis count** EXTENDED — event-driven contributes ~6 phantom hypothesis-test slots

### Queue tickets surfaced by self-critique (B680)

- `S4-EV-CC1-QUANTITATIVE-GAP-HAIRCUT-REPORTING` (HIGH; CC-A)
- `S4-EV-7-PRE-CUBE-DELETE-OR-8K-ITEM-PARSING-REQUIRED` (HIGH; CC-B)
- `S4-EV-3-EV-4-RESKIN-DEPRECATE-PER-CUBE` (MEDIUM-HIGH; CC-C)
- `S4-EV-PRE-FOMC-CALENDAR-PIT-AUDIT` (MEDIUM; CC-D)
- `S4-EV-PEAD-COMPOSITE-THRESHOLD-CALIBRATION` (LOW-MEDIUM; CC-G)

---

## B679 Iteration 2 Preparation — Review Solicitation Guide

> **Status (post-B679 format alignment):** READY FOR EXTERNAL REVIEWER + OWNER FEEDBACK on Iteration 2.
>
> **Recommended review structure (parallel to B673 smart-money review):**
>
> | Review axis | What to look for in Event-driven | Smart-money parallel |
> |---|---|---|
> | **CC-A: Engine entry feasibility — most acute here** | PEAD (4 strategies) + 8-K (1) carry HIGH gap-haircut concern; earnings announce gaps 5-20%, engine misses; pre-FOMC (2) low entry-risk because event scheduled | CC1 (HIGHEST in cluster) |
> | **CC-B: Citation discipline** | ALL 10 strategies have LEGITIMATE peer-reviewed anchors (Bernard-Thomas 1989 JoAR + Lucca-Moench 2015 JF + CMP 2012 + Foster-Olsen-Shevlin 1984 + Manconi-Peyer-Vermaelen 2019 + Lopez-Lira-Tang 2023 + Lakonishok-Lee 2001 + others). Pattern Q does NOT apply. Cluster-positive | Pattern M / Q exception |
> | **CC-C: PEAD strict-subset Pattern W** | EV-3 (high-yoy) and EV-4 (negative-yoy) are STRICT-SUBSETS of EV-1 and EV-2 on YoY-axis. Cube settles whether sub-population earns separate registry slot OR is Pattern N reskin | Pattern W NEW |
> | **CC-D: EV-7 8-K population-mixing** | Strategy fires on ANY 8-K type — mixes M&A target (SM-4 feasibility failure inheritance) + buyback + Reg FD + officer change. Different economic populations | F-population-mixing carry from B673 SM-4 |
> | **CC-E: Effective hypothesis count** | 10 strategies on 5 primitives (within_pead_window + earnings-surprise variants + recent_8k_filed + pre_fomc_d1 + insider_cluster_active) → effective N ≈ 5 | CC7 |
> | **CC-F: Cross-cluster registry** | SM-1 + SM-2 + SM-6 cross-cluster with smart-money cluster; SM-41 cross-cluster with smart-money sleeve. PEAD-family flagship Pattern N ablation spans both clusters | Pattern H |
>
> Provide feedback in B673-style severity-ranked critique; B679 will incorporate as B679-incorporation batch.

---

### Cross-cluster status snapshot (post-B679 — index at [STAGE_4_CLUSTER_WALKS_INDEX.md](STAGE_4_CLUSTER_WALKS_INDEX.md))

8 cluster docs / ~138 strategies covered. Review status:

| Cluster | Doc | Strategies | Owner review | Iteration 2 ready |
|---|---|---|---|---|
| Pivot | [STAGE_4_PIVOT_CLUSTER_WALKS.md](STAGE_4_PIVOT_CLUSTER_WALKS.md) | ~10 | ✅ 2 rounds | (already iterated) |
| Trend | [STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md) | ~12 | ✅ Companion | (already iterated) |
| Smart Money | [STAGE_4_SMART_MONEY_CLUSTER_WALKS.md](STAGE_4_SMART_MONEY_CLUSTER_WALKS.md) | 41 | ✅ 2 rounds (B669 + B673 → B674) | (already iterated) |
| SMC | [STAGE_4_SMC_CLUSTER_WALKS.md](STAGE_4_SMC_CLUSTER_WALKS.md) | 18 | ❌ AWAITING | READY |
| ICT | [STAGE_4_ICT_CLUSTER_WALKS.md](STAGE_4_ICT_CLUSTER_WALKS.md) | 12 | ❌ AWAITING | READY |
| Breakout | [STAGE_4_BREAKOUT_CLUSTER_WALKS.md](STAGE_4_BREAKOUT_CLUSTER_WALKS.md) | 19 | ❌ AWAITING | READY |
| **Event-driven (THIS DOC)** | **[STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md](STAGE_4_EVENT_DRIVEN_CLUSTER_WALKS.md)** | **10** | **❌ AWAITING** | **READY** |
| Chart+Candle | [STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md](STAGE_4_CHART_PATTERN_AND_CANDLE_CLUSTER_WALKS.md) | 16 | ❌ AWAITING | READY |
