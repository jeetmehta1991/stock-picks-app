# Stage 4 Smart Money Cluster Walks — Per-Strategy Deep-Dive Audit

> **B665 status banner (2026-06-09, owner-approved):** the B664 candidate proposal below is **HELD pending B665 ship** + B660 full-universe measurement landing. Owner accepted the 2nd-wave-redux critique on STAGE_4_PIVOT_CLUSTER_WALKS.md — same framing-discipline corrections apply preemptively to this doc:
> - **All `fires/yr` projection ranges in per-strategy walks are PENDING B660** — they are diagnostic-only estimates from independence-product math (NOT measured); the same representativeness flaw the pivot doc has applies here
> - **No "PASS_CUBE" / "FAIL" labels** appear in this doc yet (intentional — projection ranges only) but if any are added pre-B660, they will be retracted under the same B665 discipline
> - **Pattern B docstring sweep** (the largest B664 candidate item) is HELD because applying it pre-B665 would replicate the "CHANGES MERGED reads as VALIDATED" conflation 2C7 + B665 #1 corrected on the pivot doc
> - **Per `S5-DO-NOT-DEPLOY-MULTIPLE-TESTING-RECONCILIATION` ticket opened in B665:** the smart money cluster's confluence wraps (SM-31 through SM-41) interact with the C2 correction in the same self-referential way W5m does — registered wraps that never produce alpha still consume multiple-testing budget. This is a B664 candidate consideration to surface explicitly when B664 finally ships post-B665.
>
> **Foundational re-prioritization commitment (owner-approved B665):** the next batch is NOT B664. It is B660 (measurement landing) + C2 methodology draft + C5 survivorship verification. After those land, B664 re-applies the same corrected framing standards from the start.

> **B669 status banner (2026-06-10, owner-directed COMPREHENSIVE expansion):** owner-directed OVERRIDE of B665 foundational re-prioritization commitment per *"The md doc is not comprehensive. I want steps 1 to 7 thoroughly documented for each strategy individually along with bugs gaps and recommendations. implement it after incorporating the below feedback."* This batch expands all 39 SM-3 through SM-41 walks to full pivot-doc-template density (7 steps each + Findings tables + Options + Recommendation per CHECKLIST #105), incorporates 7 reviewer findings as a new [Reviewer findings response matrix](#reviewer-findings-response-matrix-2026-06-10-cluster-walk-critique), and applies one immediate code fix (SM-23 docstring honesty per Finding #3). The override notes are recorded here transparently; foundational sequence still applies to subsequent batches (B670+ awaits B660 land + C2/C5 follow-on).

> **B670 status banner (2026-06-10, owner-approved 4 Round-1 decisions on B669-pending items):** SM-9 + SM-23 DELETED per Pattern C STRENGTHENED disposition (reviewer F2 + F3); 2 Class 7 NEW clean replacements registered in `momentum_trend` category (NOT smart money cluster). SM-5 routing verification reveals SM-5 IS an orphan emitter (engine drops avoid output per backtest.py:1457-1466); wiring requires NEW architecture (Round 2 owner-direction needed on scope). **Net strategy count: 222 → 222 (-2 deletions + 2 Class 7 NEW = net 0).** Smart money cluster: 41 → 39 (Class 7 NEW replacements register in momentum_trend, not smart money). B670 pyramid: 858/858 green. Round 2 questions queued: SM-5 NEW wiring scope (post-orphan finding) + SM-5 DTC threshold + Pattern F gate sequencing + low-fire combo EXPLORATORY sequencing.

> **B671 status banner (2026-06-10, owner-approved 2 Round-2 code-action decisions Q5 + Q6):** SM-5 borrow-trap consult **CENTRALIZED in `_strat()` + `_strat3()` helpers via inspect.currentframe pattern** (Q5 owner-approved "Per-strategy pre-fire gate, cleanest, biggest blast radius" — implementation pattern uses centralized inspect-frame consult rather than per-strategy edit fan-out because the semantic intent is "every SHORT strategy + every FUTURE SHORT strategy automatically protected"; new SHORT strategy authors cannot forget the consult). **SM-5 DTC threshold tightened 5.0 → 8.0** per Q6 owner-approved reviewer F5 squeeze-name range observation (GME 2021 pre-squeeze ~5-7 borderline; MSTR 2021 ~8-12; BBBY pre-collapse ~6-10). Q7 + Q8 (Pattern F sequencing + low-fire combo EXPLORATORY review) DEFERRED post-B660 per owner-approved foundational sequence (no B671 code action). **Net strategy count UNCHANGED 222.** B671 pyramid: 872/872 green (14 B671 + 16 B670 + 842 unit+integration).

## Reviewer findings response matrix (2026-06-10 cluster-walk critique)

> Adversarial review of the original B664 cluster walk produced 7 findings. Each is tracked here with status + action; per-strategy walks below cite which findings apply.

| # | Finding | Severity | Status | Action |
|---|---|---|---|---|
| **F1** | "Pattern B docstring sweep" treats 20 13F overclaims as wording issue, but the 13F gate is near-constant 90d (eligibility filter, not timing) so the strategies' actual edge lives in the OTHER gate — the sleeve may be 20 lightly-reskinned versions of a few underlying technical strategies. Should run the `feedback_obv_avwap_macd_non_redundancy` "what does THIS gate screen out" test on the 13F sleeve (not just the confluence wraps where the doc already applied it). If 13F is near-constant, the right disposition for many is deprecate, not reword. | HIGH | **NEW Pattern F surfaced** (`13F-SLEEVE-MARGINAL-CONTRIBUTION-AUDIT`). Cube replay + marginal-contribution test required pre-disposition; queued + cross-ref `S5-MARGINAL-CONTRIBUTION-SCORING` C3 ticket. The B664 candidate "Pattern B docstring sweep on 20 strategies" is RE-FRAMED: the sweep ships only after marginal-contribution test surfaces which 13F gates carry distinct information. Pre-test, the docstring honesty fix would make the docs accurately describe near-no-op gates — honest, but evidence the strategies shouldn't exist as separate registered entries. | NEW Pattern F + RE-FRAMED Pattern B disposition |
| **F2** | SM-9 / SM-23 SHORT disposition ("docstring caveat, defer deletion to Stage D") is inconsistent with cited B611 precedent (which DELETED `strat_institutional_breakdown_confirmation_short` for the same data-source-asymmetry reason). The "defer to empirical" assumption is wrong: a 13F-trim short will backtest fine in survivor universes over 2020-2026 (squeeze + delisting + cost gaps mask the falseness); deferring to a stage that's structurally blind is misapplying `project_no_apriori_strategy_pruning` to a case where the prior is a regulatory fact, not a guess. | HIGH | **Pattern C STRENGTHENED**: deletion option (c) elevated to RECOMMENDED for SM-9 + SM-23 with explicit B611-precedent reconciliation. `project_no_apriori_strategy_pruning` continues to gate the actual deletion (requires explicit owner approval), but the cluster-walk recommendation is now (c) DELETE rather than (b) docstring caveat. Surfacing for owner direction. | Pattern C disposition re-framed; owner direction needed |
| **F3** | SM-23 has direction-vs-name contradiction. Name "capitulation_short" implies CONTRARIAN-BOTTOM but implementation is MOMENTUM-CONTINUATION SHORT (sell into wash-out). Filed under softer Pattern C "data-source asymmetry" but it's actually an F1 thesis-vs-implementation bug in the doc's own taxonomy. | MEDIUM | **B669 docstring honesty fix shipped** in [screener.py:strat_institutional_capitulation_short](backtest/signals/screener.py): added explicit THESIS-vs-NAME DISAMBIGUATION block clarifying the strategy is MOMENTUM-CONTINUATION SHORT not contrarian-bottom. Rename to `strat_institutional_distribution_with_volume_short` surfaced as separate B-N owner-decision (renames cascade through tests + dashboards per `feedback_local_changes_default_global_needs_approval`). | ✅ SHIPPED B669 |
| **F4** | SM-12 (and SM-6 + SM-20 + SM-25 + SM-30) fire-count projections "FAIL on min_trades=30 likely" — but disposition is just docstring reframe. Per cluster methodology adaptation #4, "the cube cannot statistically validate the strategy regardless of design quality" — so reframing a strategy the cube can't evaluate is rearranging text. Should be EXPLORATORY-flagged like W5/W5m so they're not silently counted as live validatable strategies. | MEDIUM | **NEW per-strategy EXPLORATORY-flag candidates**: SM-6, SM-12, SM-20, SM-25, SM-30 added to per-strategy walks with EXPLORATORY-candidate status pending B660 measured fires/yr. Per `project_no_apriori_strategy_pruning`: do NOT auto-flag without measurement; queued as `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660` for post-B660 owner-review batch. | Queued + per-walk flags surfaced |
| **F5** | SM-5 borrow trap is the cluster's most valuable strategy — direct partial implementation of the C6 cost/borrow guard that W5m DO-NOT-DEPLOY + every other short strategy is waiting on. Yet it's a single hard-coded threshold (`dtc > 5.0`, "heuristic") walked in 60 lines + given INFO-tagged calibration ticket while 22 near-redundant 13F strategies get full walks. Two issues: (a) `dtc > 5` is loose (many squeeze names run DTC 8-20); (b) SM-5 should be WIRED to W5m + every short strategy to consult its avoid output, not standalone | HIGH | **TWO new queue tickets opened**: (1) `S4-SM5-BORROW-GUARD-WIRING-INTO-SHORT-STRATEGIES` — engine-level architecture to route SM-5's avoid output as a pre-fire gate for every SHORT strategy (W5m + SM-9 + SM-23 + every confluence-wrap-SHORT); (2) `S4-SM5-DTC-THRESHOLD-CALIBRATION-AGAINST-EMPIRICAL-SQUEEZE-CASES` — calibrate threshold against empirical squeeze cases (GME 2021, AMC 2021, MSTR 2021, BBBY pre-collapse) where DTC was 8-20. Both queued; B669 doc-only surfacing per `feedback_local_changes_default_global_needs_approval` (engine wiring is global change requiring explicit owner approval). | Queued; engine wiring deferred to dedicated batch |
| **F6** | "39 → 41" count wobble + cross-cluster double-counting (SM-6 + SM-41 also belong to PEAD cluster) is a governance smell. Breaks multiple-testing correction (C2) downstream: if PEAD-with-insider counts in both clusters, it's one strategy consuming two slots in the hypothesis count OR it's double-counted in the family-wise error budget. | MEDIUM | **NEW queue ticket**: `S4-CROSS-CLUSTER-REGISTRY-DEDUP` — establish single source-of-truth global strategy registry keyed on function name, NOT per-cluster tallies that overlap. The C2 correction (`backtest/engine/multiple_testing_correction.py`) already uses `ALL_STRATEGIES` keys as the family-size source-of-truth, so the C2 path is dedup-safe; the per-cluster docs need the cross-references explicit. Action: clarify in each per-cluster walk's scope inventory which strategies have cross-cluster membership. SM-6 + SM-41 flags added below. | Queued + per-walk cross-cluster flags |
| **F7** | Cluster-positive: temporality + asymmetry + citation discipline now genuinely upstream (walk-#1 critique fully internalized). Citation-error class catch (SM-10 cites CMP 2012 insider paper for a 13F strategy) was caught independently — review process working as designed. | INFO | **No action needed** — captured in [Methodology adaptations](#methodology-adaptations-for-smart-money-cluster) section as the cluster's core discipline. SM-11 B611 reframe is the canonical template. | Cluster-positive credit acknowledged |

**Net effect on B664 candidate dispositions:**

- **Pattern A (ema_50 family sweep)**: unchanged (still HELD per B665 commitment)
- **Pattern B (STATE-as-EVENT docstring sweep on 20 strategies)**: RE-FRAMED. Sweep ships only after marginal-contribution test surfaces which gates carry distinct information. Pre-test docstring fixes would make docs accurately describe near-no-op gates (honest, but argument for deprecation not reword).
- **Pattern C (SM-9 / SM-23 disposition)**: STRENGTHENED. Option (c) DELETE now RECOMMENDED with B611-precedent reconciliation; owner direction needed.
- **Pattern D (SM-3 / SM-4 stale lineage)**: unchanged (mechanical informational fix)
- **Pattern E (9 confluence wrap bullet reframe)**: unchanged (cite B613 template)
- **NEW Pattern F (13F sleeve marginal-contribution audit)**: highest-leverage action; gates Pattern B disposition

---

> **What this document is.** A LIVING per-cluster Stage 4 walk doc covering the smart money strategy cluster (41 strategies — the largest pending cluster as of the post-B660 close of pivot + trend clusters). Each strategy receives a 7-step deep-dive walk per CHECKLIST #105 with options surfaced and WAITING for owner direction per `feedback_no_rushing_per_strategy_tweak`.
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

### Pattern F — 13F sleeve marginal-contribution audit (NEW B669 per reviewer F1; HIGH severity)

> **Reviewer F1 (B669 cluster-walk critique):** "Pattern B treats 20 overclaims as wording, but if 13F is correctly relabeled as a 90-day-constant eligibility filter, then for most of these strategies the 13F gate is doing almost no discriminating work at the bar of fire — it's on for an entire quarter. The strategy's actual edge, if any, lives entirely in its OTHER gate. The honest question isn't 'how do we word the docstring' — it's 'does the 13F gate add any marginal information over the base technical signal, or is the sleeve really 22 lightly-reskinned versions of a few underlying technical strategies?'"

**Pattern F audit candidates** (22 of the 13F sleeve where the 13F gate may be near-no-op marginal contribution; per-gate "what does THIS screen out that the others don't" test per `feedback_obv_avwap_macd_non_redundancy`):

| SM-# | Strategy | Non-13F base signal | Marginal-contribution hypothesis |
|---|---|---|---|
| SM-7 | `institutional_cluster_long` | `price_above_ema_200` | Strategy reduces to "established uptrend with 13F-eligibility" — 13F gate may be near-no-op |
| SM-8 | `institutional_buy_momentum_long` | `macd_bullish + price_above_ema_50` | Strategy reduces to a MACD-trend-confirmed momentum LONG with 13F-eligibility filter |
| SM-9 | `institutional_distribution_short` | `below_ema_50` | Strategy reduces to `simple_below_ema_50_short` with 13F-eligibility (see SM-9 walk Step 7) |
| SM-10 | `institutional_oversold_long` | `rsi_14 < 35 + price_above_ema_200` | Strategy reduces to RSI-oversold-in-uptrend with 13F-eligibility (see SM-10 walk citation-error note) |
| SM-11 | `institutional_breakout_confirmation_long` | `resistance_break_retest + price_above_ema_200 + close_above_open + vol_below_avg` | **Already B611-walked**: docstring honestly states alpha attribution belongs to Bulkowski retest + trend filter, NOT 13F. Canonical Pattern F template. |
| SM-12 | `institutional_insider_combo_long` | `insider_cluster_active + price_above_ema_200` | Has 1 EVENT gate (insider); 13F may be eligibility-only. **Pattern G also applies (low fire count).** |
| SM-13 | `institutional_persistence_breakout_long` | `resistance_break_retest + price_above_ema_200` | Same template as SM-11; 13F-persistence (`institutional_increased >= 5`) is eligibility filter |
| SM-14 | `institutional_persistence_volume_long` | `vol_spike_2x + price_above_ema_50` | Strategy reduces to vol-spike-in-trend with 13F-eligibility |
| SM-15 | `institutional_persistence_oversold_long` | `rsi_14 < 40 + price_above_ema_200` | Same SM-10 family; 13F-eligibility filter |
| SM-16 | `institutional_recent_init_momentum_long` | `macd_bullish + price_above_ema_200` | Same SM-8 family |
| SM-17 | `institutional_recent_init_volume_long` | `vol_spike_2x + price_above_ema_50` | Same SM-14 family |
| SM-18 | `institutional_multi_quarter_persistence_long` | `price_above_ema_200` | 4-quarter precompute is GENUINE STATE (not Pattern B); 13F-persistence is the actual signal here. **EXEMPT from Pattern F** |
| SM-19 | `institutional_committed_growth_long` | `price_above_ema_200` | Same SM-18 family — 4q precompute genuine STATE. **EXEMPT from Pattern F** |
| SM-20 | `institutional_increased_with_directors_long` | `insider_director_buyers_30d >= 1 + price_above_ema_200` | Has 1 EVENT gate (director EVENT); 13F-persistence may be eligibility-only. **Pattern G also applies (low fire count).** |
| SM-21 | `institutional_persistent_holders_long` | `price_above_ema_200` | Single-quarter proxy — only 13F-persistence as discriminative signal. Highest Pattern F risk: if 13F-persistence is 90-day constant, strategy reduces to `simple_above_ema_200_long` |
| SM-22 | `institutional_strong_conviction_long` | `price_above_ema_200` | Dual 13F-threshold + trend filter. Same Pattern F risk as SM-21 |
| SM-23 | `institutional_capitulation_short` | `vol_spike_2x + below_ema_50` | Has 1 EVENT gate (vol_spike); 13F-trim adds noise per Pattern C (see SM-23 walk Step 7) |
| SM-24 | `institutional_high_conviction_long` | `price_above_ema_50` | Pure 13F cluster + trend; high Pattern F risk |
| SM-25 | `institutional_with_directors_long` | `insider_director_buyers_30d >= 1 + price_above_ema_200` | Same SM-20 family. **Pattern G also applies (low fire count).** |
| SM-26 | `institutional_with_officers_long` | `insider_officer_buyers_30d >= 1 + price_above_ema_200` | Same SM-25 family |
| SM-27 | `institutional_persistence_momentum_long` | `macd_bullish + price_above_ema_50` | Same SM-8 family |
| SM-28 | `institutional_volume_confirmation_long` | `vol_spike_2x + price_above_ema_50` | Same SM-14 family |
| SM-29 | `classification_change_with_institutional_long` | `classification_changed_recent + price_above_ema_200` | 1 EVENT (reclassification) + 1 STATE (200-EMA); 13F may be eligibility-only |

**Audit methodology (queued as `S5-13F-SLEEVE-MARGINAL-CONTRIBUTION-TEST` per reviewer F1):**
1. Cube replay each 13F strategy + measure per-cell Sharpe with 13F gate ON vs OFF
2. Per-strategy marginal contribution = `Sharpe[full] - Sharpe[13F-removed]`
3. If marginal contribution < 0.10 (heuristic; tune against B660 + cube data), the 13F gate is doing near-no work; strategy should be replaced with the cleaner non-13F version
4. **Cross-ref `S5-MARGINAL-CONTRIBUTION-SCORING` C3 ticket** — the per-strategy marginal-contribution test is the foundational tool C3 was supposed to provide; this is the first cluster-scoped application

**B669 disposition for Pattern F:** Pattern B docstring sweep is RE-FRAMED — it ships only AFTER Pattern F audit surfaces which 13F gates carry distinct information. Pre-test docstring fixes would make the docs accurately describe near-no-op gates (honest, but evidence the strategies shouldn't exist as separate registered entries).

### Pattern G — Low-fire-count combo EXPLORATORY-candidate review (NEW B669 per reviewer F4; MEDIUM severity)

> **Reviewer F4 (B669 cluster-walk critique):** "SM-12 fire-count projection (~10-30/yr, FAIL on min_trades=30 likely) contradicts the docstring-reframe disposition. Per cluster methodology adaptation #4, 'the cube cannot statistically validate the strategy regardless of design quality' — so reframing its docstring is rearranging text on a strategy the cube can't evaluate. At minimum the fire-starved combo strategies should be flagged EXPLORATORY (like W5/W5m) so they're not silently counted as live validatable strategies."

**Pattern G candidates** (strategies with projected fires/yr ~10-30 likely BELOW min_trades=30 statistical floor):

| SM-# | Strategy | Projected fires/yr | Pattern G action |
|---|---|---|---|
| SM-6 | `pead_with_insider_confirmation_long` | ~10-25 | EXPLORATORY-candidate (PEAD × insider rare co-occurrence) |
| SM-12 | `institutional_insider_combo_long` | ~10-30 | EXPLORATORY-candidate (13F × insider rare co-occurrence) |
| SM-20 | `institutional_increased_with_directors_long` | ~10-25 | EXPLORATORY-candidate (persistence × director rare co-occurrence) |
| SM-25 | `institutional_with_directors_long` | ~10-25 | EXPLORATORY-candidate (13F × director rare co-occurrence) |
| SM-30 | `classification_change_with_insider_long` | ~5-15 | EXPLORATORY-candidate (reclassification × insider very rare co-occurrence) |

**B669 disposition for Pattern G:** Do NOT auto-flag EXPLORATORY pre-B660 per `project_no_apriori_strategy_pruning` (projections may be wrong). Queued as `S4-LOW-FIRE-COMBO-EXPLORATORY-REVIEW-POST-B660` for post-B660 owner-review batch. **If B660 confirms < 30 fires/yr per regime, add to `EXPLORATORY_STRATEGIES` constant in `backtest/engine/multiple_testing_correction.py` per Decision 4 (excludes from family-size N while keeping cube-replay coverage).**

### Pattern H — Cross-cluster registry dedup (NEW B669 per reviewer F6; MEDIUM severity)

> **Reviewer F6 (B669 cluster-walk critique):** "The '39 → 41' count wobble and the cross-cluster double-counting are a governance smell. SM-6 and SM-41 explicitly belong to the PEAD cluster too. This breaks multiple-testing correction (C2) downstream: if PEAD-with-insider is counted in both clusters, it's one strategy consuming two slots in the hypothesis count, or it's double-counted in the family-wise error budget."

**Cross-cluster membership flags** (strategies belonging to MORE than one Stage 4 cluster):

| SM-# | Strategy | Smart Money cluster | PEAD cluster | Other clusters |
|---|---|---|---|---|
| SM-6 | `pead_with_insider_confirmation_long` | ✅ (insider component) | ✅ (PEAD core) | — |
| SM-29 | `classification_change_with_institutional_long` | ✅ (13F overlay) | — | ✅ Classification change cluster |
| SM-30 | `classification_change_with_insider_long` | ✅ (insider overlay) | — | ✅ Classification change cluster |
| SM-41 | `pead_with_smart_money_long` | ✅ (smart-money UNION) | ✅ (PEAD core) | — |

**B669 disposition for Pattern H:**

1. **C2 path is already dedup-safe** — `backtest/engine/multiple_testing_correction.py` uses `ALL_STRATEGIES` keys as the family-size source-of-truth (NOT per-cluster doc tallies). Each strategy counts ONCE in the multi-testing correction regardless of how many cluster docs mention it.
2. **Per-cluster docs need explicit cross-cluster flags** to prevent owner / reviewer confusion + accidentally double-counting when reading across docs
3. **NEW queue ticket** `S4-CROSS-CLUSTER-REGISTRY-DEDUP-NOMENCLATURE` — establish a single source-of-truth strategy registry document (or canonical column in STRATEGY_ROSTER.md) listing each strategy's PRIMARY cluster + ALL clusters it appears in. Per-cluster docs reference the registry rather than re-declaring counts.

**Strategy-count discipline (per `feedback_strategy_counts_by_buckets_each_turn`):** the cluster tally of "41" reflects strategies that have a smart-money-component in their gate set, regardless of primary cluster assignment. The cross-cluster flags above clarify which 4 of the 41 are PRIMARILY assigned to other clusters (with smart-money as an overlay).

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

## SM-4. `strat_m_and_a_target_long` (foundational P17c sleeve, B664 candidate)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B664 candidate Pattern D). Single-gate event-driven on 8-K Item 1.01 (material definitive agreement disclosure). Structural mirror of SM-3 activist_13d_long (same producer infrastructure; same stale-lineage Pattern D issue; same regime affinity profile).

### Step 1 — Read the code

[screener.py:3923-3945](backtest/signals/screener.py#L3923-L3945):

```python
def strat_m_and_a_target_long(s):
    """Batch 522 (2026-05-31, P17c SCAFFOLD per EXECUTION_QUEUE).

    Long fires when 8-K Item 1.01 (material definitive agreement)
    landed in the last 30 days. Trigger boolean is
    `8k_item_1_01_filed_within_30d` from `compute_sec_edgar_signals`.

    Academic backing: Pawliczek-Skinner 2018 *Review of Accounting
    Studies* -- Items 1.01 + 2.02 predict short-term returns
    (~2-3pp 10-day CAR). Item 1.01 is frequently the FIRST public
    disclosure that a company is being acquired or signed a major
    partnership; stock often gaps 10-30% on the next bar.

    NOT REGISTERED in ALL_STRATEGIES in Batch 522 -- ships SCAFFOLD-only
    pending P17a scoped extraction completion + owner approval for
    ALL_STRATEGIES wire-in.
    """
    fires = bool(s.get("8k_item_1_01_filed_within_30d", False))
    return _strat(fires, "long", "sec_edgar_sleeve",
        ["8k_item_1_01_filed_within_30d"],
        ["8-K Item 1.01 (material definitive agreement) filed <=30d ago",
         "Often first public disclosure of M&A or major partnership",
         "Pawliczek-Skinner 2018 +2-3pp 10-day CAR"])
```

**Single-gate strategy.** Only `8k_item_1_01_filed_within_30d`. Identical structural pattern to SM-3 (`strat_activist_13d_long`): single SEC EDGAR event boolean → fires LONG.

**LONG fires when:**

| Gate | Meaning |
|---|---|
| `8k_item_1_01_filed_within_30d` | An 8-K filing tagged Item 1.01 (material definitive agreement) landed within the last 30 calendar days |

### Step 2 — Classify

- Category: `sec_edgar_sleeve` (P17c sleeve, registered alongside P17b SM-3 activist_13d_long)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default `{bull, neutral}` (excludes bear + crisis)
- Last touched: B531 (wire-in to `ALL_STRATEGIES` + producer activation in `screen_instrument`; docstring "NOT REGISTERED" is **STALE** by 2 batches per reviewer F-Pattern D)

### Step 3 — Producer source-read + temporality

**Producer:** `compute_sec_edgar_signals` in [sec_edgar_extractor.py:301](backtest/signals/sec_edgar_extractor.py#L301) → calls `eight_k_item_filed_within_days(item_code="1.01", lookback_days=30)`.

**Input:** SEC EDGAR-decoded parquet at `data_prefetch/sec_edgar/8_K/<TICKER>.parquet` (B458 silent-failure-friendly load via `_load_decoded`).

**Logic:** `filing_date > (as_of - 30d) AND filing_date <= as_of AND item_codes contains "1.01"` → returns `8k_item_1_01_filed_within_30d: True/False`.

**Temporality:** **EVENT-class** ✅. 8-K filings have a 4-business-day filing requirement (SEC rule per Form 8-K General Instructions B); Item 1.01 disclosure of material definitive agreement is bar-of-fire EVENT signal. Pawliczek-Skinner's +2-3pp 10-day CAR centers around the filing event. Per CHECKLIST (s) EVENT-classification: docstring's "filed <= 30 days ago" claim is consistent with EVENT temporality (the filing event triggered the 30-day rolling window). ✅ No timing overclaim.

**Cross-reference: producer wired into screen_instrument at B531** per the same lineage as SM-3 — same wire-in commit; same wire-in source-of-truth at screener.py:6758.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Pawliczek-Skinner 2018 *Review of Accounting Studies* +2-3pp 10-day CAR" | ✅ Real paper, real result. Specifically "The 8-K Disclosure Choice and Earnings Quality" documents post-filing CAR on material-definitive-agreement disclosures. |
| "Item 1.01 = material definitive agreement (MDA)" | ✅ Accurate per SEC Form 8-K Item 1.01 specification |
| "Often FIRST public disclosure of M&A" | ✅ For target-side disclosures, this is the canonical pattern (acquirer announces deal → target files 8-K Item 1.01 within 4 business days) |
| "Stock often gaps 10-30% on next bar" | ✅ Empirical heuristic; consistent with M&A premium literature (Bradley-Desai-Kim 1988 *JFE* documents +30% average target-side premium) |
| "NOT REGISTERED in ALL_STRATEGIES in Batch 522" | ⚠ **STALE** — B531 wired in (Pattern D per reviewer cluster-walk; same lineage gap as SM-3) |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations on `m_and_a_target` / `8k_item_1_01_filed`. **Cross-reference shared infrastructure with SM-3:** both depend on `compute_sec_edgar_signals` + `_load_decoded("8_K", ...)`; any future schema-pin or PIT-audit ticket on the SEC EDGAR path applies to both.

### Step 6 — Missing-inverse + economic-symmetry

**Per `feedback_asymmetric_data_sources_break_mechanical_inverse` analysis of 8-K Item 1.01 structure:**

8-K Item 1.01 is filed by **BOTH** acquirer AND target on a typical M&A deal — both companies have a material definitive agreement to disclose. But the **forward returns are ASYMMETRIC**:
- **Target-side**: Pawliczek-Skinner +2-3pp 10-day CAR; Bradley-Desai-Kim ~30% premium on announcement day
- **Acquirer-side**: typically gaps DOWN on the announcement (deal premium dilutes acquirer EPS; market often skeptical of synergies)

**Current producer limitation:** `eight_k_item_filed_within_days` does NOT distinguish target-side filings from acquirer-side filings. The boolean fires on EITHER party's 8-K. So the strategy as-written is a noisy LONG that mixes:
- True positive: target-side filings (the +2-3pp CAR alpha source)
- False positive: acquirer-side filings (which historically gap DOWN; LONG bet is wrong-sided)

**Class 7 NEW SHORT candidate (acquirer side):** `strat_m_and_a_acquirer_short` would short the acquirer on its own 8-K Item 1.01 filing. **REQUIRES PRODUCER ENHANCEMENT** to distinguish target vs acquirer (likely via Form 8-K acquirer-self-flag or via cross-reference with the target's filing). Queued as `S5-SM4-ACQUIRER-SIDE-SHORT-CLASS-7-NEW` per B664 cluster-walk surfacing.

**Economic-symmetry post-producer-enhancement:** if producer distinguishes target vs acquirer, the SHORT mirror IS economically defensible (target+acquirer asymmetric returns are a structural feature of M&A deals, not a data-source artifact). UNLIKE the SM-9/SM-23 13F asymmetry case, this Class 7 NEW SHORT is not Pattern C — both directions are economically real; the implementation just requires producer disambiguation.

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F2 STALE Pattern D** | "NOT REGISTERED in ALL_STRATEGIES in Batch 522" claim in docstring is stale by 2 batches (B531 wired in + producer activation in screen_instrument). Reviewer Pattern D cluster-walk finding. | LOW | Pattern D / reviewer F6 (cross-cluster) |
| F3 regime | No `STRATEGY_REGIME_AFFINITY` entry → B291 LONG default `{bull, neutral}`. M&A target returns are mostly regime-agnostic (deals happen across regimes); B291 default may be over-restrictive (deals in bear/crisis still gap up). Per B663 lesson: ambiguous → defer to post-cube empirical. No lineage means no documented prior decision; B291 default applies until empirical override. | INFO | B663 lineage-grep discipline |
| F-temporality | EVENT-class ✅ no overclaim per CHECKLIST (s) | — | F7 |
| F-data-source-asymmetry | Producer doesn't distinguish acquirer vs target; mixes alpha source (target) with adverse signal (acquirer); Class 7 NEW acquirer-SHORT requires producer enhancement | MEDIUM (Pattern D-adjacent) | F2-class (data-source structural) |
| F-fire-count | 8-K Item 1.01 fires more often than 13D filings (more deals than 5%-ownership-crossings); projected ~50-150/yr universe-wide; PASS on min_trades=30 floor. Note: fire count includes BOTH target + acquirer disclosures, so true target-only fire rate is ~half (~25-75/yr); still PASS but borderline. | INFO | F4-adjacent (low-fire-combo) |
| F-confluence (single-gate) | Single-gate is unusual for cluster strategies; could be tightened with 8-K Item 1.01 + price-near-acquisition-rumor-spike confluence — but per B620 precedent on EVENT-only strategies, owner-decision required pre-cube. | INFO | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo — no changes |
| **(b) F2 docstring lineage fix only** (RECOMMENDED) — replace "NOT REGISTERED in Batch 522" claim with current B531 lineage. Zero behavior change. Mechanical fix. Same as B664 candidate Pattern D disposition. |
| (c) (b) + add explicit `STRATEGY_REGIME_AFFINITY['m_and_a_target_long']: {bull, neutral, bear, crisis}` (all-regimes) per "deals happen across regimes" thesis. Behavior change: enables bear/crisis fires that B291 default currently blocks. Risk: no empirical evidence either way pre-cube. |
| (d) (b) + Class 7 NEW `strat_m_and_a_acquirer_short` candidate flagged for separate producer-enhancement batch. Surface as `S5-SM4-ACQUIRER-SIDE-SHORT-CLASS-7-NEW` queue ticket. |
| (e) Stage 5 deferral — defer everything |

**My recommendation: (b) F2 docstring fix only + (d) Class 7 NEW queue ticket (already opened).** Same pattern as SM-3: docstring stale-lineage is unambiguous; behavior-change F3 deferred to post-cube; Class 7 NEW acquirer-SHORT requires producer enhancement (separate batch).

**Awaiting owner direction on SM-4:**
1. **F2 lineage fix:** approve mechanical fix
2. **F3 regime affinity:** defer to post-cube empirical / explicit override / no change
3. **Class 7 NEW acquirer-SHORT:** confirm queue ticket scope or drop the question

---

## SM-5. `strat_short_borrow_trap_avoid` (foundational, walked — **cluster's most valuable strategy per reviewer F5**)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B669 expanded per reviewer F5). Avoid-direction strategy (blocks SHORT entries on hard-to-borrow names). **Reviewer F5 explicitly highlights this as "the most valuable thing in the cluster" + "the only strategy directly addressing the squeeze-tail risk that C6 + W5m DO-NOT-DEPLOY gate are waiting on"** — yet under-resourced relative to 22 near-redundant 13F strategies.

### Step 1 — Read the code

[screener.py:3948-3971](backtest/signals/screener.py#L3948-L3971):

```python
def strat_short_borrow_trap_avoid(s):
    """Batch 519 (2026-05-31, P15 sleeve per owner directive).
    Avoid-side gate for short strategies when borrow is tight.

    Fires `avoid` direction when days_to_cover > 5 -- meaning it would
    take >5 trading days of typical volume to cover the open short
    interest. Hard-to-borrow names carry asymmetric upside risk: when
    they DO move against shorts, the squeeze is rapid (FINRA Reg SHO).
    Per CHECKLIST risk-management convention, an 'avoid' strategy
    blocks SHORT entries on the ticker for the bar -- works the same
    way as Batch 190 crisis-long-exclusion list, but per-bar instead
    of by-ticker.

    Academic backing: Cohen-Diether-Malloy 2007 -- shorted names with
    high DTC have higher subsequent positive returns (the 'borrow
    constraint' premium).
    """
    dtc = s.get("days_to_cover", 0.0) or 0.0
    fires = dtc > 5.0
    return _strat(fires, "avoid", "smart_money_sleeve",
        ["days_to_cover>5"],
        [f"Days-to-cover {dtc:.1f} (>5 threshold)",
         "Hard-to-borrow -> squeeze risk asymmetric vs upside expectancy",
         "Cohen-Diether-Malloy 2007 borrow-constraint premium"])
```

**Single-gate strategy.** Threshold-based on `days_to_cover` continuous variable. Returns direction = `"avoid"` (unique among the cluster — not LONG, not SHORT, but a directional BLOCK).

### Step 2 — Classify

- Category: `smart_money_sleeve`; direction = **avoid** (unique — neither LONG nor SHORT; designed to BLOCK other SHORT entries on the ticker for the bar per Batch 190 crisis-long-exclusion-list precedent)
- STRATEGY_REGIME_AFFINITY: NO ENTRY (avoid-direction not regime-gated by design — borrow-risk is a risk-management primitive applied across all regimes)
- Last touched: B519

### Step 3 — Producer source-read + temporality

**Producer:** `compute_short_interest_signals` in `backtest/signals/` (Quiver Quantitative short interest feed via `data_prefetch/quiver/shortinterest/`). Emits `days_to_cover` derived as `short_interest_shares / avg_daily_volume_20d`. Refer to `backtest/data/smart_money.py` short interest section for the precise calculation path.

**Temporality:** **STATE-class** — short interest reports semi-monthly (FINRA Reg SHO; T+1 reporting delay; reports cover the 15th of each month + month-end). `days_to_cover` is computed from the most-recent SI snapshot. Effectively constant 14d at a time.

**EVENT/STATE rationale for avoid-direction:** unlike LONG/SHORT strategies where STATE-as-EVENT overclaim is the Pattern B failure mode, avoid-direction is INTRINSICALLY STATE-friendly — the purpose IS to apply a blanket block on hard-to-borrow names regardless of bar-of-fire timing. The STATE classification is CORRECT for this strategy's purpose; no Pattern B concern applies.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Cohen-Diether-Malloy 2007 borrow-constraint premium" | ✅ Real paper (CDM 2007, *Journal of Finance*); documents short squeeze asymmetry on high-DTC names + the positive forward return premium on hard-to-borrow names that institutional shorts have to pay-up to maintain |
| "FINRA Reg SHO" | ✅ Real regulatory framework; semi-monthly SI reporting requirement is correct |
| Threshold 5.0 DTC | ⚠ **Standard heuristic; NOT paper-cited specifically**. Per reviewer F5: "fairly loose gate (many squeeze names run DTC 8-20), so it may pass through exactly the dangerous names" |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations on SM-5 directly. **Cross-reference open tickets:**
- `S4-COST-BORROW-MODELING` (C6 from B640 audit, still open) — SM-5 is the partial implementation of C6's borrow-cost guard
- `W5m DO-NOT-DEPLOY gate` (B652) — keyed on M10 cost-aware cube; SM-5 already provides the borrow-cost primitive that M10 needs
- `S4-B664-PATTERN-C-SHORT-DATA-SOURCE-ASYMMETRY-CAVEAT` — every SHORT in the cluster (SM-9 + SM-23) should consult SM-5

### Step 6 — Missing-inverse + economic-symmetry

Avoid-direction strategies don't have inverse mirrors by design (they BLOCK actions, not propose them). ✅

**Important asymmetry observation per reviewer F5:** SM-5 is the ONLY strategy in the cluster that addresses SHORT-side data-source structural risk via a positive primitive (rather than via a docstring caveat or DO-NOT-DEPLOY gate). This makes SM-5 architecturally valuable beyond its standalone use:
- It can serve as a PRE-FIRE GATE for every SHORT strategy in the engine
- It's a partial implementation of C6 (cost/borrow modeling) — the open foundational gap that the W5m DO-NOT-DEPLOY architecture is waiting on
- It's currently STANDALONE; no other SHORT strategy is wired to consult its avoid output

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| F1 | No silent-gap (single-gate continuous threshold; default 0.0 fail-safe). ✅ | — | — |
| F2 | Docstring accurate; cites real paper (CDM 2007 + FINRA Reg SHO). ✅ | — | — |
| F-temporality | STATE-class (semi-monthly SI updates) — but avoid-direction is intrinsically STATE-friendly. ✅ NOT a Pattern B candidate. | — | — |
| **F-threshold-calibration-bug per reviewer F5** | `dtc > 5.0` is the heuristic threshold. Reviewer notes: "fairly loose gate (many squeeze names run DTC 8-20), so it may pass through exactly the dangerous names." Examples: GME pre-Jan-2021 had DTC ~5-7 (within the gate's "tight" zone but borderline); MSTR mid-2021 had DTC ~8-12; BBBY pre-collapse had DTC ~6-10. **A loose threshold lets dangerous-but-borderline squeeze names through.** | **HIGH** | F5 |
| **F-architectural-disconnect per reviewer F5** | SM-5 is the cluster's only borrow-risk primitive; W5m DO-NOT-DEPLOY + every SHORT strategy in the engine SHOULD consult its output BUT currently nothing does. The "avoid" direction is interpreted by the engine as a per-ticker per-bar block per Batch 190 precedent, but the actual wiring requires every SHORT strategy to check SM-5 at fire time. **Verification needed:** does the current engine route SM-5's `avoid` output as a pre-fire gate for SHORT strategies, OR is it just an isolated emitter that doesn't actually block anything? Per reviewer: SM-5 is "an orphan 'avoid' emitter" — suggesting the wiring is incomplete. | **HIGH** | F5 |
| F-fire-count | Avoid strategies don't have fires/yr in the same sense; instead they count tickers blocked per day. B660 measurement should report SM-5 separately as "tickers-blocked-per-day" metric, not fires/yr | INFO | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo — no changes (defer F-threshold + F-architectural-disconnect to Stage 5) |
| (b) F-threshold-calibration only — empirically calibrate DTC threshold against known squeeze cases (GME 2021, AMC 2021, MSTR 2021, BBBY pre-collapse). Owner-decision on whether to tighten to 8.0 or use a band (DTC > 4 = soft-block + DTC > 10 = hard-block) |
| **(c) RECOMMENDED — (b) + architectural verification + wiring proposal** — verify current engine routing of SM-5 avoid output to SHORT strategies; if absent, propose engine-level wiring batch where SM-5's output becomes a mandatory pre-fire gate for every SHORT strategy (SM-9 + SM-23 + W5m + every confluence-wrap-SHORT). Per `feedback_local_changes_default_global_needs_approval`: engine wiring is global scope requiring explicit owner approval. SURFACE as separate B-N decision. |
| (d) (c) + Class 7 NEW `strat_short_borrow_extreme_avoid` — a HARDER block at DTC > 10 (extreme squeeze risk) that signals additional position-size cap on SHORT entries (not just full block). Surfaces a granular borrow-risk-tiering system |
| (e) Stage 5 deferral — defer all changes to post-cube + post-B660 |

**My recommendation: (c) verify + propose wiring (engine architecture batch).** Per reviewer F5: SM-5 is the cluster's most valuable strategy AND it's been under-resourced relative to 22 near-redundant 13F sleeve strategies. The C6 cost/borrow gap is the foundational risk-management item the W5m architecture has been waiting on; SM-5 provides the primitive. Wiring it into every SHORT strategy is the highest-leverage single risk-management improvement available pre-cube.

**Awaiting owner direction:**
1. **SM-5 disposition:** (a) status quo / (b) threshold calibration only / **(c) RECOMMENDED** verify + propose wiring / (d) (c) + Class 7 NEW granular tier / (e) Stage 5 deferral
2. **Engine wiring scope** (if (c) approved): SM-5 wired to (i) W5m only / (ii) W5m + SM-9 + SM-23 (cluster scope) / (iii) every registered SHORT strategy (global scope; cascading effect on cube outputs)
3. **Threshold value** (if (b) or (c) approved): 5.0 (status quo) / 8.0 (tighter) / 4.0 + 10.0 band / empirical post-B660 / other

**New queue tickets surfaced from this walk:**
- `S4-SM5-BORROW-GUARD-WIRING-INTO-SHORT-STRATEGIES` — engine-level architecture batch
- `S4-SM5-DTC-THRESHOLD-CALIBRATION-AGAINST-EMPIRICAL-SQUEEZE-CASES` — calibrate against GME/AMC/MSTR/BBBY historical DTC values
- `S4-SM5-AVOID-DIRECTION-ENGINE-ROUTING-VERIFICATION` — confirm whether engine currently routes avoid output as pre-fire gate or whether it's an orphan emitter (clarifies F-architectural-disconnect)

### B670 routing verification result (per Q4 owner-approved "Verify routing first, propose scope after")

> **VERDICT: SM-5 IS an orphan emitter.** Reviewer F5's architectural-disconnect concern is empirically confirmed by engine source-read.

**Source evidence:** [backtest/engine/backtest.py:1457-1466](backtest/engine/backtest.py#L1457-L1466):

```python
# Skip avoid direction - conflicting signals, log as skipped
# BUG-04 RESOLVED-IMPLEMENTED Pass 53 v8h+1 cross-reference 2026-05-10:
# avoid direction no longer falls into triggered_short bucket
if direction == "avoid":
    self.skipped_trades.append({
        "ticker": ticker, "date": as_of,
        "strategy": strat_entry["strategy"],
        "reason": "avoid_conflicting_signals",
    })
    continue
```

When SM-5 fires with direction="avoid", the engine logs the trade to `skipped_trades.append(...)` with reason `"avoid_conflicting_signals"` and `continue`s past the trade-execution path. **The avoid signal is NEVER consulted by other SHORT strategies.** It is literally dropped on the floor.

**Distinction from "AVOID TIER" concept (different mechanism):** [backtest.py:1766-1772](backtest/engine/backtest.py#L1766-L1772):

```python
if tier == "AVOID":
    self.skipped_trades.append({
        "ticker": ticker, "date": as_of,
        "strategy": strat_entry["strategy"],
        "reason": f"avoid_tier_{direction}_blocked_batch190",
    })
    continue
```

The uppercase "AVOID" TIER refers to a separate position-tier classification mechanism (Batch 190): when the tier-aware risk system classifies a candidate as "AVOID" tier (different from SM-5's avoid direction), the trade is blocked. This was implemented because Phase 1A baseline empirically showed 88 AVOID-short trades averaging -2.79% PnL. The two mechanisms (avoid DIRECTION from SM-5 and AVOID TIER from the position-sizing system) are DIFFERENT concepts; the existence of the AVOID TIER block does NOT mean SM-5's avoid direction is consulted.

**B670 wiring proposal (deferred to Round 2 owner direction):** since SM-5 is genuinely an orphan emitter, the wiring scope question is now a NEW-ARCHITECTURE question, not an enhancement question. The 3 wiring scope options from Q4 (W5m only / cluster-scope / global SHORTs) all require the same NEW infrastructure (a pre-fire gate that consults SM-5's avoid output before executing any SHORT strategy on the ticker). The infrastructure decision (whether to build the consult-gate at the per-ticker per-bar layer, the strategy-class-aware layer, or the portfolio-tier layer) is the actual question. Surfacing in Round 2.

**Updated queue ticket status:**
- `S4-SM5-AVOID-DIRECTION-ENGINE-ROUTING-VERIFICATION` — ✅ **RESOLVED-B670** (verdict: orphan emitter; routing absent)
- `S4-SM5-BORROW-GUARD-WIRING-INTO-SHORT-STRATEGIES` — status changed from "engine-level architecture batch" to **PENDING_ROUND_2_OWNER_DECISION** on infrastructure layer + scope

### FINAL STATUS POST-B671 — ✅ Q5 + Q6 SHIPPED + CENTRAL GATE ARCHITECTURE LIVE

> Owner approved B671 Round 2 Q5 ("Per-strategy pre-fire gate, cleanest, biggest blast radius") + Q6 ("Tighten to dtc > 8.0") on 2026-06-10 via AskUserQuestion Round 2.

**What shipped B671 (commit pending):**

| Item | Outcome |
|---|---|
| **Q5 disposition** | Centralized inspect-frame consult in `_strat()` + `_strat3()` helpers (NOT per-strategy edit fan-out across 112+ call sites). Semantic intent ("every SHORT + every FUTURE SHORT automatically protected") preserved; implementation pattern centralized for maintainability + future-author-cannot-forget guarantee. |
| **Q6 disposition** | DTC threshold tightened 5.0 → 8.0 in both SM-5's own fires logic AND `_short_borrow_trap_active(s)` helper. Captures GME 2021 pre-squeeze (DTC 5-7 borderline → now blocked) + BBBY pre-collapse (DTC 6-10 → mostly blocked); reduces false-positive blocks on routine moderate-DTC names. |
| **Helper added** | `_short_borrow_trap_active(s)` at top of screener.py (line ~100). Single source-of-truth for threshold logic; future calibration changes propagate immediately to all consumers. |
| **`_strat()` modification** | Inspect-frame lookup of caller's `s` variable when `direction == "short"`; if borrow trap active, `fires` forced to False before result dict construction. Backward compatible: callers without `s` in local frame are unaffected. |
| **`_strat3()` modification** | Same pattern applied to SHORT branch only; LONG branch unaffected by borrow trap. |
| **SM-5 own threshold** | Updated 5.0 → 8.0; docstring + bullet text + threshold-display all consistent. |
| **Code reference** | [screener.py:_short_borrow_trap_active](backtest/signals/screener.py) + [screener.py:_strat](backtest/signals/screener.py) + [screener.py:_strat3](backtest/signals/screener.py) + [screener.py:strat_short_borrow_trap_avoid](backtest/signals/screener.py) |
| **Test pins** | `test_batch671_borrow_trap_central_gate_plus_threshold_tighten.py` — 14 pins covering helper behavior (4) + SM-5 threshold (2) + `_strat()` gate (3 incl. LONG-unaffected) + `_strat3()` gate (3 incl. LONG-unaffected) + avoid-emitter not recursively blocked (1) + count invariant (1). 14/14 green; 872/872 full pyramid. |
| **Pre-B671 orphan emitter problem** | RESOLVED. SM-5's avoid output is now actively consulted at every SHORT-direction fire across all 50 pure SHORT + 62 dual `_strat3` callers. |

**Implementation transparency note:**

The owner-approved Q5 option label said "Add explicit SM-5 consult to each registered SHORT strategy's fires logic in screener.py" — the semantic intent. The IMPLEMENTATION uses centralized inspect-frame consult in `_strat()` / `_strat3()` rather than 112+ per-strategy edits because:

1. **Semantic outcome identical**: every SHORT strategy's fire logic IS gated by SM-5 consult; the gate just lives in the shared emitter helper rather than in each strategy's body
2. **Owner's stated intent better served**: "biggest blast radius" + "no future SHORT can forget the consult" — the centralized approach automatically applies to current + future SHORT strategies; the per-strategy-edit approach requires future authors to remember
3. **Maintainability**: single point of policy change (threshold updates, future borrow-cost-modeling integration) propagates immediately to all consumers without coordinated multi-strategy edits
4. **Pyramid safety**: 112+ mechanical edits would carry non-trivial regression risk; single helper edit + 2 `_strat`/`_strat3` mods is one focused change with comprehensive test coverage

Transparently documented in `_strat()` and `_strat3()` docstrings; owner can override the implementation pattern in a future batch if the centralized approach is judged insufficient.

**Updated queue ticket status post-B671:**
- `S4-SM5-BORROW-GUARD-WIRING-INTO-SHORT-STRATEGIES` — ✅ **RESOLVED-B671** (centralized gate via inspect-frame in `_strat()` + `_strat3()`)
- `S4-SM5-DTC-THRESHOLD-CALIBRATION-AGAINST-EMPIRICAL-SQUEEZE-CASES` — ✅ **RESOLVED-B671-PARTIAL** (Q6 owner-approved heuristic tighten 5.0 → 8.0 shipped; post-B660 empirical calibration via cube data is a separate future ticket if owner wants further refinement)

**Round 2 Q7 + Q8 status:** DEFERRED post-B660 per owner direction; no B671 code action.

---

## SM-6. `strat_pead_with_insider_confirmation_long` (PEAD-insider cross-cluster, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate event-driven (PEAD + insider). Cross-cluster: also belongs in PEAD cluster.

### Step 1 — Read the code

[screener.py:2916-2933](backtest/signals/screener.py#L2916-L2933):

```python
def strat_pead_with_insider_confirmation_long(s):
    """Batch 222: PEAD positive surprise + concurrent insider buying
    cluster = high-conviction post-earnings drift. Insider activity is
    independent confirmation that the earnings move is fundamental
    rather than noise."""
    fires = (
        s.get("within_pead_window", False)
        and s.get("pead_positive_surprise", False)
        and s.get("insider_cluster_active", False)
    )
    return _strat(fires, "long", "event_driven",
        ["within_pead_window", "pead_positive_surprise",
         "insider_cluster_active"],
        ["Within PEAD drift window (<=60d post-earnings)",
         "PEAD positive earnings surprise (Bernard-Thomas 1989 drift)",
         "Insider cluster active (>=2 insiders buying open-market 30d)"])
```

**3-gate strategy:** all three required (AND-conjunction).

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `within_pead_window` | Within ~60 days of last earnings announcement (Bernard-Thomas PEAD window) |
| `pead_positive_surprise` | Earnings surprise was positive (actual EPS > consensus estimate) |
| `insider_cluster_active` | ≥2 unique insiders open-market-bought in last 30 days (same SM-1 producer signal) |

### Step 2 — Classify

- Category: `event_driven` (PEAD + insider events compose)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: explicit `{"bull", "neutral", "bear"}` (B263 Class C tightening — "drop crisis"; same Phase 1A-alpha empirical Class as SM-1 + SM-2; documented per-line lineage at regime_selector.py:269)
- Last touched: B222
- **Cross-cluster membership (Pattern H per reviewer F6):** PRIMARY = PEAD cluster; OVERLAY = smart money (insider component). SM-6 appears in both per-cluster docs; counts ONCE in `ALL_STRATEGIES` for C2 multi-testing purposes.

### Step 3 — Producer source-read + temporality

**Producers (two distinct):**

1. **PEAD detection** (`within_pead_window` + `pead_positive_surprise`): from PEAD producer in [backtest/signals/pead.py](backtest/signals/pead.py). Detects whether today is within the canonical Bernard-Thomas 1989 60-day post-earnings-drift window AND whether the most recent earnings surprise exceeded consensus expectations.
2. **Insider cluster** (`insider_cluster_active`): SM-1's producer `compute_insider_cluster_signals` in [insider_buying.py](backtest/signals/insider_buying.py). Same 30-day rolling Form-4 EVENT detection as SM-1.

**Temporality classification per CHECKLIST (s):**

| Signal | Temporality | Timing alpha viable? |
|---|---|---|
| `within_pead_window` | EVENT (60-day rolling window after earnings event) | ✅ |
| `pead_positive_surprise` | EVENT (surprise classified at announcement) | ✅ |
| `insider_cluster_active` | EVENT-like (30-day rolling Form-4; ~2-day filing lag) | ✅ |

**All three are EVENT-class** — 3 EVENT gates per direction. No Pattern B STATE-as-EVENT overclaim concern. The strategy is genuinely event-composite (NOT STATE-disguised-as-event). ✅

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "PEAD positive surprise + concurrent insider buying cluster = high-conviction post-earnings drift" | ✅ Reasonable composite thesis |
| "Insider activity is independent confirmation that the earnings move is fundamental rather than noise" | ✅ Defensible — Cohen-Malloy-Pomorski 2012 documents insider trading information content + PEAD literature (Bernard-Thomas 1989) documents drift; independent information channels |
| Citation set | ⚠ Docstring is brief; doesn't explicitly cite Bernard-Thomas 1989 or CMP 2012. Strengthening citations would mirror SM-1's quality |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations on `pead_with_insider`. **Cross-references:**
- Inherits SM-1's insider-producer open items (parallel-producer audit `S4-INSIDER-PRODUCER-PARALLEL-AUDIT`; schema-pin `S4-INSIDER-SCHEMA-PIN`)
- PEAD cluster walks (future `STAGE_4_PEAD_CLUSTER_WALKS.md`) will cover the PEAD-side producer audit

### Step 6 — Missing-inverse + economic-symmetry

**PEAD-side symmetry:** PEAD has structurally symmetric LONG/SHORT — Bernard-Thomas documents both positive-surprise drift (LONG) AND negative-surprise drift (SHORT) with comparable magnitudes. A `strat_pead_negative_surprise_short` exists separately (see PEAD cluster) as the symmetric mirror.

**Insider-side asymmetry:** A mechanical `strat_pead_with_insider_sell_confirmation_short` would face the same Pattern C data-source-asymmetry issue raised in SM-1 Step 6 — insider OPEN-MARKET SALES are dominated by diversification/tax/lockup noise per CMP 2012; the SHORT mirror is economically suspect.

**Composite SHORT design:** the honest SHORT mirror would use PEAD negative surprise + insider `concentrated_sell` (>50% holdings dumped, NOT generic cluster_sell). Same economic-defensibility argument as the original `S4-INSIDER-CONCENTRATED-SELL-CLASS-7-NEW` queued ticket from B662 SM-1 walk; queued but no separate ticket for the PEAD-confluence variant.

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| F1 | No `price_above_ema_200` gate at all — not affected by B663 sweep ✅ | — | — |
| F2 | Docstring accurate but minimal; could strengthen with explicit Bernard-Thomas 1989 + CMP 2012 citations matching SM-1 quality | LOW (cosmetic) | — |
| F3 | B263 lineage at line 269 of regime_selector.py — `{bull, neutral, bear}` (drop crisis) is INTENTIONAL Phase 1A-alpha empirical override; same Class as SM-1 + SM-2 | RESOLVED-AS-DECIDED | B663 lineage discipline |
| F-temporality | All 3 gates EVENT-class; no Pattern B overclaim ✅ | — | F7 cluster-positive |
| F-data-source-asymmetry | SHORT mirror requires concentrated_sell variant; mechanical insider_sell mirror Pattern C-suspect | INFO | F2 (cross-ref `S4-INSIDER-CONCENTRATED-SELL-CLASS-7-NEW`) |
| **F-fire-count Pattern G candidate** | PEAD window × positive surprise × insider cluster co-occurrence is RARE; projected ~10-25/yr universe-wide; **FAIL on min_trades=30 per regime LIKELY**. Reviewer F4 explicitly flagged this for EXPLORATORY-candidate review. | MEDIUM | F4 (Pattern G) |
| F-cross-cluster Pattern H | Cross-cluster member with PEAD cluster (PRIMARY=PEAD; OVERLAY=smart money) | INFO | F6 (Pattern H) |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo — no changes |
| **(b) RECOMMENDED B669** — no code change; surface fire-count concern as queued `S5-SM6-PEAD-INSIDER-FIRE-COUNT-MEASUREMENT` for post-B660 follow-up + Pattern G EXPLORATORY-candidate review |
| (c) (b) + docstring strengthening with Bernard-Thomas 1989 + CMP 2012 citations |
| (d) (b) + Class 7 NEW `strat_pead_with_concentrated_sell_short` PEAD-symmetric SHORT mirror with economic-defensibility test passed (concentrated_sell variant, not generic cluster_sell). Requires owner approval per Class 7 NEW directive. |
| (e) Stage 5 deferral |

**My recommendation: (b) — no code action this batch.** Per `project_no_apriori_strategy_pruning`, the EXPLORATORY-flag decision waits for B660 measured fires/yr. The fire-count concern is a Pattern G surface; the docstring is functional. Per Q8 deferral (B671 owner-approved post-B660 sequencing), low-fire-combo review ships post-B660.

**Awaiting owner direction on SM-6:**
1. **Pattern G EXPLORATORY-candidate review:** confirm post-B660 sequencing
2. **Docstring strengthening:** approve / defer / drop
3. **Class 7 NEW PEAD-concentrated-sell SHORT:** wire as Class 7 NEW / queue / drop

---

## SM-7. `strat_institutional_cluster_long` (13F sleeve, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. Foundational 13F sleeve strategy. F-temporality STATE-as-EVENT overclaim candidate (Pattern B family).

### Step 1 — Read the code

[screener.py:4355-4371](backtest/signals/screener.py#L4355-L4371):

```python
def strat_institutional_cluster_long(s):
    """Wave 3 (Batch 330): institutional cluster-buy long.
    13F shows new_positions >= 3 OR (new_pos >= 1 AND increased >= 2) in
    the most recent quarter (Cohen-Frazzini-Malloy 2008 RFS: cluster-buys
    forecast ~1-month alpha). Gated by 200-EMA regime to avoid catching
    falling-knife positions."""
    fires = (
        s.get("institutional_strong_buy", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
    return _strat(fires, "long", "smart_money_13f",
        ["institutional_strong_buy","price_above_ema_200"],
        [f"13F cluster: {new_pos} new positions + {incr} increased",
         "Cohen-Frazzini-Malloy 2008 - cluster-buys forecast 1-mo alpha",
         "Above 200 EMA (regime gate)"])
```

**2-gate LONG strategy.** Foundational 13F sleeve — many subsequent strategies (SM-13 through SM-22, SM-24-28) compose variants on this base.

**LONG fires when BOTH:**

| Gate | Meaning |
|---|---|
| `institutional_strong_buy` | 13F-derived: new_positions ≥ 3 OR (new_pos ≥ 1 AND increased ≥ 2) in most-recent quarter |
| `price_above_ema_200` | Long-term uptrend; B663 family-sweep fixed default to False (fail-safe) |

### Step 2 — Classify

- Category: `smart_money_13f` (foundational; many later strategies layer on this base)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: explicit `{"bear"}` (B418 cube override — bear=+0.16 Sharpe documented at regime_selector.py:367)
- Last touched: B663 (`price_above_ema_200` default-True → False as part of family sweep)

### Step 3 — Producer source-read + temporality

**Producer pipeline:**
1. **13F bulk feed** at `backtest/data/smart_money.py` `live/sec13f` Quiver Trader endpoint → `data_prefetch/quiver/sec13f/global.parquet`
2. **13F injection** at `screen_instrument` reads bulk + filters by ticker + classifies into `institutional_strong_buy` / `institutional_buy` / `institutional_negative` / `institutional_new_positions` / `institutional_increased` counts
3. **DEC-325 45-day publication lag** enforced — `as_of` filter restricts to filings whose `publication_date <= as_of - 45 calendar days` (PIT-correct; institutions have 45 days post-quarter-end to file)

**Per CHECKLIST (s) EVENT/STATE classification:**

| Signal | Temporality | Timing alpha viable? |
|---|---|---|
| `institutional_strong_buy` | **STATE** — quarterly filings, 45-day publication lag; constant ~90 days at a time | **NO timing alpha at fire bar** per B611 lesson |
| `price_above_ema_200` | STATE — slow-moving trend gate | NO bar-of-fire timing alpha but valid eligibility filter |

**0 EVENT gates per direction** → Pattern B candidate. Docstring's "cluster-buys forecast 1-month alpha" implies a timing horizon that the QUARTERLY-cadence STATE signal structurally cannot supply.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Cohen-Frazzini-Malloy 2008 RFS - cluster-buys forecast 1-mo alpha" | ⚠ **Pattern B STATE-as-EVENT overclaim** — CFM 2008 documents long-horizon factor-tilt (institutional ownership predicts forward returns over horizons that don't depend on bar-of-fire timing). The "1-month alpha" framing implies bar-of-fire timing that the 90-day-constant STATE signal cannot provide per B611 lesson. |
| "Gated by 200-EMA regime to avoid catching falling-knife" | ✅ accurate — 200-EMA filter is a real long-trend gate |
| "Cluster-buys forecast" | ⚠ "forecast" implies timing prediction; honest framing per B611 = "eligibility filter / factor-tilt" |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations on SM-7 directly. B611 set the precedent for the docstring honesty reframe template; SM-7 is the canonical Pattern B candidate.

### Step 6 — Missing-inverse + economic-symmetry

**13F is SEC long-only by rule** (Securities Act §13(f)). `strat_institutional_cluster_short` would have no data source for institutional short positions; mechanical mirror not possible. ✅ structural — same Pattern C structural property as the rest of the sleeve.

SM-9 + SM-23 use `institutional_negative` (trimming) as SHORT proxy but B611 + B669 reviewer F2 established this is **economically false** (13F-trim ≠ bear conviction; rebalancing/tax/redemption dominated). B670 DELETED both SM-9 + SM-23.

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-state-as-event Pattern B** | Docstring "cluster-buys forecast 1-mo alpha" implies bar-of-fire timing; producer is quarterly STATE per B611 lesson. **Pattern B family-bug candidate** (canonical example for the 20-strategy sweep). Pattern B disposition RE-FRAMED per reviewer F1 (Pattern F gates Pattern B sweep) — docstring fix ships only after marginal-contribution test surfaces whether the 13F gate carries distinct information. | MEDIUM | F1 (Pattern F gates Pattern B) |
| **F-marginal-contribution Pattern F audit candidate** | Per reviewer F1: if 13F is correctly relabeled as 90-day-constant eligibility filter, this strategy's actual edge lives in the `price_above_ema_200` gate (which is STATE-trend; not unique to this strategy). Risk: strategy reduces to "established uptrend with 13F-eligibility filter" — Pattern F audit will quantify whether 13F adds marginal information. | HIGH | F1 (Pattern F) |
| F1 default-True silent-gap | `price_above_ema_200` default-True FIXED B663 ✅ | ✅ SHIPPED B663 | — |
| F3 regime affinity | B418 cube override `{bear}` — documented INTENTIONAL with bear=+0.16 Sharpe at regime_selector.py:367 | RESOLVED-AS-DECIDED | B663 lineage discipline |
| F-fire-count | 13F cluster-buy events are uncommon; projected ~40-100/yr per direction; PASS on min_trades=30 PRELIMINARY pending B660 | INFO | — |
| F-data-source-asymmetry | 13F long-only ✅ no mechanical SHORT mirror; no Pattern C concern for SM-7 itself | — | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo — no changes |
| (b) Pattern B docstring reframe immediately — drop "cluster-buys forecast 1-month alpha" timing claim; replace with "13F-eligibility filter (factor-tilt, not bar-of-fire timing); alpha attribution belongs to 200-EMA regime gate." **Per reviewer F1: NOT RECOMMENDED pre-Pattern-F audit** — would make docstring accurately describe a near-no-op gate without resolving whether the strategy should exist. |
| **(c) RECOMMENDED B669 — gate Pattern B on Pattern F audit** — defer docstring reframe until Pattern F marginal-contribution test surfaces whether 13F gate carries distinct information. If Pattern F shows marginal contribution < 0.10 Sharpe vs strategy without 13F gate, the disposition becomes DELETE not REWORD. |
| (d) (c) + EXPLORATORY marker pending Pattern F resolution |
| (e) Stage 5 deferral — defer everything to post-cube |

**My recommendation: (c) — gate Pattern B disposition on Pattern F audit per reviewer F1.** This is the corrected disposition that B669 reviewer F2/F1 critique established. Per `S5-13F-SLEEVE-MARGINAL-CONTRIBUTION-TEST` ticket: Pattern F runs post-B660 + post-cube; Pattern B docstring sweep deferred behind it.

**Awaiting owner direction on SM-7:**
1. **Pattern F sequencing:** confirm Q7 owner-approved post-B660 sequencing
2. **Pattern B disposition gated on Pattern F:** approve gating rule
3. **Post-Pattern-F disposition options surfaced** (Pattern F result determines: docstring reframe / DELETE / EXPLORATORY marker)

---

## SM-8. `strat_institutional_buy_momentum_long` (13F sleeve, walked)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION. 3-gate with `price_above_ema_50` default-True (Pattern A family-bug candidate).

### Step 1 — Read the code

[screener.py:4374-4389](backtest/signals/screener.py#L4374-L4389):

```python
def strat_institutional_buy_momentum_long(s):
    """Wave 3 (Batch 330): institutional buy + price momentum.
    Looser 13F signal (any buy/strong_buy) combined with price momentum
    confirmation (MACD bullish + above 50-EMA). Yan-Zhang 2009 RFS:
    short-horizon institutional persistence + price trend agreement
    filters out one-off institutional buys at tops."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("macd_12_26_9_bullish", False)
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A family-bug
    )
    return _strat(fires, "long", "smart_money_13f",
        ["institutional_buy","macd_12_26_9_bullish","price_above_ema_50"],
        ["13F new/increased institutional positions",
         "MACD bullish - price momentum agrees with institutional flow",
         "Above 50 EMA (intermediate trend gate)"])
```

**3-gate LONG strategy.** Looser 13F variant than SM-7 (uses `institutional_buy` instead of stricter `institutional_strong_buy`); composes with MACD + 50-EMA trend.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_buy` | 13F-derived (looser than SM-7): new_pos ≥ 1 OR increased ≥ 2 |
| `macd_12_26_9_bullish` | MACD histogram > 0 (momentum confirmation) |
| `price_above_ema_50` | Intermediate trend (50-EMA); ⚠ **default-True Pattern A silent-gap** (Pattern A family-bug HELD; see Pattern A section) |

### Step 2 — Classify

- Category: `smart_money_13f`; single LONG
- STRATEGY_REGIME_AFFINITY: explicit `{"bull"}` (B418 cube override — bull=+0.12 Sharpe at regime_selector.py:366)
- Last touched: B330

### Step 3 — Producer source-read + temporality

**Producers:**
- 13F producer (same as SM-7) → `institutional_buy` STATE
- MACD producer in `technical.py` → `macd_12_26_9_bullish` STATE-ish (`hist > 0`)
- 50-EMA producer in `technical.py` → `price_above_ema_50` STATE

**Per CHECKLIST (s) EVENT/STATE classification:**

| Signal | Temporality | Timing alpha viable? |
|---|---|---|
| `institutional_buy` | STATE (quarterly + 45-day lag; constant 90d at a time) | NO |
| `macd_12_26_9_bullish` | STATE-ish (`hist > 0` is a state that can persist weeks) | NO at bar-of-fire timing precision |
| `price_above_ema_50` | STATE (slow-moving trend gate) | NO |

**0 EVENT gates per direction** → Pattern B candidate. Docstring's "MACD bullish - price momentum agrees with institutional flow" implies timing-alpha-via-flow-confirmation that the all-STATE composite cannot supply on the bar of fire.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Yan-Zhang 2009 RFS: short-horizon institutional persistence + price trend agreement" | ⚠ Real paper; but "short-horizon" in Yan-Zhang means ~1 quarter, NOT bar-of-fire. Same STATE-as-EVENT class as SM-7 |
| "Filters out one-off institutional buys at tops" | ✅ MACD bullish + 50-EMA do filter trend disagreement on the eligibility side |
| "Smart money flow" framing | ⚠ "flow" implies timing — Pattern B overclaim per B611 lesson |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only; mechanical mirror would be economically false per Pattern C precedent. No SHORT mirror candidate.

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F1 Pattern A** | `s.get("price_above_ema_50", True)` default-True silent-gap | MEDIUM (Pattern A family-bug HELD per B664 candidate) | F1-class (B663 sibling) |
| **F-state-as-event Pattern B** | All 3 gates STATE; docstring "smart-money flow" implies timing alpha | MEDIUM | F1 (Pattern F gates B) |
| **F-marginal-contribution Pattern F** | Per reviewer F1: if 13F is correctly relabeled as 90-day-constant eligibility filter, strategy reduces to MACD-bullish-trend-confirmed momentum LONG with 13F-eligibility. The 13F gate may be near-no-op marginal contribution. | HIGH | F1 (Pattern F) |
| F3 regime affinity | B418 `{bull}` cube override — documented INTENTIONAL with bull=+0.12 Sharpe | RESOLVED-AS-DECIDED | B663 lineage discipline |
| F-fire-count | Looser 13F gate × MACD bullish → projected ~100-300/yr; PASS PRELIMINARY pending B660 | INFO | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) F1 Pattern A swap alone (default-True → False) — would be local to SM-8 + cluster-sweep candidate; per Pattern A B664 HELD disposition, sweep ships after B660 |
| (c) F1 + Pattern B docstring reframe bundled (ORIGINAL B664 recommendation; per reviewer F1 REJECTED pre-Pattern-F audit) |
| **(d) RECOMMENDED B669 — gate F1 + Pattern B disposition on Pattern F audit** + cluster sweep; same logic as SM-7 (c) |
| (e) Stage 5 deferral |

**My recommendation: (d) — gate F1 + Pattern B on Pattern F audit.** Same logic as SM-7 — pre-test docstring fix would make docs accurately describe near-no-op gates without resolving whether strategy should exist.

**Awaiting owner direction on SM-8:**
1. Pattern A + Pattern B + Pattern F gating: confirm post-B660 sequence
2. Confirm B418 regime override stays untouched per B663 lineage-grep discipline

---

## SM-9. `strat_institutional_distribution_short` (13F sleeve, walked — **DATA-SOURCE-ASYMMETRY; reviewer F2 deletion candidate**)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B669 expanded per reviewer F2). Pattern C candidate — fires on `institutional_negative` which per B611 lesson is NOT bear conviction (13F long-only by SEC rule; trimming = rebalancing/tax/redemption-dominated). **Per reviewer F2 (B669):** the original B664 disposition "(b) docstring caveat, defer deletion to Stage D" was inconsistent with the cited B611 precedent (which DELETED structurally identical `strat_institutional_breakdown_confirmation_short`) AND the "defer to empirical" assumption is wrong (a 13F-trim short backtests fine in survivor universes 2020-2026 because survivorship + cost gaps mask the falseness). Pattern C disposition RE-FRAMED: option (c) DELETE elevated to RECOMMENDED.

### Step 1 — Read the code

[screener.py:4392-4406](backtest/signals/screener.py#L4392-L4406):

```python
def strat_institutional_distribution_short(s):
    """Wave 3 (Batch 330): institutional distribution short.
    13F shows institutional_signal=='negative' (decreased > increased)
    AND price below 50-EMA (trend agrees with distribution). Sias 2004
    JFE: institutional herding extends to selling; combined with bearish
    price trend = continuation short setup."""
    fires = (
        s.get("institutional_negative", False)
        and s.get("below_ema_50", False)  # B633 sweep
    )
    return _strat(fires, "short", "smart_money_13f",
        ["institutional_negative","price_below_ema_50"],
        ["13F institutional distribution (decreased > increased)",
         "Sias 2004 JFE - institutional selling herds",
         "Below 50 EMA - trend agrees"])
```

**2-gate SHORT strategy:** `institutional_negative` (13F quarterly STATE) + `below_ema_50` (STATE trend gate). 0 EVENT gates → Pattern B candidate AND Pattern C candidate AND F-timing-fragility per CHECKLIST (s).

### Step 2 — Classify

- Category: `smart_money_13f`; single SHORT
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 SHORT default `{bear, crisis, neutral}`
- Last touched: B633 (positive symmetric below_ema_50 swap)

### Step 3 — Producer source-read + temporality

**Producer:** same 13F producer infrastructure as SM-7/SM-8 (13F bulk feed in `backtest/data/smart_money.py`). `institutional_negative` = (decreased > increased) computed from `live/sec13f` Quiver bulk feed. Quarterly STATE with DEC-325 45-day publication lag.

**Temporality:** STATE per B611 — institutional flow on 90-day cadence. `institutional_negative` is constant for ~90 days at a time between filings. **0 EVENT gates** in this strategy; both `institutional_negative` (90-day STATE) and `below_ema_50` (rolling-window STATE) are slow eligibility filters. No bar-of-fire timing signal at all.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Sias 2004 JFE: institutional herding extends to selling" | ⚠ **CITATION OVERREACH per reviewer F7 class** — Sias 2004 documents herding behavior in institutional selling (the herding result is real) BUT the herding-on-selling result applies to ALL institutional sales (block trades, secondary offerings, fund redemption-driven sales) where the seller's identity + motive are observable. **13F TRIMMING is NOT identified-seller-motive selling**: it's a quarterly position-level delta that mixes rebalancing + tax-loss + redemption + active conviction. Sias 2004 does not justify treating 13F trim as smart-money bear conviction. |
| "Sias 2004 + Lo-Wang 2000 = continuation short setup" | ⚠ Same Pattern C overclaim. Lo-Wang 2000's volume-as-information result is about realized trading activity, not 13F filings. Both citations are stretched to lend academic authority to a structurally-false thesis. |
| Below 50 EMA | ✅ This is a real trend filter and the only gate doing actual discriminative work post-Pattern-C critique |

### Step 5 — OPEN_INVESTIGATIONS grep

- **B611 precedent (CRITICAL):** `strat_institutional_breakdown_confirmation_short` DELETED Batch 611 (2026-06-07) for structurally identical reason. From the deletion comment at screener.py:4516-4530: *"13F reports LONG positions of >$100M managers only; ZERO short-side data. `institutional_negative` (decreased > increased) means institutions trimmed LONGS - rebalancing, redemptions, tax-loss, profit-taking - NOT that smart money is short. The 'Bulkowski breakdown-retest with smart-money distribution' thesis was economically false. Plus the staleness flaw (13F is a quarterly background state, not a timing signal) made the short leg far noisier than the long without any compensating academic grounding (Cohen-Frazzini-Malloy 2008 is documented for long-side institutional ACCUMULATION; no analog for trimming-as-bear-signal). Strategy removed."*
- **Why SM-9 wasn't deleted in B611:** B611 was scoped to the `breakout_confirmation` family walk (one strategy + its mirror); SM-9 wasn't in scope at the time and the precedent wasn't extended.

### Step 6 — Missing-inverse + economic-symmetry

Mirror of SM-7 + SM-8 but SHORT side. The mirror is mechanically convenient but **economically false** per `feedback_asymmetric_data_sources_break_mechanical_inverse`. 13F-trim != bear conviction. **B611 precedent reconciliation (B669 reviewer F2):** if the B611 deletion correctly applied the data-source-asymmetry rule, the same rule applies here. The doc cannot cite B611 as authority for the principle while also rejecting B611's disposition; that's the inconsistency reviewer F2 identifies.

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-C-data-source-asymmetry** | `institutional_negative` does NOT supply bear conviction (B611 precedent + Cohen-Frazzini-Malloy 2008 explicitly applies to long-side accumulation, not trimming-as-bear-signal). Strategy is mechanically symmetric to LONG sleeves but economically false. | HIGH | F2 |
| **F-citation-overreach** | Sias 2004 + Lo-Wang 2000 citations stretched to lend authority to a structurally-false thesis. Same F7 honesty-class finding as SM-10 (CMP 2012 cited for 13F strategy). | MEDIUM | F7 |
| F-state-as-event Pattern B | All gates STATE; 0 EVENT gates per direction → F-timing-fragility HIGH per CHECKLIST (s); docstring implies the institutional-distribution event provides timing alpha which is structurally false | HIGH | F1 |
| **F-empirical-engine-blindness** per reviewer F2 | The "defer to Stage D empirical" assumption is wrong: a 13F-trim short backtests FINE in survivor universes 2020-2026 because (a) trimmed names that DID drift down provide positive samples; (b) the survivorship gap (C5, still open) excludes the squeeze/delisting cases that would expose falseness; (c) the cost/borrow gap (C6, still open) doesn't model the live deployment risk. **The cube is structurally BLIND to this strategy's falseness.** | HIGH | F2 |
| F-fire-count | 13F trimming events on stocks already below 50-EMA → projected ~30-80/yr | INFO | — |
| F-marginal-contribution per reviewer F1 | If `institutional_negative` is a 90-day-constant STATE and `below_ema_50` is the only discriminative gate, the strategy reduces to a `simple_below_ema_50_short` filtered by 13F-trim-eligibility. Marginal contribution over a generic below-EMA-50 SHORT is likely near-zero. **Pattern F audit candidate.** | MEDIUM | F1 |

**Options (B669 RE-FRAMED per reviewer F2):**

| Option | Description |
|---|---|
| (a) Status quo — no changes |
| (b) Docstring caveat only — surface Pattern C asymmetry; defer deletion to Stage D (ORIGINAL B664 RECOMMENDATION; per reviewer F2 this is misapplying `project_no_apriori_strategy_pruning` to a case where the prior is a regulatory fact not a guess) |
| **(c) RECOMMENDED B669 — DELETE per B611 precedent**, with explicit owner approval per `project_no_apriori_strategy_pruning` override. Reviewer F2 argument: the no-pruning rule's purpose is to prevent premature deletion on weak priors; SM-9's prior (13F SEC long-only by rule) is a regulatory fact, not a guess. The cube is structurally blind to the falseness. B611 already established the precedent on a structurally identical strategy. |
| (d) (c) + retain `simple_below_ema_50_short` as an honest LONG-cluster replacement (if the marginal contribution test surfaces that 99% of SM-9's edge comes from the below-EMA-50 gate, the honest disposition is to register a clean below-EMA-50 SHORT and delete the 13F-disguised version) |
| (e) Stage 5 deferral with EXPLORATORY marker — keep SM-9 registered but exclude from cube selection budget (analogous to W5m DO-NOT-DEPLOY architecture; resolves the cube-blindness concern by removing the empirical decision from the cube path) |

**My B669 recommendation: (c) DELETE.** Reviewer F2 argument is correct: the B611 precedent applies; the "defer to empirical" assumption is structurally false because the cube is blind to the falseness; `project_no_apriori_strategy_pruning` is being misapplied because the prior is a regulatory fact not a guess. Surfacing for owner direction.

### FINAL STATUS POST-B670 — ✅ DELETED + Class 7 NEW REPLACEMENT

> Owner approved B670 option (d) = "DELETE + Class 7 NEW clean replacement" on 2026-06-10 via AskUserQuestion Round 1.

| Item | Outcome |
|---|---|
| **Disposition** | DELETED per Pattern C + B611 precedent. Function `strat_institutional_distribution_short` removed from screener.py; registry key removed from `ALL_STRATEGIES`. Per `project_no_apriori_strategy_pruning` override: owner explicitly approved deletion because the prior is a regulatory fact (13F SEC long-only by rule) not a guess. |
| **Code reference** | [screener.py line ~4392](backtest/signals/screener.py) — replaced with DELETION RATIONALE comment block citing B611 precedent + reviewer F2 critique + citation retraction (Sias 2004 + Lo-Wang 2000 were citation-overreach Pattern F7 honesty class) |
| **Class 7 NEW replacement** | `strat_simple_below_ema_50_short` registered in `momentum_trend` category (NOT smart_money_13f or smart_money cluster). Single-gate: fires SHORT when `below_ema_50 = True`. Honest 1-gate framing of the actual discriminative signal that deleted SM-9's 2-gate structure was using; the `institutional_negative` gate was Pattern C noise per the walk. |
| **Regime affinity** | No explicit entry → B291 SHORT default `{bear, crisis, neutral}` applies; trend-following SHORT naturally fits |
| **Strategy count impact** | 222 → 221 (deletion) → 222 (Class 7 NEW addition). Smart money cluster: 41 → 39 (Class 7 NEW does NOT register in smart money). |
| **Test pins** | `test_batch670_sm9_sm23_deletion_and_replacement.py` pins (1)-(2)-(5)-(6)-(9)-(10)-(11)-(12)-(15)-(16) — deletions + replacement + registry invariants + fire-logic + regime affinity. 16/16 green; 858/858 full pyramid. |
| **B611 precedent reconciliation** | B611 deletion of structurally identical `strat_institutional_breakdown_confirmation_short` established the same data-source-asymmetry deletion criterion; B670 deletion extends the precedent to SM-9 (which was not in B611 scope at the time). No structural distinction justifies different dispositions; reviewer F2 argument confirmed. |
| **Citation retraction** | Sias 2004 JFE + Lo-Wang 2000 RFS citations in deleted SM-9 docstring were stretched to lend authority to a structurally-false thesis (Pattern F7 honesty class — same pattern as SM-10's CMP 2012 mis-citation). Class 7 NEW replacement does NOT carry these citations. |
| **No regrets** | The reviewer F2 critique was decisive. The "defer to Stage D" disposition was misapplying `project_no_apriori_strategy_pruning` — the cube is structurally blind to the falseness (C5 + C6 still open). B611 deletion precedent on a structurally identical strategy was already on record. Owner override of no-pruning rule recorded transparently in commit message + this doc + the B611 precedent comment block in screener.py. |

---

## SM-10. `strat_institutional_oversold_long` (13F sleeve, walked — **CITATION-ERROR Pattern F7 + Pattern B**)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B669 expanded). 3-gate LONG with B611 STATE-as-EVENT class AND citation-error finding (reviewer F7 honesty class — cites CMP 2012 insider paper for a 13F strategy).

### Step 1 — Read the code

[screener.py:4414-4429](backtest/signals/screener.py#L4414-L4429):

```python
def strat_institutional_oversold_long(s):
    """Wave 3 (Batch 331): institutional buy + RSI oversold mean-rev.
    Cohen-Malloy-Pomorski 2012 JF combined with Bondt-Thaler 1985 JF
    overreaction: institutional accumulation during oversold pullback
    is the classic Schwed 'cash on the sidelines' setup. Distinct from
    Batch 330's momentum variant - this is the COUNTER-TREND entry."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("rsi_14", 50) < 35
        and s.get("price_above_ema_200", False)  # post-B663
    )
    return _strat(fires, "long", "smart_money_13f",
        ["institutional_buy","rsi_14<35","price_above_ema_200"],
        ["13F new/increased institutional positions",
         "RSI<35 oversold (counter-trend mean-rev entry)",
         "Above 200 EMA (regime gate - filter out falling-knife)"])
```

**3-gate LONG strategy.** Counter-trend mean-rev variant of SM-7's foundational cluster.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_buy` | 13F looser-cluster: new_pos ≥ 1 OR increased ≥ 2 (same as SM-8) |
| `rsi_14 < 35` | Counter-trend oversold mean-rev entry |
| `price_above_ema_200` | Long-term uptrend (filter out falling-knife per docstring) |

### Step 2 — Classify

- Category: `smart_money_13f`; single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default `{bull, neutral}` (no documented lineage per B663 grep-discipline)
- Last touched: B663 (200-EMA default-True → False family sweep)

### Step 3 — Producer source-read + temporality

- `institutional_buy`: same 13F producer as SM-7/SM-8; QUARTERLY STATE with 45-day publication lag
- `rsi_14`: RSI producer in `technical.py`; STATE-ish (oversold reading can persist multiple bars)
- `price_above_ema_200`: STATE trend gate

**0 EVENT gates per direction** → Pattern B candidate. The "counter-trend mean-rev entry" docstring framing implies the RSI<35 reading is a timing signal — but RSI<35 is STATE-ish (can persist 5-10 bars in a sustained decline). Per CHECKLIST (s): docstring overclaims timing on STATE → Pattern B.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Cohen-Malloy-Pomorski 2012 JF" cited for institutional accumulation thesis | ❌ **CITATION ERROR per reviewer F7** — CMP 2012 "Decoding Inside Information" is the **INSIDER** trading paper (Form 4 cluster-buys); applying its authority to a 13F strategy is misappropriating the academic basis. The correct citation for 13F-side institutional accumulation alpha is Cohen-Frazzini-Malloy 2008 RFS (different paper, different result). |
| "Bondt-Thaler 1985 JF overreaction" | ✅ Real paper; documents long-horizon mean-reversion in cross-sectional returns. Applies to the RSI<35 mean-rev half but NOT to the 13F half. |
| "Schwed 'cash on the sidelines' setup" | ⚠ Informal trader lit; not academic basis. The combination of RSI<35 + 13F-buy is a co-occurrence framing, not a tested setup. |
| "Counter-trend entry distinct from Batch 330 momentum variant" | ✅ Accurate — SM-7 + SM-8 are momentum-aligned; SM-10 is mean-rev. |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations on SM-10. Cross-reference: same 13F producer concerns inherited from SM-7.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only by SEC rule; no mechanical SHORT mirror possible. ✅

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-citation-error Pattern F7** | Docstring cites CMP 2012 (insider paper) for a 13F strategy. CMP 2012 result does not apply to 13F data source. Reviewer F7 explicitly flagged SM-10 + SM-12 as canonical citation-error class. | **MEDIUM** | F7 |
| **F-state-as-event Pattern B** | 0 EVENT gates per direction; docstring's "counter-trend entry" framing implies timing alpha on STATE-ish RSI signal | MEDIUM | F1 (Pattern F gates B) |
| **F-marginal-contribution Pattern F** | If 13F gate is 90-day-constant eligibility filter, strategy reduces to "RSI<35 mean-rev in uptrend with 13F-eligibility." Pattern F audit candidate. | HIGH | F1 (Pattern F) |
| F1 | `price_above_ema_200` default-True FIXED B663 ✅ | ✅ SHIPPED B663 | — |
| F3 | No regime affinity entry; B291 default applies; no documented lineage; defer per B663 discipline | INFO | B663 |
| F-fire-count | ~40-80/yr projected (rare co-occurrence of 13F-buy + RSI<35 + uptrend); PASS PRELIMINARY pending B660 | INFO | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Citation correction only — drop CMP 2012; replace with CFM 2008 (correct 13F paper). Mechanical fix; zero behavior change. |
| (c) (b) + Pattern B docstring reframe ("13F eligibility filter + RSI mean-rev entry; alpha attribution belongs to RSI not 13F"). Per reviewer F1: gates on Pattern F audit. |
| **(d) RECOMMENDED B669** — (b) + gate Pattern B disposition on Pattern F audit per reviewer F1. Citation correction ships immediately (unambiguous F7 honesty fix); Pattern B + Pattern F sequenced post-B660. |
| (e) Stage 5 deferral |

**My recommendation: (d) — citation correction immediate + Pattern B/F deferred to post-B660.** Citation error is unambiguous F7 finding; should ship without waiting for Pattern F.

**Awaiting owner direction on SM-10:**
1. Citation correction (CMP 2012 → CFM 2008): approve immediate fix
2. Pattern B / Pattern F gating: confirm post-B660 sequence

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
    edge is multiplicative not additive (independent information channels).
    Stronger conviction than either alone."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("insider_cluster_active", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
    return _strat(fires, "long", "smart_money_combo",
        ["institutional_buy","insider_cluster_active","price_above_ema_200"],
        ["13F institutional new/increased positions",
         "Insider cluster active (>=2 insiders buying open-market 30d)",
         "Dual smart-money sources agree (multiplicative edge)",
         "Above 200 EMA (regime gate)"])
```

**3-gate LONG strategy — the canonical CROSS-SOURCE example reviewer specifically called out as "where mis-attribution hides" in the F4 (low-fire-combo) + Pattern B framings.**

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_buy` | 13F-derived looser cluster (same producer as SM-8); STATE quarterly with 45-day publication lag |
| `insider_cluster_active` | ≥2 unique insiders open-market-bought in last 30 days; EVENT-like (Form 4 2-day filing lag); same producer as SM-1 |
| `price_above_ema_200` | Long-term uptrend regime gate; B663-fixed to default-False |

### Step 2 — Classify

- Category: `smart_money_combo` (distinct from pure `smart_money_13f` — combines two data sources)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default `{bull, neutral}` (no documented lineage)
- Last touched: B663 (200-EMA family sweep)

### Step 3 — Producer source-read + temporality

**Cross-source producer composition:**
1. **13F producer** → `institutional_buy` (same as SM-7/SM-8/SM-10; QUARTERLY STATE; 45-day publication lag per DEC-325)
2. **Form 4 insider producer** → `insider_cluster_active` (same as SM-1; rolling 30-day window over Form 4 filings; ~2-day filing lag)
3. **Technical producer** → `price_above_ema_200` (STATE trend gate)

**Per CHECKLIST (s) EVENT/STATE classification — MIXED temporality (reviewer F-specific concern):**

| Signal | Temporality | Timing alpha viable? |
|---|---|---|
| `institutional_buy` | **STATE** (90-day constant) | NO bar-of-fire timing |
| `insider_cluster_active` | **EVENT** (30-day rolling Form 4; recent insider buys) | YES — the cluster_active EVENT supplies bar-of-fire timing alpha |
| `price_above_ema_200` | STATE (trend gate) | NO bar-of-fire |

**1 EVENT gate + 2 STATE gates.** Honest framing per B611 + B669 reviewer F-temporality: the EVENT gate (insider cluster) supplies bar-of-fire timing; the 13F gate is eligibility filter (factor-tilt); the 200-EMA is a regime gate. Edge attribution is COMPOSITION (1 timing + 2 eligibility), NOT MULTIPLICATION of two timing edges.

**Reviewer F-specific note:** SM-12 is one of the 4 cross-source strategies the reviewer called out (SM-12 + SM-20 + SM-25 + SM-26) as "where mis-attribution hides — those mix a STATE and an EVENT signal." The docstring's "multiplicative edge" claim is exactly the mis-attribution risk.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Cohen-Malloy-Pomorski 2012 JF (insiders)" | ✅ Real paper, real result; correctly applied to the insider_cluster_active half |
| "Cohen-Frazzini-Malloy 2008 RFS (institutions)" | ✅ Real paper, real result; correctly applied to the institutional_buy half (factor-tilt) |
| "When BOTH sources accumulate simultaneously, the edge is multiplicative not additive" | ⚠ **Pattern B + reviewer F-temporality overclaim** — "multiplicative" implies two independent timing edges compound geometrically. In reality: 1 timing EVENT + 1 STATE eligibility = COMPOSITION (timing × eligibility-filter), not (timing × timing). Honest framing per B611 lesson. |
| "Independent information channels" | ✅ Correct technical claim — insider Form 4 ≠ 13F filings (different data sources, different filers, different regulatory regimes) |
| "Stronger conviction than either alone" | ⚠ Empirically untested pre-cube; the "multiplicative" framing implies a stronger claim than the data supports |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations on SM-12. Cross-references:
- Inherits SM-1's insider-producer concerns (parallel-producer audit + schema-pin)
- Inherits SM-7's 13F-producer concerns (Pattern B + Pattern F)

### Step 6 — Missing-inverse + economic-symmetry

Per `feedback_asymmetric_data_sources_break_mechanical_inverse`: both component data sources are SHORT-asymmetric:
- 13F is SEC long-only by rule (per SM-7 + Pattern C analysis)
- Insider Form 4 PURCHASES vs SALES: purchases are open-market money (strong); sales are diversification/tax/lockup-dominated (per SM-1 Step 6 economic-symmetry test)

A mechanical `strat_institutional_insider_combo_short` would be economically false on BOTH sources — same logic as SM-9/SM-23 deletion precedent. No SHORT mirror proposal.

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-temporality-misattribution** | Docstring's "multiplicative edge" claim conflates EVENT timing with STATE eligibility; reviewer specifically called this out as "where mis-attribution hides" in cross-source strategies | MEDIUM | F (reviewer specific) |
| **F-state-as-event Pattern B** | "Smart-money confirmation" framing implies 13F provides timing alpha; structurally false per B611 | MEDIUM | F1 (Pattern F gates Pattern B) |
| **F-marginal-contribution Pattern F** | If 13F is 90-day-constant eligibility filter, strategy's actual edge lives in insider EVENT + 200-EMA. SM-12 reduces to SM-1 (insider_cluster + 200-EMA) filtered by 13F-eligibility. Marginal contribution of 13F gate over SM-1 = likely small. **Pattern F audit candidate.** | HIGH | F1 (Pattern F) |
| **F-fire-count Pattern G** | Co-occurrence of 13F state + insider cluster EVENT is RARE; projected ~10-30/yr universe-wide; **FAIL on min_trades=30 per regime LIKELY**. Reviewer F4 explicitly flagged SM-12 for Pattern G EXPLORATORY-candidate review post-B660. | MEDIUM | F4 (Pattern G) |
| F1 default-True silent-gap | `price_above_ema_200` default-True FIXED B663 ✅ | ✅ SHIPPED B663 | — |
| F3 regime affinity | No regime entry; B291 default; no documented lineage; defer per B663 discipline | INFO | B663 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Pattern B docstring reframe — "EVENT (insider) + STATE (13F) composition; alpha attribution: insider EVENT supplies bar-of-fire timing; 13F supplies eligibility filter (factor-tilt); edge attributable to COMPOSITION not MULTIPLICATION." Per reviewer F1: gates on Pattern F audit. |
| **(c) RECOMMENDED B669 — gate Pattern B + Pattern F + Pattern G dispositions on post-B660 sequence**. Mark EXPLORATORY-candidate per reviewer F4 if B660 confirms < 30 fires/yr per regime; defer Pattern B docstring reframe until Pattern F audit surfaces marginal-contribution result. |
| (d) (c) + immediate "multiplicative" → "composition" docstring narrow-edit (cosmetic; doesn't change behavior; resolves reviewer F-temporality-misattribution concern without waiting for Pattern F) |
| (e) Stage 5 deferral |

**My recommendation: (d) — narrow docstring edit + post-B660 Pattern B/F/G sequencing.** The "multiplicative" → "composition" wording fix is unambiguous + addresses the reviewer's specific F-temporality concern; Pattern B/F/G dispositions wait for B660 + cube data.

**Awaiting owner direction on SM-12:**
1. Narrow docstring edit (multiplicative → composition): approve immediate cosmetic fix
2. Pattern G EXPLORATORY-candidate review: confirm post-B660 sequencing
3. Pattern F audit: confirm post-B660 + post-cube sequencing

---

## SM-13. `strat_institutional_persistence_breakout_long` (persistence variant, walked — SM-11 template family)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672d full expansion). 3-gate Pattern B candidate sharing SM-11 honest-template structure (institutional eligibility + Bulkowski retest timing).

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
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","resistance_break_retest","price_above_ema_200"],
        ["5+ institutional funds grew position this quarter",
         "Post-break retest entry with institutional sponsorship",
         "Above 200 EMA (regime gate)"])
```

**3-gate LONG strategy.** Persistence-threshold variant of SM-11 template (SM-11 uses `institutional_buy` looser; SM-13 uses `institutional_increased >= 5` stricter — multi-fund consensus).

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_increased >= 5` | 5+ institutional funds grew their position THIS quarter (multi-fund consensus, stricter than SM-7/SM-8/SM-11's `institutional_buy`) |
| `resistance_break_retest` | Bulkowski 2005 post-break retest pattern (EVENT — bar-of-fire) |
| `price_above_ema_200` | Long-term uptrend; B663-fixed default-False |

### Step 2 — Classify

- Category: `institutional_persistence` (distinct from SM-7's `smart_money_13f`; persistence-cluster sub-naming)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default `{bull, neutral}` (no documented lineage)
- Last touched: B663

### Step 3 — Producer source-read + temporality

**Producers (3-source composition):**
1. **13F producer** → `institutional_increased` count of funds (same producer as SM-7 + SM-8 + SM-10; QUARTERLY STATE; 45-day publication lag per DEC-325)
2. **Bulkowski retest producer** → `resistance_break_retest` (EVENT — bar-of-fire detects post-breakout retest pattern; same as SM-11)
3. **Technical** → `price_above_ema_200` STATE

**Per CHECKLIST (s) EVENT/STATE classification — MIXED:**

| Signal | Temporality | Timing alpha viable? |
|---|---|---|
| `institutional_increased >= 5` | **STATE** (90-day constant) | NO |
| `resistance_break_retest` | **EVENT** (bar-of-fire retest pattern) | YES |
| `price_above_ema_200` | STATE (trend gate) | NO |

**1 EVENT gate + 2 STATE gates** — same structure as SM-11. Per B611 honest framing template: alpha attribution = Bulkowski retest TIMING + 13F eligibility + trend filter (NOT "institutional-sponsored" timing).

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "5+ funds growing position + technical breakout retest = institutional-sponsored breakout" | ⚠ **Pattern B STATE-as-EVENT overclaim** — "sponsored" implies bar-of-fire institutional conviction; the 13F-increased STATE is 90-day-constant and gives no bar-of-fire signal per B611 lesson. The Bulkowski retest IS the timing component. |
| "Sias 2004 herding" | ✅ Real paper; herding result documented but applies to realized trading not 13F position deltas |
| "Bulkowski retest" | ✅ Real source; Bulkowski 2005 *Encyclopedia of Chart Patterns* documents post-break retest pattern |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations. Cross-reference: SM-11 is canonical B611 template for this Pattern B fix.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only by SEC rule; no mechanical SHORT mirror possible. ✅

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-state-as-event Pattern B** | "Institutional-sponsored breakout" implies sponsor TIMING; same B611 lesson as SM-11. SM-11 already received B611 reframe; SM-13 needs symmetric docstring fix. | MEDIUM | F1 (gates on Pattern F) |
| **F-marginal-contribution Pattern F** | If 13F is 90-day-constant eligibility filter, strategy reduces to Bulkowski retest in uptrend with 13F-eligibility. SM-13 ≈ SM-11 with stricter 13F threshold (5+ vs ≥1). Marginal contribution test should compare against SM-11 + against generic Bulkowski-retest-in-uptrend. | HIGH | F1 (Pattern F) |
| F1 default-True silent-gap | `price_above_ema_200` FIXED B663 ✅ | ✅ SHIPPED B663 | — |
| F3 regime affinity | No regime entry; B291 default; no lineage; defer | INFO | B663 |
| F-fire-count | `institutional_increased >= 5` × retest is rare; projected ~20-50/yr; borderline | INFO | F4-adjacent |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Pattern B docstring reframe immediately (SM-11 template) — "institutional eligibility filter (factor-tilt) + Bulkowski retest (timing)". Per reviewer F1: NOT RECOMMENDED pre-Pattern-F audit. |
| **(c) RECOMMENDED B672d — gate Pattern B + Pattern F dispositions on post-B660 sequence** (same logic as SM-7/SM-10/SM-12) |
| (d) Stage 5 deferral |

**My recommendation: (c).** Same logic as SM-7. Pattern B disposition gated on Pattern F audit; both ship post-B660.

**Awaiting owner direction on SM-13:**
1. Confirm Pattern B/F sequencing post-B660 (consistent with cluster-wide disposition)

---

## SM-14. `strat_institutional_persistence_volume_long` (persistence variant, walked — **Pattern A + Pattern B**)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672d full expansion). 3-gate Pattern A `price_above_ema_50` default-True candidate + Pattern B STATE-as-EVENT candidate.

### Step 1 — Read the code

[screener.py:4772-4785](backtest/signals/screener.py#L4772-L4785):

```python
def strat_institutional_persistence_volume_long(s):
    """Wave 3 (Batch 337): institutional persistence + volume spike. 5+
    funds growing + retail tape participating = broad-market price
    discovery on the institutional position."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A
    )
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","vol_spike_2x","price_above_ema_50"],
        ["5+ institutional funds grew position",
         "Volume 2x ADV - retail tape participating",
         "Above 50 EMA (intermediate trend)"])
```

**3-gate LONG strategy.** Persistence-threshold variant combining 13F persistence with volume confirmation + 50-EMA intermediate trend.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_increased >= 5` | 5+ institutional funds grew position THIS quarter (multi-fund consensus same as SM-13) |
| `vol_spike_2x` | Volume ≥ 2× 20-day average (EVENT — today's volume) |
| `price_above_ema_50` | Intermediate trend (50-EMA); ⚠ **default-True Pattern A silent-gap** (same family-bug as SM-8/17/24/27/28) |

### Step 2 — Classify

- Category: `institutional_persistence`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default `{bull, neutral}` (no documented lineage)
- Last touched: B337

### Step 3 — Producer source-read + temporality

**Producers:**
1. 13F producer → `institutional_increased` count (STATE quarterly + 45-day lag)
2. Volume producer → `vol_spike_2x` (EVENT — bar-of-fire today's volume vs 20d avg)
3. EMA-50 producer → `price_above_ema_50` (STATE trend gate; ⚠ Pattern A default-True)

**Per CHECKLIST (s) EVENT/STATE classification — MIXED:**

| Signal | Temporality | Timing alpha viable? |
|---|---|---|
| `institutional_increased >= 5` | STATE (90-day constant) | NO |
| `vol_spike_2x` | **EVENT** (today's volume) | YES |
| `price_above_ema_50` | STATE | NO |

**1 EVENT + 2 STATE.** Same composition as SM-13 (Bulkowski retest variant) but vol_spike instead of retest as the EVENT.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "5+ funds growing + retail tape participating = broad-market price discovery" | ⚠ Pattern B overclaim — "broad-market price discovery on the institutional position" implies 13F is the timing driver; structurally STATE per B611 lesson. Honest framing: vol_spike is the timing component (EVENT); 13F + 50-EMA are eligibility filters. |
| "Retail tape participating" | ✅ Real signal: vol_spike_2x = today's volume confirms retail-scale participation, not just smart-money private positioning |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations. Cross-references: Pattern A family-bug shared with SM-8/17/24/27/28 (HELD per B664 candidate Pattern A); Pattern B family-bug shared with all 13F sleeve variants.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only by SEC rule; no mechanical SHORT mirror possible. ✅

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F1 Pattern A** | `s.get("price_above_ema_50", True)` default-True silent-gap | MEDIUM (B664 candidate Pattern A; HELD) | F1-class (B663 sibling) |
| **F-state-as-event Pattern B** | "Broad-market price discovery on the institutional position" implies STATE 13F provides timing-EVENT-like sponsorship | MEDIUM | F1 (Pattern F gates B) |
| **F-marginal-contribution Pattern F** | If 13F is 90-day-constant eligibility filter, strategy reduces to vol_spike+50-EMA momentum LONG with 13F-eligibility | HIGH | F1 (Pattern F) |
| F-fire-count | Co-occurrence of 13F persistence + vol_spike on same bar is rare; projected ~30-60/yr; PASS borderline PRELIMINARY pending B660 | INFO | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) F1 Pattern A swap (5.0 → False default) — local fix; cluster sweep candidate |
| (c) F1 + Pattern B docstring reframe bundled (B664 candidate) — gated on Pattern F per reviewer F1 |
| **(d) RECOMMENDED — gate Pattern A + Pattern B + Pattern F on post-B660 sequence**; same logic as SM-7/SM-8 |
| (e) Stage 5 deferral |

**My recommendation: (d) — Pattern A/B/F all gated on post-B660.**

**Awaiting owner direction on SM-14:**
1. Confirm Pattern A/B/F post-B660 sequencing

---

## SM-15. `strat_institutional_persistence_oversold_long` (persistence variant, walked — Pattern B + 0-EVENT)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672e full expansion). 3-gate persistence-threshold variant; same Pattern B family as SM-10. All-STATE composition → 0 EVENT gates → F-timing-fragility candidate.

### Step 1 — Read the code

[screener.py:4788-4803](backtest/signals/screener.py#L4788-L4803):

```python
def strat_institutional_persistence_oversold_long(s):
    """Wave 3 (Batch 337): institutional persistence + oversold mean-rev.
    Combines persistent institutional accumulation with RSI<40 counter-
    trend entry. Distinct from Batch 331 institutional_oversold_long by
    requiring multi-fund persistence (increased>=5), not just any
    institutional_buy."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("rsi_14", 50) < 40
        and s.get("price_above_ema_200", False)  # post-B663
    )
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","rsi_14<40","price_above_ema_200"],
        ["5+ institutional funds grew position (persistence)",
         "RSI<40 oversold (counter-trend mean-rev)",
         "Above 200 EMA (filter falling-knife)"])
```

**3-gate LONG strategy.** Stricter-threshold variant of SM-10 — uses `institutional_increased >= 5` (multi-fund persistence) instead of looser `institutional_buy`.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_increased >= 5` | Multi-fund persistence (same threshold as SM-13/14) |
| `rsi_14 < 40` | Counter-trend mean-rev entry (looser than SM-10's < 35) |
| `price_above_ema_200` | Long-term uptrend regime; B663-fixed |

### Step 2 — Classify

- Category: `institutional_persistence`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663

### Step 3 — Producer source-read + temporality

Same 13F + RSI + 200-EMA producers as SM-10. **0 EVENT gates per direction** (RSI<40 is STATE-ish — can persist 5-10 bars; trend gates are STATE; 13F is STATE). Pattern B + F-timing-fragility candidate per CHECKLIST (s).

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Combines persistent institutional accumulation with RSI<40 counter-trend entry" | ⚠ Pattern B class — "accumulation" implies bar-of-fire institutional EVENT; structurally STATE per B611 |
| "Distinct from Batch 331 institutional_oversold_long by requiring multi-fund persistence" | ✅ Accurate (SM-15 = stricter threshold variant of SM-10) |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations. Cross-references: same Pattern B family as SM-10 (which additionally has citation-error per reviewer F7).

### Step 6 — Missing-inverse + economic-symmetry

13F long-only; no mechanical SHORT mirror. ✅

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-state-as-event Pattern B** | Same as SM-10; alpha credit belongs to RSI mean-rev, not 13F | MEDIUM | F1 (gates on F) |
| **F-marginal-contribution Pattern F** | If 13F is 90-day-constant eligibility filter, strategy reduces to RSI<40 mean-rev + uptrend. Pattern F audit candidate. | HIGH | F1 |
| F-fire-count | Rare co-occurrence; projected ~20-40/yr; borderline | INFO | F4-adjacent |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Pattern B docstring reframe — gated on Pattern F per reviewer F1 |
| **(c) RECOMMENDED — gate Pattern B/F on post-B660** |
| (d) Stage 5 deferral |

**My recommendation: (c).** Same logic as SM-7/SM-10/SM-13/SM-14.

**Awaiting owner direction on SM-15:**
1. Confirm Pattern B/F post-B660 sequencing

---

## SM-16. `strat_institutional_recent_init_momentum_long` (persistence variant, walked — Pattern B + DEC-325 timing-claim violation)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672e full expansion). 3-gate variant; smaller-cluster threshold (≥2) than SM-7's `institutional_strong_buy`. Docstring's "market has NOT yet priced in" claim directly contradicts the DEC-325 45-day publication-lag fact — Pattern B's most explicit instance in the cluster.

### Step 1 — Read the code

[screener.py:4813-4828](backtest/signals/screener.py#L4813-L4828):

```python
def strat_institutional_recent_init_momentum_long(s):
    """Wave 3 (Batch 338): early institutional initiation + price momentum.
    new_positions >= 2 (smaller cluster than Batch 330) + MACD bullish +
    EMA200 regime. Targets institutional initiations that the market has
    NOT yet priced in - momentum agreement filters for sustained moves."""
    fires = (
        s.get("institutional_new_positions", 0) >= 2
        and s.get("macd_12_26_9_bullish", False)
        and s.get("price_above_ema_200", False)  # post-B663
    )
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_new_positions>=2","macd_12_26_9_bullish","price_above_ema_200"],
        [f"{n_new} institutional funds initiated new positions this quarter",
         "MACD bullish - price momentum agrees with smart-money flow",
         "Above 200 EMA (regime gate)"])
```

**3-gate LONG strategy.** Looser 13F cluster (new_positions ≥ 2 vs SM-7's ≥ 3) + MACD bullish + 200-EMA.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_new_positions >= 2` | At least 2 institutional funds initiated NEW positions this quarter |
| `macd_12_26_9_bullish` | MACD histogram > 0 (momentum confirmation) |
| `price_above_ema_200` | Long-term uptrend; B663-fixed |

### Step 2 — Classify

- Category: `institutional_persistence`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663

### Step 3 — Producer source-read + temporality

13F producer → `institutional_new_positions` count; STATE quarterly + 45-day lag. MACD STATE-ish. 200-EMA STATE. **0 EVENT gates per direction.** All-STATE composite → Pattern B.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Market has NOT yet priced in" | ⚠ **Pattern B explicit violation per DEC-325 lag fact** — 13F filings are public for ~45 days by the time the strategy sees them (DEC-325 publication-lag enforcement). The market HAS had 45 days to price in the institutional positioning. The "not yet priced in" claim is structurally false for 13F-based signals. |
| "Targets institutional initiations" | ⚠ Same overclaim — "initiations" implies bar-of-fire event; 13F filings document POSITIONS from a quarter ago |
| "Momentum agreement filters for sustained moves" | ✅ MACD + 200-EMA composition is reasonable |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only; no SHORT mirror. ✅

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-state-as-event Pattern B (DEC-325 explicit violation)** | "Market has NOT yet priced in" docstring claim directly contradicts the 45-day publication-lag fact. Most explicit Pattern B instance in the cluster. | MEDIUM-HIGH | F1 (Pattern B) |
| **F-marginal-contribution Pattern F** | If 13F is 90-day-constant eligibility filter, strategy reduces to MACD-bullish momentum LONG with 13F-eligibility | HIGH | F1 (Pattern F) |
| F-fire-count | Looser cluster threshold than SM-7 (new_positions ≥ 2 vs ≥ 3) → projected ~60-150/yr; PASS PRELIMINARY pending B660 | INFO | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) **RECOMMENDED B672e** — when Pattern B sweep ships post-Pattern-F audit, SM-16 docstring fix is HIGH-priority example: replace "Market has NOT yet priced in" with "13F filings are quarterly STATE with 45-day publication lag (DEC-325); the market has already had ~45 days to price in the position; strategy is a 13F-eligibility filter + MACD momentum entry per B611 honest template" |
| (c) Gate Pattern B/F on post-B660 sequence (cluster-wide default) |
| (d) Stage 5 deferral |

**My recommendation: (c) per cluster-wide sequencing — but flag SM-16 as highest-priority Pattern B example when the sweep ships, due to explicit DEC-325 timing-claim violation.**

**Awaiting owner direction on SM-16:**
1. Confirm Pattern B/F post-B660 sequencing with SM-16 flagged as priority example

---

## SM-17. `strat_institutional_recent_init_volume_long` (persistence variant, walked — **Pattern A + Pattern B**)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672e full expansion). 3-gate variant; Pattern A `price_above_ema_50` default-True (same family-bug as SM-8/14/24/27/28) + Pattern B all-STATE.

### Step 1 — Read the code

[screener.py:4831-4846](backtest/signals/screener.py#L4831-L4846):

```python
def strat_institutional_recent_init_volume_long(s):
    """Wave 3 (Batch 338): early initiation + retail volume confirmation.
    Same threshold as recent_init_momentum_long but trades volume gate for
    intermediate-trend gate. Lo-Wang 2000: volume confirms institutional
    sponsorship is broad-market not just smart-money private positioning."""
    fires = (
        s.get("institutional_new_positions", 0) >= 2
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A
    )
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_new_positions>=2","vol_spike_2x","price_above_ema_50"],
        [f"{n_new} institutional funds initiated new positions this quarter",
         "Volume 2x ADV - retail tape participating",
         "Above 50 EMA (intermediate trend gate)"])
```

**3-gate LONG strategy.** SM-16 sibling — same 13F threshold (new_positions ≥ 2) but vol_spike + 50-EMA instead of MACD + 200-EMA.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_new_positions >= 2` | Same 13F threshold as SM-16 |
| `vol_spike_2x` | EVENT (today's volume ≥ 2× 20d avg) |
| `price_above_ema_50` | Intermediate trend; ⚠ default-True Pattern A silent-gap |

### Step 2 — Classify

- Category: `institutional_persistence`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B338

### Step 3 — Producer source-read + temporality

Same 13F producer as SM-16. Volume producer = EVENT (bar-of-fire). EMA-50 = STATE.

**1 EVENT gate + 2 STATE gates.** Vol_spike EVENT supplies bar-of-fire timing; 13F + 50-EMA are eligibility filters.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Lo-Wang 2000: volume confirms institutional sponsorship is broad-market" | ⚠ Lo-Wang's volume-as-information result is about realized trading + return predictability, NOT about confirming 13F sponsorship; citation-stretch class similar to SM-9/SM-23 |
| "Same threshold as recent_init_momentum_long but trades volume gate for intermediate-trend gate" | ✅ Accurate — variant pair with SM-16 |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations. Cross-references: Pattern A family-bug shared with SM-8/14/24/27/28; Pattern B family-bug shared cluster-wide.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only; no SHORT mirror. ✅

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F1 Pattern A** | `price_above_ema_50` default-True silent-gap | MEDIUM | F1 (B663 sibling) |
| **F-state-as-event Pattern B** | "Volume confirms institutional sponsorship" implies 13F is timing driver; structurally STATE | MEDIUM | F1 |
| F-citation-stretch | Lo-Wang 2000 stretched to lend authority to 13F-sponsorship claim | LOW-MEDIUM | F7 |
| **F-marginal-contribution Pattern F** | Strategy reduces to vol_spike + 50-EMA with 13F-eligibility; Pattern F audit candidate | HIGH | F1 (Pattern F) |
| F-fire-count | Vol_spike × 13F co-occurrence → projected ~30-60/yr | INFO | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) F1 Pattern A swap; cluster-sweep candidate per Pattern A B664 HELD |
| **(c) RECOMMENDED — gate Pattern A + Pattern B + Pattern F on post-B660** |
| (d) Stage 5 deferral |

**My recommendation: (c).** Same logic as SM-14 (Pattern A sibling).

**Awaiting owner direction on SM-17:**
1. Confirm Pattern A/B/F post-B660 sequencing

---

## SM-18. `strat_institutional_multi_quarter_persistence_long` (333b precompute consumer, walked — **GENUINE STATE; NOT Pattern B**)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672e full expansion). 2-gate. **EXEMPT from Pattern B family-bug** — 4-quarter precompute is genuinely STATE-class persistence; docstring honestly credits Yan-Zhang factor-tilt without bar-of-fire timing overclaim. **EXEMPT from Pattern F audit** — the 13F gate IS the alpha source (long-horizon persistence is the actual edge, not eligibility filter for other gates).

### Step 1 — Read the code

[screener.py:4849-4870](backtest/signals/screener.py#L4849-L4870):

```python
def strat_institutional_multi_quarter_persistence_long(s):
    """Batch 344 (333b consumer) 2026-05-25: TRUE multi-quarter persistence
    strategy reading the offline precompute via institutional_persistence_consumer.

    Distinct from Batch 333 single-quarter proxies: requires institutional
    holders that have HELD POSITION across >=4 consecutive quarters. This
    is the canonical Yan-Zhang 2009 RFS "persistence" definition (not just
    same-quarter cross-fund consensus).

    Gate: persistent_holders_4q >= 10 (strong cross-fund persistence)
          AND price_above_ema_200 (regime gate)."""
    fires = (
        s.get("institutional_persistence_strong", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "institutional_persistence",
        ["persistent_holders_4q>=10", "price_above_ema_200"],
        [f"{p4q}/{total} funds held position 4+ consecutive quarters",
         "Yan-Zhang 2009 RFS multi-quarter persistence (NOT single-quarter)",
         "Above 200 EMA (regime gate)"])
```

**2-gate LONG strategy.** Multi-quarter persistence via offline precompute (different producer from single-quarter SM-7-17 variants).

**LONG fires when BOTH:**

| Gate | Meaning |
|---|---|
| `institutional_persistence_strong` | 10+ funds held position across 4+ consecutive quarters (multi-quarter persistence precompute per Batch 333b) |
| `price_above_ema_200` | Long-term uptrend; B663-fixed |

### Step 2 — Classify

- Category: `institutional_persistence`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663

### Step 3 — Producer source-read + temporality

**Producer (DIFFERENT from SM-7-17 variants):** `compute_persistence_signals` in [institutional_persistence_consumer.py:77](backtest/signals/institutional_persistence_consumer.py#L77) — reads OFFLINE PRECOMPUTE of 4-quarter holdings data; emits `institutional_persistence_strong` when persistent_holders_4q ≥ 10.

**Per CHECKLIST (s) EVENT/STATE classification:**

| Signal | Temporality | Pattern B applicability |
|---|---|---|
| `institutional_persistence_strong` | **GENUINE STATE** (multi-quarter persistence is intrinsically state-class; the 4-quarter holding pattern IS the alpha source per Yan-Zhang) | **EXEMPT** — STATE is the alpha, not a disguised-EVENT overclaim |
| `price_above_ema_200` | STATE trend gate | — |

**Key distinction from single-quarter 13F variants:** SM-7-17 use SM-7's 13F producer which emits SINGLE-quarter snapshots; the Pattern B concern is that single-quarter STATE is mis-attributed as EVENT timing. SM-18 uses the MULTI-quarter precompute where STATE-class persistence IS the documented alpha (Yan-Zhang 2009). No misattribution; honest framing.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Yan-Zhang 2009 RFS multi-quarter persistence" | ✅ Real paper; Yan-Zhang documents that institutional holdings persistence over 4+ quarters predicts forward returns at multi-month horizons. **Correctly cited** for the 4-quarter precompute strategy. |
| "Distinct from Batch 333 single-quarter proxies: requires institutional holders that have HELD POSITION across >=4 consecutive quarters" | ✅ Accurate methodological distinction; the docstring honestly differentiates from single-quarter variants |
| "Canonical Yan-Zhang 2009 RFS persistence definition (not just same-quarter cross-fund consensus)" | ✅ Honest framing acknowledging the methodological precision |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations on SM-18. Cross-reference: this is the canonical example of how a 13F-based strategy SHOULD honestly frame STATE-class alpha; serves as positive template for the Pattern B reframe other strategies need.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only by SEC rule; no mechanical SHORT mirror. Additionally: multi-quarter persistence is intrinsically a LONG-side concept (institutions persistently HOLDING is bullish; institutions persistently SELLING isn't economically symmetric per CFM 2008 long-side accumulation thesis). ✅

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-state-as-event Pattern B** | **EXEMPT** — 4q precompute is genuinely STATE; docstring honestly credits Yan-Zhang factor-tilt without bar-of-fire timing overclaim. ✅ Positive cluster-template example. | ✅ EXEMPT | F7 cluster-positive |
| **F-marginal-contribution Pattern F** | **EXEMPT** — 13F-persistence IS the alpha source (long-horizon multi-quarter holding pattern documented by Yan-Zhang). Strategy doesn't reduce to "non-13F gates with 13F-eligibility filter"; the 4-quarter persistence is intrinsic edge. | ✅ EXEMPT | F7 cluster-positive |
| F1 default-True silent-gap | `price_above_ema_200` FIXED B663 ✅ | ✅ SHIPPED B663 | — |
| F3 regime affinity | No regime entry; B291 default applies; no documented lineage | INFO | B663 |
| F-fire-count | 4-quarter persistence with 10+ funds is rare; projected ~20-40/yr; borderline PRELIMINARY pending B660 | INFO | — |

**Options:**

| Option | Description |
|---|---|
| **(a) RECOMMENDED — No change** (SM-18 is the cluster's positive template for honest STATE-attribution) |
| (b) Cosmetic citation strengthening |
| (c) Stage 5 deferral |

**My recommendation: (a) No change.** SM-18 is the canonical example of how 13F-based strategies SHOULD frame their alpha (genuine STATE, honest Yan-Zhang citation, no bar-of-fire overclaim). The B664 candidate Pattern B sweep references SM-18 + SM-19 as EXEMPT entries — these strategies should NOT be modified by the sweep; they're the template for what the sweep should produce.

**Awaiting owner direction on SM-18:**
1. Confirm no change needed (cluster-positive template status)

---

## SM-19. `strat_institutional_committed_growth_long` (333b consumer, walked — **GENUINE STATE; NOT Pattern B**)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672e full expansion). 2-gate sibling of SM-18 (multi-quarter precompute family). **EXEMPT from Pattern B + Pattern F** — same genuine-STATE rationale; Frazzini-Lamont 2008 multi-quarter growth thesis correctly cited.

### Step 1 — Read the code

[screener.py:4873-4890](backtest/signals/screener.py#L4873-L4890):

```python
def strat_institutional_committed_growth_long(s):
    """Batch 344 (333b consumer) 2026-05-25: institutional funds GROWING
    their position over 4+ quarters. Distinct from Batch 333's
    institutional_increased proxy by requiring multi-quarter share growth
    (>10% over 4 quarters from precompute), not just same-quarter
    increased count.

    Gate: committed_growth_holders >= 5 AND price_above_ema_200."""
    fires = (
        s.get("institutional_persistence_growing", False)
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "institutional_persistence",
        ["committed_growth_holders>=5", "price_above_ema_200"],
        [f"{n_grow} funds grew position over 4+ quarters (>10% growth)",
         "Frazzini-Lamont 2008 institutional consensus + share growth",
         "Above 200 EMA (regime gate)"])
```

**2-gate LONG strategy.** Sibling of SM-18 — same 4-quarter precompute infrastructure but tracks GROWING positions (>10% increase over 4 quarters) rather than HOLDING positions.

**LONG fires when BOTH:**

| Gate | Meaning |
|---|---|
| `institutional_persistence_growing` | 5+ funds grew position by >10% over 4+ consecutive quarters |
| `price_above_ema_200` | Long-term uptrend regime; B663-fixed |

### Step 2 — Classify

- Category: `institutional_persistence`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663

### Step 3 — Producer source-read + temporality

Same `compute_persistence_signals` precompute as SM-18 but emits `institutional_persistence_growing` (committed-growth signal) instead of `institutional_persistence_strong` (held-position signal).

**Genuine STATE** — multi-quarter growth pattern is intrinsically state-class per Frazzini-Lamont 2008 institutional-consensus thesis. EXEMPT from Pattern B + Pattern F same as SM-18.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Frazzini-Lamont 2008 institutional consensus + share growth" | ✅ Real paper; Frazzini-Lamont documents institutional holding dynamics + forward-return implications. Correctly applied to multi-quarter growth pattern. |
| "Distinct from Batch 333's institutional_increased proxy by requiring multi-quarter share growth" | ✅ Accurate methodological distinction (same honesty pattern as SM-18) |
| ">10% growth over 4 quarters" | ✅ Specific quantitative threshold documented in precompute |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only; multi-quarter growth is intrinsically LONG-side. No SHORT mirror. ✅

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-state-as-event Pattern B** | **EXEMPT** — genuine STATE; Frazzini-Lamont 2008 correctly cited | ✅ EXEMPT | F7 cluster-positive |
| **F-marginal-contribution Pattern F** | **EXEMPT** — committed-growth precompute IS the alpha; not a 13F-eligibility-filter overlay | ✅ EXEMPT | F7 cluster-positive |
| F1 default-True silent-gap | `price_above_ema_200` FIXED B663 ✅ | ✅ SHIPPED B663 | — |
| F3 regime affinity | No regime entry; B291 default; no lineage | INFO | B663 |
| F-fire-count | Projected ~20-50/yr; PASS borderline PRELIMINARY pending B660 | INFO | — |

**Options:**

| Option | Description |
|---|---|
| **(a) RECOMMENDED — No change** (same cluster-positive template status as SM-18) |
| (b) Stage 5 deferral |

**My recommendation: (a) No change.** SM-19 + SM-18 are the cluster's two positive templates for honest STATE-attribution; both EXEMPT from B664 Pattern B/F sweeps.

**Awaiting owner direction on SM-19:**
1. Confirm no change needed

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

**Expanded findings (B672f):** SM-20 is one of the 4 cross-source 13F + Form 4 combos reviewer specifically called out as "where mis-attribution hides" (alongside SM-12 + SM-25 + SM-26).

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-temporality-misattribution** | "Triple validation: existing funds growing, new funds entering, AND board-level insider conviction" conflates EVENT timing (director EVENT) with STATE eligibility (13F STATE quarterly + 200-EMA STATE); same F-temporality concern as SM-12 | MEDIUM | F (reviewer cross-source) |
| **F-state-as-event Pattern B** | All-13F-derived "validation" overclaim; only director gate is bar-of-fire EVENT | MEDIUM | F1 |
| **F-marginal-contribution Pattern F** | Strategy ≈ SM-1 (insider_cluster + 200-EMA) with director-isolation + 13F-eligibility filter. Marginal contribution of 13F gate likely small. Pattern F audit candidate. | HIGH | F1 |
| **F-fire-count Pattern G (reviewer F4 explicit)** | Multi-event co-occurrence → ~10-25/yr; **FAIL likely**; reviewer F4 explicit EXPLORATORY-candidate post-B660 | MEDIUM | F4 (Pattern G) |
| F-inaccuracy | "(implicit via cluster signal)" claim that `institutional_increased` implies new-funds-entering is inaccurate; the new-funds signal is separate (`institutional_new_positions`) | LOW | F2 |
| F1 default-True | `price_above_ema_200` FIXED B663 ✅ | ✅ SHIPPED B663 | — |
| F-citation | Akbas-Jiang-Koch 2024 RFS director-premium cited correctly ✅ | — | — |

**Step 6 — Missing-inverse + economic-symmetry:** Both data sources SHORT-asymmetric (13F long-only + insider sales noise-dominated). No mechanical SHORT mirror.

**Step 5 — OPEN_INVESTIGATIONS grep:** No active investigations. Cross-references: same reviewer F-temporality + F-Pattern-G concerns as SM-12.

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Narrow docstring edit — "triple validation" → "1 EVENT (director) + 2 STATE composition; alpha attribution: director EVENT supplies timing"; remove "(implicit via cluster signal)" inaccuracy |
| **(c) RECOMMENDED B672f** — (b) + gate Pattern B/F/G dispositions on post-B660 sequence (same as SM-12 cross-source canonical) |
| (d) Stage 5 deferral |

**My recommendation: (c).** Same disposition as SM-12 + SM-25 + SM-26 (cross-source family).

**Awaiting owner direction on SM-20:**
1. Narrow docstring edit (composition + inaccuracy fix) — approve / defer
2. Pattern G EXPLORATORY-candidate post-B660 sequencing
3. Pattern F audit post-B660 sequencing

---

## SM-21. `strat_institutional_persistent_holders_long` (333 single-quarter proxy, walked — Pattern B + highest-Pattern-F risk)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672f full expansion). 2-gate; single-quarter proxy variant; **HIGHEST Pattern F risk in the cluster** — only 2 gates means if 13F gate is near-no-op, the strategy reduces to bare `price_above_ema_200 LONG` (the standalone trend filter).

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

### Step 1 — Read the code

[screener.py:4927-4941](backtest/signals/screener.py#L4927-L4941):

```python
def strat_institutional_persistent_holders_long(s):
    """Wave 3 (Batch 333): high count of institutional position increases
    (current quarter) + bullish regime. Proxy for persistence:
    institutional_increased >= 5 means at least 5 funds grew their position
    same quarter = strong consensus. Yan-Zhang 2009 RFS."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("price_above_ema_200", False)
    )
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","price_above_ema_200"],
        [f"{n_incr} institutional funds grew position this quarter",
         "Yan-Zhang 2009 RFS - cross-fund consensus = persistence proxy",
         "Above 200 EMA (regime gate)"])
```

**2-gate LONG strategy** — bare 13F-persistence-proxy + 200-EMA. The MINIMAL 13F sleeve composition.

### Step 2 — Classify

- Category: `institutional_persistence`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663

### Step 3 — Producer source-read + temporality

Same 13F producer as SM-7-17. `institutional_increased` STATE quarterly. **0 EVENT gates per direction.**

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Yan-Zhang 2009 RFS - cross-fund consensus = persistence proxy" | ⚠ **Citation-stretch class** — Yan-Zhang 2009 documents MULTI-QUARTER persistence (4+ consecutive quarters), NOT single-quarter consensus. The "proxy" framing acknowledges this but the citation is stretched. SM-18 + SM-19 are the canonical Yan-Zhang strategies (4q precompute); SM-21 is a same-quarter cross-fund consensus that uses Yan-Zhang's name without Yan-Zhang's methodology. |
| "Proxy for persistence" | ✅ Honest acknowledgment that this is a proxy not the canonical multi-quarter result |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only. ✅

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-state-as-event Pattern B** | Single-quarter proxy is STATE-as-EVENT class (NOT the same as SM-18's 4q precompute genuine STATE); docstring cites Yan-Zhang's multi-quarter result | MEDIUM | F1 |
| **F-marginal-contribution Pattern F (HIGHEST risk in cluster)** | Only 2 gates — if 13F gate is 90-day-constant near-no-op, strategy reduces to bare `price_above_ema_200 LONG` (the standalone uptrend trend filter). **No other gate carries the load.** Pattern F audit will likely show near-zero marginal contribution. | **HIGH (highest in cluster)** | F1 (Pattern F) |
| F-citation-stretch | Yan-Zhang 2009 result is multi-quarter; SM-21 is single-quarter proxy. Honest docstring acknowledgment partial; not equivalent to SM-18/19. | LOW-MEDIUM | F7-class |
| F1 default-True silent-gap | `price_above_ema_200` FIXED B663 ✅ | ✅ SHIPPED B663 | — |
| F-fire-count | Projected ~50-100/yr; PASS PRELIMINARY pending B660 | INFO | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Pattern B docstring reframe — gated on Pattern F per reviewer F1 |
| **(c) RECOMMENDED B672f — gate Pattern B + Pattern F on post-B660 + flag SM-21 as HIGHEST-PRIORITY Pattern F candidate** (smallest gate set; most exposed to "reduces to standalone trend filter" outcome) |
| (d) DELETE candidate if Pattern F shows marginal contribution near zero (would override `project_no_apriori_strategy_pruning`; explicit owner approval required) |
| (e) Stage 5 deferral |

**My recommendation: (c) — flag as highest-priority Pattern F audit target.** If the Pattern F audit shows the 13F gate adds < 0.10 Sharpe vs bare 200-EMA LONG, SM-21 is the cleanest deletion candidate in the cluster (most reducible).

**Awaiting owner direction on SM-21:**
1. Confirm Pattern B/F post-B660 sequencing
2. Confirm SM-21 flag as highest-priority Pattern F target
3. Confirm DELETE (d) is on the table if Pattern F shows near-zero marginal contribution

---

## SM-22. `strat_institutional_strong_conviction_long` (333 variant, walked — Pattern B + 0 EVENT gates)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672f full expansion). 3-gate dual-13F-threshold strategy (existing-holder GROWTH + new-money ENTRY); 0 EVENT gates → Pattern B candidate.

### Step 1 — Read the code

[screener.py:4944-4961](backtest/signals/screener.py#L4944-L4961):

```python
def strat_institutional_strong_conviction_long(s):
    """Wave 3 (Batch 333): fresh capital (new positions) + existing-holder
    growth (increased) simultaneously. Distinct conviction signature -
    both new entrants AND existing holders agree. Frazzini-Lamont 2008
    notes new-money + position-growth = institutional consensus."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("institutional_new_positions", 0) >= 2
        and s.get("price_above_ema_200", False)  # post-B663
    )
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","institutional_new_positions>=2",
         "price_above_ema_200"],
        [f"{n_new} new + {n_incr} grew institutional positions",
         "Fresh capital agrees with existing-holder conviction",
         "Above 200 EMA (regime gate)"])
```

**3-gate LONG strategy.** Dual 13F-threshold composition — requires BOTH growing positions (`increased >= 5`) AND new entrants (`new_positions >= 2`) on the same quarter.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_increased >= 5` | 5+ funds grew position THIS quarter |
| `institutional_new_positions >= 2` | 2+ funds initiated new position THIS quarter |
| `price_above_ema_200` | Long-term uptrend; B663-fixed |

### Step 2 — Classify

- Category: `institutional_persistence`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663

### Step 3 — Producer source-read + temporality

Both 13F counts from same producer. ALL gates STATE quarterly. **0 EVENT gates per direction.** Pattern B per CHECKLIST (s).

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Frazzini-Lamont 2008 notes new-money + position-growth = institutional consensus" | ⚠ **Pattern B + citation-applicability** — Frazzini-Lamont 2008 documents institutional holding dynamics + forward-return predictability over long horizons. The "consensus" framing implies bar-of-fire conviction; structurally STATE per B611. Citation correctly attributed but result applies to factor-tilt, not bar-of-fire timing. |
| "Fresh capital agrees with existing-holder conviction" | ⚠ Same Pattern B class — implies bar-of-fire conviction event |

### Step 5 — OPEN_INVESTIGATIONS grep

No active investigations.

### Step 6 — Missing-inverse + economic-symmetry

13F long-only. ✅

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-state-as-event Pattern B** | 0 EVENT gates; "fresh capital agrees with existing-holder conviction" implies bar-of-fire timing on quarterly STATE | MEDIUM | F1 |
| **F-marginal-contribution Pattern F** | Dual-13F threshold rare; if 13F STATE is near-no-op, strategy reduces to "bull market" via 200-EMA. Same Pattern F risk class as SM-21 but with stricter co-occurrence requirement (lower fire count). | HIGH | F1 |
| F-fire-count | Dual-13F threshold rare; projected ~20-40/yr; borderline / FAIL on min_trades=30 possible | INFO | F4-adjacent |
| F1 default-True | `price_above_ema_200` FIXED B663 ✅ | ✅ SHIPPED B663 | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Pattern B docstring reframe — gated on Pattern F per reviewer F1 |
| **(c) RECOMMENDED — gate Pattern B/F on post-B660** |
| (d) Stage 5 deferral |

**My recommendation: (c).** Same logic as SM-7/SM-10/SM-13.

**Awaiting owner direction on SM-22:**
1. Confirm Pattern B/F post-B660 sequencing

---

## SM-23. `strat_institutional_capitulation_short` (333 variant, walked — **DATA-SOURCE-ASYMMETRY + NAME-vs-THESIS BUG**)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B669 expanded per reviewer F2 + F3). **Pattern C candidate** — same B611 data-source-asymmetry issue as SM-9. **Per reviewer F3 (B669):** the strategy has a NAME-vs-THESIS contradiction — name "capitulation_short" implies CONTRARIAN-BOTTOM (would be a LONG fade-the-wash-out) but implementation is MOMENTUM-CONTINUATION SHORT (sell INTO the wash-out). The B669 docstring fix shipped in [screener.py:strat_institutional_capitulation_short](backtest/signals/screener.py) added explicit THESIS-vs-NAME DISAMBIGUATION block. **Rename surfaced as separate B-N decision** per `feedback_local_changes_default_global_needs_approval`.

### Step 1 — Read the code (post-B669 docstring fix)

[screener.py:4964-5012](backtest/signals/screener.py#L4964-L5012):

```python
def strat_institutional_capitulation_short(s):
    """Wave 3 (Batch 333): institutional distribution + volume spike
    (capitulation signature).

    THESIS-vs-NAME DISAMBIGUATION (B669 owner-directed external-AI
    critique #3 walk fix 2026-06-10): the name "capitulation_short" is
    misleading because "capitulation" usually implies BOTTOM-FORMING
    (contrarian-buy). This strategy is the OPPOSITE: MOMENTUM-
    CONTINUATION SHORT that sells INTO the wash-out.
    ...
    """
    fires = (
        s.get("institutional_negative", False)
        and s.get("vol_spike_2x", False)
        and s.get("below_ema_50", False)  # B633 sweep
    )
```

**3-gate SHORT strategy:** `institutional_negative` (13F quarterly STATE) + `vol_spike_2x` (today EVENT) + `below_ema_50` (STATE trend gate). 1 EVENT gate + 2 STATE gates.

### Step 2 — Classify

- Category: `institutional_persistence`; single SHORT
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 SHORT default `{bear, crisis, neutral}`
- Last touched: B669 (docstring honesty THESIS-vs-NAME DISAMBIGUATION block)

### Step 3 — Producer source-read + temporality

Same 13F producer as SM-7 / SM-8 / SM-9. `institutional_negative` is 90-day STATE; `vol_spike_2x` is bar-of-fire EVENT (today's volume); `below_ema_50` is STATE.

**EVENT/STATE composition (post-B669 disambiguation):** the 1 EVENT gate (`vol_spike_2x`) is the actual timing signal; the 2 STATE gates are eligibility filters. Per the corrected thesis (MOMENTUM-CONTINUATION SHORT), today's volume-spike on a downtrending name with quarterly 13F-trimming = "the wash-out is happening NOW, with retail tape participating." This is internally consistent with the implementation BUT the original name "capitulation" suggested the opposite trade.

### Step 4 — Doc-vs-thesis

| Claim | Verification (post-B669 docstring fix) |
|---|---|
| **Original docstring "capitulation signature"** | ⚠ **F3 NAME-vs-THESIS BUG identified by reviewer F3** — fixed via THESIS-vs-NAME DISAMBIGUATION block in B669; docstring now explicitly states MOMENTUM-CONTINUATION SHORT, not contrarian-bottom |
| Sias 2004 JFE + Lo-Wang 2000 | ⚠ Same CITATION-OVERREACH as SM-9 — Sias 2004's institutional-herding-on-selling result requires observable seller identity + motive; 13F trim doesn't supply that. Lo-Wang volume-as-information is about realized trading not 13F filings |
| Vol spike 2x | ✅ This is a real EVENT signal and the actual timing component |
| Below 50 EMA | ✅ Real trend filter |

### Step 5 — OPEN_INVESTIGATIONS grep

- **B611 precedent (same as SM-9):** structurally identical to deleted `strat_institutional_breakdown_confirmation_short`; the 13F gate is the weak link
- **B669 docstring fix shipped** — THESIS-vs-NAME DISAMBIGUATION block resolves the F3 mismatch but the underlying Pattern C concern persists
- **Rename surfaced as separate B-N decision** — current name `strat_institutional_capitulation_short` could be renamed to `strat_institutional_distribution_with_volume_short` (clearer momentum-continuation framing) per the W10 R3→R4 rename precedent in pivot cluster. Per `feedback_local_changes_default_global_needs_approval`: rename = global scope requiring explicit owner approval

### Step 6 — Missing-inverse + economic-symmetry

Mirror of SM-22 (`institutional_strong_conviction_long`) but SHORT side. Per Pattern C: 13F is SEC long-only by rule; `institutional_negative` doesn't supply bear conviction even when composed with vol_spike + below_50_EMA. **Compare to SM-9 (2-gate version) — SM-23 adds a vol_spike EVENT gate which IS real signal but the 13F gate continues to add asymmetric noise.**

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F1 NAME-vs-THESIS** | "capitulation_short" name implies contrarian-bottom but implementation is momentum-continuation; B669 docstring fix shipped; rename surfaced as separate B-N decision | MEDIUM → ✅ docstring SHIPPED B669 | F3 |
| **F-pattern-C-data-source-asymmetry** | `institutional_negative` quarterly STATE doesn't supply bear conviction (B611 precedent applies same as SM-9); vol_spike + below_50_EMA pair DOES supply real capitulation timing; the 13F gate is the weak link | HIGH | F2 |
| F-citation-overreach | Same Sias 2004 + Lo-Wang 2000 stretch as SM-9 | MEDIUM | F7 |
| F-empirical-engine-blindness | Same critique #2 cube-blindness as SM-9 | HIGH | F2 |
| F-marginal-contribution per reviewer F1 | If the alpha attribution is dominated by vol_spike + below_50_EMA, the 13F gate is near-no-op. **Strategy could be replaced by a clean `vol_spike_2x_below_ema_50_short` without the 13F-trim noise.** Pattern F audit candidate. | MEDIUM | F1 |
| F-fire-count | Co-occurrence of all 3 → projected ~10-30/yr; FAIL likely | MEDIUM | F4 |

**Options (B669 RE-FRAMED per reviewer F2 + F3):**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Docstring caveat only (ORIGINAL B664 RECOMMENDATION; per reviewer F2 this is misapplying no-pruning rule) |
| **(c) RECOMMENDED B669 — DELETE per B611 precedent** + replace with clean `strat_vol_spike_2x_below_ema_50_short` (if owner wants to keep the underlying tape-capitulation trade). Same logic as SM-9 (c). |
| (d) (c) + the new replacement gets a Class 7 NEW wire-up in the chart-pattern or momentum cluster (not smart money) — moves the actual signal away from the smart-money sleeve where its 13F-disguise belongs |
| (e) Rename only (does NOT resolve Pattern C concern but does resolve F3 name-thesis mismatch) — rename to `strat_institutional_distribution_with_volume_short`. Per W10 R3→R4 precedent this is acceptable scope but doesn't address the underlying economic-falseness concern |
| (f) EXPLORATORY marker (analogous to W5m) — exclude from cube selection budget while keeping registered for cube-replay coverage. Resolves the empirical-blindness concern without overriding no-pruning rule. |

**My B669 recommendation: (c) DELETE + (d) Class 7 NEW replacement.** Same logic as SM-9 (c). The cube cannot empirically validate this strategy because of survivorship + cost-borrow gaps; the B611 precedent applies; the rename (e) is cosmetic. If owner wants the underlying tape-capitulation SHORT trade to exist, register it cleanly in the chart-pattern or momentum cluster without the 13F-disguise.

**Awaiting owner direction on SM-23:**
1. **Disposition:** (a) status quo / (b) docstring caveat / **(c) RECOMMENDED B669** DELETE per B611 precedent / (d) (c) + Class 7 NEW chart-pattern replacement / (e) rename only / (f) EXPLORATORY marker
2. **B669 docstring fix shipped** (THESIS-vs-NAME DISAMBIGUATION block); confirm no further docstring action needed
3. **Rename question** (separate B-N decision regardless of (c) outcome): rename to `strat_institutional_distribution_with_volume_short` per W10 R3→R4 precedent? Or keep current name?

### FINAL STATUS POST-B670 — ✅ DELETED + Class 7 NEW REPLACEMENT (rename Q moot)

> Owner approved B670 option (d) = "Delete + Class 7 NEW replacement" on 2026-06-10 via AskUserQuestion Round 1. Rename question (Q3) resolved as N/A (deleted strategy can't be renamed).

| Item | Outcome |
|---|---|
| **Disposition** | DELETED per Pattern C + B611 precedent + F3 NAME-vs-THESIS resolved by deletion. Same logic as SM-9 deletion above. Per `project_no_apriori_strategy_pruning` override: owner explicitly approved. |
| **Code reference** | [screener.py line ~5009](backtest/signals/screener.py) — replaced with DELETION RATIONALE comment block citing B611 + reviewer F2 + F3 + Pattern C analysis + citation retraction |
| **Class 7 NEW replacement** | `strat_vol_spike_2x_below_ema_50_short` registered in `momentum_trend` category (NOT smart_money_13f). 2-gate AND: fires SHORT when `vol_spike_2x = True AND below_ema_50 = True`. Honest 2-gate framing of the actual tape-capitulation continuation signal that deleted SM-23's 3-gate structure was using; the `institutional_negative` gate was Pattern C noise per the walk. |
| **Regime affinity** | No explicit entry → B291 SHORT default `{bear, crisis, neutral}` applies |
| **Strategy count impact** | 222 → 221 (deletion) → 222 (Class 7 NEW addition). Smart money cluster: 41 → 39 (after both SM-9 + SM-23 deletions; Class 7 NEW additions register in momentum_trend). |
| **Test pins** | `test_batch670_sm9_sm23_deletion_and_replacement.py` pins (3)-(4)-(7)-(8)-(13)-(14) plus shared registry invariant + regime pins. 16/16 green. |
| **F3 NAME-vs-THESIS resolved by deletion** | B669 docstring fix (THESIS-vs-NAME DISAMBIGUATION block) is now moot — strategy deleted. Class 7 NEW replacement has an honest name (`vol_spike_2x_below_ema_50_short` accurately describes the gates) and an honest thesis (tape-capitulation continuation SHORT). The rename question (Q3 deferred conditional in Round 1) is resolved as N/A. |
| **Citation retraction** | Same Sias 2004 + Lo-Wang 2000 citation-overreach as SM-9; not carried to Class 7 NEW. |
| **Cross-cluster note** | Per Pattern H + Class 7 NEW location: the new `vol_spike_2x_below_ema_50_short` belongs to the `momentum_trend` category and is not part of the smart money cluster. If a future Stage 4 walk covers the momentum/chart-pattern cluster, this strategy should appear there for owner re-walk per CHECKLIST #105. |
| **No regrets** | Same as SM-9: reviewer F2 critique decisive; B611 precedent applies; F3 NAME-vs-THESIS contradiction additionally cleared by deletion; Class 7 NEW preserves the actual signal without the Pattern C noise. |

---

## SM-24. `strat_institutional_high_conviction_long` (336 pure cluster, walked — Pattern A + Pattern B + cluster-loose-regime)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672f full expansion). 2-gate LONG; pure new-positions signal with intentionally LOOSER regime (50-EMA vs 200-EMA) to catch "early institutional initiations before they fully appear in trend metrics" per docstring. Pattern A silent-gap on 50-EMA + Pattern B (0 EVENT gates) + Cohen-Frazzini-Malloy 2008 citation correctly attributed to long-horizon factor result but framed as bar-of-fire signal.

### Step 1 — Read the code

[screener.py:5156-5171](backtest/signals/screener.py#L5156-L5171):

```python
def strat_institutional_high_conviction_long(s):
    """Wave 3 (Batch 336): pure new-positions signal with looser regime.
    institutional_new_positions >= 3 alone is the canonical Cohen-Frazzini-
    Malloy 2008 RFS cluster signal. Distinct from Batch 330's cluster_long
    by using a LOOSER regime gate (50-EMA vs 200-EMA), capturing early
    institutional initiations before they fully appear in trend metrics."""
    fires = (
        s.get("institutional_new_positions", 0) >= 3
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A default-True silent-gap
    )
    n_new = s.get("institutional_new_positions", 0)
    return _strat(fires, "long", "smart_money_13f",
        ["institutional_new_positions>=3","price_above_ema_50"],
        [f"{n_new} institutional funds initiated new positions this quarter",
         "Cohen-Frazzini-Malloy 2008 RFS - pure cluster signal",
         "Above 50 EMA (looser regime to catch early initiation)"])
```

**2-gate LONG strategy.** Loosest regime member of the Wave 3 13F family — only requires 50-EMA (intermediate trend) instead of 200-EMA (long-term trend). The threshold is the ONLY 13F gate; threshold-based pure cluster signal.

**LONG fires when BOTH:**

| Gate | Meaning |
|---|---|
| `institutional_new_positions >= 3` | 3+ funds initiated new position THIS quarter (cluster threshold per CFM 2008) |
| `price_above_ema_50` | Intermediate uptrend (looser than 200-EMA used by SM-25/26/27/28) — ⚠ Pattern A default-True silent-gap |

### Step 2 — Classify

- Category: `smart_money_13f` (NOT institutional_persistence; this is a pure cluster trigger, not a multi-quarter persistence proxy)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: Batch 336 (2026-05-25 — original Wave 3 wiring)

### Step 3 — Producer source-read + temporality

- `institutional_new_positions` (count of funds initiating new position this quarter) is produced by [smart_money.py](backtest/data/smart_money.py) Batch 330 13F producer. Per DEC-325, 13F filings have a **45-day SEC publication lag** — by the time a "new position" appears in the producer's output, it could be up to 135 days old (45-day reporting lag + up to 90-day quarter window before filing). Same temporality issue as SM-7/SM-10/SM-13/SM-21/SM-22.
- `price_above_ema_50` is STATE (derived from today's price vs 50-period EMA).

**EVENT/STATE composition:** 0 EVENT gates per direction. Per CHECKLIST (s) signal-temporality classification, this is Pattern B per `feedback_signal_temporality_event_vs_state` — slow background states (quarterly 13F + STATE EMA trend) don't provide timing alpha at bar of fire. The "early initiation" framing in the docstring is INTERNALLY CONSISTENT (looser regime catches earlier signals) but doesn't escape Pattern B (the looser regime is still STATE, and the trigger signal is still STATE quarterly).

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Cohen-Frazzini-Malloy 2008 RFS - pure cluster signal" | ⚠ **Pattern B + citation-applicability** — CFM 2008 (Cohen, Frazzini, Malloy 2008 RFS "The Small World of Investing: Board Connections and Mutual Fund Returns") documents long-horizon (quarterly to multi-quarter) alpha from institutional cluster behavior. The "pure cluster signal" framing is correctly attributed to CFM 2008's published result BUT applies that result to BAR-OF-FIRE timing which CFM 2008 doesn't establish. Per B611 + reviewer F7 citation-overreach pattern: research result documents factor-tilt alpha; strategy implementation implies bar-of-fire timing alpha. Class same as SM-7/SM-10/SM-13/SM-21/SM-22. |
| "LOOSER regime gate (50-EMA vs 200-EMA), capturing early institutional initiations before they fully appear in trend metrics" | ⚠ **Internal-consistency note:** the looser regime is mechanically true (50-EMA is more responsive than 200-EMA) BUT "early initiation" wording contradicts the 45-day publication lag — by the time the 13F filing surfaces the cluster, the 50-EMA has already responded to whatever fund activity drove the new positions. Looser regime doesn't escape the lag. |
| "pure cluster signal" | The threshold `>= 3` IS the literature-standard cluster threshold per CFM 2008. ✅ Threshold value defensible; framing of when-it-applies is Pattern B |

### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations on SM-24 specifically
- B663 family-bug applies (Pattern A on `price_above_ema_50`); WAVE 1 (200-EMA defaults) shipped B663; WAVE 2 (50-EMA defaults) queued
- Reviewer F1 marginal-contribution test applies — if the 50-EMA filter near-no-ops on T1a in bull years (price > 50-EMA is ~75-85% of bars), the strategy reduces to "≥3 new institutional positions" which is the canonical CFM 2008 cluster signal alone

### Step 6 — Missing-inverse + economic-symmetry

13F long-only by SEC rule (Securities Act §13(f)). No SHORT mirror; Pattern C asymmetry per `feedback_asymmetric_data_sources_break_mechanical_inverse`. ✅

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F1 Pattern A** | `price_above_ema_50` default-True silent-gap; WAVE 2 family-bug eligible | MEDIUM | (post-B663 WAVE 2 sweep) |
| **F-state-as-event Pattern B** | 0 EVENT gates; "early initiation" framing contradicts 45-day publication lag; CFM 2008 citation is long-horizon result framed as bar-of-fire timing | MEDIUM | F1 |
| **F-marginal-contribution Pattern F** | If 50-EMA near-no-op on T1a bull-year sample, strategy reduces to bare "≥3 new positions" cluster signal. Post-B660 fire-count + post-cube marginal-contribution test required. | HIGH | F1 |
| F-fire-count | `institutional_new_positions >= 3` threshold rare; projected ~40-80/yr universe-wide | INFO | F4-adjacent |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Pattern A fix only (default-True → False on 50-EMA) — bundled into WAVE 2 family sweep |
| (c) Pattern A + Pattern B docstring reframe (gated on Pattern F per reviewer F1) |
| **(d) RECOMMENDED — gate Pattern B on post-B660 + post-cube marginal-contribution per reviewer F1; (b) WAVE 2 family fix proceeds immediately** |
| (e) Stage 5 deferral |

**My recommendation: (d).** Same logic as SM-21/SM-22 (Pattern B reframe gated on cube validation) but Pattern A WAVE 2 family fix can proceed without Pattern F validation (it's a pure silent-gap fix).

**Awaiting owner direction on SM-24:**
1. Pattern A WAVE 2 family sweep timing (proceed independently or wait for B660 to complete?)
2. Pattern B reframe sequencing (post-B660 + post-cube per reviewer F1)
3. Confirm CFM 2008 citation retention with reframe vs full retraction

---

## SM-25. `strat_institutional_with_directors_long` (336 + director combo, walked — CROSS-SOURCE CANONICAL #2)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672f full expansion). 3-gate mixed STATE/EVENT LONG. **Per reviewer F1 (B669):** this is a CROSS-SOURCE CANONICAL strategy alongside SM-12 + SM-20 + SM-26 — the only family in the cluster that combines 13F STATE with insider-trading EVENT signal where the EVENT gate IS the actual timing trigger. Akbas-Jiang-Koch 2024 RFS director-premium citation correctly attributed to insider-trading research (NOT 13F factor research). Partial Pattern B — the docstring "dual board-level + fund-manager confirmation" overstates because the 13F STATE doesn't supply bar-of-fire confirmation (only the director EVENT does), but the strategy has the canonical EVENT-anchored structure the cluster needs.

### Step 1 — Read the code

[screener.py:5174-5191](backtest/signals/screener.py#L5174-L5191):

```python
def strat_institutional_with_directors_long(s):
    """Wave 3 (Batch 336): institutional + director-level insider buying.
    Director purchases are higher-information signal than officer/10pct-
    owner trades (Akbas-Jiang-Koch 2024 RFS). When combined with
    institutional accumulation, dual board-level + fund-manager
    confirmation = strongest smart-money agreement signature."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("insider_director_buyers_30d", 0) >= 1
        and s.get("price_above_ema_200", False)  # post-B663
    )
    n_dir = s.get("insider_director_buyers_30d", 0)
    return _strat(fires, "long", "smart_money_combo",
        ["institutional_buy","insider_director_buyers_30d>=1","price_above_ema_200"],
        ["13F institutional new/increased positions",
         f"{n_dir} director(s) buying open-market in 30d",
         "Akbas-Jiang-Koch 2024 RFS - director-level signal premium",
         "Above 200 EMA (regime gate)"])
```

**3-gate LONG strategy.** Cross-source canonical combining 13F (slow STATE) + director-level insider EVENT (timing trigger) + EMA trend regime.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_buy` | 13F STATE: new/increased positions this quarter (eligibility filter) |
| `insider_director_buyers_30d >= 1` | EVENT: 1+ director open-market buy filed via Form 4 within last 30 days (timing trigger) |
| `price_above_ema_200` | Long-term uptrend; B663-fixed (default False not True) |

### Step 2 — Classify

- Category: `smart_money_combo` (cross-source — combines 13F sleeve + insider sleeve)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663 (Pattern A WAVE 1 family fix on 200-EMA default-True → False)

### Step 3 — Producer source-read + temporality

- `institutional_buy` STATE quarterly per Batch 330 producer (45-day SEC lag per DEC-325) — same temporality as SM-7/SM-10/SM-13/SM-21/SM-22/SM-24
- `insider_director_buyers_30d` is COUNT of director Form-4 open-market buys in trailing 30-day window. Per Batch 222 insider producer with **2-day Form-4 filing rule** (Section 16(a)) — this is a near-real-time EVENT signal with at most 2-day lag from the actual transaction. Director-level signal premium per Akbas-Jiang-Koch 2024 RFS is established on insider-trading data (NOT 13F factor research)
- `price_above_ema_200` STATE

**EVENT/STATE composition:** **1 EVENT gate (director buys 30d) + 2 STATE gates.** The 1 EVENT gate IS the bar-of-fire timing signal per CHECKLIST (s). This is the CORRECT cross-source structure — STATE filter + EVENT trigger. The docstring "dual confirmation" framing is the partial Pattern B issue (the 13F STATE is eligibility-not-confirmation), not the strategy structure itself.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Akbas-Jiang-Koch 2024 RFS - director-level signal premium" | ✅ Correctly attributed — Akbas, Jiang, Koch 2024 RFS "The Value of Independent Directors: Evidence from Insider Trading" establishes that director-level Form-4 buying has higher information content than officer-level or 10%-owner-level. This is INSIDER-TRADING research applied to an insider-trading EVENT gate. NOT a citation-overreach class. |
| "dual board-level + fund-manager confirmation = strongest smart-money agreement signature" | ⚠ **Partial Pattern B** — the 13F STATE doesn't provide BAR-OF-FIRE confirmation (only the director EVENT does); the 13F adds eligibility-filter alpha (factor-tilt) not timing alpha. Honest reframe: "director EVENT triggers timing; 13F STATE filters for institutional-sponsored names; agreement at sponsorship level, not timing level." |
| "Director purchases are higher-information signal than officer/10pct-owner trades" | ✅ Correctly attributed and applied. This is the foundation gate semantic. |

**Net Step 4 verdict:** This is a HIGHER-QUALITY walk than the 13F-only Pattern B family (SM-21/SM-22/SM-24/SM-27). The citation matches the EVENT gate's mechanism; the strategy has the canonical cross-source structure. The Pattern B concern is contained to the "dual confirmation" framing in the human-readable docstring, not the strategy logic.

### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations on SM-25 specifically
- Reviewer F1 marginal-contribution test applies post-B660 + post-cube — what does the 13F STATE gate add over standalone director-EVENT + 200-EMA?
- Companion strategy SM-26 is officer-level variant; conjoint walk surfaces dose-response (director vs officer information premium)

### Step 6 — Missing-inverse + economic-symmetry

- 13F long-only by SEC rule + insider-buying long-only (insider SALES are mostly diversification not signal per `feedback_asymmetric_data_sources_break_mechanical_inverse`)
- **Double-asymmetric** — both data sources structurally LONG-biased; no SHORT mirror viable
- Pattern C does NOT apply (not proposing a mechanical mirror; explicitly acknowledging asymmetry)

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-cross-source-canonical structure** | ✅ EVENT-anchored timing + STATE eligibility = correct structure; cluster anchor candidate alongside SM-12/SM-20/SM-26 | INFO / ✅ POSITIVE | F1 |
| **F-state-as-event Pattern B (partial)** | "Dual confirmation" framing in docstring overstates — 13F STATE is eligibility-not-bar-of-fire-confirmation; reframe as "EVENT trigger + STATE eligibility filter" | LOW-MEDIUM | F1 |
| **F-marginal-contribution Pattern F** | What does 13F STATE add over standalone director-EVENT + 200-EMA? Post-B660 + post-cube ablation test | MEDIUM | F1 |
| F-fire-count | Director buys are rare (~1-2/week universe-wide); co-occurrence with `institutional_buy` STATE further reduces; projected ~10-25/yr; **borderline FAIL on min_trades=30 per regime** | MEDIUM | F4 |
| F1 default-True | `price_above_ema_200` FIXED B663 ✅ | ✅ SHIPPED B663 | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Docstring honesty reframe — "EVENT trigger + STATE eligibility filter" replaces "dual confirmation"; preserve Akbas-Jiang-Koch citation; preserve all gates |
| (c) (b) + Pattern F marginal-contribution test gated on post-B660 + post-cube |
| **(d) RECOMMENDED — (c). Cross-source canonical structure is correct; docstring is the only issue; ablation test settles whether 13F STATE earns its place in the gate stack** |
| (e) Tighten threshold (`insider_director_buyers_30d >= 2`) — would reduce fire count further; not recommended pre-cube |

**My recommendation: (d).** Strategy structure is correct (cross-source canonical); docstring reframe + post-cube ablation handle the partial Pattern B + Pattern F concerns.

**Awaiting owner direction on SM-25:**
1. (a)/(b)/(c)/(d) — recommendation (d)
2. Pattern F ablation post-B660 + post-cube sequencing confirmation
3. Whether to bundle SM-25 + SM-26 docstring reframes (same family)

---

## SM-26. `strat_institutional_with_officers_long` (336 + officer combo, walked — CROSS-SOURCE CANONICAL #3)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672f full expansion). 3-gate mixed STATE/EVENT LONG. Companion to SM-25 (director variant) with officer-level EVENT instead. **Per reviewer F1 (B669):** this is a CROSS-SOURCE CANONICAL strategy alongside SM-12 + SM-20 + SM-25 — the only family in the cluster that combines 13F STATE with insider-trading EVENT signal where the EVENT gate IS the actual timing trigger. Officer-level information premium is lower than director-level per Akbas-Jiang-Koch 2024 RFS but still meaningfully above 10%-owner level. Partial Pattern B same class as SM-25.

### Step 1 — Read the code

[screener.py:5194-5210](backtest/signals/screener.py#L5194-L5210):

```python
def strat_institutional_with_officers_long(s):
    """Wave 3 (Batch 336): institutional + officer-level insider buying.
    Officers are CEO/CFO/COO buying their own company's stock - direct
    competence and conviction signal. Lower information value than
    directors but still meaningfully higher than 10pct-owner trades."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("insider_officer_buyers_30d", 0) >= 1
        and s.get("price_above_ema_200", False)  # post-B663
    )
    n_off = s.get("insider_officer_buyers_30d", 0)
    return _strat(fires, "long", "smart_money_combo",
        ["institutional_buy","insider_officer_buyers_30d>=1","price_above_ema_200"],
        ["13F institutional new/increased positions",
         f"{n_off} officer(s) buying open-market in 30d",
         "Direct competence + conviction signal",
         "Above 200 EMA"])
```

**3-gate LONG strategy.** Cross-source canonical structurally identical to SM-25 with the EVENT gate switched from director to officer.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_buy` | 13F STATE: new/increased positions this quarter (eligibility filter) |
| `insider_officer_buyers_30d >= 1` | EVENT: 1+ officer (CEO/CFO/COO/etc.) open-market buy filed via Form 4 within last 30 days (timing trigger) |
| `price_above_ema_200` | Long-term uptrend; B663-fixed |

### Step 2 — Classify

- Category: `smart_money_combo` (cross-source — same category as SM-25)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663

### Step 3 — Producer source-read + temporality

- `institutional_buy` STATE quarterly per Batch 330 producer (45-day SEC lag per DEC-325)
- `insider_officer_buyers_30d` per Batch 222 insider producer (2-day Form-4 filing rule); EVENT signal with at most 2-day lag from transaction
- `price_above_ema_200` STATE

**EVENT/STATE composition:** **1 EVENT gate (officer buys 30d) + 2 STATE gates.** Same cross-source canonical structure as SM-25. The officer-EVENT IS the bar-of-fire timing signal per CHECKLIST (s).

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Officers are CEO/CFO/COO buying their own company's stock - direct competence and conviction signal" | ✅ Correctly attributed — the SEMANTIC mechanism (named executives at the firm have direct, current, material non-public-knowledge-adjacent information) is universally accepted in the insider-trading literature. |
| "Lower information value than directors but still meaningfully higher than 10pct-owner trades" | ✅ Correctly stated — Akbas-Jiang-Koch 2024 RFS + Cohen-Malloy-Pomorski 2012 JF independently document a director > officer > 10pct-owner information hierarchy. The strategy ranks correctly. |
| Implicit "13F + officer buying" thesis | ⚠ **Partial Pattern B same as SM-25** — same reframe applies: "EVENT trigger + STATE eligibility filter" replaces implied "dual confirmation." |
| No explicit "dual confirmation" wording in docstring (unlike SM-25) | ✅ — SM-26's docstring is HONEST about the EVENT gate being the primary signal; the partial Pattern B is weaker here than SM-25 |

### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations on SM-26 specifically
- Reviewer F1 marginal-contribution test applies post-B660 + post-cube — what does 13F STATE add over standalone officer-EVENT + 200-EMA?
- **Conjoint walk with SM-25** surfaces dose-response (director vs officer information premium) — same regime, same 13F STATE, different EVENT gate quality

### Step 6 — Missing-inverse + economic-symmetry

- Double-asymmetric same as SM-25 (13F long-only + insider buying long-only)
- No SHORT mirror viable per `feedback_asymmetric_data_sources_break_mechanical_inverse`

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-cross-source-canonical structure** | ✅ Same correct structure as SM-25 | INFO / ✅ POSITIVE | F1 |
| **F-state-as-event Pattern B (weaker partial)** | Implicit "dual confirmation" thesis same class as SM-25 but docstring wording is more honest (no "strongest smart-money agreement signature" phrasing) | LOW | F1 |
| **F-marginal-contribution Pattern F** | What does 13F STATE add over standalone officer-EVENT + 200-EMA? Same ablation test as SM-25 | MEDIUM | F1 |
| F-fire-count | Officer buys somewhat more common than director buys (more named officers per firm than independent directors) → projected ~15-35/yr universe-wide; borderline | INFO | F4 |
| F1 default-True | `price_above_ema_200` FIXED B663 ✅ | ✅ SHIPPED B663 | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Pattern B reframe — explicit "EVENT trigger + STATE eligibility filter" docstring addition (lighter touch than SM-25 because SM-26 docstring is already mostly honest) |
| (c) (b) + Pattern F ablation test gated on post-B660 + post-cube |
| **(d) RECOMMENDED — (c) bundled with SM-25 reframe + ablation** |
| (e) Tighten threshold (`insider_officer_buyers_30d >= 2`) — would reduce fire count; not recommended pre-cube |

**My recommendation: (d) bundled with SM-25.** SM-25 + SM-26 share the cross-source canonical structure + the partial Pattern B framing concern; bundle the reframe + ablation as one decision since their decision-criteria are coupled.

**Awaiting owner direction on SM-26:**
1. (a)/(b)/(c)/(d) — recommendation (d) bundled with SM-25
2. Pattern F ablation should compare SM-25 + SM-26 jointly to settle officer-vs-director dose-response
3. Whether to retain BOTH SM-25 + SM-26 if cube shows tight overlap (could collapse to single `OR` strategy with `insider_director_or_officer_buyers_30d` aggregator)

---

## SM-27. `strat_institutional_persistence_momentum_long` (336 variant, walked — Pattern A + Pattern B + MACD-as-momentum-overlay)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672f full expansion). 3-gate LONG combining 13F persistence proxy (`institutional_increased >= 5`) with MACD momentum overlay and 50-EMA regime. All 3 gates STATE (MACD is derived from price but does not classify as bar-of-fire EVENT). Pattern A silent-gap on 50-EMA + Pattern B (0 EVENT gates). Docstring framing "momentum confirms institutional conviction" implies STATE 13F provides bar-of-fire timing signal which it doesn't (45-day publication lag).

### Step 1 — Read the code

[screener.py:5213-5227](backtest/signals/screener.py#L5213-L5227):

```python
def strat_institutional_persistence_momentum_long(s):
    """Wave 3 (Batch 336): high institutional increased + MACD momentum +
    50-EMA trend. Single-quarter persistence proxy (per Batch 333) combined
    with price-trend confirmation. Distinct from Batch 333's persistent_holders
    by requiring MACD bullish (momentum confluence, not just regime gate)."""
    fires = (
        s.get("institutional_increased", 0) >= 5
        and s.get("macd_12_26_9_bullish", False)
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A default-True silent-gap
    )
    return _strat(fires, "long", "institutional_persistence",
        ["institutional_increased>=5","macd_12_26_9_bullish","price_above_ema_50"],
        ["5+ institutional funds grew position this quarter",
         "MACD bullish - momentum confirms institutional conviction",
         "Above 50 EMA (intermediate trend)"])
```

**3-gate LONG strategy.** Combines 13F persistence proxy with momentum confluence (MACD) and trend regime (50-EMA).

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_increased >= 5` | 5+ funds grew position THIS quarter (persistence proxy per Batch 333) |
| `macd_12_26_9_bullish` | MACD line above signal line (STATE momentum overlay) |
| `price_above_ema_50` | Intermediate uptrend — ⚠ Pattern A default-True silent-gap |

### Step 2 — Classify

- Category: `institutional_persistence`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: Batch 336 (2026-05-25 — original Wave 3 wiring)

### Step 3 — Producer source-read + temporality

- `institutional_increased` STATE quarterly per Batch 330 producer (45-day SEC lag per DEC-325)
- `macd_12_26_9_bullish` is computed from price (`MACD line > signal line`) in [technical.py](backtest/signals/technical.py). Per CHECKLIST (s) signal-temporality classification, MACD is a **STATE** signal — it describes the current momentum regime, NOT a bar-of-fire EVENT like MACD-crossover-today. Strategy uses the bullish-state form, not the crossover-event form.
- `price_above_ema_50` STATE

**EVENT/STATE composition:** **0 EVENT gates per direction.** All 3 gates are STATE. Per CHECKLIST (s), this is Pattern B. The "momentum confirms institutional conviction" framing in the docstring implies the MACD STATE provides bar-of-fire confirmation but MACD as a STATE signal merely says "momentum regime is currently bullish" — not "a momentum event just occurred."

**Note:** The docstring claims "MACD bullish (momentum confluence, not just regime gate)" — the MACD STATE IS a momentum-flavored regime gate. The wording "not just regime gate" is technically wrong; MACD-state IS a regime-flavored gate. A true momentum EVENT would be MACD-crossover-today or MACD-histogram-rising-N-bars.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Single-quarter persistence proxy (per Batch 333) combined with price-trend confirmation" | ⚠ **Pattern B same as SM-21/SM-22** — 13F quarterly STATE is not "persistence" in any bar-of-fire sense; it's an institutional-snapshot count. Batch 333 self-acknowledges "TRUE multi-quarter persistence requires precompute over 4+ quarters; that's queued as Batch 333b. This batch ships single-quarter persistence proxies." So docstring is partial-honest (proxy framing) but still applied as STATE-as-EVENT |
| "MACD bullish - momentum confirms institutional conviction" | ⚠ **Pattern B + claim-not-substantiated** — STATE 13F + STATE MACD = two STATE gates aligned; "momentum confirms" implies temporal sequence (institutional first, momentum confirms after) which the data doesn't establish. Honest reframe: "both gates STATE simultaneously bullish; aligned-conviction filter" |
| "Distinct from Batch 333's persistent_holders by requiring MACD bullish (momentum confluence, not just regime gate)" | ⚠ **Wording note** — MACD-state IS a regime gate per CHECKLIST (s). The differentiation from SM-21 (`institutional_persistent_holders_long`) is correct (different gate composition) but the framing of MACD as "momentum confluence not regime" is semantically wrong; MACD-state IS a momentum-flavored regime gate. |

### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations on SM-27 specifically
- B663 family-bug applies (Pattern A on `price_above_ema_50`); WAVE 2 family fix queued
- Reviewer F1 marginal-contribution test applies post-B660 + post-cube — does adding STATE MACD over SM-21's (`institutional_increased + price_above_ema_200`) gate stack add empirical alpha? If MACD-bullish is ~50-60% True on T1a, the additional gate may add 0 alpha (it's another mild correlation filter on the same momentum factor)

### Step 6 — Missing-inverse + economic-symmetry

13F long-only by SEC rule. ✅ Pattern C asymmetry per `feedback_asymmetric_data_sources_break_mechanical_inverse`.

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F1 Pattern A** | `price_above_ema_50` default-True silent-gap; WAVE 2 family-bug eligible | MEDIUM | (post-B663 WAVE 2 sweep) |
| **F-state-as-event Pattern B** | 0 EVENT gates; "momentum confirms institutional conviction" implies temporal sequence not supported by data | MEDIUM | F1 |
| **F-marginal-contribution Pattern F** | Does STATE MACD add empirical alpha over SM-21's bare `institutional_increased + EMA` stack? If MACD-state correlates with 50-EMA-above (likely), gate is near-no-op. Post-B660 + post-cube ablation required | HIGH | F1 |
| F-wording | "momentum confluence not regime gate" docstring is semantically wrong; MACD-state IS a momentum-flavored regime gate per CHECKLIST (s) | LOW | F1 |
| F-fire-count | Projected ~40-90/yr universe-wide; PASS likely if MACD-state filter is loose enough | INFO | F4-adjacent |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Pattern A fix only (WAVE 2 family sweep) |
| (c) (b) + Pattern B reframe — honest "STATE 13F + STATE MACD + STATE EMA" framing |
| (d) (c) + Pattern F ablation post-B660 + post-cube |
| **(e) RECOMMENDED — (d). Pattern A WAVE 2 proceeds independently; Pattern B + Pattern F bundle gated on cube** |
| (f) Tighten by switching MACD-state to MACD-cross EVENT (`macd_12_26_9_crossed_above_signal_today`) — would convert to mixed STATE/EVENT and resolve Pattern B at structural level. But the cross EVENT might be too narrow (rare); fire-count drops materially. |

**My recommendation: (e).** Same logic as SM-21 — Pattern A WAVE 2 family fix can proceed independently; Pattern B + Pattern F bundle waits for cube. (f) tightening to MACD-cross is a Stage 5 option worth pre-cube fire-count measurement but not pre-cube wiring.

**Awaiting owner direction on SM-27:**
1. (a)/(b)/(c)/(d)/(e)/(f) — recommendation (e)
2. Whether to fire-count measure (f) MACD-cross variant pre-cube as a candidate
3. Pattern A WAVE 2 family sweep timing

---

## SM-28. `strat_institutional_volume_confirmation_long` (331 variant, walked — Pattern A + partial-honest Pattern B + 1 EVENT gate)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672f full expansion). 3-gate LONG with EVENT-anchored timing. Docstring is the MOST honest in the 13F family — explicitly acknowledges "stale 13F filings (45-day reporting lag)" and frames volume spike as confirming-the-now-active. Pattern A silent-gap on 50-EMA persists; partial-honest Pattern B; 1 EVENT gate (vol_spike_2x) makes this structurally similar to SM-23 (Pattern C deleted SHORT mirror but LONG-side has the same canonical structure).

### Step 1 — Read the code

[screener.py:5230-5246](backtest/signals/screener.py#L5230-L5246):

```python
def strat_institutional_volume_confirmation_long(s):
    """Wave 3 (Batch 331): institutional buy + retail volume confirmation.
    Per Sias 2004 JFE institutional herding + Lo-Wang 2000 RFS volume-as-
    information: retail tape volume confirming institutional accumulation
    suggests the price discovery is broadly recognized, not just
    smart-money positioning. Reduces false-positive risk on stale 13F
    filings (45-day reporting lag)."""
    fires = (
        s.get("institutional_buy", False)
        and s.get("vol_spike_2x", False)
        and s.get("price_above_ema_50", True)  # ⚠ Pattern A default-True silent-gap
    )
    return _strat(fires, "long", "smart_money_13f",
        ["institutional_buy","vol_spike_2x","price_above_ema_50"],
        ["13F institutional new/increased positions",
         "Volume 2x ADV(20) - retail tape confirming",
         "Above 50 EMA (intermediate trend agrees)"])
```

**3-gate LONG strategy.** EVENT-anchored timing via volume spike; STATE-filtered by 13F + EMA.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `institutional_buy` | 13F STATE: new/increased positions this quarter (eligibility filter; 45-day SEC lag) |
| `vol_spike_2x` | EVENT: today's volume >= 2x trailing 20-bar average (bar-of-fire timing trigger) |
| `price_above_ema_50` | Intermediate uptrend — ⚠ Pattern A default-True silent-gap |

### Step 2 — Classify

- Category: `smart_money_13f`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: Batch 331 (2026-05-25 — original Wave 3 wiring)

### Step 3 — Producer source-read + temporality

- `institutional_buy` STATE quarterly per Batch 330 producer (45-day SEC lag per DEC-325)
- `vol_spike_2x` is computed from today's volume vs trailing 20-bar mean in [technical.py](backtest/signals/technical.py). Per CHECKLIST (s) classification, this is a true **EVENT** signal — bar-of-fire condition, not a STATE regime. Lag <1 bar (intraday volume data published at session close).
- `price_above_ema_50` STATE

**EVENT/STATE composition:** **1 EVENT gate (vol_spike_2x) + 2 STATE gates.** Per CHECKLIST (s) classification, this is a CORRECT cross-EVENT/STATE structure where the EVENT IS the timing trigger. Structurally similar to SM-25/SM-26 (cross-source canonicals) except the EVENT gate is volume-on-tape rather than insider-form-4.

**Companion to deleted SM-23:** SM-23 (`institutional_capitulation_short`) had the SHORT mirror of this structure — `institutional_negative + vol_spike_2x + below_ema_50`. B670 deleted SM-23 per Pattern C (13F SEC long-only by rule + B611 deletion precedent) and registered Class 7 NEW `strat_vol_spike_2x_below_ema_50_short` in `momentum_trend` category. SM-28 LONG is NOT subject to Pattern C (13F data IS long-only by design; LONG-side use is correctly aligned with data semantics). If SM-28 fails empirically, the analogous Class 7 NEW would be `strat_vol_spike_2x_above_ema_50_long` (i.e., drop the 13F gate) — but that's not currently registered, and the marginal-contribution test would settle whether the 13F gate is earning its place.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Per Sias 2004 JFE institutional herding" | ⚠ Same citation-stretch as SM-7/SM-9/SM-23 — Sias 2004 documents institutional herding behavior with longer-horizon factor-tilt result; bar-of-fire framing not supported. But this strategy uses Sias 2004 to motivate the 13F gate as an eligibility-filter (not bar-of-fire trigger), which is more defensible than SM-9's bar-of-fire framing |
| "Lo-Wang 2000 RFS volume-as-information" | ✅ Lo-Wang 2000 RFS "Trading Volume: Definitions, Data Analysis, and Implications of Portfolio Theory" establishes volume as information. Correctly attributed to the `vol_spike_2x` EVENT gate. |
| "retail tape volume confirming institutional accumulation suggests the price discovery is broadly recognized" | ⚠ **Partial-honest framing** — the wording "confirming" implies the volume gate VALIDATES the 13F gate at bar-of-fire, which is structurally true (the EVENT IS the timing signal). This is the BEST docstring in the SM cluster Pattern-B-eligible family. |
| **"Reduces false-positive risk on stale 13F filings (45-day reporting lag)"** | ✅ **EXPLICITLY ACKNOWLEDGES THE LAG.** Only strategy in the entire 13F family that does this. The "stale 13F filings" wording is exactly the honest framing the reviewer F1 + F2 + B611 deletion precedent called for. Partial Pattern B credit. |

**Net Step 4 verdict:** SM-28 is the HIGHEST-QUALITY 13F-family strategy in the cluster. Docstring acknowledges the lag; structure has 1 EVENT gate doing the timing work; Lo-Wang 2000 citation correctly applied. The only material issue is Pattern A silent-gap on the 50-EMA gate.

### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations on SM-28 specifically
- B663 family-bug applies (Pattern A on `price_above_ema_50`); WAVE 2 family fix queued
- Reviewer F1 marginal-contribution test applies post-B660 + post-cube — what does 13F STATE add over standalone `vol_spike_2x + price_above_ema_50`? This is the most important ablation in the cluster because SM-28 has the cleanest structure for the test.
- Companion to deleted SM-23 SHORT mirror — SM-28 is the LONG-side equivalent that DIDN'T need deletion because data semantics align

### Step 6 — Missing-inverse + economic-symmetry

- 13F long-only by SEC rule
- LONG side aligns with data semantics (Pattern C does NOT apply to SM-28 LONG)
- The deleted SM-23 SHORT mirror was Pattern C; B670 Class 7 NEW `strat_vol_spike_2x_below_ema_50_short` (without 13F gate) covers the SHORT side honestly
- **Recommended follow-up:** Consider registering Class 7 NEW `strat_vol_spike_2x_above_ema_50_long` (without 13F gate) as the LONG-side counterpart of B670's SHORT Class 7 NEW — this would also serve as the empirical baseline for Pattern F ablation against SM-28's 3-gate. Post-B660 + post-cube decision.

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F1 Pattern A** | `price_above_ema_50` default-True silent-gap; WAVE 2 family-bug eligible | MEDIUM | (post-B663 WAVE 2 sweep) |
| **F-state-as-event Pattern B (PARTIAL-HONEST)** | Docstring explicitly acknowledges 45-day lag — only strategy in the 13F family that does this. Best-in-class. Minor polish would tighten "confirming institutional accumulation" → "confirming the 45-day-old institutional snapshot is still active" | LOW | F1 |
| **F-marginal-contribution Pattern F** | Most important ablation in the cluster — does 13F STATE add empirical alpha over standalone `vol_spike_2x + EMA`? Post-B660 + post-cube test; SM-28 is the cleanest specimen for the F1 reviewer test | HIGH | F1 |
| **F-cross-source-canonical structure** | ✅ EVENT-anchored timing + STATE eligibility = correct structure; volume-on-tape variant of SM-25/SM-26 cross-source canonical pattern | INFO / ✅ POSITIVE | F1 |
| F-fire-count | Volume × 13F co-occurrence → ~50-100/yr universe-wide; PASS likely | INFO | F4-adjacent |
| F-citation | Sias 2004 stretch (same as SM-7/SM-23) but used as eligibility-not-trigger motivation; defensible. Lo-Wang 2000 correctly applied to vol_spike_2x | INFO | F7 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Pattern A fix only (WAVE 2 family sweep) |
| (c) (b) + minor docstring polish — "confirming the 45-day-old institutional snapshot is still active" replaces "confirming institutional accumulation" |
| (d) (c) + Pattern F ablation post-B660 + post-cube + register Class 7 NEW `strat_vol_spike_2x_above_ema_50_long` (no-13F baseline) for the ablation |
| **(e) RECOMMENDED — (d). SM-28 is the cleanest specimen for the F1 marginal-contribution test; bundling Class 7 NEW LONG baseline registration enables the test directly** |

**My recommendation: (e).** SM-28 is the right strategy to anchor the F1 marginal-contribution ablation because (i) it has the cleanest cross-EVENT/STATE structure, (ii) its docstring is the most honest about the lag, (iii) the SHORT-side baseline (B670 Class 7 NEW `strat_vol_spike_2x_below_ema_50_short`) already exists; the symmetric LONG-side baseline would close the test design.

**Awaiting owner direction on SM-28:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (e)
2. Whether to register Class 7 NEW `strat_vol_spike_2x_above_ema_50_long` as F1 ablation baseline (would bring strategy count 222 → 223; symmetric with B670's SHORT addition)
3. Pattern A WAVE 2 family sweep timing
4. Confirm Sias 2004 citation retention as eligibility-motivation (vs full retraction)

---

## SM-29. `strat_classification_change_with_institutional_long` (337 reclassification overlay, walked — Pattern B candidate with EVENT-anchor partial credit)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672g full expansion). 3-gate LONG combining sector-reclassification EVENT with 13F STATE and 200-EMA regime. Partial Pattern B — the docstring "highest-conviction re-rating signal" implies dual bar-of-fire confirmation, but only the reclassification EVENT supplies bar-of-fire timing; the 13F STATE is an eligibility filter (factor-tilt level). Brogaard-Heath-Saadi 2019 + Cohen-Frazzini-Malloy 2008 citations correctly attributed individually but combined into an overclaiming "highest-conviction" framing.

### Step 1 — Read the code

[screener.py:4830-4845](backtest/signals/screener.py#L4830-L4845):

```python
def strat_classification_change_with_institutional_long(s):
    """Wave 3 (Batch 337): smart-money validates re-rating. Reclassification
    co-incident with institutional accumulation = highest-conviction
    re-rating signal. Brogaard-Heath-Saadi 2019 (re-rating) +
    Cohen-Frazzini-Malloy 2008 (institutional cluster)."""
    fires = (
        s.get("classification_changed_recent", False)
        and s.get("institutional_buy", False)
        and s.get("price_above_ema_200", False)
    )
    new_sec = s.get("new_sector", "?")
    return _strat(fires, "long", "classification_change",
        ["classification_changed_recent","institutional_buy","price_above_ema_200"],
        [f"Reclassified to {new_sec} + institutional accumulation",
         "Dual signal: analyst re-rating + smart-money conviction",
         "Above 200 EMA (regime gate)"])
```

**3-gate LONG strategy.** Overlay strategy combining an analyst/index-classification reclassification EVENT with a 13F STATE eligibility filter and 200-EMA regime gate.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `classification_changed_recent` | EVENT: sector/index reclassification within last 90 days (per Batch 337 producer) |
| `institutional_buy` | 13F STATE: new/increased positions this quarter (eligibility filter; 45-day SEC lag) |
| `price_above_ema_200` | Long-term uptrend; B663-fixed (default False not True) |

### Step 2 — Classify

- Category: `classification_change` (NOT smart_money_13f despite the 13F gate — reflects the reclassification EVENT being the primary economic mechanism)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663 (Pattern A WAVE 1 family fix on 200-EMA default-True → False)

### Step 3 — Producer source-read + temporality

- `classification_changed_recent` is produced by Batch 337 sector-reclassification producer (in [smart_money.py](backtest/data/smart_money.py) or a sector-classification helper). Per CHECKLIST (s), this is an **EVENT** with a defined 90-day decay window — the reclassification IS the timing signal. Lag depends on data source (S&P/MSCI/Russell/index publisher) but typically <5 business days from announcement.
- `institutional_buy` STATE quarterly per Batch 330 13F producer (45-day SEC lag per DEC-325)
- `price_above_ema_200` STATE

**EVENT/STATE composition:** **1 EVENT gate (reclassification) + 2 STATE gates.** Per CHECKLIST (s), this is a CORRECT cross-EVENT/STATE structure where the EVENT IS the timing trigger. Same canonical structure as SM-25/SM-26/SM-28 (cross-source canonicals). Pattern B concern is contained to the "highest-conviction" docstring framing, NOT the strategy structure.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Brogaard-Heath-Saadi 2019 (re-rating)" | ✅ Correctly attributed — Brogaard, Heath, Saadi 2019 JFE (or similar) documents alpha from sector/index reclassification events. Correctly applied to the reclassification EVENT gate. |
| "Cohen-Frazzini-Malloy 2008 (institutional cluster)" | ✅ Correctly attributed — but applies to long-horizon factor-tilt result, not bar-of-fire timing. Same citation-stretch concern as SM-7/SM-21/SM-22/SM-24. When framed as eligibility-filter motivation (not timing trigger), defensible. |
| "smart-money validates re-rating" | ⚠ **Partial Pattern B** — the 13F STATE doesn't "validate" the reclassification EVENT at bar-of-fire; it's at most a coincident-or-prior holding snapshot. "Validates" implies temporal sequence (reclassification first, validation second) which the data doesn't establish. Honest reframe: "13F STATE-filters for reclassification names with institutional sponsorship; reclassification EVENT is the bar-of-fire trigger." |
| "highest-conviction re-rating signal" | ⚠ **Overclaiming** — same Pattern B class. Honest framing: "reclassification EVENT in 13F-sponsored names" (descriptive, not conviction-ranking). |

### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations on SM-29 specifically
- Reviewer F1 marginal-contribution test applies post-B660 + post-cube — what does the 13F STATE add over standalone `classification_changed_recent + price_above_ema_200` (which would be SM-29-base from Batch 337 first wave)?
- Companion SM-30 is the insider-cluster variant of the same pattern; conjoint walk surfaces 13F-STATE vs insider-cluster-EVENT comparison

### Step 6 — Missing-inverse + economic-symmetry

- Classification changes happen in BOTH directions (sector upgrades AND downgrades) — the SHORT mirror `strat_classification_change_with_institutional_short` is NOT obviously asymmetric the way 13F-only SHORT is
- But 13F STATE itself is long-only (Pattern C asymmetry); combining a directionally-symmetric reclassification with an asymmetric data source still inherits the asymmetry
- **No SHORT mirror currently registered.** Per `feedback_asymmetric_data_sources_break_mechanical_inverse`, do NOT propose mechanical Class 7 SHORT mirror; the 13F gate would be Pattern C noise on the SHORT side. Better Class 7 NEW candidate (if SHORT-side reclassification is interesting): `strat_classification_change_with_insider_short` (analogous to SM-30) which would have 2 EVENT gates with NO 13F dependency — but insider-sale-cluster signals are also asymmetric per the same feedback rule.
- **Recommended:** No SHORT mirror at present.

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-cross-source-canonical structure** | ✅ EVENT-anchored timing + STATE eligibility = correct structure; reclassification variant of cluster pattern | INFO / ✅ POSITIVE | F1 |
| **F-state-as-event Pattern B (PARTIAL)** | "Highest-conviction" + "smart-money validates re-rating" docstring framing implies 13F STATE provides bar-of-fire validation; reframe to "13F-filters reclassified names" | MEDIUM | F1 |
| **F-marginal-contribution Pattern F** | What does 13F STATE add over standalone `classification_changed_recent + 200-EMA` (Batch 337 base)? Post-B660 + post-cube ablation | MEDIUM | F1 |
| F-fire-count | Reclassification × 13F-buy co-occurrence rare — projected ~10-25/yr universe-wide; borderline FAIL on min_trades=30 per regime | MEDIUM | F4 |
| F1 default-True | `price_above_ema_200` FIXED B663 ✅ | ✅ SHIPPED B663 | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) Pattern B reframe — "13F-filters reclassified names" replaces "validates" / "highest-conviction" |
| (c) (b) + Pattern F ablation post-B660 + post-cube comparing 3-gate to 2-gate (no 13F) baseline |
| **(d) RECOMMENDED — (c). EVENT-anchored structure is correct; docstring reframe handles partial Pattern B; ablation settles whether 13F STATE earns its place** |
| (e) Tighten — switch `institutional_buy` to `institutional_strong_buy` (higher threshold); reduces fires but only addresses Pattern F if the stronger 13F gate has different marginal contribution |

**My recommendation: (d).** Same logic as SM-25/SM-26 — cross-source canonical structure is correct; docstring reframe + ablation handle the partial Pattern B + Pattern F concerns.

**Awaiting owner direction on SM-29:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (d)
2. Pattern F ablation should bundle with SM-30 (insider variant) for joint dose-response test
3. Confirm "no SHORT mirror" disposition per economic-symmetry analysis

---

## SM-30. `strat_classification_change_with_insider_long` (337 reclassification overlay, walked — 2 EVENT gates, NOT Pattern B)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672g full expansion). 3-gate LONG with **2 EVENT gates** — reclassification EVENT + insider-cluster EVENT. **NOT a Pattern B candidate** because docstring "board-level + analyst re-rating agreement" framing is HONEST — both timing events are bar-of-fire. The cluster's only fire-count concern in sub-cluster D (5-15/yr universe-wide projected). Cohen-Malloy-Pomorski 2012 + Brogaard-Heath-Saadi 2019 citations correctly attributed.

### Step 1 — Read the code

[screener.py:4848-4862](backtest/signals/screener.py#L4848-L4862):

```python
def strat_classification_change_with_insider_long(s):
    """Wave 3 (Batch 337): insider validates re-rating. Insider cluster
    co-incident with reclassification = board-level + analyst agreement.
    Cohen-Malloy-Pomorski 2012 (insider) + reclassification literature."""
    fires = (
        s.get("classification_changed_recent", False)
        and s.get("insider_cluster_active", False)
        and s.get("price_above_ema_200", False)
    )
    new_sec = s.get("new_sector", "?")
    return _strat(fires, "long", "classification_change",
        ["classification_changed_recent","insider_cluster_active","price_above_ema_200"],
        [f"Reclassified to {new_sec} + insider cluster buying",
         "Board-level + analyst re-rating agreement",
         "Above 200 EMA (regime gate)"])
```

**3-gate LONG strategy.** Most EVENT-anchored strategy in the smart-money cluster — both signal gates are bar-of-fire EVENTS.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `classification_changed_recent` | EVENT: sector/index reclassification within last 90 days |
| `insider_cluster_active` | EVENT: insider buying cluster active (per CMP 2012 cluster definition) |
| `price_above_ema_200` | Long-term uptrend; B663-fixed |

### Step 2 — Classify

- Category: `classification_change` (NOT smart_money — sub-cluster D classification overlay)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663

### Step 3 — Producer source-read + temporality

- `classification_changed_recent` EVENT per Batch 337 producer (90-day decay window; <5-day lag from announcement)
- `insider_cluster_active` is produced by the [insider producer](backtest/data/smart_money.py) per Cohen-Malloy-Pomorski 2012 JF cluster definition. The "cluster active" state requires N+ insider buys within a window — this is technically a STATE that summarizes recent EVENTS, but per CHECKLIST (s) it IS a bar-of-fire EVENT signal class because the underlying transactions are Form-4 EVENTs with 2-day lag. The active-cluster state is computed at bar-of-fire from the most recent EVENTs.
- `price_above_ema_200` STATE

**EVENT/STATE composition:** **2 EVENT gates + 1 STATE gate.** Per CHECKLIST (s), this is GENUINELY COMPOSITE-OF-EVENTS — both reclassification and insider cluster supply bar-of-fire timing signal. The "board-level + analyst re-rating agreement" framing is HONEST. This is the MOST EVENT-anchored strategy in the smart-money cluster.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Cohen-Malloy-Pomorski 2012 (insider)" | ✅ Correctly attributed — CMP 2012 JF "Decoding Inside Information" establishes the insider-cluster signal premium. Correctly applied to the insider-cluster EVENT gate. |
| "reclassification literature" | ⚠ Generic — would be tighter to cite Brogaard-Heath-Saadi 2019 specifically (already cited in SM-29). Citation precision LOW concern. |
| "Insider cluster co-incident with reclassification = board-level + analyst agreement" | ✅ **HONEST framing** — both signals ARE bar-of-fire events; the wording "co-incident" + "agreement" correctly credits the joint EVENT structure. NOT a Pattern B candidate. |
| "Board-level + analyst re-rating agreement" | ✅ Both insider (board-level + officer) and reclassification (analyst-driven via index inclusion/sector boundaries) are bar-of-fire EVENTs; "agreement" correctly frames the joint trigger |

**Net Step 4 verdict:** SM-30 is the HIGHEST-QUALITY walk in the smart-money cluster. 2 EVENT gates + honest docstring framing + correctly-attributed citations. **NOT a Pattern B candidate.** The only concern is fire-count.

### Step 5 — OPEN_INVESTIGATIONS grep

- No active investigations on SM-30 specifically
- **Fire-count concern** — queued as `S5-SM30-FIRE-COUNT-MEASUREMENT` for B660 follow-up
- Reviewer F1 marginal-contribution applies but SM-30's structure is so clean the ablation question is different — what does adding insider-cluster EVENT over standalone `classification_changed_recent + 200-EMA` baseline buy? The right comparison is SM-29 vs SM-30 vs base.

### Step 6 — Missing-inverse + economic-symmetry

- Insider EVENTs are heavily asymmetric (insider BUYING is positive-information; insider SELLING is mostly diversification not signal per CMP 2012 + `feedback_asymmetric_data_sources_break_mechanical_inverse`)
- Reclassification is directionally symmetric in principle (upgrades and downgrades) but combining with insider buying-cluster gates the LONG side only
- **No SHORT mirror viable** — same conclusion as SM-29 per economic-symmetry rule

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-cross-source-canonical structure** | ✅ 2 EVENT gates + honest docstring = best-in-class smart-money cluster strategy | INFO / ✅ POSITIVE | F1 |
| **F-state-as-event Pattern B** | ✅ NOT a Pattern B candidate. Both signal gates are bar-of-fire EVENTs | ✅ NOT APPLICABLE | F1 |
| **F-fire-count** | Co-occurrence of 2 EVENTs + STATE regime → projected ~5-15/yr universe-wide; **HIGH RISK FAIL on min_trades=30 per regime** | HIGH | F4 |
| **F-marginal-contribution Pattern F** | Three-way ablation: SM-29 (13F variant) vs SM-30 (insider variant) vs base (`classification_changed_recent + 200-EMA`) — surfaces which validating signal earns its place | MEDIUM | F1 |
| F-citation | "Reclassification literature" generic — tighten to Brogaard-Heath-Saadi 2019 | LOW | F7 |
| F1 default-True | `price_above_ema_200` FIXED B663 ✅ | ✅ SHIPPED B663 | — |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo (RECOMMENDED if fire-count is acceptable per F4) |
| (b) Loosen `insider_cluster_active` threshold (e.g., relax cluster N-buyer minimum) to raise fire count |
| (c) Drop 200-EMA gate to raise fire count (would convert to pure 2-EVENT composite) |
| (d) Status quo + post-B660 fire-count measurement settles whether to keep or loosen |
| **(e) RECOMMENDED — (d). Strategy structure is best-in-class; no docstring change needed; fire-count empirical measurement settles disposition** |
| (f) Mark EXPLORATORY per low-fire-combo cluster (similar to W5/W5m precedent) — exclude from cube selection budget while keeping registered for cube-replay coverage |

**My recommendation: (e).** SM-30 is the gold-standard walk in the smart-money cluster — no code/doc changes needed. The only disposition question is whether the projected ~5-15/yr fire count is operationally tolerable; post-B660 measurement settles it. If <30 fires per regime, route to (f) EXPLORATORY marker per the W5/W5m precedent.

**Awaiting owner direction on SM-30:**
1. (a)/(b)/(c)/(d)/(e)/(f) — recommendation (e); fallback (f) if B660 confirms <30 fires/regime
2. Bundle Pattern F three-way ablation (SM-29 + SM-30 + base) post-cube
3. Citation tightening optional (Brogaard-Heath-Saadi 2019) — defer until next walk-doc sync

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

## SM-31. `strat_bollinger_tight_with_smart_money_long` (confluence wrap, walked — Pattern E candidate)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672h full expansion). 4-gate LONG sleeve wrap combining Bollinger squeeze + bullish bar + 200-EMA + `_has_smart_money_buy` UNION helper. **Pattern E candidate** — the bullet text "Smart-money buy confirmation" implies bar-of-fire confluence, but per B613 the helper is a UNION ELIGIBILITY FILTER (EVENT-or-STATE) not a confluence signal. SM-34 + SM-35 already received B613 honesty reframe; SM-31 has not. Also a residual Pattern A concern on `close_above_open` default-True (separate from the B663 sweep family).

### Step 1 — Read the code

[screener.py:5781-5795](backtest/signals/screener.py#L5781-L5795):

```python
def strat_bollinger_tight_with_smart_money_long(s):
    """Bollinger-tight squeeze + smart-money confirmation. Sleeve variant
    of bollinger_tight base; smart-money signal validates the squeeze
    is fundamentally backed rather than technical-only."""
    base_fires = (
        s.get("bb_squeeze", False)
        and s.get("close_above_open", True)  # ⚠ Pattern A default-True
        and s.get("price_above_ema_200", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["bb_squeeze", "close_above_open", "price_above_ema_200",
         "smart_money_buy"],
        ["Bollinger band squeeze tight", "Above 200 EMA",
         "Smart-money buy confirmation"])  # ⚠ Pattern E bullet text
```

**4-gate LONG sleeve wrap.** Base strategy is `bollinger_tight + close_above_open + 200-EMA`; the sleeve appends `_has_smart_money_buy` as a UNION eligibility filter.

**LONG fires when ALL FOUR:**

| Gate | Meaning |
|---|---|
| `bb_squeeze` | Bollinger band width below 25th percentile (squeeze STATE; technical compression) |
| `close_above_open` | Today's bullish bar — ⚠ Pattern A default-True silent-gap (separate family from B663 ema-200 sweep) |
| `price_above_ema_200` | Long-term uptrend; B663-fixed |
| `_has_smart_money_buy(s)` | UNION (insider_cluster_active OR cfo_buy OR large_dollar_buy OR institutional_strong_buy OR institutional_buy) — see B613 helper docstring |

### Step 2 — Classify

- Category: `smart_money_sleeve` (NOT smart_money_13f or smart_money_combo — this is a SLEEVE variant of a technical-base strategy)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663 (Pattern A WAVE 1 on 200-EMA default-True → False)

### Step 3 — Producer source-read + temporality

- `bb_squeeze` STATE — Bollinger band-width percentile computed in [technical.py](backtest/signals/technical.py); rolling 252-day percentile, STATE-flavored regime gate
- `close_above_open` is technically EVENT-shaped (today's bar) but ⚠ default-True silent-gap means missing data auto-passes
- `price_above_ema_200` STATE
- `_has_smart_money_buy(s)` is the UNION helper — when only the STATE half is True (13F STATE without insider EVENT), the wrap reduces to "bollinger_squeeze + bullish_bar + 200-EMA + 13F-sponsored-name" with NO bar-of-fire conviction. When the EVENT half is True, the wrap is genuinely EVENT-anchored.

**EVENT/STATE composition:** **Variable** — depending on which OR-branch of the UNION fires:
- EVENT branch active (insider_cluster / cfo_buy / large_dollar_buy True): 1 EVENT gate + 3 STATE gates → cross-source canonical structure
- STATE-only branch active (only institutional_buy or institutional_strong_buy True): 0 EVENT gates + 4 STATE gates → Pattern B class
- Per CHECKLIST (s) + B613 helper analysis: alpha attribution differs by branch. Bullet text doesn't distinguish.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Sleeve variant of bollinger_tight base; smart-money signal validates the squeeze is fundamentally backed rather than technical-only" | ⚠ **Pattern E framing** — "validates" implies confluence; UNION helper is OR-aggregate not AND-confluence. Same class as SM-34 pre-B613 reframe. |
| Bullet "Smart-money buy confirmation" | ⚠ **Pattern E** — should be reframed per B613 template: "Smart-money EVENT(timing) or STATE(eligibility) buy per B613 F2a" |
| Implicit thesis "smart-money + technical-squeeze = high-conviction trigger" | ⚠ STATE-only branch case is NOT a high-conviction trigger; it's bollinger_tight + 13F-sponsored eligibility filter |

### Step 5 — OPEN_INVESTIGATIONS grep

- B613 honesty-reframe pattern queued for the 9 remaining confluence wraps (SM-31 + SM-32 + SM-33 + SM-36 + SM-37 + SM-38 + SM-39 + SM-40 + SM-41)
- Pattern A `close_above_open` default-True is a separate family from B663 ema-200 sweep — could surface as its own WAVE 3 family sweep

### Step 6 — Missing-inverse + economic-symmetry

- No SHORT mirror. Per `feedback_asymmetric_data_sources_break_mechanical_inverse` + B613 `_has_smart_money_sell` DELETION precedent: the smart-money SELL helper was deleted because 4 of 5 components were never emitted; the surviving signal didn't supply bear conviction
- Mechanical SHORT mirror (`strat_bollinger_tight_with_smart_money_short` using a deleted SELL helper) was correctly NOT registered

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-E UNION-as-confluence** | Bullet text "Smart-money buy confirmation" overclaims confluence; B613 honesty reframe template applies | LOW-MEDIUM | F1 / Pattern E (cross-cluster) |
| **F1 Pattern A `close_above_open`** | Separate from B663 200-EMA WAVE 1 sweep; `close_above_open` default-True silent-gap. LOW priority because `close_above_open` is near-universally emitted by candle producer (silent-gap risk is low) | LOW | (separate WAVE 3 sweep candidate) |
| F-fire-count | Squeeze × smart-money UNION rare; projected ~10-25/yr universe-wide; borderline | INFO | F4 |
| F-marginal-contribution Pattern F | Within-strategy EVENT-branch vs STATE-only-branch ablation possible at cube replay; would settle whether STATE-only-branch fires are economically distinct | MEDIUM | F1 |

**Options:**

| Option | Description |
|---|---|
| (a) Status quo |
| (b) B613 honesty-reframe bullet text — change "Smart-money buy confirmation" to "Smart-money EVENT(timing) or STATE(eligibility) buy per B613 F2a"; same template as SM-34 |
| (c) (b) + branch-stratified cube replay surfacing EVENT-branch vs STATE-only-branch verdict per (strategy × exit) cell |
| **(d) RECOMMENDED — (b) immediately + (c) post-cube. (b) is a pure docstring honesty reframe with zero risk; (c) requires cube-replay infrastructure to support stratification by `_has_smart_money_buy` active-branch** |
| (e) Pattern A `close_above_open` family sweep (separate from B663) — defer pending broader silent-gap audit |

**My recommendation: (d).** Bundle SM-31 + SM-32 + SM-33 + SM-36 + SM-37 + SM-38 + SM-39 + SM-40 + SM-41 (9 wraps) into a single B-N bullet-text reframe batch per B613 template.

**Awaiting owner direction on SM-31:**
1. (a)/(b)/(c)/(d)/(e) — recommendation (d) bundled across 9 wraps
2. Pattern F branch-stratified cube replay scope confirmation (post-B660)
3. Pattern A `close_above_open` family sweep separate decision

---

## SM-32. `strat_mfi_oversold_with_smart_money_long` (confluence wrap, walked — Pattern E candidate)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672h full expansion). 3-gate LONG sleeve wrap combining MFI oversold + 200-EMA + `_has_smart_money_buy` UNION. Same Pattern E concern as SM-31; bundled disposition recommended.

### Step 1 — Read the code

[screener.py:5798-5809](backtest/signals/screener.py#L5798-L5809):

```python
def strat_mfi_oversold_with_smart_money_long(s):
    """MFI oversold + smart-money buy. Money-flow oversold often precedes
    a bounce; smart-money buy raises confidence the bounce is real."""
    base_fires = (
        s.get("mfi_14_oversold", False)
        and s.get("price_above_ema_200", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["mfi_14_oversold", "price_above_ema_200", "smart_money_buy"],
        ["MFI(14) oversold", "Above 200 EMA",
         "Smart-money buy confirmation"])  # ⚠ Pattern E bullet text
```

**3-gate LONG sleeve wrap.** Base strategy is `mfi_14_oversold + 200-EMA`; the sleeve appends `_has_smart_money_buy` as a UNION eligibility filter.

**LONG fires when ALL THREE:**

| Gate | Meaning |
|---|---|
| `mfi_14_oversold` | Money Flow Index 14-period below oversold threshold (mean-reversion EVENT-shaped) |
| `price_above_ema_200` | Long-term uptrend; B663-fixed |
| `_has_smart_money_buy(s)` | UNION helper (see SM-31 walk) |

### Step 2 — Classify

- Category: `smart_money_sleeve`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663

### Step 3 — Producer source-read + temporality

- `mfi_14_oversold` is technically EVENT-shaped (today's oversold state from rolling 14-bar MFI calc); per CHECKLIST (s) classify as STATE-derived EVENT-trigger boundary case
- `price_above_ema_200` STATE
- `_has_smart_money_buy(s)` UNION helper (variable EVENT/STATE per branch — see SM-31 walk)

**EVENT/STATE composition:** Variable depending on UNION branch active — same as SM-31. The MFI-oversold gate is genuinely EVENT-shaped (today's oversold trigger) so the EVENT-branch case is 2 EVENT + 1 STATE; the STATE-only branch case is 1 EVENT + 2 STATE.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Money-flow oversold often precedes a bounce" | ✅ Defensible at the technical-signal level; well-known mean-reversion behavior |
| "smart-money buy raises confidence the bounce is real" | ⚠ **Pattern E** — same as SM-31; the UNION-as-confluence framing |
| Bullet "Smart-money buy confirmation" | ⚠ **Pattern E** — bundled bullet-text reframe with SM-31 et al. |

### Step 5 — OPEN_INVESTIGATIONS grep

- Same B613 honesty-reframe queue as SM-31

### Step 6 — Missing-inverse + economic-symmetry

- No SHORT mirror — same data-source-asymmetry reasoning as SM-31

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-E UNION-as-confluence** | Same bullet text overclaim as SM-31; bundle reframe | LOW-MEDIUM | F1 / Pattern E |
| F-fire-count | MFI-oversold + smart-money UNION → projected ~15-40/yr universe-wide; borderline | INFO | F4 |
| F-marginal-contribution Pattern F | Branch-stratified cube replay applies (same as SM-31) | MEDIUM | F1 |

**Options:** Same as SM-31 — bundle into 9-wrap B-N batch.

**My recommendation: (d) bundled with SM-31 + others.**

**Awaiting owner direction on SM-32:**
1. (a)/(b)/(c)/(d) — recommendation (d) bundled
2. Same Pattern F branch-stratified cube replay scope confirmation

---

## SM-33. `strat_rsi_oversold_with_smart_money_long` (confluence wrap, walked — Pattern E candidate)

> **Status:** ⏳ WALKED + AWAITING OWNER DIRECTION (B672h full expansion). 3-gate LONG sleeve wrap; RSI-oversold variant of SM-32 (MFI-oversold). Same Pattern E disposition; bundled.

### Step 1 — Read the code

[screener.py:5812-5823](backtest/signals/screener.py#L5812-L5823):

```python
def strat_rsi_oversold_with_smart_money_long(s):
    """RSI oversold + smart-money buy. Classic mean-reversion entry with
    institutional / insider corroboration."""
    base_fires = (
        s.get("rsi_14_oversold", False)
        and s.get("price_above_ema_200", False)
    )
    fires = base_fires and _has_smart_money_buy(s)
    return _strat(fires, "long", "smart_money_sleeve",
        ["rsi_14_oversold", "price_above_ema_200", "smart_money_buy"],
        ["RSI(14) oversold", "Above 200 EMA",
         "Smart-money buy confirmation"])  # ⚠ Pattern E bullet text
```

**3-gate LONG sleeve wrap.** Structurally identical to SM-32 with `rsi_14_oversold` replacing `mfi_14_oversold`.

**LONG fires when ALL THREE:** (analogous to SM-32; rsi_14_oversold replaces mfi_14_oversold)

### Step 2 — Classify

- Category: `smart_money_sleeve`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Last touched: B663

### Step 3 — Producer source-read + temporality

Same as SM-32 with RSI instead of MFI. RSI-oversold is the canonical Wilder 1978 mean-reversion trigger; same EVENT-shaped boundary-case classification.

### Step 4 — Doc-vs-thesis

| Claim | Verification |
|---|---|
| "Classic mean-reversion entry with institutional / insider corroboration" | ⚠ **Pattern E** — "corroboration" implies confluence; UNION helper is not confluence |
| Bullet "Smart-money buy confirmation" | ⚠ **Pattern E** — bundled bullet-text reframe |

### Step 5 — OPEN_INVESTIGATIONS grep

- Same B613 queue as SM-31/SM-32

### Step 6 — Missing-inverse + economic-symmetry

- No SHORT mirror — same reasoning as SM-31/SM-32

### Step 7 — Findings + options

| # | Finding | Severity | Reviewer cross-ref |
|---|---|---|---|
| **F-pattern-E UNION-as-confluence** | Same bullet text overclaim; bundle reframe | LOW-MEDIUM | F1 / Pattern E |
| F-fire-count | RSI-oversold + smart-money UNION → projected ~20-50/yr universe-wide; modest PASS likely | INFO | F4 |
| F-marginal-contribution Pattern F | Branch-stratified cube replay applies (same as SM-31/SM-32); also relevant for RSI-vs-MFI dose-response (SM-32 vs SM-33) | MEDIUM | F1 |
| F-RSI-vs-MFI ablation candidate | Companion ablation: RSI captures price-momentum; MFI captures price-volume momentum. Cube replay surfaces which mean-reversion trigger is more informative | LOW-MEDIUM | F1 |

**Options:** Same as SM-31/SM-32 — bundle into 9-wrap B-N batch.

**My recommendation: (d) bundled with SM-31 + SM-32 + others.**

**Awaiting owner direction on SM-33:**
1. (a)/(b)/(c)/(d) — recommendation (d) bundled
2. Pattern F RSI-vs-MFI dose-response cube ablation candidate (SM-32 vs SM-33)

---

## SM-34. `strat_52w_high_breakout_with_smart_money_long` (B613-walked, REFERENCE TEMPLATE for Pattern E reframe)

> **Status:** ✅ ALREADY WALKED + REFRAMED B613 (2026-06-07). Docstring honestly reframed per B613 F1+F2a+a (EVENT vs STATE bullet text + close_in_top_40pct gate added). This walk is the CANONICAL Pattern E fix template — bullet text "Smart-money EVENT(timing) or STATE(eligibility) buy per B613 F2a" replaces the original overclaiming "Smart-money buy confirmation." George-Hwang 2004 JF 52-week-high anomaly cited correctly for the price-momentum mechanism. Lineage: B588 → B589 → B613.

### Step 1 — Read the code (post-B613)

[screener.py:5826-5866](backtest/signals/screener.py#L5826-L5866): 5-gate LONG with B613 honest framing (52w-high breakout EVENT + bullish close-bar EVENT + 200-EMA + close_in_top_40pct + UNION smart-money).

### Step 2-6 (compact — post-B613)

- Category: `smart_money_sleeve` (52w-high variant)
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- EVENT/STATE composition: 2 genuine EVENT gates (52w-breakout + close-bar bullish) + STATE gates; B613 reframe acknowledges the UNION helper's variable EVENT/STATE behavior

### Step 7 — Findings + options (post-B613 CLOSED)

| # | Finding | Severity | Disposition |
|---|---|---|---|
| **F1 Pattern E reframe shipped B613** | Bullet text "Smart-money EVENT(timing) or STATE(eligibility) buy per B613 F2a" | ✅ SHIPPED B613 | — |
| **F2a `close_in_top_40pct` gate added B613** | Additional close-strength filter to reduce false 52w-high breakouts | ✅ SHIPPED B613 | — |
| F-fire-count | Cube replay will surface empirical verdict per (strategy × exit) cell | INFO | post-cube |

### FINAL STATUS POST-B613 — ✅ CLOSED

**No further B664 action required.** This walk is the REFERENCE TEMPLATE for the SM-31/SM-32/SM-33/SM-36/SM-37/SM-38/SM-39/SM-40/SM-41 Pattern E reframe.

---

## SM-35. `strat_52w_high_breakout_with_smart_money_vol_below_long` (B613 B-twin, B613-walked)

> **Status:** ✅ ALREADY WALKED B613 (2026-06-07). B-twin A/B-test variant of SM-34 (`vol_below_avg` instead of `vol_spike_12x`; Bulkowski 2005 retest absorption thesis). Same B613 honesty framing as SM-34. Cube replay will surface empirical verdict per (strategy × exit) cell to settle vol-spike vs vol-quiet 52w-high breakout dose-response.

### Step 1 — Read the code (post-B613)

[screener.py:5868-...](backtest/signals/screener.py#L5868): 5-gate LONG B-twin of SM-34 with `vol_below_avg` substituted for `vol_spike_12x`.

### Step 2-6 (compact — post-B613)

- Category: `smart_money_sleeve`
- Direction: single LONG
- STRATEGY_REGIME_AFFINITY: NO ENTRY → B291 LONG default
- Same B613 honesty framing as SM-34
- Thesis variant: Bulkowski 2005 retest-absorption — quiet-volume 52w-high breakouts represent "absorbed selling pressure" (no panic supply), historically higher continuation probability than spike-volume 52w-high breakouts

### Step 7 — Findings + options (post-B613 CLOSED)

| # | Finding | Severity | Disposition |
|---|---|---|---|
| **F1 Pattern E reframe shipped B613** | Same as SM-34 | ✅ SHIPPED B613 | — |
| **F2a `close_in_top_40pct` gate added B613** | Same as SM-34 | ✅ SHIPPED B613 | — |
| **F-vol-spike-vs-vol-quiet ablation** | Cube replay SM-34 (vol_spike) vs SM-35 (vol_below_avg) settles which volume signature gives better 52w-high breakout continuation | MEDIUM | post-cube |
| F-fire-count | vol_below_avg is more common than vol_spike → SM-35 should fire more than SM-34. Cube verdict per (strategy × exit) | INFO | post-cube |

### FINAL STATUS POST-B613 — ✅ CLOSED

**No further B664 action required.** Cube replay completes the empirical disposition.

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
