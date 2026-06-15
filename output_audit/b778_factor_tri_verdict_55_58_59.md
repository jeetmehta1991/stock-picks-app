# B778 -- TIER 3 TRI-VERDICT on B769 council #55 + #58 + #59 (factor sub-cluster design audits)

# per CHECKLIST #77 + #44(b) + #69 + #94 + #105 + #106 + #107 + #108
# Source: B769 council TIER 3 tickets #55 (architecture audit) + #58 (survivorship) + #59 (cost-aware)
# Source: backtest/signals/cross_sectional.py (B220-B222 producer; 380 lines)
# Source: backtest/signals/screener.py:7953-7954 (engine invocation)
# Source: backtest/engine/backtest.py:824 (universe slicing _get_liquid_universe_for_date)
# per memory: feedback_no_a_priori_strategy_pruning.md + feedback_data_consumption_audit_must_apply_checklist_44b.md + feedback_path_c_min_batch_size.md

## Three TIER 3 tickets shipped in one batch (per `feedback_path_c_min_batch_size`)

#55 + #58 + #59 all read `backtest/signals/cross_sectional.py` end-to-end + are tractable without #56 fire-count gate verdict (which is still in-flight as background bp7s0d6w2). Per `feedback_path_c_min_batch_size`: Path C batches min 5 decisions; one batch consolidates the producer audit across three council concerns.

## #55 ARCHITECTURE AUDIT: portfolio-tilt vs entry-signal -- HYBRID; over-firing structural

### Council F1 claim

> "Citing BAB / Jegadeesh-Titman literature on daily-bar event-driven long-only is a category error... BAB works as portfolio-tilt with monthly rebalance, not as discrete entry signal."

### Producer architecture (cross_sectional.py)

**Output shape:** dict-of-dicts keyed by ticker, each value a dict containing:
- DECILE ranks (int 1-10): `xs_momentum_decile`, `xs_beta_decile`, `xs_ivol_decile`, `xs_max_anomaly_decile`, `xs_quality_decile`
- BOOLEAN flags (derived from deciles):
  - `xs_momentum_top_decile = (d == 10)`         -- top 10% momentum
  - `xs_momentum_bottom_decile = (d == 1)`        -- bottom 10% momentum
  - `xs_low_beta_decile = (d <= 2)`               -- bottom 20% beta
  - `xs_high_beta_decile = (d >= 9)`              -- top 20% beta
  - `xs_avoid_high_ivol = (d <= 8)`               -- NOT top 20% IVOL
  - `xs_avoid_high_max = (d <= 8)`                -- NOT top 20% MAX
  - `xs_quality_top_quintile = (d >= 9)`          -- top 20% quality
  - `xs_quality_bottom_quintile = (d <= 2)`       -- bottom 20% quality

**Producer is portfolio-tilt-shaped** -- ranks across full universe per as_of (correctly).

### Strategy consumption shape (entry-signal)

Factor strategies (B-27 to B-32) consume these as **per-ticker boolean entry gates**:

```python
# Approximate factor strategy shape (e.g., strat_xs_low_beta_long):
fires = (s.get("xs_low_beta_decile", False)
         and s.get("xs_avoid_high_ivol", False)
         and s.get("xs_avoid_high_max", False)
         and <regime-affinity>)
```

This is the architectural mismatch the Expansionist + Reviewer 1 flagged: **portfolio-tilt PRIMITIVES used as entry-signal GATES.**

### The over-firing structural concern

B776 #63 wireup uses `sample_cadence_days=21` (monthly cadence; matches literature rebalance + reduces compute 21x). Between rebalance dates, xs_features are FILLED FORWARD -- same value for ~21 consecutive business days.

**Consequence:** a ticker in the top momentum decile on day D stays in the top decile for ~21 days. Strategy with `xs_momentum_top_decile == True` gate fires EVERY DAY in that window, not just on the rebalance date.

This is NOT portfolio-tilt-monthly-rebalance behavior. It's "ticker passes today's filter, fires daily until next rebalance refreshes the ranks."

**This connects to Pattern Q (STATE vs EVENT) directly.** Same pattern, applied to cross-sectional ranks:
- STATE form (current): `xs_momentum_top_decile` is TRUE for ~21 consecutive days
- EVENT form (proposed): `xs_momentum_top_decile_entry_recent_5d` = newly entered top decile in last 5 days

### Verdict + recommendation

**HYBRID architecture confirmed.** Producer is portfolio-tilt-shaped; strategies consume as entry-signal. Council Expansionist's critique is empirically valid at the architectural level.

**Three resolution options (NOT pre-applied per `feedback_no_a_priori_strategy_pruning`):**
- (a) **Convert strategies to portfolio-tilt**: at each rebalance date, set portfolio = top N momentum / low N beta tickers. Significant refactor (changes strategy contract from per-ticker to portfolio-level).
- (b) **Add EVENT-on-rank-crossing gate**: producer-side new `xs_*_decile_entry_recent_5d` signals; strategies fire on FRESH ENTRY into the decile, not membership. Pattern Q precedent (B655 T10 / B772 B-13). Per CHECKLIST #108: fire-count projection required.
- (c) **Add MONTHLY-REBALANCE date gate**: fires only on rebalance dates (every 21st business day). Simpler but loses the "stay-in-decile retention" semantics from option (b).
- (d) **Accept hybrid + measure**: cube measures whether hybrid produces edge; if cube fails on these strategies, the architecture concern is empirically validated.

**Disposition:** REPORT-AS-FINDING. Per `feedback_no_a_priori_strategy_pruning`: cube is authoritative. #56 GATE re-attempt (bp7s0d6w2 in flight) will determine cube-readiness. Owner can then decide option (a)/(b)/(c)/(d). If choosing (b), CHECKLIST #108 applies + producer-side new EVENT signals are needed.

## #58 PIT DISCIPLINE + SURVIVORSHIP/SELECTION-BIAS AUDIT -- producer CLEAN; survivorship STRUCTURAL upstream

### Council Expansionist claim

> "BAB published edge gets eaten in practice by survivorship/selection bias (Novy-Marx 2014, Asness-Frazzini-Pedersen 'Quality Minus Junk' 2019 follow-ups). xs_low_beta ranks within ACTIVE UNIVERSE -- which is filtered by liquidity/listing/index-membership."

### Producer PIT slicing audit

`backtest/signals/cross_sectional.py:107-109`:

```python
if hasattr(df.index, "date"):
    sliced = df[df.index.date <= as_of]
else:
    sliced = df[df.index <= as_of]
```

**Backward-only slice.** Same pattern as engine `_process_day` line 824 + pool worker line 7819 + measure_fire_count line 559 (all validated PIT-clean B770). NaN handling via `dropna(how="all")` + `min_history=252` floor.

**Verdict: producer PIT slicing is CLEAN.** No lookahead path in cross_sectional.py.

### Universe construction (upstream survivorship)

Universe is supplied by caller via `ohlcv_dict` parameter. In backtest engine:
- `screener.py:7954` invokes with `ohlcv_dict` = `ohlcv_pit`
- `ohlcv_pit` built in `backtest/engine/backtest.py:_process_day` lines 818-826:
  ```python
  liquid_this_year = self._get_liquid_universe_for_date(as_of)
  ohlcv_pit = {}
  for t in liquid_this_year:
      df = self.ohlcv_dict.get(t)
      if df is None: continue
      sliced = df[df.index.date <= as_of]
      if len(sliced) >= 30: ohlcv_pit[t] = sliced
  ```
- `_get_liquid_universe_for_date(as_of)` returns the YEAR-APPROPRIATE liquid universe (per CLAUDE.md L46-L88: T1a 614 rows with `added_date` / `removed_date` columns; PIT loader filters by `(added_date IS NULL OR added_date ≤ as_of) AND (removed_date IS NULL OR removed_date > as_of)`).

**Universe-construction PIT: CLEAN** -- year-appropriate T1a-PIT membership at each as_of.

### Survivorship-bias structural concern (Expansionist's actual point)

The T1a-PIT universe is, by definition, a "current-S&P-500-survivors-up-to-as_of" universe. Companies that:
- Were S&P-500 in 1995 but delisted before 2020-01-01 (start of backtest) -- NOT in T1a
- Never reached S&P-500 -- NOT in T1a
- Are in T1b/T1c/T2/T3 universes -- not in factor compute (only T1a is passed to compute_cross_sectional_features in current screener.py invocation)

**Selection bias is structural at the T1a universe choice level**, NOT at the cross_sectional.py producer level. The Novy-Marx 2014 critique of BAB applies to ANY backtest using a survivors-only universe -- including this one.

**Mitigation options (NOT pre-applied):**
- (e) Expand factor universe to T1a + T2 + T3 (include spinoffs/IPOs + momentum names; broadens beyond S&P-survivors)
- (f) Add explicit "added-this-year" filter to exclude recently-added tickers (avoid catching the late-arriver winners)
- (g) Accept the structural bias; document it in interpretation guide

### Verdict + recommendation

**Producer PIT discipline: CLEAN at all 3 layers** (engine universe construction + producer slicing + caller-passed dict).

**Survivorship bias: STRUCTURAL at T1a universe choice** -- not removable without universe expansion (option e). Council Expansionist's concern is real but ATTRIBUTABLE TO UNIVERSE-LEVEL DESIGN, not cross_sectional.py producer bug.

**Disposition:** REPORT-AS-FINDING. The structural survivorship bias affects published Sharpe vs measured Sharpe by some amount; cube measurement will be biased UPWARD relative to "true" factor edge by this amount. Cube interpretation guide must note this. No producer-level fix needed; option (e) is a universe-expansion decision separate from factor design.

## #59 COST-AWARE EVALUATION DIMENSION -- per-strategy cost matrix

### Council Expansionist claim + Reviewer 3 specificity

> Reviewer 3 flagged generic check-box risk -- "specify which costs dominate: (a) commission per trade, (b) slippage % of bid-ask, (c) borrow cost on SHORT-side factors, (d) cap-saturation queue cost."

### Per-strategy cost matrix (B-27 to B-32)

| Strategy | Direction | Commission | Slippage | Borrow | Cap-sat | Net cost rank |
|---|---|---|---|---|---|---|
| B-27 xs_combined_momentum_low_ivol | LONG | YES | YES (mid-cap-skew) | NO | YES (top-decile congestion) | MEDIUM |
| B-28 xs_momentum_top_decile | LONG | YES | YES (top-decile = recent winners; trends established; slippage moderate) | NO | YES (50+ tickers may be top-decile depending on rank distribution) | MEDIUM-HIGH |
| B-29 xs_low_beta_long (BAB) | LONG | YES | YES (low-beta = utilities/staples; HIGHER slippage in low-volume names) | NO | YES (bottom-quintile = ~100 names) | MEDIUM |
| B-30 xs_momentum_bottom_decile_short | **SHORT** | YES | YES (bottom-decile = recent losers; bid-ask wider) | **YES (HIGH on small/distressed)** | YES | **HIGH** |
| B-31 xs_momentum_quality_combined | LONG | YES | YES | NO | YES (quality + momentum intersection narrower) | MEDIUM |
| B-32 xs_quality_top_quintile_long | LONG | YES | YES (quality top-quintile = large-cap blue-chip; LOW slippage) | NO | YES (top-quintile = ~100 names; congestion lower than decile) | LOW-MEDIUM |

### Cost-aware-evaluation interpretation notes

- **Borrow cost on B-30**: Per backtest config `borrow_cost_bps`: applies to all SHORT trades. xs_momentum_bottom_decile_short targets names with worst 21-day momentum -- often distressed / small-cap / declining-listing names with HIGHEST borrow rates (10-30% annualized for hard-to-borrow). Cube cell verdict on B-30 must apply realistic borrow cost (not 25bp/yr generic).
- **Cap-saturation on B-28**: top-decile fires across ~50+ T1a tickers; with `max_candidates_per_day=30` cap (CLAUDE.md), the cap fills with the highest-ranked candidates and the rest are starved. Per-strategy fire-count cap is NOT the same as raw fire-count. Cube verdict on B-28 must measure POST-CAP delivered fires per ticker.
- **Slippage on B-29 (low-beta)**: low-beta names skew toward utilities / staples / older blue-chips. Bid-ask spread typically tight (1-3bp). Slippage cost LOW.
- **Slippage on B-30 (bottom-momentum)**: bottom-decile names skew toward recent declines / earnings disappointments / distressed. Bid-ask spread typically wider (10-50bp). Slippage cost HIGH.
- **Commission**: uniform per-trade per backtest config (typically 1bp). Low impact for ALL factor strategies given monthly-rebalance shape.

### Verdict + recommendation

**Cost dimensions per-strategy DOCUMENTED.** Per Reviewer 3 specificity-add: per-strategy net cost rank (LOW-MEDIUM / MEDIUM / MEDIUM-HIGH / HIGH) surfaces relative cost exposure. B-30 (SHORT-bottom-momentum) is the highest-cost factor; B-32 (LONG-quality-top) is the lowest-cost.

**Cube evaluation framework requires:**
- B-30: realistic borrow cost per-name (not generic 25bp/yr); flag if cube uses default low rate
- B-28: post-cap delivered fire-count per ticker (not raw fires)
- B-29: low-beta universe-of-low-volume names -- size-of-trade vs daily-volume slippage scaling

**Disposition:** REPORT-AS-FINDING + matrix documented. No producer change needed. Cube interpretation guide must absorb per-strategy cost notes.

## Combined CHECKLIST #107 reconciliation (B778)

- **Findings surfaced:** 3 primary (#55 HYBRID architecture surfaced with over-firing within 21-day window; #58 producer PIT-clean / survivorship STRUCTURAL upstream; #59 per-strategy cost matrix documented) + 1 nuanced (cap-saturation interaction with top-decile congestion is its own multi-strategy concern)
- **Tickets filed:** 0 NEW + 3 annotations on existing #55 + #58 + #59 (all COMPLETED-DOCUMENTED with verdicts)
- **Audit-clean: YES**

Cumulative ticket count post-B778: 131 unique S4-B7XX tickets (no change; #55 + #58 + #59 closed in place).

## Strategy counts (unchanged)

221 / 0 / 1 / **220 active.** No strategies modified.

## Memory + checklist compliance

- `feedback_no_a_priori_strategy_pruning.md` -- no strategies modified; verdicts surface findings, owner decides options (a)-(g)
- `feedback_data_consumption_audit_must_apply_checklist_44b.md` -- producer source read end-to-end + PIT discipline traced through 3 layers (engine -> caller -> producer)
- `feedback_minimum_fire_count_gate_before_cube.md` -- #55 architecture concern (~21-day STATE-retention over-firing) is exactly what fire-count gate would catch; #56 GATE re-attempt in-flight will measure
- `feedback_local_changes_default_global_needs_approval.md` -- this batch is read-only producer audit; no code changes
- `feedback_path_c_min_batch_size.md` -- 3 tickets in one batch via shared producer source read
- CHECKLIST #44(b) -- 6-step audit applied where relevant (producer source + caller paths + universe construction + PIT slicing); investigate-why steps mapped to architecture concern (over-firing comes from STATE-retention within rebalance window)
- CHECKLIST #67 -- doc-sync same turn
- CHECKLIST #69 -- pyramid (842/842; no code changes)
- CHECKLIST #77 -- canonical-source headers
- CHECKLIST #94 -- queue-mandatory-per-turn
- CHECKLIST #105 -- producer source + 3-layer caller paths read end-to-end
- CHECKLIST #106 -- producer-data audit class
- CHECKLIST #107 -- findings-vs-tickets reconciliation (THIRTEENTH-FULL-EXECUTION)
- CHECKLIST #108 -- N/A this batch (no gate modifications); SCOPED-COMPATIBLE (verdicts surface options for future gate modifications which would then need #108 pre-flight)
