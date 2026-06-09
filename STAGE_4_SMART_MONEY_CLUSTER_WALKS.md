# Stage 4 Smart Money Cluster Walks — Per-Strategy Deep-Dive Audit

> **What this document is.** A LIVING per-cluster Stage 4 walk doc covering the smart money strategy cluster (~39 strategies — the largest pending cluster as of the post-B660 close of pivot + trend clusters). Each strategy receives a 7-step deep-dive walk per CHECKLIST #105 with options surfaced and WAITING for owner direction per `feedback_no_rushing_per_strategy_tweak`.
>
> **Owner directive 2026-06-09 (this batch start):** *"smart money largest pending start"* — begin the smart money cluster walks.
>
> **Audience.** Two:
>  (1) **External reviewer** who issued the adversarial audit on the pivot cluster (methodology #1-9 + market-structure C1-C6 + 2nd-wave 2C1-2C7). For you: the smart money cluster is materially different from pivot because (a) data sources are STRUCTURALLY asymmetric (13F long-only, 13D long-only, insider buying open-market money), (b) signals are mostly STATE (quarterly 13F snapshots; weekly bulk feed refresh) not EVENT (insider Form 4 with 2-day lag is the most-EVENT-like signal in the cluster), (c) "smart money" is a confluence overlay applied to ~11 other-cluster strategies (B487-style wraps). The walk methodology adapts to these differences — see [Methodology adaptations for smart money cluster](#methodology-adaptations-for-smart-money-cluster) section.
>  (2) **Future readers** (owner, Claude in later sessions, new collaborators). For you, the [Cluster scope inventory](#cluster-scope-inventory) is the orientation; per-strategy walks below.
>
> **Source of truth.** Code references reflect the current state at commit `1224073bf` (post-B661 doc update). Per `feedback_walk_step3_must_read_producer_source` + CHECKLIST #105: each walk reads producer source end-to-end + grep OPEN_INVESTIGATIONS + schema-vs-API cross-checks.

---

## Methodology adaptations for smart money cluster

The smart money cluster has structural properties that materially change how the 7-step walks apply vs. the pivot + trend clusters. These adaptations are codified once here and referenced from each walk.

### 1. Asymmetric data sources — per `feedback_asymmetric_data_sources_break_mechanical_inverse`

The pivot + trend clusters had mostly-symmetric data sources (OHLCV is symmetric; volume is symmetric; technical indicators support both sides). Smart money is the OPPOSITE — most data sources are STRUCTURALLY long-only by regulatory design:

| Data source | Symmetry | Reason |
|---|---|---|
| **13F (Form 13F)** | LONG-only | SEC rule — 13F discloses only LONG positions of institutional investment managers >$100M; short positions are NOT disclosed. Quarterly with 45-day publication lag. |
| **13D (Schedule 13D)** | LONG-only | SEC rule — 13D filed only when an entity acquires >5% beneficial ownership; no equivalent SHORT disclosure (because shorts don't constitute "beneficial ownership" in the SEC-13D sense). |
| **Form 4 (insider transactions)** | Dual but asymmetric signal value | Open-market PURCHASE (TransactionCode P or L) is strong signal — insider chose to deploy real money. Open-market SALE (TransactionCode S) is much weaker — diversification, tax-planning, lockup expiry, deferred-comp triggers are routine. `data/smart_money.py` insider_signal mitigates with `concentrated_sell` filter (>50% of holdings sold) but the noise asymmetry remains. |
| **Congressional STOCK Act** | Dual | Senators / Representatives disclose both buys + sells; 45-day disclosure window. Producer `data/smart_money.py:congressional_signal` age-weights by transaction_date not disclosure_date (DEC-324 / BUG-240 fix). |
| **Quiver alt-data (lobbying, gov contracts, patents, off-exchange)** | Dual | Activity counts both directions are observable; but most alt-data signals are STATE-ish (monthly cadence). |

**Step 6 missing-inverse audit MUST flag data-source asymmetry.** If a strategy's primary signal is 13F or 13D, a mechanical SHORT mirror is economically false per `feedback_asymmetric_data_sources_break_mechanical_inverse`. Per `feedback_long_short_inverse_audit`: surface the missing-inverse question BUT also surface whether the data structure permits one.

### 2. EVENT vs STATE temporality — per `feedback_signal_temporality_event_vs_state`

Smart money signals span the EVENT/STATE spectrum more broadly than technical clusters:

| Signal class | Temporality | Timing alpha viable? |
|---|---|---|
| Insider Form 4 (`insider_cluster_active`, `insider_unique_buyers_30d`) | EVENT-like | YES — 2-day filing lag; daily cadence; the cluster_buy event happens on a specific bar |
| 13D filing | EVENT | YES — 10-day filing window after 5% threshold crossed; daily cadence; the filing date is the event |
| 13F filing (`institutional_increased_*`, `institutional_persistence_*`) | **STATE** | **NO timing alpha at fire bar** — quarterly snapshots with 45-day publication lag; the position-change happened ~45-135 days before the signal becomes available. Strategies that credit 13F state signals with "smart money sponsorship at this bar" mis-attribute alpha. |
| Congressional STOCK Act (`congressional_signal`) | EVENT-ish | PARTIAL — 45-day disclosure window means the trade happened up to 45 days before the signal; the producer age-weights to mitigate but real timing is fuzzier than insider Form 4 |
| Activist 13D (`activist_13d_long`) | EVENT | YES — same as generic 13D |

**Step 3 producer-temporality classification MUST distinguish 13F-STATE from insider-EVENT.** Docstrings that credit timing-alpha to 13F state signals are overclaim candidates per CHECKLIST (s).

### 3. Confluence wraps vs. standalone strategies

The B487 SM1+SM2 batch added 11 "smart money confluence wraps" — strategies that AND a smart-money gate onto an existing standalone strategy (e.g., `strat_52w_high_breakout_with_smart_money_long` = `strat_52w_high_breakout_long` + smart-money gate). These wraps have a different walk profile:

- **Step 1 (read code)** is mostly the inherited gate set from the base strategy + 1-2 new smart-money gates
- **Step 4 (doc-vs-thesis)** should ask: does the smart-money confluence add information the base strategy lacks, or is it a near-no-op gate that just throttles fires?
- **Step 6 (missing-inverse)** is moot — these are explicitly LONG variants of LONG strategies; the SHORT mirror question is the base strategy's, not the wrap's
- **Step 7 (findings)** options focus on: (a) does the wrap's smart-money gate share marginal information with the base strategy's gates per `feedback_obv_avwap_macd_non_redundancy` distinct-failure-mode test?

### 4. Fire-count starvation risk — per `feedback_minimum_fire_count_gate_before_cube`

Smart money signals fire less often than technical signals. 13F is quarterly; 13D is ~weekly across the universe; insider Form 4 cluster (>=2 unique insiders in 30 days) is monthly per ticker at best. Confluence wraps that AND smart-money onto a base strategy will multiply the fire-rate-suppression. Several B487 wraps may project < min_trades=30/yr post-confluence even when the base strategy is fire-rich.

**Step 7 fire-count discussion** should surface the projected fire-rate independent of the cube; if the projection is < 30/yr (min_trades floor), the cube cannot statistically validate the strategy regardless of design quality. Three responses available: (a) accept rare-but-strong (EXPLORATORY marker like W5/W5m); (b) loosen confluence gate; (c) delete confluence wrap.

---

## Cluster scope inventory

39 strategies in the smart money cluster, grouped by sub-cluster. Status as of doc creation: **0 walked / 39 pending**.

### Sub-cluster A: Foundational insider + activist (5 strategies)

| # | Strategy | Direction | Primary data source | Status |
|---|---|---|---|---|
| SM-1 | `strat_insider_cluster_long` | LONG | Form 4 (insider Quiver bulk feed) | ⏳ PENDING WALK |
| SM-2 | `strat_insider_cluster_with_director_long` | LONG | Form 4 + director isolation | ⏳ PENDING WALK |
| SM-3 | `strat_activist_13d_long` | LONG | SEC 13D | ⏳ PENDING WALK |
| SM-4 | `strat_m_and_a_target_long` | LONG | M&A target alt-data | ⏳ PENDING WALK |
| SM-5 | `strat_short_borrow_trap_avoid` | LONG | Short interest / borrow cost (Quiver) | ⏳ PENDING WALK |

### Sub-cluster B: PEAD + insider confluence (1 strategy)

| # | Strategy | Direction | Primary data source | Status |
|---|---|---|---|---|
| SM-6 | `strat_pead_with_insider_confirmation_long` | LONG | PEAD signal + insider cluster | ⏳ PENDING WALK (cross-cluster: also belongs in PEAD cluster) |

### Sub-cluster C: 13F institutional sleeve — Batch 487 SM1 (B487 + later additions) (~22 strategies)

The largest sub-group. All 13F-based (`institutional_persistence_consumer.py` + helpers). All LONG except `institutional_distribution_short` (and `institutional_capitulation_short` which is a contrarian SHORT inversion).

| # | Strategy | Direction | Notes |
|---|---|---|---|
| SM-7 | `strat_institutional_cluster_long` | LONG | |
| SM-8 | `strat_institutional_buy_momentum_long` | LONG | |
| SM-9 | `strat_institutional_distribution_short` | SHORT | Only mechanical-SHORT in the 13F sleeve — uses 13F NET-DECREASE as proxy; data-source-asymmetry caveat |
| SM-10 | `strat_institutional_oversold_long` | LONG | |
| SM-11 | `strat_institutional_breakout_confirmation_long` | LONG | |
| SM-12 | `strat_institutional_insider_combo_long` | LONG | 13F + Form 4 cross-source |
| SM-13 | `strat_institutional_persistence_breakout_long` | LONG | |
| SM-14 | `strat_institutional_persistence_volume_long` | LONG | |
| SM-15 | `strat_institutional_persistence_oversold_long` | LONG | |
| SM-16 | `strat_institutional_recent_init_momentum_long` | LONG | |
| SM-17 | `strat_institutional_recent_init_volume_long` | LONG | |
| SM-18 | `strat_institutional_multi_quarter_persistence_long` | LONG | |
| SM-19 | `strat_institutional_committed_growth_long` | LONG | |
| SM-20 | `strat_institutional_increased_with_directors_long` | LONG | 13F + insider directors |
| SM-21 | `strat_institutional_persistent_holders_long` | LONG | |
| SM-22 | `strat_institutional_strong_conviction_long` | LONG | |
| SM-23 | `strat_institutional_capitulation_short` | SHORT | Contrarian — 13F mass-exit as bottom signal |
| SM-24 | `strat_institutional_high_conviction_long` | LONG | |
| SM-25 | `strat_institutional_with_directors_long` | LONG | 13F + Form 4 directors |
| SM-26 | `strat_institutional_with_officers_long` | LONG | 13F + Form 4 officers |
| SM-27 | `strat_institutional_persistence_momentum_long` | LONG | |
| SM-28 | `strat_institutional_volume_confirmation_long` | LONG | |

### Sub-cluster D: Classification change × smart-money confluence (2 strategies)

| # | Strategy | Direction | Notes |
|---|---|---|---|
| SM-29 | `strat_classification_change_with_institutional_long` | LONG | Sector-classification-change × 13F overlay |
| SM-30 | `strat_classification_change_with_insider_long` | LONG | Sector-classification-change × insider overlay |

### Sub-cluster E: B487 smart-money confluence wraps (~10 strategies)

These layer a smart-money gate onto a standalone base strategy. Walk profile differs per [methodology adaptation #3](#3-confluence-wraps-vs-standalone-strategies) above.

| # | Strategy | Direction | Base strategy | Notes |
|---|---|---|---|---|
| SM-31 | `strat_bollinger_tight_with_smart_money_long` | LONG | bollinger_tight | |
| SM-32 | `strat_mfi_oversold_with_smart_money_long` | LONG | mfi_oversold | |
| SM-33 | `strat_rsi_oversold_with_smart_money_long` | LONG | rsi_oversold | |
| SM-34 | `strat_52w_high_breakout_with_smart_money_long` | LONG | 52w_high_breakout | |
| SM-35 | `strat_52w_high_breakout_with_smart_money_vol_below_long` | LONG | 52w_high_breakout (low-vol variant) | B613 B-twin |
| SM-36 | `strat_squeeze_breakout_with_smart_money_long` | LONG | squeeze_breakout | |
| SM-37 | `strat_xs_momentum_with_smart_money_long` | LONG | xs_momentum | |
| SM-38 | `strat_xs_low_beta_with_smart_money_long` | LONG | xs_low_beta | |
| SM-39 | `strat_donchian_breakout_with_smart_money_long` | LONG | donchian_breakout | |
| SM-40 | `strat_macd_bullish_with_smart_money_long` | LONG | macd_bullish | |
| SM-41 | `strat_pead_with_smart_money_long` | LONG | PEAD | Cross-cluster with PEAD |

**Cluster total inventory: ~41 strategies** (`~39` per CLAUDE.md docstring; precise count post-inventory `41` because PEAD-with-insider crossed-cluster + 2 classification-change variants. Tightening this number to exactly 41 at end of walk cycle.)

---

## Walk ordering — owner-direction needed

Per `feedback_no_rushing_per_strategy_tweak`: surface options + WAIT for owner direction; one strategy at a time unless owner explicitly batches. Three orderings to choose from:

| Order | Rationale | First 5 walks |
|---|---|---|
| **(a) Foundational-first** (RECOMMENDED) | Walk the standalone insider + 13D + M&A producers first (sub-clusters A + B = 6 strategies); these are foundational because the confluence wraps (sub-cluster E) layer on top of these signal classes. Catching producer-level bugs at the foundation prevents repeated re-findings across the 22-strategy 13F sleeve + 10-strategy confluence wraps. | SM-1 insider_cluster_long → SM-2 insider_cluster_with_director_long → SM-3 activist_13d_long → SM-4 m_and_a_target_long → SM-5 short_borrow_trap_avoid |
| **(b) Sub-cluster sweep** | Walk all 22 13F sleeve strategies (sub-cluster C) first as the biggest single block — risk: same producer (`compute_persistence_signals`) is consumed by all 22; if it has a bug, that bug appears 22 times in the walks. Going first means catching it at strategy #1 instead of #22. | SM-7 institutional_cluster_long → SM-8 institutional_buy_momentum_long → SM-9 institutional_distribution_short → SM-10 institutional_oversold_long → SM-11 institutional_breakout_confirmation_long |
| **(c) Direction-balanced** | Walk the 3 SHORT-direction strategies first (SM-9 distribution, SM-23 capitulation contrarian) for the data-source-asymmetry test, then move to LONG. Surface the symmetric-data-source vs asymmetric-data-source distinction early in the cycle. | SM-9 institutional_distribution_short → SM-23 institutional_capitulation_short (contrarian) → SM-3 activist_13d_long (foundational 13D) → SM-1 insider_cluster_long → SM-7 institutional_cluster_long |

**My recommendation: (a) foundational-first.** Producers in sub-clusters A + B are the dependency root; finding bugs there prevents repeated cross-finding work. Insider-cluster is also the cleanest 2-gate strategy in the cluster, ideal for the first walk to establish the doc's per-walk format.

---

## Walks (status: 0 / 41)

> Each per-strategy walk follows the CHECKLIST #105 7-step format with sub-rules a-s applied where relevant. Each closes with options + my recommendation; owner direction WAITS per `feedback_no_rushing_per_strategy_tweak`. Walks added below as they complete.

### Strategy 1: `strat_insider_cluster_long` — proposed first walk (status: SURFACED, AWAITING OWNER GREEN-LIGHT)

> See [proposed walk block below](#proposed-walk-strat_insider_cluster_long-foundational-sm-1).

---

## Proposed walk: `strat_insider_cluster_long` (foundational SM-1)

> **Status:** PROPOSED — owner direction WAITED per `feedback_no_rushing_per_strategy_tweak`. This is a preview of the walk; the actual walk lands when owner approves direction (and optionally selects an option from Step 7).

### Step 1 — Read the code

[screener.py:2836-2853](backtest/signals/screener.py#L2836-L2853):

```python
def strat_insider_cluster_long(s):
    """Batch 222 (insider clusters 2026-05-18 owner-approved). Cluster of
    insider buys (>=2 unique insiders, open-market purchases, last 30
    days) -> documented ~7pct 12-month alpha.

    Source: Cohen-Malloy-Pomorski 2012 JF "Decoding Inside Information";
    Akbas-Jiang-Koch 2024 RFS update confirming post-publication.
    """
    fires = (
        s.get("insider_cluster_active", False)
        and s.get("price_above_ema_200", True)
    )
    n = s.get("insider_unique_buyers_30d", 0)
    return _strat(fires, "long", "event_driven",
        ["insider_cluster_active", "price_above_ema_200"],
        [f"Insider buying cluster: {n} unique insiders bought "
         f"open-market in last 30 days",
         "Above 200 EMA (regime gate)"])
```

**LONG fires when ALL TWO:**

| Gate | Meaning | Default policy |
|---|---|---|
| `insider_cluster_active` | ≥2 unique insiders open-market-bought in last 30 days (per `compute_insider_cluster_signals` in `signals/insider_buying.py`) | **default-False** (fail-safe) |
| `price_above_ema_200` | Today's close > 200-day EMA | **default-True** ⚠ silent-gap candidate |

Single direction — LONG only. No SHORT mirror (data-source asymmetry — see Step 6).

### Step 2 — Classify

- Category: `event_driven` (insider buying is the foundational event)
- Single LONG (not dual)
- STRATEGY_REGIME_AFFINITY: TBD — needs grep at walk time
- Last touched: B222 (added 2026-05-18 in the insider-clusters batch)

### Step 3 — Producer source-read + temporality (per CHECKLIST #105 + `feedback_signal_temporality_event_vs_state`)

**Producer:** `compute_insider_cluster_signals` in [backtest/signals/insider_buying.py:96-157](backtest/signals/insider_buying.py#L96-L157).

**Inputs:** Quiver `live/insiders` bulk feed (column-name mismatch BUG-272 fixed Pass 53; reads from `_INSIDERS_BY_TICKER` cache populated by `_load_insiders_global` from `data_prefetch/quiver/insiders/global.parquet`).

**Filter chain (per source):**
1. Date window: `Date >= as_of - 30 days` AND `Date <= as_of`
2. Per Pass 53 BUG-272 hot-path: `AcquiredDisposedCode == 'A' AND TransactionCode == 'P'` (open-market purchase)
3. Group by `Name` (unique-insider count)
4. `insider_cluster_active = unique_buyers >= 2` (min threshold)

**Outputs produced:**
- `insider_cluster_active` (bool — primary gate)
- `insider_unique_buyers_30d` (int — sample-size diagnostic)
- `insider_total_shares_bought_30d` (float — magnitude diagnostic)
- `insider_director_buyers_30d` (int — feeds SM-2 strat_insider_cluster_with_director_long)
- `insider_officer_buyers_30d` (int — could feed an officer-isolation variant)

**Temporality:** EVENT-like. Form 4 has a 2-day reporting requirement (insider must file within 2 business days of the transaction). The producer reads `Date` (filing date) so the signal becomes available ~2-3 business days after the actual purchase. For a 30-day rolling window, this is timing-EVENT (the cluster event itself occurred recently and the signal lights up within days). ✅ Docstring claim "real money in last 30 days" is consistent with EVENT classification per CHECKLIST (s).

**Note re. parallel producer:** `data/smart_money.py:insider_signal` exists in parallel and produces a categorical signal (none/buy/weak_buy/strong_buy/cluster_sell/concentrated_sell). It is a DIFFERENT producer from `compute_insider_cluster_signals` despite reading the same Quiver bulk feed. Strategies in this cluster appear to consume the boolean producer; the categorical producer may be consumed elsewhere (B487 wraps?). **OPEN: cross-reference which strategies consume which insider producer** — surface in walk Step 5.

**`insider_buying.py` schema cross-check:** the producer assumes columns `Date`, `AcquiredDisposedCode`, `TransactionCode`, `Name`, `Shares`, `isDirector`, `isOfficer`. If the underlying Quiver bulk-feed schema changes (e.g., column rename — BUG-272 lineage), the producer fails-safe via `if sub is None or sub.empty: return {}` paths but the failure mode is silent. Per CHECKLIST #105 docs-cross-check: there is no explicit schema-version pin in the producer. **OPEN: add schema-version pin or producer-version assertion** — surface in walk Step 5.

### Step 4 — Doc-vs-thesis

**Docstring claim:** "Cluster of insider buys (>=2 unique insiders, open-market purchases, last 30 days) → documented ~7pct 12-month alpha. Source: Cohen-Malloy-Pomorski 2012 JF; Akbas-Jiang-Koch 2024 RFS."

**Code-vs-docstring match:**
- ✅ "≥2 unique insiders" — yes, `unique_buyers >= 2` in producer
- ✅ "open-market purchases" — yes, `TransactionCode == 'P'` filter
- ✅ "last 30 days" — yes, `lookback_days=30` default
- ⚠ "12-month alpha" — the strategy doesn't enforce a 12-month hold; that's the holding horizon in the Cohen-Malloy-Pomorski paper. **OPEN: does the engine's exit method match a 12-month-alpha thesis or does the default 1× ATR trail close most positions in 1-4 weeks?** This is the canonical "thesis-vs-implementation mismatch" finding class for event-driven strategies.

**Source credibility:**
- ✅ Cohen-Malloy-Pomorski 2012 JF "Decoding Inside Information" — real paper, well-cited (~600 citations).
- ✅ Akbas-Jiang-Koch 2024 RFS — real post-publication update, addresses Cohen-Malloy-Pomorski post-2012 anomaly persistence.

### Step 5 — OPEN_INVESTIGATIONS grep (per CHECKLIST #105)

To run at walk time:
```sh
grep -nE "insider_cluster|insider_unique_buyers|compute_insider_cluster_signals" OPEN_INVESTIGATIONS.md AUDIT.md
```

Expected findings to surface in the actual walk (preview):
- BUG-272 historical (RESOLVED-IMPLEMENTED Pass 53 v8h+1) — column-name mismatch in `live/insiders` schema; ALREADY FIXED. Mention for completeness.
- The parallel-producer concern from Step 3 — should be a NEW open investigation if not yet logged.

### Step 6 — Missing-inverse + economic-symmetry (per `feedback_long_short_inverse_audit` + `feedback_asymmetric_data_sources_break_mechanical_inverse`)

**Mechanical inverse check:** A symmetric SHORT mirror would be `strat_insider_cluster_short` firing when ≥2 unique insiders SOLD in last 30 days. Producer `data/smart_money.py:insider_signal` does emit `cluster_sell` and `concentrated_sell` categorical values that could support this.

**Economic-symmetry test:** **FAILS.** Per `feedback_asymmetric_data_sources_break_mechanical_inverse`:
- Insider PURCHASES (TransactionCode P) are open-market money — insider chose to deploy capital. Strong signal.
- Insider SALES (TransactionCode S) have multiple non-information-driven reasons:
  - Diversification (typical executive comp concentrates wealth in own stock)
  - Tax planning (long-term cap gains realization timing)
  - Lockup expiry (post-IPO 6-month restriction)
  - Deferred-compensation triggers (Rule 10b5-1 pre-scheduled sales)
  - Estate planning
- The producer's `concentrated_sell` (>50% of holdings) tries to filter — but even concentrated sells have non-information reasons (founder retiring, divorce).

**Conclusion:** A mechanical SHORT mirror would be **economically false**. Per `feedback_asymmetric_data_sources_break_mechanical_inverse`, do NOT propose `strat_insider_cluster_short` as a Class 7 NEW. The asymmetry is structural and inherent to the data source.

**Class 7 NEW candidates that ARE economically defensible** (raise for owner consideration):
- `strat_insider_cluster_concentrated_sell_short` — only SHORT on `concentrated_sell` (>50% holdings dumped), NOT generic cluster_sell. Tighter threshold matches stronger thesis.
- DEFERRED — needs owner consideration before any new wire-up; per `feedback_wire_new_strategies_on_the_spot` Class 7 NEW gets wired same-turn, but only with owner approval.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1** | `s.get("price_above_ema_200", True)` is default-True silent-gap pattern — same family as the B659-unified W6/W7/W8 cases. When `price_above_ema_200` key is absent (e.g., short-history ticker), the gate auto-passes the trend filter, effectively reducing the strategy to insider_cluster alone. Symmetric fix: swap to `s.get("price_above_ema_200", False)`. Per `feedback_family_bug_grep_before_one_liners`: this is the B659 family-bug pattern; should be applied to all event_driven strategies as a sweep (SM-1, SM-2, and any others using `price_above_ema_200` as default-True). | MEDIUM |
| F1b | Per `feedback_never_use_NOT_s_get_pattern` cross-check: no NOT-pattern in this strategy. ✅ | — |
| F2 | Docstring is present, cites real sources, accurately describes producer behavior. ✅ | — |
| **F3** | Regime affinity entry TBD — need to grep at walk time. Insider-cluster events are themselves regime-conditional (insider buying spikes during bear regimes — Cohen-Malloy-Pomorski finds the alpha is largest in crisis / oversold conditions). If no regime entry, B291 default applies. If a 21-DEC-style narrow regime entry exists, it's a B271 family-bug candidate. | TBD |
| **F-temporality** | Producer is EVENT-classified. Docstring claim of "12-month alpha" suggests the strategy expects a long-hold profile, but the engine's exit method (1× ATR trail per default) likely closes positions in days-to-weeks. Surfacing as F-thesis-vs-implementation mismatch. **Cube replay against multiple hold durations would surface whether the 12-month thesis is realized.** | MEDIUM |
| F-data-source-asymmetry | Per `feedback_asymmetric_data_sources_break_mechanical_inverse`: mechanical SHORT mirror would be economically false; do NOT propose. ✅ | — |
| F-fire-count | Insider cluster (≥2 unique insiders, 30-day window) is a **rare event** — Cohen-Malloy-Pomorski reports ~0.5-1% of stock-months exhibit a cluster in their sample. T1a universe-scale projection: 500 tickers × 12 months × 0.005-0.01 = 30-60/yr per direction. **BORDERLINE on min_trades=30.** Cube empirical adjudicates. Per `feedback_minimum_fire_count_gate_before_cube`: surface this BEFORE adding new gates. | INFO |
| F-parallel-producer | Two parallel insider producers exist (`insider_buying.py:compute_insider_cluster_signals` boolean + `data/smart_money.py:insider_signal` categorical). Which strategies consume which? Cross-source consistency? Surface as new investigation. | LOW (housekeeping) |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo — no changes (defer F1 sweep + F-temporality to Stage 5) |
| **(b)** F1 swap `price_above_ema_200` default True → False symmetric with B659 unified policy. RECOMMENDED for narrow scope (this strategy only). |
| (c) (b) + family-grep sweep across all event_driven strategies for the same default-True pattern, applied bundled. Per `feedback_family_bug_grep_before_one_liners`: this IS the right scope-level if the pattern is widespread. Per `feedback_local_changes_default_global_needs_approval`: needs explicit owner approval before applying because >1 strategy affected. |
| (d) (b) + Class 7 NEW `strat_insider_cluster_concentrated_sell_short` wired with `concentrated_sell` boolean (tighter threshold) per economic-symmetry test in Step 6. Per `feedback_wire_new_strategies_on_the_spot`: Class 7 NEW gets wired same-turn IF owner approves the design. |
| (e) Stage 5 deferral — defer all changes to cube empirical |

**My recommendation: (b) narrow-scope F1 swap.** Cleanest application of the B659 silent-gap-unify discipline; closes the documented `feedback_family_bug_grep_before_one_liners` concern locally without expanding blast radius. Surface (c) as the natural follow-on for owner to consider AFTER (b) lands; surface (d) as a separate Class 7 NEW question for owner consideration.

**Awaiting owner direction:**
1. **Ordering choice:** (a) foundational-first / (b) sub-cluster sweep / (c) direction-balanced — see [Walk ordering](#walk-ordering--owner-direction-needed)
2. **First-walk option:** (a) status quo / **(b) RECOMMENDED** F1 narrow swap / (c) family-grep bundled fix / (d) F1 + Class 7 NEW concentrated_sell short / (e) Stage 5 deferral
3. **Class 7 NEW concentrated_sell_short:** wire as separate consideration? — see Step 6

---

## Outstanding queue tickets surfaced (smart money cluster)

> Will be populated as walks complete; preview from SM-1 surface:

- `S4-EVENT-DRIVEN-DEFAULT-TRUE-EMA-SWEEP` — family-grep sweep of event_driven strategies using `price_above_ema_200` default-True (B659 silent-gap-unify family-bug discipline)
- `S5-INSIDER-CLUSTER-HOLD-DURATION-VALIDATION` — Cohen-Malloy-Pomorski 12-month-alpha thesis vs default 1× ATR trail exit; cube replay across hold durations
- `S4-INSIDER-PRODUCER-PARALLEL-AUDIT` — two parallel insider producers (boolean vs categorical); which strategies consume which; cross-source consistency
- `S4-INSIDER-SCHEMA-PIN` — Quiver `live/insiders` schema-version assertion / pin

---

## Cluster-wide methodology references

Linked feedback memories applied throughout this cluster's walks:

- [`feedback_no_rushing_per_strategy_tweak`](memory) — one strategy at a time; surface + WAIT
- [`feedback_per_strategy_deep_dive_stage4`](memory) — 7-step deep-dive; trigger-logic + producer-health + thesis + arbitrary-threshold + missing-inverse
- [`feedback_walk_step3_must_read_producer_source`](memory) + CHECKLIST #105 — read all associated scripts + docs end-to-end
- [`feedback_signal_temporality_event_vs_state`](memory) — EVENT vs STATE classification + timing-alpha viability
- [`feedback_asymmetric_data_sources_break_mechanical_inverse`](memory) — data-source-symmetry check before proposing inverses
- [`feedback_long_short_inverse_audit`](memory) — missing-inverse audit
- [`feedback_never_use_NOT_s_get_pattern`](memory) — positive-symmetric signals
- [`feedback_obv_avwap_macd_non_redundancy`](memory) — per-gate distinct-failure-mode test
- [`feedback_minimum_fire_count_gate_before_cube`](memory) — pre-cube fire-count gate
- [`feedback_avwap_redundant_with_ema_trend_filter`](memory) — AVWAP/EMA collinearity skip-rationale
- [`feedback_sequence_or_split_when_stacking_changes`](memory) — ≥3 simultaneous changes warning
- [`feedback_family_bug_grep_before_one_liners`](memory) — family-bug grep before one-line removals
- [`feedback_structural_symmetry_not_economic_symmetry`](memory) — explicit economic-symmetry comment on dual strategies
- [`feedback_reconcile_against_prior_deletions`](memory) — when adding gates, check prior deletions
- [`feedback_narrow_scope_blast_radius`](memory) + [`feedback_local_changes_default_global_needs_approval`](memory) — LOCAL default; global needs approval

CHECKLIST extensions applied:
- (g) sequence-or-split
- (k) fire-count gate (measurement not projection)
- (l) skip-rationale must be POSITIVE
- (m) economic-symmetry comment on dual strategies
- (n) family-bug bundled audit before one-liners
- (q) candle-pattern PIT (N/A this cluster)
- (r) timeframe-mismatch (N/A this cluster — smart money is by-construction daily-bar)
- (s) EVENT-STATE-wired-finding
- #105 walks read producer source + docs end-to-end
