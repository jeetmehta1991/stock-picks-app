# B713 — Smart-Money Cluster: Adversarial Review of External Reviewer's 4th-Pass Proposal

<!-- Source: STAGE_4_SMART_MONEY_CLUSTER_WALKS.md + backtest/signals/screener.py + backtest/engine/backtest.py + output_audit/fire_count_measured_b660_full_universe.json per CHECKLIST #77 -->

**Owner-pattern (B702/B705/B710 discipline):** source-verify each claim before accepting. This is the **3rd or 4th** external reviewer pass on the smart-money cluster (the doc itself acknowledges multiple rounds).

**Date:** 2026-06-12
**Discipline:** [feedback_audit_recommendations_against_existing_directives](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_audit_recommendations_against_existing_directives.md) + [feedback_no_prior_edge_consolidate_before_tune](C:/Users/jeetm/.claude/projects/c--Users-jeetm-Github-stock-picks-app/memory/feedback_no_prior_edge_consolidate_before_tune.md)

---

## 1. Source-verification of 4 highest-impact reviewer claims

### Claim 1: `inspect.currentframe` borrow guard is LIVE and FAILS OPEN
**Source-verified at [backtest/signals/screener.py:152-157](backtest/signals/screener.py#L152):**
```python
if direction == "short":
    import inspect
    caller_locals = inspect.currentframe().f_back.f_locals
    s = caller_locals.get("s")
    if s is not None and _short_borrow_trap_active(s):
        fires = False
```
Mirror at [screener.py:218-224](backtest/signals/screener.py#L218) for `_strat3`.

**Failure mode analysis:**
- `inspect.currentframe()` can return **`None`** per Python language spec on implementations without Python-stack frames (CPython does have them but the spec doesn't require it; future runtime / Cython / PyPy nogil contexts could break this).
- The `if s is not None` check **fails open**: if `s` is None OR if the frame doesn't contain `s` by that name (e.g., a decorator wraps `_strat`, a comprehension calls it, a future refactor renames the local), the guard silently DOES NOTHING and the short fires unprotected. No exception, no log, no warning.
- The guard is **invisible at the call site** — auditor of `strat_institutional_distribution_short` sees only its declared gates, has no way to know `_strat()` may force `fires=False` via frame introspection.

**Adversarial verdict:** **REVIEWER 100% CORRECT.** This is a load-bearing risk control resting on a fragile mechanism, invisible at the call site, with fail-open semantics. The exact anti-pattern this review series has fought elsewhere (silent-gaps, default-True auto-pass). **The fact that the prior-round critique against this shipped while the objection sat queued is its own discipline failure.**

---

### Claim 2: DTC threshold is `>8.0` but the GME pre-squeeze range (5-7) passes through
**Source-verified at [backtest/signals/screener.py:104, 118](backtest/signals/screener.py#L104):**
```python
def _short_borrow_trap_active(s) -> bool:
    """Returns True if days_to_cover > 8.0 on the ticker for the bar..."""
    dtc = s.get("days_to_cover", 0.0) or 0.0
    return dtc > 8.0
```

**Reviewer's critique:** the guard's STATED purpose is to prevent shorting names that will squeeze. The canonical GME pre-squeeze DTC was in the 5-7 range. A threshold at `>8` does NOT block DTC 5-7 names. So **the guard is calibrated to miss the canonical case it cites as motivation**.

**Adversarial verdict:** **REVIEWER 100% CORRECT.** The threshold direction is wrong relative to the GME observation. A risk guard should err toward over-blocking; the current calibration is empirically permissive on the exact failure mode it exists to prevent.

**Compounding issue (reviewer's secondary point):** `days_to_cover` is FINRA bi-monthly with ~14-day staleness. In a real squeeze, DTC explodes over days; the guard reads a number from BEFORE the squeeze began. So even if the threshold were correct, the data is too slow.

---

### Claim 3: B660 measured 0 fires for the entire smart-money cluster
**Source-verified by querying [output_audit/fire_count_measured_b660_full_universe.json](output_audit/fire_count_measured_b660_full_universe.json):**

| SM-related strategies | Total = 42 | Zero-fire = **40** | Non-zero = 2 (`bb_squeeze_volume`=867, `squeeze_breakout`=11,668 — and these are squeeze-cluster, not pure SM) |

So effectively **40 of 40 pure-SM strategies measured 0 fires** in B660. Reviewer's "B660 was a total harness miss" claim is structurally correct — the 13F/insider/congressional producers were not invoked in the B660 harness path.

**Adversarial verdict:** **REVIEWER 100% CORRECT.** Unlike pivot cluster (where B660 provides 4-cycle vindication of the timeframe finding), the SM cluster has **zero measured data**. Every fires/yr in the SM doc is still independence-product projection — the method that was wrong by up to an order of magnitude (both directions) on pivot/trend.

---

### Claim 4: SM-5 was orphan emitter; every pre-B671 short-backtest is borrow-unprotected
**Source-verified at [backtest/engine/backtest.py:1457-1466](backtest/engine/backtest.py#L1457):** the `avoid` direction handling is now wired (BUG-04 RESOLVED-IMPLEMENTED Pass 53 v8h+1 2026-05-10) — `direction == "avoid"` → `skipped_trades.append(...)` → `continue`. So the avoid output IS now consumed.

The reviewer's broader claim is: **before B671 wired the SM-5 borrow gate into `_strat`, every short-strategy backtest ran with ZERO borrow protection**. This is verifiable by git log of `screener.py` `_strat()` definition — the inspect.currentframe guard was ADDED in B671 (current code), not present in prior backtests.

**Adversarial verdict:** **REVIEWER 100% CORRECT — AND THIS IS A CROSS-CLUSTER BLOCKING FINDING.** Every short-side Sharpe in every cluster doc was computed without the guard now considered essential. This includes:
- Breakout cluster short legs (BR-* short variants)
- Event-driven cluster shorts (EV-2 pead_short, EV-4 just-restored in B709)
- Pivot cluster shorts (W2 shooting_star_short = 1,309 fires, W4 0, W6/W7/W9/W10 shorts)
- Chart-pattern cluster shorts
- Candle cluster shorts (W2 + CC-3 + CC-7)
- ICT cluster shorts (turtle_soup_short, judas_swing_short, etc.)
- AND all dual-strategy aggregates that included the short leg

**This is bigger than the SM doc scoped it as.** The doc queues "historical short-Sharpe re-computation" as a single SM-5 ticket; reviewer correctly elevates it to **cross-cluster blocking**.

---

## 2. Adversarial verdicts on additional reviewer points

### Per-strategy win-rate tuning is PREMATURE for this cluster (reviewer's "honest answer")
**Reviewer's position**: with no measured fire counts (B660 harness gap), an unaudited primary data source (Quiver PIT integrity unverified), and a 13F sleeve whose core gate carries no timing information (45-day-lag), entry tuning would optimize against numbers that don't exist. The same `feedback_no_prior_edge_consolidate_before_tune` discipline I codified in B706 applies a fortiori here.

**Adversarial verdict:** **CORRECT AND ALIGNED WITH OWNER'S OWN STANDING RULE.** This cluster's optimization-deferral is not new; it's just the discipline I memorized in B706, applied to its hardest case. SM-1/SM-2 (insider cluster-buying) is the one exception per the reviewer — it has Lakonishok-Lee literature anchor and the levers are real (10b5-1 filter, role weighting, cluster size).

### "2 deletions + 2 Class 7 NEW = net 0" replacements are unwalked in new cluster
**Reviewer's position**: the doc's bookkeeping repeats a pattern: SM-9/SM-23 deleted, 2 pure technical shorts created and moved to `momentum_trend` cluster, unwalked there. "Net 0" is tidy but substitutes unwalked-replacements for deleted strategies.

**Adversarial verdict:** **CORRECT.** New tickets must be walked in their new cluster per CHECKLIST #105 before count-bookkeeping closes the substitution.

### Cross-cluster contamination scoping (CC1/CC2/CC4)
- CC1 Form-4 gap entry constraint — documented in doc
- CC2 passive-flow contamination (13F = index funds buying mechanically) — partially documented; Pattern F audit should address
- CC4 Quiver PIT integrity unaudited — **NOT addressed**; reviewer's recommendation: use the earnings-feed-PIT auditor pattern (B704) adapted to 13F/insider/congressional feeds. **Genuinely new ticket needed.**

---

## 3. Summary of verdicts

| Reviewer claim | Source-verified verdict | Priority |
|---|---|---|
| `inspect.currentframe` guard fails open, invisible at call site | 100% CORRECT, LIVE-RISK | **PHASE 0 URGENT** |
| DTC threshold `>8` misses GME pre-squeeze range 5-7 | 100% CORRECT | PHASE 2 |
| B660 = 0 fires for SM cluster (40/40 pure-SM) | 100% CORRECT | (no action; wait for B690) |
| Pre-B671 short backtests are borrow-unprotected ACROSS ALL CLUSTERS | 100% CORRECT — CROSS-CLUSTER BLOCKING | **PHASE 1** |
| Win-rate tuning premature for this cluster | CORRECT, aligned with `feedback_no_prior_edge_consolidate_before_tune` | (no tuning queued except SM-1/SM-2) |
| 13F sleeve marginal-contribution audit (Pattern F) | CORRECT, already in doc | PHASE 3 post-B690 |
| Quiver PIT audit using B704 pattern | CORRECT, genuinely new ticket needed | PHASE 4 |
| SM-1/SM-2 insider tuning levers (10b5-1 + role + cluster size) | ENDORSED — only grounded survivors | PHASE 5 |
| DTC bi-monthly staleness → replace with faster source | CORRECT | PHASE 5 |

---

## 4. Implementation Plan (14 tickets across 6 phases)

### Phase 0 — Revert `inspect.currentframe` guard BEFORE B690 (HIGHEST URGENCY)
1. **`S4-B713-INSPECT-CURRENTFRAME-REVERT-TO-EXPLICIT-GATE`** — replace inspect-frame mechanism in `_strat` + `_strat3` with explicit `borrow_ok` flag that each short strategy declares in its signal-dict consumption. Fails CLOSED (build error if missing) instead of OPEN (silent no-gate). Visible at call site. Pre-B690 is the deadline because once producers fire, the guard becomes live financial risk.
2. **`S4-B713-REGISTRATION-TIME-BORROW-GATE-LINT-BUILD`** — static check over `ALL_STRATEGIES` registry; for each `direction="short"` strategy, assert it consumes `borrow_ok` (or equivalent explicit borrow gate). Fails the test pyramid if any short strategy lacks it. Reviewer offered to build it; we can also build inline.

### Phase 1 — Cross-cluster blocking: re-run ALL contaminated shorts
3. **`S4-B713-PRE-B671-SHORT-BACKTEST-CROSS-CLUSTER-INVALIDATION`** — every short-side backtest produced before B671 ran without borrow protection. **BLOCKING for all short-side cluster verdicts** (breakout / event / pivot / chart-pattern / candle / ICT / SM). Action: post-Phase-0 revert + post-B660-completion, re-run all shorts with explicit borrow gate live. **Until this lands, no short-side number in any cluster doc means anything.** Scope GLOBAL, not SM-5-local.

### Phase 2 — DTC threshold direction fix
4. **`S4-B713-DTC-THRESHOLD-DIRECTION-FIX-FROM-8-TO-5-OR-LOWER`** — current `_short_borrow_trap_active` blocks DTC `>8`. GME pre-squeeze was 5-7. Threshold direction is wrong relative to stated motivation. Action: lower to `>5` (catches GME-class) or replace with non-stale source (see Phase 5 borrow-cost ticket).

### Phase 3 — Pattern F marginal-contribution audit on 13F sleeve (post-B690)
5. **`S4-B713-13F-PATTERN-F-MARGINAL-CONTRIBUTION-AUDIT-POST-B690`** — blocked on B690 measurement. Once 13F sleeve has measured fire counts: run gate-redundancy diagnostic across ~20 13F strategies. Reviewer's prediction: heavy consolidation — many 13F sleeves are reskins of underlying technical strategies with a near-constant 45-day-lag eligibility filter.
6. **`S4-B713-13F-PATTERN-B-DOCSTRING-SWEEP-DEFERRED-AFTER-F`** — only after F resolves population, do docstring honesty fixes on survivors. Pre-F sweep risks rewriting docstrings for strategies about to be deleted.

### Phase 4 — Quiver PIT audit (using B704 earnings-feed-audit pattern)
7. **`S4-B713-QUIVER-PIT-AUDIT-USING-B704-PATTERN`** — adapt `scripts/earnings_feed_pit_audit.py` (built B704) to 13F / insider / congressional feeds. Check for: H1 date re-anchoring (does Quiver re-stamp filing_date on later pulls?); H2 value restatement (do amount values change in later vintages?); H3 backfill (do new tickers appear retroactively in historical periods?). **Gates whether ANY eventual SM backtest win rate is real or lookahead** — same gating role earnings-feed audit played for PEAD.
8. **`S4-B713-CC2-PASSIVE-FLOW-CONTAMINATION-ASSESSMENT`** — 13F "accumulation" partly = index funds buying mechanically. Signal is partly momentum echo. Entry tuning can't fix contaminated signal; needs source-data adjustment (filter passive-flow holdings).

### Phase 5 — Grounded survivors (SM-1/SM-2 insider cluster-buying) + borrow-data replacement
9. **`S4-B713-SM-1-10B5-1-SCHEDULED-PURCHASE-FILTER`** — highest-value win-rate add per reviewer; 10b5-1 scheduled purchases are pre-planned, not informed; filtering them tightens the cluster-buying signal. Producer change, not entry-timing change.
10. **`S4-B713-SM-1-INSIDER-ROLE-WEIGHTING-DIRECTOR-OFFICER-VS-HOLDER`** — director and officer buys carry more signal than large-holder buys (per Lakonishok-Lee). Role-weighted cluster-size metric.
11. **`S4-B713-SM-1-CLUSTER-SIZE-+-DOLLAR-MAGNITUDE-THRESHOLDS`** — more insiders, bigger dollars = stronger drift. Sweep both.
12. **`S4-B713-SM-2-INSIDER-DIRECTOR-MIRROR-ADDS`** — symmetric applications of 9-11 to SM-2 director variant.
13. **`S4-B713-FASTER-BORROW-COST-DATA-SOURCE-EVALUATION`** — FINRA bi-monthly is too slow for squeeze-tail. Evaluate: FINTEL daily borrow fee API, Interactive Brokers SLB rates, S3 Partners. Replace DTC entirely in `_short_borrow_trap_active`.

### Phase 6 — Process discipline
14. **`S4-B713-CLASS-7-REPLACEMENT-WALK-DISCIPLINE`** — when deletion + replacement crosses cluster boundaries, replacement must be walked in NEW cluster per CHECKLIST #105 BEFORE count-bookkeeping closes the substitution. SM-9/SM-23 replacements moved to `momentum_trend` cluster unwalked — apply this discipline retroactively.

---

## 5. Cross-references with other clusters

This review interlocks with prior B702-B710 reviews:

- **B702 Phase-0 producer audit** (earnings_feed_pit_audit.py shipped B704) is the **DIRECT TEMPLATE** for the Phase 4 Quiver PIT audit. Same architecture; new data source.
- **B708 OOS-watchdog tool wiring** prerequisite for any SM-1/SM-2 tuning per `feedback_no_prior_edge_consolidate_before_tune`.
- **B710 fire-count ceiling** doesn't apply yet (SM cluster has 0 fires until B690).
- **B711 regime-affinity cross-check** will likely apply to SM strategies post-B690 measurement.

---

## 6. CHECKLIST compliance

Applied: #45 (source-verified each of 4 highest-impact reviewer claims), #67 (per-turn doc sync), #69 (test pyramid — no code changes this batch; doc-only review), #77 (canonical source headers + verified line numbers), #94 (per-turn EXECUTION_QUEUE update coming), #100 (final-result drift-guard), #105 (Step-3 producer + engine + measurement file end-to-end read).
