# B719 — SMC Cluster: Adversarial Review of External Reviewer's Proposal

<!-- Source: STAGE_4_SMC_CLUSTER_WALKS.md + backtest/signals/smc_ict.py + backtest/signals/smc_panel_cache.py per CHECKLIST #77 -->

**Method:** Per `feedback_line_by_line_ticket_extraction_before_synthesis` (memory rule codified B715 after owner correction). 18 actionable reviewer sentences extracted to discrete tickets BEFORE writing this synthesis doc. This doc is written FROM the queued tickets, not the other way around.

**Date:** 2026-06-12

---

## 1. Three reviewer claims source-verified at line-number level

| Reviewer claim | Source-verified location | Verdict |
|---|---|---|
| `event_recency_bars=90` default | [smc_ict.py:81](backtest/signals/smc_ict.py#L81) | VERIFIED |
| `liquidity_range_pct=0.01` (1% hardcoded) | [smc_ict.py:79](backtest/signals/smc_ict.py#L79) | VERIFIED |
| `dealing_range_lookback=50` + `ohlc.tail(50)` pattern | [smc_ict.py:80, 407-414](backtest/signals/smc_ict.py#L80) | VERIFIED |
| B555 OPT-C SMC panel-cache layer exists | [smc_panel_cache.py](backtest/signals/smc_panel_cache.py) | VERIFIED — and the doc EXPLICITLY documents the PIT-risk caveat (B554 parity test): *"The library's OB function has forward-mutating state... When precomputed on the full series, an OB at bar 100 may show different final state than when computed on a truncated slice at bar 300."* |

**The panel-cache PIT-risk is not theoretical** — the doc has acknowledged it as an OPEN CAVEAT but the cache is in production. Reviewer's elevation of Pattern K from "low-confidence" to PHASE-0 priority is empirically justified.

---

## 2. The three headline findings (re-ranked per reviewer)

The cluster doc currently treats Patterns I (detection lag), K (dealing-range lookahead), M (61% backtest = overclaim) as **three of seven mid-priority architectural concerns**. Reviewer's Part 5 critique: these should be the **three HEADLINE findings**, not items among many. B719 elevates accordingly.

### Headline 1 — Detection lag (Pattern I) is an existence-of-edge problem, not staleness
Reviewer Part 1 verbatim: *"detection lag makes 'enter at the right time' structurally impossible for 11 of 18 strategies"*. The library's swing-confirmation requires future bars (20-80 bar detection lag); the 90-bar recency window then keeps signals "active" for ~4 months after the structural break. Result: entry timing is 20-170 bars after the event, by construction. **No parameter sweep can fix this** — tightening recency below ~30 bars collides with the detection lag floor and catches nothing. Affected: SMC-1/2/3 (FVG), SMC-4/5/6/7 (OB), SMC-8/9 (dealing-range), SMC-14/15/16 (BOS/CHOCH).

**B719 actions queued:** `S4-B719-SMC-DETECTION-LAG-REFRAME-11-STRATEGIES-AS-POSITIONAL` + `S4-B719-SMC-EVENT-RECENCY-BARS-NOT-CUBE-SWEEPABLE-DOC-CORRECTION` + `S4-B719-SMC-DETECTION-LAG-FLOOR-PARAMETER-DOCSTRING-PIN`.

### Headline 2 — Dealing-range lookahead (Pattern K) is the most likely fake-edge vector
Source-verified: [smc_ict.py:408](backtest/signals/smc_ict.py#L408) `window = ohlc.tail(dealing_range_lookback)`. PIT-correct only if `ohlc` is pre-sliced; the B555 panel-cache path is the silent-break vector the doc itself acknowledges.

**B719 actions queued:** `S4-B719-SMC-PRODUCER-AUDIT-DEALING-RANGE-PATH-PIT-CHECK` + `S4-B719-SMC-PRODUCER-AUDIT-PANEL-CACHE-B555-LAYER`. Same producer-audit harness from B699/B700 chart-pattern + B704 earnings-feed PIT audits, adapted to SMC.

### Headline 3 — The 61% Quantum-Algo backtest is anti-evidence, not weak evidence
Reviewer Part 3 verbatim: *"A 61% win rate on a 2,600-trade sample across 90 cells is exactly what selection from an over-parameterized space produces... The 61% number should be treated as anti-evidence — a red flag of over-fitting — not as a baseline."* 18 strategies × ~5 exits × library-author-on-cherry-pickable-10-asset-sample = textbook over-parameterization signature.

**B719 action queued:** `S4-B719-SMC-PATTERN-M-61-PCT-ANTI-EVIDENCE-RE-FRAME` (explicit "DO NOT OPTIMIZE FROM THIS BASELINE" caveat).

---

## 3. The one genuinely-optimizable sub-cluster: liquidity-sweep (SMC-12/13/18)

Reviewer Part 4: SMC-12/13/18 = the **stop-run/failed-breakout effect** documented in non-SMC literature (same mechanism as ICT Turtle Soup). Real microstructure basis. **The one part of SMC worth tuning.**

Critical asymmetry: SMC-18 uses the **90-bar-windowed** `smc_liquidity_swept_*` — **wrong for fast stop-runs**. SMC-12/13 use `smc_equal_*_swept + FVG-active` (better-timed). Reviewer's "single highest-value tuning change in the cluster": tight 1-5 bar recency variant for SMC-18.

**B719 actions queued:**
- `S4-B719-SMC-18-LIQUIDITY-SWEEP-TIGHT-1-5-BAR-RECENCY-PARALLEL-TO-TURTLE-SOUP` — **bundle with B705 ICT Turtle Soup recency fix**; identical pattern
- `S4-B719-SMC-12-13-SWEEP-DEPTH-ATR-SCALED-PARAMETER` — ATR-scaled depth
- `S4-B719-SMC-LIQUIDITY-RANGE-PCT-HARDCODED-1PCT-REPLACE-WITH-ATR-SCALED` — Pattern O parameter externalization
- `S4-B719-SMC-12-13-STRONG-CLOSE-REVERSAL-CONFIRMATION` — close-position > 0.66 gate
- `S4-B719-SMC-CROSS-CLUSTER-CONSOLIDATE-SMC-12-13-18-WITH-ICT-TURTLE-SOUP-JUDAS-SWING` — **flagship cross-cluster action**: consolidate 7 strategies (SMC-12/13/18 + ICT-7/8/9/10) to one liquidity-sweep-reversal family

---

## 4. FVG (SMC-1/2/3): thin-to-arbitraged; heavily-crowded retail pattern

Reviewer Part 4: heavily-crowded → maximal crowding decay. If tuned: touch-vs-bounce reclaim entry + zone-tolerance sweep. Honest prior is thin edge.

**B719 actions queued:** `S4-B719-SMC-1-2-3-FVG-RECLAIM-BOUNCE-VS-TOUCH-ENTRY` + `S4-B719-SMC-1-2-3-FVG-ZONE-TOLERANCE-SWEEP` (both **gated behind producer-audit Phase 0** to confirm FVG zone definition isn't itself lookahead).

---

## 5. Trend gate addition (SMC-10/11 OTE + non-structural others)

Reviewer Part 4: *"The OTE strategies (SMC-10/11) have an additional flagged defect — no trend filter (no EMA gate) — so they fire OTE-zone entries in any trend context."* Plus cluster-wide missing-trend-filter on SMC-10/11/12/13/16/18 — but reviewer EXPLICITLY EXCLUDES structural strategies from trend-gate add (it's "rearranging gates on a lag-bound strategy"). Only non-structural (liquidity sweeps) benefit.

**B719 actions queued:** `S4-B719-SMC-10-11-OTE-ADD-TREND-FILTER-EMA-GATE` + `S4-B719-SMC-MISSING-TREND-FILTER-CLUSTER-WIDE-6-STRATEGIES`.

---

## 6. Architectural new finding: vendored-library SPOF needs loud-failure sentinel

Reviewer Closing: *"The new architectural risk this cluster surfaces — the vendored-library silent-failure SPOF — is the one thing none of the existing tools cover, and a loud-failure sentinel test is the cheap fix."*

**B719 action queued:** `S4-B719-SMC-PATTERN-L-VENDORED-LIBRARY-LOUD-FAILURE-SENTINEL-TEST`. Engine-startup test asserts `smartmoneyconcepts` library imports + key functions present; fails pyramid loudly if broken; eliminates the silent no-fire degradation that mimics "no opportunity" in cube outputs.

---

## 7. Process discipline: Pattern G "accept rarity, don't add gates"

Reviewer Part 4: SMC-12/13 are Pattern G fire-starved. *"The fix isn't more gates — it's the recency/tolerance tuning above, plus accepting these may be genuinely rare."* Adding gates makes it worse.

**B719 action queued:** `S4-B719-SMC-PATTERN-G-FIRE-STARVED-ACCEPT-RARITY-DO-NOT-ADD-GATES`. Cross-ref `feedback_minimum_fire_count_gate_before_cube`.

---

## 8. Implementation phasing (reviewer's 5 phases)

| Phase | Action | Tickets |
|---|---|---|
| **Phase 0** (PHASE-0 GATE) | Producer-audit dealing-range + B555 panel-cache | 2 |
| **Phase 1** (POSITIONAL REFRAME) | Reclassify 11 structural strategies; doc-correction | 3 |
| **Phase 2** (LIQUIDITY-SWEEP TUNING) | SMC-18 tight recency + SMC-12/13 depth/tolerance/strong-close + trend gates + cross-cluster consolidate | 7 |
| **Phase 3** (POST-B689 PATTERN J) | Marginal-contribution audit on 18 strategies / 7 effective primitives | 1 |
| **Phase 4** (ARCHITECTURAL) | Vendored-library loud-failure sentinel | 1 |
| **Phase 5** (DOC RESTRUCTURE + LIMITED FVG TUNING) | Pattern I/K/M re-rank + Pattern M anti-evidence reframe + FVG reclaim/tolerance + Pattern G discipline note | 4 |

**Total: 18 tickets across 6 phases.**

---

## 9. Cross-cluster interactions

- **B705 ICT Turtle Soup recency fix** should ship TOGETHER with `S4-B719-SMC-18-LIQUIDITY-SWEEP-TIGHT-1-5-BAR-RECENCY` — same producer-additive change, same family
- **B713 SM cluster pre-B671 short-backtest contamination** also affects SMC shorts
- **B704 earnings-feed-PIT-audit pattern** is the direct template for B719 Phase 0 (dealing-range + panel-cache)
- **B710 ceiling sweep** flagged SMC `smc_breaker_block_long/short` at 17K + 9K/yr → also subject to Pattern I detection-lag-positional reframe
- **`S4-B687-ICT-CLUSTER-PATTERN-N-CROSS-CLUSTER-CUBE-ABLATION-WITH-SMC`** (already queued) becomes the routing destination for the consolidation action

---

## 10. CHECKLIST compliance

Applied: #45 (per-recommendation source-verification — 4 claims verified at line-number level before queuing), #67 (per-turn doc sync), #69 (test pyramid — doc-only review batch), #77 (canonical source headers), #94 (per-turn EXECUTION_QUEUE update — 18 tickets queued SAME TURN per `feedback_line_by_line_ticket_extraction_before_synthesis`), #100 (final-result drift-guard), #105 (Step-3 producer source-read end-to-end including B555 panel-cache layer). The new memory rule `feedback_line_by_line_ticket_extraction_before_synthesis` (codified B715, applied B717 retroactively to B702/B705/B710, applied B719 prospectively for the first time) was the operative discipline this batch.
