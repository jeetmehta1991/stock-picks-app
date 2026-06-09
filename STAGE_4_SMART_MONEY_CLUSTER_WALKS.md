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

## Cross-strategy patterns surfaced by the cluster walk (B664 candidate)

> After walking all 41 strategies, five cross-strategy patterns emerged. These are the actionable cluster-level findings; each per-strategy walk's Step 7 references the relevant pattern. The patterns + recommended B664 batch are presented here for owner approval before any code changes apply.

### Pattern A — `price_above_ema_50` default-True silent-gap (B663 ema_200 sibling)

Pre-flight grep shows 9 occurrences of `s.get("price_above_ema_50", True)` in `screener.py`. 6 belong to the smart money cluster; 3 are in other clusters.

| Strategy | Cluster | Line |
|---|---|---|
| SM-8 `strat_institutional_buy_momentum_long` | smart money | 4383 |
| SM-14 `strat_institutional_persistence_volume_long` | smart money | 4779 |
| SM-17 `strat_institutional_recent_init_volume_long` | smart money | 4839 |
| SM-24 `strat_institutional_high_conviction_long` | smart money | 4996 |
| SM-27 `strat_institutional_persistence_momentum_long` | smart money | 5053 |
| SM-28 `strat_institutional_volume_confirmation_long` | smart money | 5072 |
| `strat_avwap_50_reclaim` | other | 4118 |
| `strat_flag_bull_long` | other (chart pattern) | 4185 |
| `strat_classification_change_momentum_long` | other (classification change) | 4652 |

**Same family-bug as B663's ema_200 sweep.** Options:
- (A.b) **Cluster-only sweep** — 6 SM-cluster strategies; matches `feedback_narrow_scope_blast_radius`
- (A.c) **Full screener sweep** — 9 strategies; symmetric with B663 precedent (B663 was a 70-strategy full-screener sweep on ema_200)

### Pattern B — STATE-as-EVENT docstring overclaim on 13F institutional sleeve

B611 + B613 established the correct framing: 13F is QUARTERLY with 45-day filing lag → `institutional_buy` is a slow ELIGIBILITY FILTER (constant ~90 days), NOT bar-of-fire timing alpha. B611 reframed SM-11 (`institutional_breakout_confirmation_long`). 20 other institutional sleeve strategies still have docstrings that imply timing alpha:

| Strategy | Overclaim phrase |
|---|---|
| SM-7 `institutional_cluster_long` | "cluster-buys forecast 1-month alpha" |
| SM-8 `institutional_buy_momentum_long` | "smart money flow" with momentum |
| SM-9 `institutional_distribution_short` | "Sias 2004 institutional herding" |
| SM-10 `institutional_oversold_long` | "Schwed cash on sidelines" |
| SM-12 `institutional_insider_combo_long` | "multiplicative edge" |
| SM-13 `institutional_persistence_breakout_long` | "institutional-sponsored breakout" |
| SM-14 `institutional_persistence_volume_long` | "retail tape participating" |
| SM-15 `institutional_persistence_oversold_long` | "institutional accumulation during oversold" |
| SM-16 `institutional_recent_init_momentum_long` | "market has NOT yet priced in" |
| SM-17 `institutional_recent_init_volume_long` | "retail tape participating" |
| SM-20 `institutional_increased_with_directors_long` | "triple smart-money validation" |
| SM-21 `institutional_persistent_holders_long` | "Yan-Zhang RFS cross-fund consensus" |
| SM-22 `institutional_strong_conviction_long` | "Frazzini-Lamont institutional consensus" |
| SM-23 `institutional_capitulation_short` | "Sias 2004 + Lo-Wang capitulation signature" |
| SM-24 `institutional_high_conviction_long` | "canonical CFM cluster signal" |
| SM-25 `institutional_with_directors_long` | "dual board-level + fund-manager confirmation" |
| SM-26 `institutional_with_officers_long` | "direct competence + conviction signal" |
| SM-27 `institutional_persistence_momentum_long` | "momentum confirms institutional conviction" |
| SM-29 `classification_change_with_institutional_long` | "highest-conviction re-rating signal" |
| SM-10 also has citation error | Cites Cohen-Malloy-Pomorski 2012 (insider paper) for a 13F strategy |

**Exempt (already honest or genuinely STATE-class):** SM-11 (B611 done), SM-18 (4q precompute), SM-19 (4q precompute), SM-28 (already partially acknowledges 45-day lag), SM-30 (2 EVENT gates).

**Fix:** docstring-honesty sweep symmetric with B611+B613 — zero behavior change; just truthful documentation. SM-10 additionally needs citation correction.

### Pattern C — `institutional_negative` SHORT data-source-asymmetry (SM-9 + SM-23)

B611 explicitly deleted `strat_institutional_breakdown_confirmation_short` because **13F is SEC long-only by rule**; `institutional_negative` (decreased > increased) means trimming, not bear-conviction (rebalancing/redemptions/tax-loss dominate).

Two SHORT strategies still use this pattern: SM-9 (institutional_distribution_short) + SM-23 (institutional_capitulation_short).

Per `project_no_apriori_strategy_pruning.md`: no a-priori deletion before Stage D empirical verdict. **Options:**
- (C.b) **Docstring caveat only** — acknowledge B611-class asymmetry; defer deletion to Stage D
- (C.c) **Delete both** per B611 precedent — would override no-pruning rule; needs explicit owner approval

### Pattern D — Stale "NOT REGISTERED" docstrings on SM-3 + SM-4

Both SM-3 (`strat_activist_13d_long`) and SM-4 (`strat_m_and_a_target_long`) have docstrings claiming "NOT REGISTERED in ALL_STRATEGIES in Batch 522 — ships SCAFFOLD-only" — but B531 wired both into `ALL_STRATEGIES` (line 5939+5944) and the producer into `screen_instrument` (line 6758). Stale lineage; informational fix.

### Pattern E — `_has_smart_money_buy` UNION-not-confluence docstring overclaim on 9 confluence wraps

`_has_smart_money_buy` helper at [screener.py:5567](backtest/signals/screener.py#L5567) is documented (per B613) as a UNION of EVENT-or-STATE components, NOT a confluence signal. 9 wraps still claim "Smart-money buy confirmation" in their bullet text:

| Strategy | Status |
|---|---|
| SM-31 `bollinger_tight_with_smart_money_long` | needs B613 reframe |
| SM-32 `mfi_oversold_with_smart_money_long` | needs B613 reframe |
| SM-33 `rsi_oversold_with_smart_money_long` | needs B613 reframe |
| SM-34 `52w_high_breakout_with_smart_money_long` | ✅ B613 done |
| SM-35 `52w_high_breakout_with_smart_money_vol_below_long` | ✅ B613 done |
| SM-36 `squeeze_breakout_with_smart_money_long` | needs B613 reframe |
| SM-37 `xs_momentum_with_smart_money_long` | needs B613 reframe |
| SM-38 `xs_low_beta_with_smart_money_long` | needs B613 reframe |
| SM-39 `donchian_breakout_with_smart_money_long` | needs B613 reframe |
| SM-40 `macd_bullish_with_smart_money_long` | needs B613 reframe |
| SM-41 `pead_with_smart_money_long` | needs B613 reframe |

**Fix:** Bullet-text reframe to "Smart-money EVENT(timing) or STATE(eligibility) buy per B613 F2a" (mirror of SM-34's existing bullet text). Zero behavior change.

### F3 cluster-wide regime affinity audit per B663 lesson

Per B663 self-correction, every regime affinity entry was grep'd for lineage BEFORE proposing any change:

| Status | Count | Entries | Decision |
|---|---|---|---|
| Explicit `STRATEGY_REGIME_AFFINITY` with documented lineage | 4 | SM-1 + SM-2 (B263 Phase 1A-alpha empirical); SM-7 (B418 cube bear=+0.16); SM-8 (B418 cube bull=+0.12); SM-6 (B263 explicit `drop crisis`) | **DO NOT CHANGE — intentional** |
| No explicit entry → B291 LONG default `{bull, neutral}` | 33 LONG | All other LONG strategies | **DO NOT CHANGE — no lineage; B291 default applies** |
| No explicit entry → B291 SHORT default `{bear, crisis, neutral}` | 2 SHORT | SM-9 + SM-23 | **DO NOT CHANGE — B291 default applies** |

**F3 result: 0 regime entry changes.** Same discipline as B663 self-correction (lineage-grep-before-delete) per [`feedback_regime_selector_lineage_grep_before_delete`](memory).

---

## B664 candidate consolidated proposal

Bundling the conservative recommended option from each pattern into one batch per `feedback_path_c_min_batch_size`:

| Pattern | (a) Status quo | (b) RECOMMENDED | (c) Larger |
|---|---|---|---|
| **A. ema_50 default-True sweep** | No change | **Cluster-only sweep (6 SM strategies)** | Full screener sweep symmetric with B663 (9 strategies — requires explicit cross-cluster approval) |
| **B. STATE-as-EVENT docstring sweep** | No change | **20-strategy docstring honesty reframe + SM-10 citation fix** | Same + Class 7 NEW research ticket `S5-13F-EVENT-COMPONENT-ISOLATION` |
| **C. SM-9 + SM-23 data-source-asymmetry** | No change | **Docstring caveat only** — flag the asymmetry, defer deletion to Stage D | Delete SM-9 + SM-23 (overrides `project_no_apriori_strategy_pruning` — needs explicit owner approval) |
| **D. SM-3 + SM-4 stale docstrings** | No change | **Replace "NOT REGISTERED" with B531 lineage** (mechanical) | — |
| **E. 9 confluence-wrap bullet text** | No change | **B613 reframe on 9 wraps** — symmetric with SM-34/SM-35 | — |

**B664 = (A.b) + (B.b) + (C.b) + (D.b) + (E.b).** Net code change: **6 mechanical ema_50 line edits** + ~30 docstring rewrites + 1 citation correction. **Zero behavior change** apart from the 6 ema_50 silent-gap fixes. New test pin file with isolation pins for the 6 ema_50 fixes + bundle assertion for `s.get("price_above_ema_50", True)` regression-block (symmetric with B663 test pin file).

**Alternative: A.c full screener sweep on ema_50** — if owner prefers symmetric handling with B663 ema_200 precedent (B663 was a 70-strategy full-screener sweep), then ema_50 should be too. Trade-off: blast radius extends to 2 strategies outside smart money cluster, but the family-bug pattern is mechanically identical.

**Awaiting cluster-level owner direction (B664 approval):**
1. Pattern A scope: **(b) cluster-only** / (c) full screener sweep symmetric with B663
2. Pattern B scope: **(b) 20-strategy docstring sweep** / no change
3. Pattern C disposition: **(b) docstring caveat** / (c) delete (overrides no-pruning rule)
4. Patterns D + E: approve as recommended (small, mechanical)
5. **Class 7 NEW from B662 SM-1 surface:** `concentrated_sell_short` — still deferred / wire it / drop the question
6. **Class 7 NEW from SM-3 walk:** `strat_activist_13d_oversold_long` confluence variant — surface as queued / wire it / drop the question
7. **Class 7 NEW from SM-4 walk:** acquirer-side SHORT (requires producer extension to distinguish target vs acquirer) — surface as queued / wire it / drop the question

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

## Cluster current state — all 41 strategies snapshot

> Snapshot of every strategy in the smart money cluster after the full cluster walk. For each: sub-cluster + direction + walk status + pattern findings + B664 candidate action.

| SM# | Strategy | Sub-cluster | Direction | Walk status | Patterns flagged | B664 candidate |
|---|---|---|---|---|---|---|
| SM-1 | `insider_cluster_long` | A | LONG | ✅ B663 | A1 (ema_200) | (none — closed) |
| SM-2 | `insider_cluster_with_director_long` | A | LONG | ✅ B663 | A1 (ema_200) | (none — closed) |
| SM-3 | `activist_13d_long` | A | LONG | ⏳ | D | D — docstring fix |
| SM-4 | `m_and_a_target_long` | A | LONG | ⏳ | D | D — docstring fix |
| SM-5 | `short_borrow_trap_avoid` | A | avoid | ⏳ | — | (queue ticket only) |
| SM-6 | `pead_with_insider_confirmation_long` | B | LONG | ⏳ | — | (queue ticket only) |
| SM-7 | `institutional_cluster_long` | C | LONG | ⏳ | B | B — docstring reframe |
| SM-8 | `institutional_buy_momentum_long` | C | LONG | ⏳ | A + B | A.b + B |
| SM-9 | `institutional_distribution_short` | C | SHORT | ⏳ | **C** + B | C.b + B |
| SM-10 | `institutional_oversold_long` | C | LONG | ⏳ | B + citation error | B + citation fix |
| SM-11 | `institutional_breakout_confirmation_long` | C | LONG | ✅ B611 | (already done) | (none — closed) |
| SM-12 | `institutional_insider_combo_long` | C | LONG | ⏳ | B | B |
| SM-13 | `institutional_persistence_breakout_long` | C | LONG | ⏳ | B | B |
| SM-14 | `institutional_persistence_volume_long` | C | LONG | ⏳ | A + B | A.b + B |
| SM-15 | `institutional_persistence_oversold_long` | C | LONG | ⏳ | B | B |
| SM-16 | `institutional_recent_init_momentum_long` | C | LONG | ⏳ | B | B |
| SM-17 | `institutional_recent_init_volume_long` | C | LONG | ⏳ | A + B | A.b + B |
| SM-18 | `institutional_multi_quarter_persistence_long` | C | LONG | ⏳ | (none — genuine STATE) | (none) |
| SM-19 | `institutional_committed_growth_long` | C | LONG | ⏳ | (none — genuine STATE) | (none) |
| SM-20 | `institutional_increased_with_directors_long` | C | LONG | ⏳ | B | B |
| SM-21 | `institutional_persistent_holders_long` | C | LONG | ⏳ | B | B |
| SM-22 | `institutional_strong_conviction_long` | C | LONG | ⏳ | B | B |
| SM-23 | `institutional_capitulation_short` | C | SHORT | ⏳ | **C** + B | C.b + B |
| SM-24 | `institutional_high_conviction_long` | C | LONG | ⏳ | A + B | A.b + B |
| SM-25 | `institutional_with_directors_long` | C | LONG | ⏳ | B | B |
| SM-26 | `institutional_with_officers_long` | C | LONG | ⏳ | B | B |
| SM-27 | `institutional_persistence_momentum_long` | C | LONG | ⏳ | A + B | A.b + B |
| SM-28 | `institutional_volume_confirmation_long` | C | LONG | ⏳ | A + B partial | A.b + minor doc polish |
| SM-29 | `classification_change_with_institutional_long` | D | LONG | ⏳ | B | B |
| SM-30 | `classification_change_with_insider_long` | D | LONG | ⏳ | (none — 2 EVENT gates) | (queue ticket only) |
| SM-31 | `bollinger_tight_with_smart_money_long` | E | LONG | ⏳ | E | E |
| SM-32 | `mfi_oversold_with_smart_money_long` | E | LONG | ⏳ | E | E |
| SM-33 | `rsi_oversold_with_smart_money_long` | E | LONG | ⏳ | E | E |
| SM-34 | `52w_high_breakout_with_smart_money_long` | E | LONG | ✅ B613 | (already done) | (none — closed) |
| SM-35 | `52w_high_breakout_with_smart_money_vol_below_long` | E | LONG | ✅ B613 | (already done) | (none — closed) |
| SM-36 | `squeeze_breakout_with_smart_money_long` | E | LONG | ⏳ | E | E |
| SM-37 | `xs_momentum_with_smart_money_long` | E | LONG | ⏳ | E | E |
| SM-38 | `xs_low_beta_with_smart_money_long` | E | LONG | ⏳ | E | E |
| SM-39 | `donchian_breakout_with_smart_money_long` | E | LONG | ⏳ | E | E |
| SM-40 | `macd_bullish_with_smart_money_long` | E | LONG | ⏳ | E | E |
| SM-41 | `pead_with_smart_money_long` | E | LONG | ⏳ | E + redundancy w/ SM-6 | E + queue overlap ticket |

**Tally:**
- Already closed by prior batches: 4 (SM-1, SM-2 — B663; SM-11 — B611; SM-34, SM-35 — B613)
- B664 candidate per-strategy actions: 32 (Patterns A: 6 strategies; B: 18 strategies; C: 2 strategies; D: 2 strategies; E: 9 strategies — overlapping where strategies need multiple patterns applied)
- No action needed (queue tickets only): 5 (SM-5, SM-6, SM-18, SM-19, SM-30)
- **Cluster walk status: 41/41 walked.** B664 approval gates the code/doc changes.

---

## Walks (status: 41 / 41 walked; B663 closed 2; B611+B613 closed 3; B664 candidate covers 32; 5 require no action)

> Each per-strategy walk follows the CHECKLIST #105 7-step format with sub-rules a-s applied where relevant. Each closes with options + my recommendation; owner direction WAITS per `feedback_no_rushing_per_strategy_tweak`. Walks added below as they complete.

### Strategy 1: `strat_insider_cluster_long` — ✅ WALKED B663 (FINAL STATUS POST-B663 below)

### Strategy 2: `strat_insider_cluster_with_director_long` — ✅ WALKED B663 (same family-bug fix applied; FINAL STATUS POST-B663 below)

---

## FINAL STATUS POST-B663 — SM-1 + SM-2 closed

> Owner directive 2026-06-09 (B662 first-walk surface + B663 pre-flight discovery): owner approved option (δ) "full screener sweep" after pre-flight grep revealed the SM-1 F1 finding was a 70-strategy family-bug pattern, not a narrow 1-strategy fix. B663 shipped the full family-bug sweep + closed SM-1 + SM-2 simultaneously since both received identical treatment.

### What shipped (B663 — full screener-wide family-bug sweep)

**F1 — `price_above_ema_200` default-True silent-gap (70 strategies):**
- All 70 occurrences of `s.get("price_above_ema_200", True)` swapped to default-False across screener.py
- Symmetric with B659 LONG default-True silent-gap unification policy (W6/W7/W8 AVWAP)
- 4 strategies already used default-False; total post-B663 default-False count = 74

**F1b — `(not above_200)` NOT-pattern silent-gap (7 strategies):**

The 70-occurrence grep surfaced 5 local-var assignments + 2 additional cases where the local-var was already default-False but still used `(not above_200)` in SHORT branches. ALL 7 received positive-symmetric refactor per `feedback_never_use_NOT_s_get_pattern`:

| Strategy | Line | Refactor |
|---|---|---|
| `strat_stochrsi_oversold` | ~941 | LONG `above_200` + SHORT `below_200 = s.get("below_ema_200", False)` |
| `strat_rsi_oversold` | ~1258 | Same |
| `strat_bollinger_lower` | ~1340 | Same |
| `strat_bollinger_tight` | ~1379 | Same |
| `strat_smc_inverse_fvg` | ~3180 | Same (also replaces `below_200 = not above_200` literal) |
| `strat_williams_r_oversold` | ~869 | Was default-False local-var but still NOT-pattern SHORT — pre-flight surfaced |
| `strat_cpr_narrow_momentum` | ~2074 | Was default-False local-var but still NOT-pattern SHORT — removed misleading "left as-is for readability" comment (the rationale was WRONG: default-False → `not False = True` → SHORT auto-passes) |

**F3 — regime affinity audit (10 exclude-crisis entries) — NO DELETIONS, lineage-grep self-correction documented:**

The SM-1 walk's original F3 finding proposed deleting the `insider_cluster_long` + `insider_cluster_with_director_long` exclude-crisis regime entries citing Cohen-Malloy-Pomorski 2012 (crisis is the alpha regime for insider buying).

**Pre-flight grep of `regime_selector.py` lines 261-264 revealed:**

```python
# Event-driven + quality (Batch 222): insider clusters work across
# all regimes (Cohen-Malloy-Pomorski 2012); quality factor long-
# only in bull/neutral; PEAD+insider confirmation similarly long-bias.
# Batch 263 Class C tightening: long-bias strategies should NOT fire
# in crisis. Even strong smart-money signals (insider clusters) fail
# in crisis regime (Phase 1A-alpha: 36 crisis trades at 22pct WR).
"insider_cluster_long":                {"bull", "neutral", "bear"},
"insider_cluster_with_director_long":  {"bull", "neutral", "bear"},
```

**The entries are INTENTIONAL B263 Phase 1A-alpha empirical overrides of the literature thesis** (36 crisis trades at 22% WR — far below the 55% WR passing-criterion floor; literature thesis explicitly overridden by our empirical data on T1a 2020-2024). The F3 finding was a CHECKLIST violation on my part: I cited the literature without grep'ing the lineage BEFORE proposing the delete.

**Audit of all 10 exclude-crisis entries:**

| Entry | Lineage | Status |
|---|---|---|
| `totm_long` / `pre_holiday_long` / `january_effect_small_cap_long` / `halloween_seasonal_long` | Calendar group header at lines 142-150: "Crisis NOT added per the original 'calendar premia presume risk-on' reasoning" | ✅ INTENTIONAL |
| `xs_combined_momentum_low_ivol` | Factor group header at 252-254: "filter is self-gating" | ✅ INTENTIONAL |
| `insider_cluster_long` | B263 lineage at 261-264 (above) | ✅ INTENTIONAL |
| `insider_cluster_with_director_long` | Same B263 lineage | ✅ INTENTIONAL |
| `pead_with_insider_confirmation_long` | Explicit per-line `# Batch 263: drop crisis` at 269 | ✅ INTENTIONAL |
| `smc_inverse_fvg` | Explicit per-line `# Batch 263: drop crisis` at 296 | ✅ INTENTIONAL |
| `smc_equal_lows_sweep_long` | SMC group header at 290-293 (B271 framework consistency) | ✅ INTENTIONAL |

**Result: 0 regime entries deleted.** New memory note added: [`feedback_regime_selector_lineage_grep_before_delete.md`](memory) — codifies the lineage-grep-before-delete rule into walk methodology going forward.

### Code reference

- [screener.py strat_insider_cluster_long](backtest/signals/screener.py) — line ~2846: `s.get("price_above_ema_200", False)` (was True)
- [screener.py strat_insider_cluster_with_director_long](backtest/signals/screener.py) — line ~2864: same fix
- [regime_selector.py STRATEGY_REGIME_AFFINITY](backtest/engine/regime_selector.py) — lines 265-266: UNCHANGED (B263 intentional)

### Test pins

- [test_batch663_price_above_ema_200_family_sweep.py](backtest/tests/test_batch663_price_above_ema_200_family_sweep.py) — 14 pins:
  - Pin 1: SM-1 insider_cluster_long blocked without ema_200 key (direct test)
  - Pin 2: xs_momentum_top_decile blocked without ema_200 key (sample factor)
  - Pin 3: xs_quality_top_quintile_long blocked without ema_200 key (sample 2-gate)
  - Pin 4: pead_long blocked without ema_200 key (sample event-driven)
  - Pin 5: SM-7 institutional_cluster_long blocked without ema_200 key (sample 13F sleeve)
  - Pins 6-12: 7 NOT-pattern SHORT-side blocked without below_ema_200 isolation pins
  - Pin 13: bundle assertion — 0 `s.get("price_above_ema_200", True)` remains
  - Pin 14: bundle assertion — 0 `(not above_200)` patterns remain
- [test_unit.py test_batch216_smc_inverse_fvg_handles_both_directions](backtest/tests/test_unit.py) — fixture updated to set `below_ema_200: True` explicitly (post-B663 positive-symmetric requirement)

### Measured fires/yr (universe) — pre-B663

- **SM-1 insider_cluster_long: ~30-60/yr** projected (Cohen-Malloy-Pomorski reports ~0.5-1% of stock-months exhibit a cluster; T1a 500 tickers × 12 months × 0.005-0.01)
- **SM-2 insider_cluster_with_director_long: ~10-30/yr** projected (subset of SM-1 + director-isolation tightening)
- Both BORDERLINE on min_trades=30/yr; cube empirically adjudicates. **PENDING B660 full-universe measurement for authoritative numbers.**

### Measured fires/yr (universe) — post-B663

- **Pending B660** — expected modest drop on tickers with insufficient 200-EMA history (where pre-B663 default-True path was auto-passing the regime gate). On tickers with full history, no behavior change.
- The 70-strategy family-bug sweep also affects measurements for the 22-strategy 13F sleeve, the 4 calendar strategies, ~30 other strategies — B660 captures all post-sweep numbers in a single full-universe run.

### Open items queued

| Ticket | Description |
|---|---|
| `S5-INSIDER-CLUSTER-HOLD-DURATION-VALIDATION` | Cohen-Malloy-Pomorski 12-month-alpha thesis vs default 1× ATR trail exit; cube replay across hold durations |
| `S4-INSIDER-PRODUCER-PARALLEL-AUDIT` | Two parallel insider producers (`compute_insider_cluster_signals` boolean in `insider_buying.py` + `data/smart_money.py:insider_signal` categorical) — which strategies consume which; cross-source consistency |
| `S4-INSIDER-SCHEMA-PIN` | Quiver `live/insiders` schema-version assertion / pin |
| ~~`S4-EVENT-DRIVEN-DEFAULT-TRUE-EMA-SWEEP`~~ | **CLOSED B663** — full screener-wide sweep applied; supersedes the originally-narrower-scope ticket |

### Class 7 NEW question — deferred (was original Q3 from B662 surface)

`strat_insider_cluster_concentrated_sell_short` (only-SHORT on `concentrated_sell` >50% holdings dumped per economic-symmetry test in Step 6) — **NOT wired in B663** because owner's "approve all recs" was interpreted conservatively; Q3 was a separate consideration not in my recommendation block. Still available for owner consideration; data-source-asymmetry check is satisfied (concentrated_sell is the only economically-defensible SHORT mirror of insider buying — generic cluster_sell is noise per `feedback_asymmetric_data_sources_break_mechanical_inverse`).

### No regrets

The B663 family-bug sweep was the right scope decision. Pre-flight grep revealed the original "narrow" SM-1 fix would have left 69 same-pattern silent-gaps + violated `feedback_family_bug_grep_before_one_liners`. The F3 self-correction also caught a CHECKLIST violation before it would have shipped — `feedback_regime_selector_lineage_grep_before_delete.md` memory note codifies the lesson for future walks. Net: SM-1 + SM-2 closed-out with stronger evidence base than a narrow walk would have produced.

---

## SM-1. `strat_insider_cluster_long` (foundational, B663 closed)

> **Status:** ✅ WALKED + SHIPPED B663. See [FINAL STATUS POST-B663 block above](#final-status-post-b663--sm-1--sm-2-closed) for what shipped. The 7-step walk below is preserved for the external reviewer's reference and to maintain consistent walk-format across all 41 strategies in the cluster.

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

**Original recommendation: (b) narrow-scope F1 swap.** Owner chose (δ) full screener sweep after pre-flight grep revealed the F1 finding was a 70-strategy family-bug. See [FINAL STATUS POST-B663 block above](#final-status-post-b663--sm-1--sm-2-closed) for what shipped.

**Outcome:** SM-1 closed B663 via full-screener `price_above_ema_200` default-True → False sweep + family-bug regression-block test pin. F3 finding self-corrected via lineage-grep (B263 Phase 1A-alpha empirical override of CMP 2012 literature). Class 7 NEW `concentrated_sell_short` still deferred.

---

## SM-2. `strat_insider_cluster_with_director_long` (foundational, B663 closed)

> **Status:** ✅ WALKED + SHIPPED B663. Bundled with SM-1 in the family-bug fix since both received identical default-True → False treatment.

### Step 1 — Read the code

[screener.py:2856-2872](backtest/signals/screener.py#L2856-L2872):

```python
def strat_insider_cluster_with_director_long(s):
    """Batch 222: Higher-conviction insider variant -- cluster requires
    at least 1 DIRECTOR (board member) as a buyer..."""
    fires = (
        s.get("insider_cluster_active", False)
        and s.get("insider_director_buyers_30d", 0) >= 1
        and s.get("price_above_ema_200", True)  # B663 swapped to False
    )
```

**3-gate strategy:** cluster_active + ≥1 director among the cluster + 200-EMA regime.

### Step 2 — Classify

- Category: `event_driven`; single LONG
- STRATEGY_REGIME_AFFINITY: `{"bull", "neutral", "bear"}` (B263 explicit; same lineage as SM-1 — Phase 1A-alpha 36 crisis trades at 22% WR)
- Last touched: B663

### Step 3 — Producer source-read + temporality

Same producer as SM-1 (`compute_insider_cluster_signals` in `insider_buying.py`). Same EVENT-class temporality (Form 4 2-day filing lag). Director-count diagnostic `insider_director_buyers_30d` is a derived count, not a separate producer.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Director purchases higher signal value than purely-officer transactions" | ✅ Lakonishok-Lee 2001 RFS confirmed (the cited paper) |
| "Batch 222" lineage | ✅ accurate |

### Step 5 — OPEN_INVESTIGATIONS grep

Same as SM-1 — parallel-producer concern + Quiver schema-pin concern apply identically.

### Step 6 — Missing-inverse + economic-symmetry

Same asymmetric data-source profile as SM-1; no mechanical SHORT mirror is possible. Class 7 NEW `_director_concentrated_sell_short` even harder to defend since director-level concentrated sells are even more often diversification-driven (early-retirement, estate planning).

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1** | Same default-True silent-gap pattern as SM-1 | MEDIUM → SHIPPED B663 (family sweep) |
| F3 | Same B263 `{bull, neutral, bear}` empirical entry as SM-1 — RESOLVED-AS-DECIDED per lineage | — |
| F-fire-count | Subset of SM-1 fires (director-only requirement) → projected ~10-30/yr | INFO |

Closed via B663 family-bug sweep. See FINAL STATUS POST-B663.

---

## SM-3. `strat_activist_13d_long` (foundational, B664 candidate)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B664 candidate). Single-gate event-driven strategy on SC 13D filings; one F2 stale-docstring finding.

### Step 1 — Read the code

[screener.py:3893-3920](backtest/signals/screener.py#L3893-L3920):

```python
def strat_activist_13d_long(s):
    """Batch 522 (P17b SCAFFOLD). Long fires when SC 13D (activist) filing
    landed in the last 30 days. Trigger boolean is sc_13d_filed_within_30d.
    Academic: Brav-Jiang-Partnoy-Thomas 2008 JF +6.8% 30d CAR..."""
    fires = bool(s.get("sc_13d_filed_within_30d", False))
    ...
    return _strat(fires, "long", "sec_edgar_sleeve", ...)
```

**Single-gate strategy.** Only `sc_13d_filed_within_30d`. No regime gate, no confluence, no trend confirmation.

### Step 2 — Classify

- Category: `sec_edgar_sleeve` (P17b); single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default `{bull, neutral}`
- Last touched: B531 (wire-in to ALL_STRATEGIES + screen_instrument; docstring still says "NOT REGISTERED" — STALE)

### Step 3 — Producer source-read + temporality

**Producer:** `compute_sec_edgar_signals` in [sec_edgar_extractor.py:301](backtest/signals/sec_edgar_extractor.py#L301) → `sc_13d_filed_within_days` at line 206.

**Input:** SEC EDGAR-decoded parquet at `data_prefetch/sec_edgar/SC_13D/<TICKER>.parquet`.

**Logic:** `filing_date > (as_of - 30d) AND filing_date <= as_of` → `sc_13d_filed_within_30d: True/False` + filer_identity + percent_owned enrichment.

**Temporality:** **EVENT-class** ✅. 13D filing window = 10 calendar days after 5% beneficial ownership crossed (SEC rule 13d-1). Strong timing-EVENT. Brav-Jiang-Partnoy-Thomas's +6.8% 30d CAR centers around the filing event.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Brav-Jiang-Partnoy-Thomas 2008 JF +6.8% 30d CAR" | ✅ Real paper, real result |
| "Bebchuk-Brav-Jiang 2015 RFS +3-5pp/yr for 5 years post-filing" | ✅ Real paper, real result |
| "NOT REGISTERED in ALL_STRATEGIES" | ⚠ **STALE** — B531 wired in |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations on `activist_13d` / `sc_13d_filed`.

### Step 6 — Missing-inverse + economic-symmetry

Per `feedback_asymmetric_data_sources_break_mechanical_inverse`: 13D is **structurally long-only by SEC rule** (5%+ beneficial ownership; no SHORT analogue). No mechanical mirror possible. ✅

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F2 STALE** | "NOT REGISTERED" lineage 2 batches stale; B531 wired in | LOW |
| F3 | No regime affinity entry; B291 LONG default `{bull, neutral}`. Brav-Jiang-Partnoy-Thomas thesis is all-regimes but no Phase 1A-alpha empirical exists either way. Per B663 lesson: ambiguous → defer to post-cube | INFO |
| F-temporality | EVENT-classified ✅ | — |
| F-data-source-asymmetry | 13D long-only ✅ no SHORT mirror possible | — |
| F-fire-count | ~30-80/yr universe-wide projection; BORDERLINE on min_trades=30 | INFO |
| F-confluence | Single-gate is unusual. 13D + price-below-200-EMA ("activist piles into oversold") could tighten signal. Owner B620 precedent on EVENT-only strategies → surface as separate Class 7 NEW candidate, not auto-apply | INFO |

**B664 candidate option (recommended):** F2 docstring update only — replace "NOT REGISTERED" with current B531 lineage. Zero behavior change.

---

## SM-4. `strat_m_and_a_target_long` (foundational, B664 candidate)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B664 candidate). Single-gate event-driven on 8-K Item 1.01.

### Step 1 — Read the code

[screener.py:3923-3945](backtest/signals/screener.py#L3923-L3945):

```python
def strat_m_and_a_target_long(s):
    """Batch 522 (P17c SCAFFOLD). Long fires when 8-K Item 1.01 (material
    definitive agreement) landed in the last 30 days. Academic: Pawliczek-
    Skinner 2018 RAS +2-3pp 10-day CAR..."""
    fires = bool(s.get("8k_item_1_01_filed_within_30d", False))
```

**Single-gate strategy.** Only `8k_item_1_01_filed_within_30d`. Identical structural pattern to SM-3.

### Step 2 — Classify

- Category: `sec_edgar_sleeve` (P17c); single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B531 (wire-in; docstring still says "NOT REGISTERED" — STALE)

### Step 3 — Producer source-read + temporality

**Producer:** `compute_sec_edgar_signals` → `eight_k_item_filed_within_days(item_code="1.01", lookback_days=30)`.

**Temporality:** **EVENT-class** ✅. 8-K filings have 4-business-day requirement (SEC rule). Item 1.01 = material definitive agreement disclosure = often FIRST public M&A disclosure. Pawliczek-Skinner's +2-3pp 10-day CAR centers around the filing.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Pawliczek-Skinner 2018 RAS +2-3pp 10-day CAR" | ✅ Real paper, real result |
| "Often first public disclosure of M&A" | ✅ Material definitive agreement disclosure |
| "NOT REGISTERED" | ⚠ **STALE** — B531 wired in |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations.

### Step 6 — Missing-inverse + economic-symmetry

8-K Item 1.01 is filed for both acquirer + target. The +2-3pp CAR is on the TARGET side (the company being acquired gaps up on the announcement). Acquirer side often gaps DOWN (deal premium dilutes acquirer). A symmetric SHORT mirror `strat_m_and_a_acquirer_short` would need separation of target vs acquirer signal — currently the producer doesn't distinguish. **Class 7 NEW candidate but requires producer enhancement.** Surface for owner consideration.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F2 STALE** | "NOT REGISTERED" lineage stale; B531 wired in | LOW |
| F3 | Same as SM-3 — B291 default; no lineage; defer | INFO |
| F-temporality | EVENT ✅ | — |
| F-data-source-asymmetry | Producer doesn't distinguish acquirer vs target — Class 7 NEW SHORT possible IF producer extended | INFO |
| F-fire-count | ~50-150/yr universe-wide projection (8-K Item 1.01 fires more often than 13D); PASS on min_trades=30 | INFO |

**B664 candidate option (recommended):** F2 docstring update only.

---

## SM-5. `strat_short_borrow_trap_avoid` (foundational, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Avoid-direction strategy (blocks SHORT entries on hard-to-borrow names).

### Step 1 — Read the code

[screener.py:3948-3971](backtest/signals/screener.py#L3948-L3971):

```python
def strat_short_borrow_trap_avoid(s):
    """Batch 519 (P15 sleeve). Avoid-side gate for short strategies when
    borrow is tight. Fires `avoid` when days_to_cover > 5..."""
    dtc = s.get("days_to_cover", 0.0) or 0.0
    fires = dtc > 5.0
    return _strat(fires, "avoid", "smart_money_sleeve", ...)
```

**Single-gate strategy.** Threshold-based on `days_to_cover` continuous variable.

### Step 2 — Classify

- Category: `smart_money_sleeve`; direction = **avoid** (unique — neither LONG nor SHORT)
- STRATEGY_REGIME_AFFINITY: NO ENTRY (avoid-direction not regime-gated by design)
- Last touched: B519

### Step 3 — Producer source-read + temporality

**Producer:** `compute_short_interest_signals` (Quiver short interest feed). Emits `days_to_cover` derived from `short_interest / avg_daily_volume`.

**Temporality:** **STATE-class** — short interest reports semi-monthly (FINRA Reg SHO; T+1 reporting delay). `days_to_cover` is computed from the most-recent SI snapshot. Effectively constant 14d at a time.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Cohen-Diether-Malloy 2007 borrow-constraint premium" | ✅ Real paper documents short squeeze asymmetry on high-DTC names |
| Threshold 5.0 DTC | Standard heuristic; not paper-cited specifically. Could be calibrated against B660 measurement once landed |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations.

### Step 6 — Missing-inverse + economic-symmetry

Avoid-direction strategies don't have inverse mirrors by design (they BLOCK actions, not propose them). ✅

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | No silent-gap (single-gate continuous threshold; default 0.0 fail-safe) | ✅ |
| F2 | Docstring accurate; cites real paper | ✅ |
| F-temporality | STATE-class (semi-monthly SI updates) — but avoid-direction is intrinsically STATE-friendly (we want a BLANKET BLOCK on hard-to-borrow names, not a bar-of-fire EVENT) | ✅ |
| F-threshold-arbitrary | `dtc > 5.0` is heuristic — could be optimized via B660 + cube empirical | INFO (queued: `S5-SM5-DTC-THRESHOLD-CALIBRATION`) |
| F-fire-count | Avoid strategies don't have fires/yr in the same sense; instead they block SHORT entries on N tickers/day | INFO |

**B664 candidate option (recommended):** No code change. Add queue ticket `S5-SM5-DTC-THRESHOLD-CALIBRATION` for post-cube threshold optimization.

---

## SM-6. `strat_pead_with_insider_confirmation_long` (PEAD-insider cross-cluster, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate event-driven (PEAD + insider). Cross-cluster: also belongs in PEAD cluster.

### Step 1 — Read the code

[screener.py:2916-2933](backtest/signals/screener.py#L2916-L2933):

```python
def strat_pead_with_insider_confirmation_long(s):
    """Batch 222: PEAD positive surprise + concurrent insider buying
    cluster = high-conviction post-earnings drift."""
    fires = (
        s.get("within_pead_window", False)
        and s.get("pead_positive_surprise", False)
        and s.get("insider_cluster_active", False)
    )
```

**3-gate strategy:** within_pead_window + pead_positive_surprise + insider_cluster_active.

### Step 2 — Classify

- Category: `event_driven`; single LONG
- STRATEGY_REGIME_AFFINITY: explicit `{"bull", "neutral", "bear"}` (B263 lineage — drop crisis; same empirical Phase 1A-alpha override class as SM-1/SM-2)
- Last touched: B222

### Step 3 — Producer source-read + temporality

- `within_pead_window` / `pead_positive_surprise`: from PEAD producer (post-earnings-announcement drift window detection)
- `insider_cluster_active`: from SM-1's producer (`compute_insider_cluster_signals`)

**Temporality:** Both producers are EVENT-class. PEAD window centers on earnings announcement event; insider cluster captures 30-day rolling Form-4 events. ✅

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Insider activity is independent confirmation that the earnings move is fundamental rather than noise" | ✅ Reasonable thesis; Cohen-Malloy-Pomorski 2012 + PEAD literature compose |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations.

### Step 6 — Missing-inverse + economic-symmetry

PEAD has symmetric LONG/SHORT (positive/negative surprise) but the insider-confirmation half is asymmetric per data source. A mechanical `strat_pead_with_insider_sell_confirmation_short` would face the same data-source-asymmetry issue as the candidate `strat_insider_cluster_short` raised in SM-1 Step 6.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| F1 | No `price_above_ema_200` gate at all — not affected by B663 sweep | ✅ |
| F2 | Docstring accurate; minimal | ✅ |
| F3 | B263 lineage at line 269 — INTENTIONAL exclude-crisis | RESOLVED-AS-DECIDED |
| F-temporality | EVENT ✅ | — |
| F-data-source-asymmetry | SHORT mirror requires PEAD-symmetric insider half; producer asymmetric → SHORT economically suspect | INFO |
| F-fire-count | PEAD window × insider cluster co-occurrence is rare; projected ~10-25/yr; **FAIL on min_trades=30** likely | MEDIUM |

**B664 candidate option (recommended):** No code change. Surface fire-count concern as queued `S5-SM6-PEAD-INSIDER-FIRE-COUNT-MEASUREMENT` for B660 follow-up.

---

## SM-7. `strat_institutional_cluster_long` (13F sleeve, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Foundational 13F sleeve strategy. F-temporality STATE-as-EVENT overclaim candidate (Pattern B family).

### Step 1 — Read the code

[screener.py:4355-4371](backtest/signals/screener.py#L4355-L4371):

```python
def strat_institutional_cluster_long(s):
    """Wave 3 (Batch 330): institutional cluster-buy long.
    13F shows new_positions >= 3 OR (new_pos >= 1 AND increased >= 2)...
    Cohen-Frazzini-Malloy 2008 RFS: cluster-buys forecast ~1-month alpha."""
    fires = (
        s.get("institutional_strong_buy", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

**2-gate strategy:** institutional_strong_buy + 200-EMA.

### Step 2 — Classify

- Category: `smart_money_13f`; single LONG
- STRATEGY_REGIME_AFFINITY: `{"bear"}` (B418 cube override — bear=+0.16 Sharpe documented at line 367)
- Last touched: B663 (default-True fix applied as part of family sweep)

### Step 3 — Producer source-read + temporality

**Producer:** `compute_persistence_signals` in `institutional_persistence_consumer.py` + 13F producer at `screen_instrument` injecting `institutional_strong_buy`, `institutional_buy`, `institutional_negative`, etc.

**Temporality:** **STATE-class** ⚠ — 13F filings are QUARTERLY with DEC-325 45-day publication lag. `institutional_strong_buy` is effectively constant ~90 days at a time. **NOT a bar-of-fire timing signal.** Per B611 lesson: docstring claim "cluster-buys forecast 1-month alpha" implies EVENT timing alpha that the producer cannot supply on the bar of fire.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Cohen-Frazzini-Malloy 2008 RFS - cluster-buys forecast 1-mo alpha" | ⚠ Real paper but the alpha is long-horizon factor-tilt; bar-of-fire timing claim **STATE-as-EVENT overclaim** per B611 |
| "Gated by 200-EMA regime to avoid catching falling-knife" | ✅ accurate |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations on the strategy. B611 set the precedent for the docstring honesty reframe class.

### Step 6 — Missing-inverse + economic-symmetry

13F is SEC long-only. `strat_institutional_cluster_short` would have no data source. SM-9 + SM-23 use `institutional_negative` (trimming) as SHORT proxy but that's economically suspect per B611 precedent — see SM-9 walk.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event** | Docstring "cluster-buys forecast 1-mo alpha" implies bar-of-fire timing; producer is quarterly STATE per B611 lesson. **Pattern B family-bug candidate** (~22 institutional sleeve strategies share this overclaim) | MEDIUM |
| F1 | `price_above_ema_200` default-True fixed B663 | ✅ SHIPPED B663 |
| F3 | B418 cube override `{bear}` — documented INTENTIONAL | RESOLVED-AS-DECIDED |
| F-fire-count | 13F cluster-buy events are uncommon; projected ~40-100/yr per direction; PASS on min_trades=30 | INFO |

**B664 candidate option (recommended):** Docstring honesty reframe — drop "cluster-buys forecast 1-month alpha" timing claim; replace with B611-style "13F-eligibility filter (factor-tilt, not bar-of-fire timing); alpha attribution belongs to 200-EMA regime gate."

---

## SM-8. `strat_institutional_buy_momentum_long` (13F sleeve, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate with `price_above_ema_50` default-True (Pattern A family-bug candidate).

### Step 1 — Read the code

[screener.py:4374-4389](backtest/signals/screener.py#L4374-L4389):

```python
def strat_institutional_buy_momentum_long(s):
    """Wave 3 (Batch 330): institutional buy + price momentum.
    Looser 13F signal combined with MACD + 50-EMA. Yan-Zhang 2009 RFS..."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("macd_12_26_9_bullish", False)
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A family-bug
    )
```

**3-gate strategy:** institutional_buy + MACD bullish + 50-EMA (default-True silent-gap).

### Step 2 — Classify

- Category: `smart_money_13f`; single LONG
- STRATEGY_REGIME_AFFINITY: `{"bull"}` (B418 cube override — bull=+0.12 Sharpe at line 366)
- Last touched: B330

### Step 3 — Producer source-read + temporality

Same producer as SM-7 (13F). `institutional_buy` STATE quarterly. MACD bullish is STATE-ish (momentum hist > 0). `price_above_ema_50` is STATE.

**Temporality:** All 3 gates are STATE. Per CHECKLIST (s): if ≤1 EVENT gate per direction AND docstring overclaims timing on STATE → F-timing-fragility HIGH. Here: 0 EVENT gates + docstring implies smart-money flow timing → Pattern B overclaim candidate.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Yan-Zhang 2009 RFS: short-horizon institutional persistence + price trend agreement" | ⚠ Real paper; but "short-horizon" in Yan-Zhang means ~1 quarter, NOT bar-of-fire. Same STATE-as-EVENT class as SM-7 |
| "Filters out one-off institutional buys at tops" | ✅ MACD bullish + 50-EMA do filter trend disagreement |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only; mechanical mirror false. Per B611 precedent — see Pattern C in cross-strategy section.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1 Pattern A** | `s.get("price_above_ema_50", True)` default-True silent-gap | MEDIUM (B664 candidate) |
| **F-state-as-event Pattern B** | All 3 gates STATE; docstring implies timing alpha | MEDIUM (B664 candidate) |
| F3 | B418 `{bull}` cube override | RESOLVED-AS-DECIDED |
| F-fire-count | Looser 13F gate × MACD bullish → projected ~100-300/yr; PASS | INFO |

**B664 candidate option (recommended):** F1 + Pattern B docstring reframe bundled.

---

## SM-9. `strat_institutional_distribution_short` (13F sleeve, walked — DATA-SOURCE-ASYMMETRY)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern C candidate — fires on `institutional_negative` which per B611 lesson is NOT bear conviction (13F long-only; trimming = rebalancing/tax/redemption).

### Step 1 — Read the code

[screener.py:4392-4406](backtest/signals/screener.py#L4392-L4406):

```python
def strat_institutional_distribution_short(s):
    """Wave 3 (Batch 330): institutional distribution short.
    13F shows institutional_signal=='negative' (decreased > increased)
    AND price below 50-EMA..."""
    fires = (
        s.get("institutional_negative", False)
        and s.get("below_ema_50", False)  # B633 sweep
    )
```

**2-gate SHORT strategy:** institutional_negative + below_50_EMA.

### Step 2 — Classify

- Category: `smart_money_13f`; single SHORT
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 SHORT default `{bear, crisis, neutral}`
- Last touched: B633 (positive symmetric below_ema_50 swap)

### Step 3 — Producer source-read + temporality

Same 13F producer. `institutional_negative` = (decreased > increased) which is quarterly STATE.

**Temporality:** STATE per B611 — institutional flow on 90-day cadence.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Sias 2004 JFE: institutional herding extends to selling" | ⚠ Real paper but the herding-on-selling result is documented for ALL types of institutional sales, not just 13F trimming. **B611 lesson:** 13F TRIMMING is NOT smart-money short conviction — it's rebalancing/tax-loss/redemption noise dominated. Pattern C economic-symmetry failure. |
| "Sias 2004 + Lo-Wang 2000 = continuation short setup" | ⚠ Same Pattern C overclaim |

### Step 5 — OPEN_INVESTIGATIONS grep

B611 deleted `strat_institutional_breakdown_confirmation_short` for the same Pattern C reason — SM-9 should be reviewed against that precedent.

### Step 6 — Missing-inverse + economic-symmetry

Mirror of SM-7/SM-8 but SHORT side. The mirror is mechanically convenient but **economically false** per `feedback_asymmetric_data_sources_break_mechanical_inverse`. 13F-trim != bear conviction.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F-pattern-C-data-source-asymmetry** | `institutional_negative` does NOT supply bear conviction (B611 precedent). Strategy is mechanically symmetric to LONG sleeves but economically suspect | HIGH |
| F-state-as-event | All gates STATE; same Pattern B overclaim | MEDIUM |
| F-fire-count | 13F trimming events on stocks already below 50-EMA → projected ~30-80/yr | INFO |

**B664 candidate option:** (b) docstring caveat acknowledging Pattern C data-source asymmetry; (c) DELETE per B611 precedent (would override `project_no_apriori_strategy_pruning` — needs explicit owner approval). RECOMMEND (b) — surface the issue for transparent reading without overriding the no-pruning rule.

---

## SM-10. `strat_institutional_oversold_long` (13F sleeve, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate LONG with B611 STATE-as-EVENT class.

### Step 1 — Read the code

[screener.py:4414-4429](backtest/signals/screener.py#L4414-L4429):

```python
def strat_institutional_oversold_long(s):
    """Wave 3 (Batch 331): institutional buy + RSI oversold mean-rev.
    Cohen-Malloy-Pomorski 2012 JF combined with Bondt-Thaler 1985 JF
    overreaction: institutional accumulation during oversold pullback
    is the classic Schwed 'cash on the sidelines' setup."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("rsi_14", 50) < 35
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

**3-gate LONG:** institutional_buy + RSI<35 + 200-EMA.

### Step 2 — Classify

- `smart_money_13f`; single LONG
- No regime entry → B291 default `{bull, neutral}`
- Last touched: B663

### Step 3 — Producer source-read + temporality

13F STATE (institutional_buy) + RSI STATE (oversold) + STATE trend gate. **0 EVENT gates → Pattern B candidate.**

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Cohen-Malloy-Pomorski 2012 + Bondt-Thaler 1985 overreaction" | ⚠ Real papers but CMP 2012 is INSIDER buying (not 13F). The 13F claim here borrows CMP authority but the data source is wrong. Pattern B + Pattern citation-error |
| "Schwed 'cash on the sidelines' setup" | ⚠ Informal lit; not academic. RSI<35 + 13F-buy is a co-occurrence not a tested setup |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F-citation-error** | Docstring cites Cohen-Malloy-Pomorski 2012 (insider paper) for a 13F strategy. The CMP 2012 result does not apply to 13F | MEDIUM |
| **F-state-as-event Pattern B** | 0 EVENT gates; docstring implies timing setup | MEDIUM |
| F-fire-count | ~40-80/yr projected | INFO |

**B664 candidate option (recommended):** Docstring reframe — drop "CMP 2012" citation (wrong paper for 13F); replace "Schwed cash on sidelines" with "13F eligibility filter + RSI oversold mean-reversion entry; alpha attribution belongs to RSI mean-rev, not 13F timing."

---

## SM-11. `strat_institutional_breakout_confirmation_long` (13F sleeve, B611-walked)

> **Status:** ✅ ALREADY WALKED B611 (2nd-wave critique response). Docstring already honestly reframed per B611. No further B664 action needed.

### Step 1 — Read the code

[screener.py:4432-4513](backtest/signals/screener.py#L4432-L4513): 5-gate LONG (institutional_buy + resistance_break_retest + 200-EMA + close_above_open + vol_below_avg). Post-B610 + B611 walks.

### Step 2-7 — already documented

See B611 docstring honesty reframe in the strategy itself. The docstring explicitly states:
- 13F is QUARTERLY STATE eligibility filter, NOT timing
- Alpha attribution credits Bulkowski retest + trend filter, NOT 13F sponsorship
- Citation set: Cohen-Frazzini-Malloy 2008 (factor-tilt) + Bulkowski 2005 (timing component)

### FINAL STATUS POST-B611 — ✅ CLOSED

The B611 reframe is the canonical example of Pattern B fix. Other 22 sleeve strategies need the same treatment. **B664 candidate Pattern B docstring sweep uses SM-11 as the template.**

---

## SM-12. `strat_institutional_insider_combo_long` (13F + insider, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate dual smart-money. Pattern B candidate.

### Step 1 — Read the code

[screener.py:4533-4549](backtest/signals/screener.py#L4533-L4549):

```python
def strat_institutional_insider_combo_long(s):
    """Wave 3 (Batch 331): dual smart-money confirmation (13F + insiders).
    Cohen-Malloy-Pomorski 2012 JF (insiders) + Cohen-Frazzini-Malloy 2008
    RFS (institutions) - when BOTH sources accumulate simultaneously, the
    edge is multiplicative not additive."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("insider_cluster_active", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

**3-gate LONG:** 13F state + insider EVENT + 200-EMA.

### Step 2 — Classify

- `smart_money_combo`; single LONG
- No regime entry → B291 default
- Last touched: B663

### Step 3 — Producer source-read + temporality

- `institutional_buy`: 13F STATE
- `insider_cluster_active`: SM-1 producer EVENT (Form 4 2-day lag)
- `price_above_ema_200`: STATE

**Temporality:** 1 EVENT gate + 2 STATE gates → docstring claim "multiplicative edge" is over-strong. The EVENT gate (insider) supplies bar-of-fire timing; the 13F gate is eligibility filter (factor-tilt). Edge is composition not multiplication.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Cohen-Malloy-Pomorski 2012 + Cohen-Frazzini-Malloy 2008" | ✅ Both real; correctly distinguish insider vs institutional |
| "Multiplicative not additive edge" | ⚠ Implies the two independent edges compound geometrically; this is a strong claim without empirical support. Pattern B family — re-frame as "EVENT timing + STATE eligibility composition" |
| "Independent information channels" | ✅ Correct technical claim (insider Form 4 ≠ 13F filings) |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations.

### Step 6 — Missing-inverse + economic-symmetry

Same as SM-1 + SM-7 — both component data sources are asymmetric on SHORT side.

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | "Multiplicative edge" claim over-strong; one of two sources is STATE | MEDIUM |
| F1 | Post-B663 ✅ | — |
| F-fire-count | Co-occurrence of 13F + insider cluster → rare → projected ~10-30/yr; **FAIL on min_trades=30** likely | MEDIUM |

**B664 candidate option (recommended):** Pattern B docstring reframe — "EVENT (insider) + STATE (13F) composition; alpha attribution: insider EVENT supplies bar-of-fire timing; 13F supplies eligibility filter (factor-tilt). Edge attributable to composition not multiplication."

---

## SM-13. `strat_institutional_persistence_breakout_long` (persistence variant, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate Pattern B candidate.

### Step 1 — Read the code

[screener.py:4756-4769](backtest/signals/screener.py#L4756-L4769):

```python
def strat_institutional_persistence_breakout_long(s):
    """Wave 3 (Batch 337): institutional persistence + post-break retest.
    5+ funds growing position + technical breakout retest = institutional-
    sponsored breakout (Sias 2004 herding + Bulkowski retest)."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("resistance_break_retest", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

### Step 2-6 (compact)

- Category: `institutional_persistence`; LONG single
- No regime entry → B291 default
- Producer: same 13F STATE + Bulkowski retest EVENT
- Temporality: 1 EVENT (retest) + 2 STATE → similar to SM-11 + SM-12
- Last touched: B663

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | "Institutional-sponsored breakout" implies sponsor TIMING; same B611 lesson — 13F-state-as-event overclaim | MEDIUM |
| F-fire-count | `institutional_increased >= 5` × retest is rare; projected ~20-50/yr; borderline | INFO |

**B664 candidate option (recommended):** Pattern B docstring reframe symmetric with SM-11 — "institutional eligibility filter (factor-tilt) + Bulkowski retest (timing)".

---

## SM-14. `strat_institutional_persistence_volume_long` (persistence variant, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate. **Pattern A `price_above_ema_50` default-True candidate** + Pattern B candidate.

### Step 1 — Read the code

[screener.py:4772-4785](backtest/signals/screener.py#L4772-L4785):

```python
def strat_institutional_persistence_volume_long(s):
    """Wave 3 (Batch 337): institutional persistence + volume spike.
    5+ funds growing + retail tape participating = broad-market price
    discovery on the institutional position."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A
    )
```

### Step 2-6 (compact)

- `institutional_persistence`; LONG single; B291 default
- Last touched: B337
- Temporality: 1 EVENT (vol spike) + 2 STATE → Pattern B candidate

### Step 7 — Findings + options

| # | Finding | Severity |
|---|---|---|
| **F1 Pattern A** | `price_above_ema_50` default-True silent-gap | MEDIUM (B664 candidate) |
| **F-state-as-event Pattern B** | "Retail tape participating" + "broad-market price discovery" implies STATE 13F provides timing-EVENT-like sponsorship | MEDIUM |
| F-fire-count | Co-occurrence of 13F persistence + vol_spike on same bar is rare; projected ~30-60/yr | INFO |

**B664 candidate option (recommended):** F1 + Pattern B docstring reframe bundled.

---

## SM-15. `strat_institutional_persistence_oversold_long` (persistence variant, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern B candidate.

### Step 1 — Read the code

[screener.py:4788-4803](backtest/signals/screener.py#L4788-L4803):

```python
def strat_institutional_persistence_oversold_long(s):
    """Wave 3 (Batch 337): institutional persistence + oversold mean-rev."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("rsi_14", 50) < 40
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

### Step 2-6 (compact)

- Same family as SM-10 + SM-13
- 3 STATE gates (13F + RSI + 200-EMA) → 0 EVENT; Pattern B candidate

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | Same as SM-10; alpha credit should go to RSI mean-rev, not 13F | MEDIUM |
| F-fire-count | Rare co-occurrence; projected ~20-40/yr; borderline | INFO |

**B664 candidate option:** Pattern B docstring reframe.

---

## SM-16. `strat_institutional_recent_init_momentum_long` (persistence variant, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate Pattern B candidate.

### Step 1 — Read the code

[screener.py:4813-4828](backtest/signals/screener.py#L4813-L4828):

```python
def strat_institutional_recent_init_momentum_long(s):
    """Wave 3 (Batch 338): early institutional initiation + price momentum.
    new_positions >= 2 + MACD bullish + EMA200 regime. Targets institutional
    initiations that the market has NOT yet priced in."""
    fires = (
        s.get("institutional_new_positions", 0) >= 2
        and s.get("macd_12_26_9_bullish", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

### Step 2-6 (compact)

- Smaller-cluster (≥2) variant of SM-7
- Same Pattern B framing class

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | "Market has NOT yet priced in" implies the 13F filing is the timing signal; per B611, 13F has 45-day filing lag — the market has had 45 days to price it in by the time the strategy sees it | MEDIUM |
| F-fire-count | Looser cluster threshold than SM-7 → ~60-150/yr | INFO |

**B664 candidate:** Pattern B docstring reframe.

---

## SM-17. `strat_institutional_recent_init_volume_long` (persistence variant, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **Pattern A** + Pattern B.

### Step 1 — Read the code

[screener.py:4831-4846](backtest/signals/screener.py#L4831-L4846):

```python
def strat_institutional_recent_init_volume_long(s):
    fires = (
        s.get("institutional_new_positions", 0) >= 2
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A
    )
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F1 Pattern A** | `price_above_ema_50` default-True silent-gap | MEDIUM |
| **F-state-as-event Pattern B** | Same as SM-16 + SM-14 | MEDIUM |
| F-fire-count | Volume + 13F co-occurrence → ~30-60/yr | INFO |

**B664 candidate:** F1 + Pattern B reframe bundled.

---

## SM-18. `strat_institutional_multi_quarter_persistence_long` (333b precompute consumer, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate. **Genuinely persistent STATE** (4-quarter precompute) — Pattern B context different.

### Step 1 — Read the code

[screener.py:4849-4870](backtest/signals/screener.py#L4849-L4870):

```python
def strat_institutional_multi_quarter_persistence_long(s):
    """Batch 344 (333b consumer) 2026-05-25: TRUE multi-quarter persistence
    strategy reading the offline precompute via institutional_persistence_consumer.
    Distinct from Batch 333 single-quarter proxies: requires institutional
    holders that have HELD POSITION across >=4 consecutive quarters."""
    fires = (
        s.get("institutional_persistence_strong", False)
        and s.get("price_above_ema_200", False)
    )
```

### Step 2-6 (compact)

- Reads `compute_persistence_signals` 333b precompute (multi-quarter)
- 4-quarter persistence is a more genuine STATE — funds holding through 4 reporting cycles is actual persistence, not bar-of-fire timing
- Yan-Zhang 2009 RFS cited for "multi-quarter persistence" thesis

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | Genuinely STATE (4q precompute). Docstring DOES NOT overclaim timing — credits Yan-Zhang factor-tilt. ✅ **NOT a Pattern B candidate** | ✅ |
| F-fire-count | 4-quarter persistence is rare; projected ~20-40/yr | INFO |

**B664 candidate option (recommended):** No change. Docstring is honest about STATE attribution.

---

## SM-19. `strat_institutional_committed_growth_long` (333b consumer, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate; same Yan-Zhang-class STATE honesty as SM-18.

### Step 1 — Read the code

[screener.py:4873-4890](backtest/signals/screener.py#L4873-L4890):

```python
def strat_institutional_committed_growth_long(s):
    """Batch 344: institutional funds GROWING their position over 4+
    quarters (>10% over 4 quarters from precompute), not just same-
    quarter increased count."""
    fires = (
        s.get("institutional_persistence_growing", False)
        and s.get("price_above_ema_200", False)
    )
```

### Step 2-6 (compact)

Same family as SM-18 — 4-quarter precompute consumer; genuinely STATE.

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | Frazzini-Lamont 2008 + 4q precompute = genuine STATE; docstring honest. ✅ NOT Pattern B candidate | ✅ |
| F-fire-count | Projected ~20-50/yr | INFO |

**B664 candidate option:** No change.

---

## SM-20. `strat_institutional_increased_with_directors_long` (333 + insider combo, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate Pattern B candidate (mixed STATE 13F + EVENT insider).

### Step 1 — Read the code

[screener.py:4893-4913](backtest/signals/screener.py#L4893-L4913):

```python
def strat_institutional_increased_with_directors_long(s):
    """Wave 3 (Batch 338): persistence + director-level insider buying.
    Triple validation: existing funds growing, new funds entering, AND
    board-level insider conviction."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("insider_director_buyers_30d", 0) >= 1
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

### Step 2-6 (compact)

- 1 EVENT (director buying) + 2 STATE (13F + 200-EMA)
- "Triple smart-money validation" overstates the alpha source

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | "Triple validation" implies 3 independent edges; in reality 2 of 3 are STATE | MEDIUM |
| F-fire-count | Multi-event co-occurrence → ~10-25/yr; borderline / FAIL on min_trades=30 | MEDIUM |

**B664 candidate option:** Pattern B docstring reframe — "1 EVENT (director EVENT) + 2 STATE; alpha attribution: director EVENT supplies timing".

---

## SM-21. `strat_institutional_persistent_holders_long` (333 single-quarter proxy, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 2-gate; Pattern B candidate.

### Step 1 — Read the code

[screener.py:4927-4941](backtest/signals/screener.py#L4927-L4941):

```python
def strat_institutional_persistent_holders_long(s):
    """Wave 3 (Batch 333): high count of institutional position increases
    (current quarter) + bullish regime. Yan-Zhang 2009 RFS."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | Single-quarter proxy is STATE-as-EVENT class (NOT the same as SM-18's 4q precompute). Docstring still cites Yan-Zhang's multi-quarter result | MEDIUM |
| F-fire-count | Projected ~50-100/yr | INFO |

**B664 candidate:** Pattern B reframe.

---

## SM-22. `strat_institutional_strong_conviction_long` (333 variant, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate Pattern B candidate.

### Step 1 — Read the code

[screener.py:4944-4961](backtest/signals/screener.py#L4944-L4961):

```python
def strat_institutional_strong_conviction_long(s):
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("institutional_new_positions", 0) >= 2
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | "Fresh capital agrees with existing-holder conviction" implies bar-of-fire timing on STATE quarterly signal. Frazzini-Lamont 2008 is factor-tilt, not bar-of-fire | MEDIUM |
| F-fire-count | Dual-13F threshold rare; ~20-40/yr; borderline | INFO |

**B664 candidate:** Pattern B reframe.

---

## SM-23. `strat_institutional_capitulation_short` (333 variant, walked — DATA-SOURCE-ASYMMETRY)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **Pattern C candidate** — same B611 data-source-asymmetry issue as SM-9.

### Step 1 — Read the code

[screener.py:4964-4979](backtest/signals/screener.py#L4964-L4979):

```python
def strat_institutional_capitulation_short(s):
    """Wave 3 (Batch 333): institutional distribution + volume spike
    (capitulation signature). Sias 2004 + Lo-Wang 2000."""
    fires = (
        s.get("institutional_negative", False)
        and s.get("vol_spike_2x", False)
        and s.get("below_ema_50", False)  # B633 sweep
    )
```

### Step 2-6 (compact)

- 3-gate SHORT. Same `institutional_negative` core as SM-9
- B611 lesson applies: 13F trimming != bear conviction
- vol_spike + below_50_EMA may compose with the trimming signal differently than SM-9 — vol spike on the way down is canonical capitulation. **But the 13F gate adds noise per Pattern C.**

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-pattern-C-data-source-asymmetry** | `institutional_negative` quarterly STATE doesn't supply bear conviction (B611 precedent); the vol_spike + below_50_EMA pair DOES supply real capitulation timing. The 13F gate is the weak link | HIGH |
| F-fire-count | Co-occurrence of all 3 → projected ~10-30/yr; FAIL likely | MEDIUM |

**B664 candidate option (recommended):** (b) docstring caveat per Pattern C — acknowledge that the `institutional_negative` gate adds noise from rebalancing/redemptions; if cube shows alpha attribution is dominated by vol_spike + below_50_EMA, consider deprecating the 13F gate. Defer deletion question to Stage D empirical.

---

## SM-24. `strat_institutional_high_conviction_long` (336 pure cluster, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **Pattern A** + Pattern B.

### Step 1 — Read the code

[screener.py:4988-5003](backtest/signals/screener.py#L4988-L5003):

```python
def strat_institutional_high_conviction_long(s):
    """Wave 3 (Batch 336): pure new-positions signal with looser regime.
    institutional_new_positions >= 3 alone is the canonical Cohen-Frazzini-
    Malloy 2008 RFS cluster signal."""
    fires = (
        s.get("institutional_new_positions", 0) >= 3
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A
    )
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F1 Pattern A** | `price_above_ema_50` default-True silent-gap | MEDIUM |
| **F-state-as-event Pattern B** | "Canonical CFM 2008 cluster signal" implies bar-of-fire timing; CFM 2008 documents long-horizon factor-tilt | MEDIUM |
| F-fire-count | new_positions >= 3 threshold rare; ~40-80/yr | INFO |

**B664 candidate:** F1 + Pattern B reframe.

---

## SM-25. `strat_institutional_with_directors_long` (336 + director combo, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate mixed STATE/EVENT.

### Step 1 — Read the code

[screener.py:5006-5023](backtest/signals/screener.py#L5006-L5023):

```python
def strat_institutional_with_directors_long(s):
    """Wave 3 (Batch 336): institutional + director-level insider buying.
    Akbas-Jiang-Koch 2024 RFS - director-level signal premium."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("insider_director_buyers_30d", 0) >= 1
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | "Dual board-level + fund-manager confirmation" overstates — 13F is STATE, only director is EVENT | MEDIUM |
| F-fire-count | ~10-25/yr; FAIL likely | MEDIUM |

**B664 candidate:** Pattern B reframe.

---

## SM-26. `strat_institutional_with_officers_long` (336 + officer combo, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate mixed STATE/EVENT.

### Step 1 — Read the code

[screener.py:5026-5042](backtest/signals/screener.py#L5026-L5042):

```python
def strat_institutional_with_officers_long(s):
    """Wave 3 (Batch 336): institutional + officer-level insider buying.
    Officers are CEO/CFO/COO buying their own company's stock - direct
    competence and conviction signal."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("insider_officer_buyers_30d", 0) >= 1
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

### Step 7

Same family as SM-25; officer EVENT instead of director EVENT.

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | Same as SM-25 | MEDIUM |
| F-fire-count | ~15-35/yr; borderline | INFO |

**B664 candidate:** Pattern B reframe.

---

## SM-27. `strat_institutional_persistence_momentum_long` (336 variant, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **Pattern A** + Pattern B.

### Step 1 — Read the code

[screener.py:5045-5059](backtest/signals/screener.py#L5045-L5059):

```python
def strat_institutional_persistence_momentum_long(s):
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("macd_12_26_9_bullish", False)
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A
    )
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F1 Pattern A** | `price_above_ema_50` default-True | MEDIUM |
| **F-state-as-event Pattern B** | 0 EVENT gates; docstring "momentum confirms institutional conviction" implies STATE 13F provides bar-of-fire signal | MEDIUM |
| F-fire-count | Projected ~40-90/yr | INFO |

**B664 candidate:** F1 + Pattern B reframe.

---

## SM-28. `strat_institutional_volume_confirmation_long` (331 variant, walked — partial-honest)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. **Pattern A** + partial Pattern B (docstring already acknowledges 45-day lag).

### Step 1 — Read the code

[screener.py:5062-5078](backtest/signals/screener.py#L5062-L5078):

```python
def strat_institutional_volume_confirmation_long(s):
    """Wave 3 (Batch 331): institutional buy + retail volume confirmation.
    Per Sias 2004 JFE institutional herding + Lo-Wang 2000 RFS volume-as-
    information... Reduces false-positive risk on stale 13F filings
    (45-day reporting lag)."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A
    )
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F1 Pattern A** | `price_above_ema_50` default-True | MEDIUM |
| **F-state-as-event Pattern B partial** | Docstring DOES acknowledge "stale 13F filings (45-day reporting lag)" — partial credit. But still implies the volume gate "confirms institutional sponsorship at bar-of-fire" | LOW |
| F-fire-count | Volume × 13F co-occurrence → ~50-100/yr; PASS | INFO |

**B664 candidate option:** F1 only; minor docstring polish on Pattern B (already partially honest).

---

## SM-29. `strat_classification_change_with_institutional_long` (sub-cluster D)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate; Pattern B candidate.

### Step 1 — Read the code

[screener.py:4703-4716](backtest/signals/screener.py#L4703-L4716):

```python
def strat_classification_change_with_institutional_long(s):
    """Wave 3 (Batch 337): smart-money validates re-rating.
    Reclassification co-incident with institutional accumulation =
    highest-conviction re-rating signal."""
    fires = (
        s.get("classification_changed_recent", False)
        and s.get("institutional_buy", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

### Step 2-6 (compact)

- `classification_change`; LONG; B291 default
- `classification_changed_recent` is EVENT (sector reclassification within 90 days)
- `institutional_buy` is STATE
- Mixed EVENT/STATE; "highest-conviction" overclaims

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event Pattern B** | "Highest-conviction re-rating signal" claim relies on STATE 13F + EVENT reclassification; honest framing should credit reclassification EVENT for timing, 13F for eligibility-filter | MEDIUM |
| F-fire-count | Rare co-occurrence; ~10-25/yr; borderline | MEDIUM |

**B664 candidate:** Pattern B reframe.

---

## SM-30. `strat_classification_change_with_insider_long` (sub-cluster D)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate, 2 EVENT gates → NOT Pattern B.

### Step 1 — Read the code

[screener.py:4721-4735](backtest/signals/screener.py#L4721-L4735):

```python
def strat_classification_change_with_insider_long(s):
    """Wave 3 (Batch 337): insider validates re-rating. Insider cluster
    co-incident with reclassification."""
    fires = (
        s.get("classification_changed_recent", False)
        and s.get("insider_cluster_active", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
```

### Step 2-6 (compact)

- 2 EVENT gates (reclassification + insider cluster) + 1 STATE (200-EMA) → genuinely composite-of-events
- "Board-level + analyst re-rating agreement" framing is honest because BOTH events are bar-of-fire

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-state-as-event** | 2 EVENT gates; docstring honestly credits both events. ✅ NOT Pattern B candidate | ✅ |
| F-fire-count | Rare co-occurrence; ~5-15/yr; **FAIL on min_trades=30** | HIGH |

**B664 candidate option:** No code/doc change. Queue fire-count concern as `S5-SM30-FIRE-COUNT-MEASUREMENT` for B660 follow-up.

---

## Sub-cluster E preamble: confluence wraps + `_has_smart_money_buy` UNION

> The 11 confluence wraps (SM-31 through SM-41) all use the same helper `_has_smart_money_buy` at [screener.py:5567](backtest/signals/screener.py#L5567). Per B613 the helper is documented as a UNION ELIGIBILITY FILTER (EVENT-or-STATE), NOT a confluence signal.
>
> **Helper logic:**
> ```python
> def _has_smart_money_buy(s) -> bool:
>     return bool(
>         # EVENT components (bar-of-fire timing)
>         s.get("insider_cluster_active", False)
>         or s.get("cfo_buy", False)
>         or s.get("large_dollar_buy", False)
>         # STATE components (slow 13F eligibility filter)
>         or s.get("institutional_strong_buy", False)
>         or s.get("institutional_buy", False)
>     )
> ```
>
> **Pattern E candidate (cross-cluster).** Each wrap's bullet text "Smart-money buy confirmation" implies confluence at bar of fire. Per B613 helper docstring: when only the STATE half is True, there is no bar-of-fire conviction; the wrap reduces to its base-strategy gates + 13F eligibility filter. SM-34 and SM-35 already received B613 honesty reframe; SM-31, SM-32, SM-33, SM-36, SM-37, SM-38, SM-39, SM-40, SM-41 all carry the same "Smart-money buy confirmation" bullet text without B613 honesty reframe.

---

## SM-31. `strat_bollinger_tight_with_smart_money_long` (confluence wrap)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern E candidate (bullet text not yet B613-reframed).

### Step 1 — Read the code

[screener.py:5613-5627](backtest/signals/screener.py#L5613-L5627):

```python
def strat_bollinger_tight_with_smart_money_long(s):
    base_fires = (
        s.get("bb_squeeze", False)
        and s.get("close_above_open", True)
        and s.get("price_above_ema_200", False)  # post-B663
    )
    fires = base_fires and _has_smart_money_buy(s)
```

### Step 2-6 (compact)

- Base strategy: bollinger_tight squeeze + bullish bar + 200-EMA
- Smart-money wrap: + `_has_smart_money_buy` UNION
- Bullet text: "Smart-money buy confirmation" — Pattern E candidate

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F1** | `close_above_open` default-True silent-gap (similar family as B663 but different signal). LOW priority because `close_above_open` is universally emitted by candle producer | LOW |
| **F-pattern-E** | Bullet text overclaims confluence; B613 honesty reframe needed | LOW |
| F-fire-count | Squeeze × smart-money rare; ~10-25/yr; borderline | INFO |

**B664 candidate:** Pattern E bullet text reframe.

---

## SM-32. `strat_mfi_oversold_with_smart_money_long` (confluence wrap)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern E candidate.

### Step 1 — Read the code

[screener.py:5630-5641](backtest/signals/screener.py#L5630-L5641):

```python
def strat_mfi_oversold_with_smart_money_long(s):
    base_fires = (
        s.get("mfi_14_oversold", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
    fires = base_fires and _has_smart_money_buy(s)
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-pattern-E** | Bullet text "Smart-money buy confirmation" implies confluence; UNION helper is not confluence | LOW |
| F-fire-count | ~15-40/yr; borderline | INFO |

**B664 candidate:** Pattern E reframe.

---

## SM-33. `strat_rsi_oversold_with_smart_money_long` (confluence wrap)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern E candidate.

### Step 1 — Read the code

[screener.py:5644-5655](backtest/signals/screener.py#L5644-L5655):

```python
def strat_rsi_oversold_with_smart_money_long(s):
    base_fires = (
        s.get("rsi_14_oversold", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
    fires = base_fires and _has_smart_money_buy(s)
```

### Step 7

Same family as SM-32; RSI instead of MFI.

| # | Finding | Severity |
|---|---|---|
| **F-pattern-E** | Same bullet text overclaim | LOW |
| F-fire-count | ~20-50/yr | INFO |

**B664 candidate:** Pattern E reframe.

---

## SM-34. `strat_52w_high_breakout_with_smart_money_long` (B613-walked)

> **Status:** ✅ ALREADY WALKED B613. Docstring already honestly reframed per B613 F1+F2a+a (EVENT vs STATE bullet text + close_in_top_40pct gate added).

### Step 1 — Read the code

[screener.py:5658-5697](backtest/signals/screener.py#L5658-L5697): 5-gate LONG with B613 honest framing.

### FINAL STATUS POST-B613 — ✅ CLOSED

The B613 reframe is the canonical Pattern E fix template:
- Bullet text "Smart-money EVENT(timing) or STATE(eligibility) buy per B613 F2a"
- George-Hwang 2004 JF 52-week-high anomaly cited correctly for price-momentum
- Lineage: B588 → B589 → B613

**No further B664 action.**

---

## SM-35. `strat_52w_high_breakout_with_smart_money_vol_below_long` (B613 B-twin)

> **Status:** ✅ ALREADY WALKED B613. B-twin A/B-test variant of SM-34 (vol_below_avg instead of vol_spike_12x; Bulkowski 2005 retest absorption thesis).

### FINAL STATUS POST-B613 — ✅ CLOSED

Same B613 framing as SM-34. Cube replay will surface empirical verdict per (strategy × exit) cell.

---

## SM-36. `strat_squeeze_breakout_with_smart_money_long` (confluence wrap)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern E candidate.

### Step 1 — Read the code

[screener.py:5741-5752](backtest/signals/screener.py#L5741-L5752):

```python
def strat_squeeze_breakout_with_smart_money_long(s):
    base_fires = (
        s.get("squeeze_on_release", False)
        and s.get("close_above_open", True)
    )
    fires = base_fires and _has_smart_money_buy(s)
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-pattern-E** | Same bullet text overclaim | LOW |
| F-fire-count | TTM squeeze × smart-money rare; ~10-30/yr; borderline | INFO |

**B664 candidate:** Pattern E reframe.

---

## SM-37. `strat_xs_momentum_with_smart_money_long` (confluence wrap)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern E candidate.

### Step 1 — Read the code

[screener.py:5755-5767](backtest/signals/screener.py#L5755-L5767):

```python
def strat_xs_momentum_with_smart_money_long(s):
    """Jegadeesh-Titman 12-1 momentum with smart-money corroboration."""
    base_fires = (
        s.get("xs_momentum_top_decile", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
    fires = base_fires and _has_smart_money_buy(s)
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-pattern-E** | Same | LOW |
| F-fire-count | Top-decile momentum cross smart-money → ~30-70/yr | INFO |

**B664 candidate:** Pattern E reframe.

---

## SM-38. `strat_xs_low_beta_with_smart_money_long` (confluence wrap)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern E candidate.

### Step 1 — Read the code

[screener.py:5770-5782](backtest/signals/screener.py#L5770-L5782):

```python
def strat_xs_low_beta_with_smart_money_long(s):
    """Cross-sectional low-beta (Frazzini-Pedersen 2014 BAB) + smart-money buy."""
    base_fires = (
        s.get("xs_low_beta_top_quintile", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
    fires = base_fires and _has_smart_money_buy(s)
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-pattern-E** | Same | LOW |
| F-fire-count | Top-quintile BAB cross smart-money → ~40-90/yr | INFO |

**B664 candidate:** Pattern E reframe.

---

## SM-39. `strat_donchian_breakout_with_smart_money_long` (confluence wrap)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern E candidate.

### Step 1 — Read the code

[screener.py:5785-5796](backtest/signals/screener.py#L5785-L5796):

```python
def strat_donchian_breakout_with_smart_money_long(s):
    base_fires = (
        s.get("dc20_breakout_up", False)
        and s.get("close_above_open", True)
    )
    fires = base_fires and _has_smart_money_buy(s)
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-pattern-E** | Same | LOW |
| F-fire-count | Donchian breakout × smart-money → ~20-50/yr | INFO |

**B664 candidate:** Pattern E reframe.

---

## SM-40. `strat_macd_bullish_with_smart_money_long` (confluence wrap)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern E candidate.

### Step 1 — Read the code

[screener.py:5799-5810](backtest/signals/screener.py#L5799-L5810):

```python
def strat_macd_bullish_with_smart_money_long(s):
    base_fires = (
        s.get("macd_bullish_cross", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
    fires = base_fires and _has_smart_money_buy(s)
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-pattern-E** | Same | LOW |
| F-fire-count | MACD bullish cross × smart-money → ~30-70/yr | INFO |

**B664 candidate:** Pattern E reframe.

---

## SM-41. `strat_pead_with_smart_money_long` (confluence wrap, cross-cluster with PEAD)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Pattern E candidate. Cross-cluster with PEAD.

### Step 1 — Read the code

[screener.py:5813-5827](backtest/signals/screener.py#L5813-L5827):

```python
def strat_pead_with_smart_money_long(s):
    """Variant of strat_pead_with_insider_confirmation_long (SM-6) that
    uses the broader smart-money composite rather than insider_cluster alone."""
    base_fires = (
        s.get("within_pead_window", False)
        and s.get("pead_positive_surprise", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
```

### Step 7

| # | Finding | Severity |
|---|---|---|
| **F-pattern-E** | Same bullet text overclaim | LOW |
| F-redundancy-vs-SM6 | SM-41 differs from SM-6 in using the broader UNION (insider OR 13F) vs SM-6's narrower (insider only). Cube empirically adjudicates whether broader UNION dilutes or amplifies SM-6's edge | INFO |
| F-fire-count | PEAD window × smart-money UNION → ~25-60/yr | INFO |

**B664 candidate:** Pattern E reframe + queue ticket `S5-SM41-VS-SM6-OVERLAP-AUDIT` for cube comparison.

---

## Outstanding queue tickets surfaced (smart money cluster)

> Full inventory of queue tickets surfaced across the 41 per-strategy walks. Tickets are grouped by status:

### ✅ Closed by prior batches (4 tickets)

| Ticket | Closed by | Description |
|---|---|---|
| `S4-EVENT-DRIVEN-DEFAULT-TRUE-EMA-SWEEP` | B663 | Family-bug full-screener sweep on `price_above_ema_200`; superseded narrower-scope ticket |
| `S4-SM-1-FAMILY-BUG-FIX` (implicit) | B663 | SM-1 + SM-2 silent-gap default-True fix |
| `S4-PATTERN-B-STATE-AS-EVENT-OVERCLAIM-SM-11` | B611 | First-application of Pattern B docstring honesty reframe |
| `S4-PATTERN-E-SMART-MONEY-CONFLUENCE-SM-34/35` | B613 | First-application of Pattern E `_has_smart_money_buy` UNION framing |

### ⏳ B664 candidate (gated on owner approval — 5 patterns × multi-strategy scope)

| Ticket | Patterns | Strategies |
|---|---|---|
| `S4-PATTERN-A-EMA-50-FAMILY-SWEEP` | A | SM-8, SM-14, SM-17, SM-24, SM-27, SM-28 (cluster-only) OR 9 strategies (full screener sweep symmetric with B663) |
| `S4-PATTERN-B-STATE-AS-EVENT-DOCSTRING-SWEEP` | B | 20 institutional sleeve strategies (SM-7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 20, 21, 22, 23, 24, 25, 26, 27, 29 + SM-10 citation fix) |
| `S4-PATTERN-C-SHORT-DATA-SOURCE-ASYMMETRY-CAVEAT` | C | SM-9 + SM-23 docstring caveat (defer deletion to Stage D) |
| `S4-PATTERN-D-STALE-LINEAGE-FIX` | D | SM-3 + SM-4 "NOT REGISTERED" docstring update |
| `S4-PATTERN-E-CONFLUENCE-WRAP-BULLET-REFRAME` | E | SM-31, 32, 33, 36, 37, 38, 39, 40, 41 |

### ⏳ Open queue tickets (no immediate action; queued for Stage D / B660 / S5)

| Ticket | Description |
|---|---|
| `S5-INSIDER-CLUSTER-HOLD-DURATION-VALIDATION` | Cohen-Malloy-Pomorski 12-month-alpha thesis vs default 1× ATR trail exit; cube replay across hold durations |
| `S4-INSIDER-PRODUCER-PARALLEL-AUDIT` | Two parallel insider producers (`insider_buying.py:compute_insider_cluster_signals` boolean vs `data/smart_money.py:insider_signal` categorical); cross-consumer audit |
| `S4-INSIDER-SCHEMA-PIN` | Quiver `live/insiders` schema-version assertion / pin |
| `S5-SM5-DTC-THRESHOLD-CALIBRATION` | SM-5 `days_to_cover > 5.0` heuristic threshold; calibrate against B660 + cube |
| `S5-SM6-PEAD-INSIDER-FIRE-COUNT-MEASUREMENT` | SM-6 fire-count BORDERLINE/FAIL on min_trades=30; B660 quantifies |
| `S5-SM30-FIRE-COUNT-MEASUREMENT` | SM-30 2-EVENT rare co-occurrence likely FAIL on min_trades=30; B660 quantifies |
| `S5-SM41-VS-SM6-OVERLAP-AUDIT` | SM-41 (PEAD + smart-money UNION) vs SM-6 (PEAD + insider only) — does UNION dilute or amplify? Cube empirically adjudicates |
| `S5-13F-EVENT-COMPONENT-ISOLATION` (Pattern B.c larger option) | Research: extract pure-EVENT smart-money composite (insider only, no 13F) for factor-pure variant of wraps |
| `S5-SM-9-SM-23-DELETION-DECISION` (Pattern C.c larger option) | Stage D empirical verdict will inform whether SM-9 + SM-23 should be deleted per B611 precedent |
| `S4-SM-3-13D-OVERSOLD-CONFLUENCE-CLASS-7-NEW` (deferred) | Class 7 NEW candidate from SM-3 walk; activist 13D + price-below-200-EMA |
| `S4-SM-4-ACQUIRER-SIDE-SHORT-CLASS-7-NEW` (deferred) | Class 7 NEW candidate from SM-4 walk; requires producer extension to distinguish target vs acquirer |
| `S4-INSIDER-CONCENTRATED-SELL-CLASS-7-NEW` (deferred from B662) | Class 7 NEW candidate from SM-1 walk; `concentrated_sell` > 50% holdings as the only economically-defensible SHORT mirror of insider buying |

### Cross-cluster references

- B660 full-universe fire-count measurement (in flight overnight) provides authoritative fires/yr numbers for all SM strategies — refer to [STAGE_4_PIVOT_CLUSTER_WALKS.md](STAGE_4_PIVOT_CLUSTER_WALKS.md#measurement-status--b660-full-universe-in-flight) for the methodology + caveat framing
- B611 + B613 precedent established by pivot + chart-pattern cluster walks (SM-11, SM-34, SM-35); B664 extends to remaining institutional sleeve + confluence wraps
- B663 ema_200 family-bug sweep precedent — directly informs Pattern A scope decision
- [STAGE_4_TREND_CLUSTER_WALKS.md](STAGE_4_TREND_CLUSTER_WALKS.md) — same B649-corrected redundancy-vs-confluence methodology applied in trend cluster (B655/B656/B657 T3+T8+T10 redundancy audits)
- [`feedback_regime_selector_lineage_grep_before_delete`](memory) — B663 self-correction memory note codifies the lineage-grep discipline applied to all 39 regime affinity checks in this cluster

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
