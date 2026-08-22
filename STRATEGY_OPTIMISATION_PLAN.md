<!-- B1497 (2026-08-09). Owner-requested optimisation plan for the 207-strategy population.
     STATUS: PROPOSAL. Nothing here is implemented. Owner approval required per phase. -->

# Strategy Optimisation Plan — Phase 1 (tightening) and Phase 2 (loosening)

**Population:** 207 strategies (`222 registered - 3 Phase-1B roster - 12 disabled`).
**Current roster:** 2 cells / 3 strategies, ROBUST 2 / PROVISIONAL 0.
**Purpose of this programme:** the roster is 2 cells. Optimisation is not an enhancement; it is the
only remaining path to a deployable Phase 1B.

---

## 0a. SUPERSESSION BANNER — B1500-B1510 (2026-08-10)

The first worked example (`smc_breaker_block_long`) ran end-to-end and **corrected four load-bearing
claims in this plan.** Read this before Sections 2.2 / 2.3 / 2.3a, which are marked inline.

| # | claim as originally written | corrected by measurement |
|---|---|---|
| 1 | "no resimulation is required for tightening" | **Only for SUBSET-SAFE parameters.** A parameter that can ADD fires (`swing_length`, EMA `span`) produces trades R5 never took, and the cube holds no P&L for those. §2.3a corrected. |
| 2 | population = 41 strategies at n>300 | **The band is built on UNVERIFIED n.** The worked example's measured holdout n is **147**, not the 356 carried — it was never in the n>300 band. **The whole partition must be re-derived from measured n (S6-B1502a).** |
| 3 | tunable surface = numerics in the gate expression | **Wrong layer.** The surface is the transitive closure of the PRODUCER parameters. A strategy whose gate is two booleans still had 6 producer parameters (L355). |
| 4 | cost scales with combinations | **Cost = ENGINE RUNS = product of the fire-ADDING bands only.** 4,000 combinations needed **20** runs, not 4,000 (L371). |

**Reporting is now standardised and mechanically enforced — see §6.**

## 0b. STEP-1 WINDOW — THE THREE CONSTRAINTS CANNOT ALL BE MET (B1817, MEASURED)

**`S6-B1605c` withdrew the acceptance of Step 1 reading the holdout and proposed moving Step 1 to
`2023-05-05 -> 2025-05-05`. That remedy CONTRADICTS the 2026-08-17 ruling** in SS10.1: *"2022-23 data
is not wanted even for exit selection. Both phases run 2024-05-05 -> 2026-05-05."*

Three standing constraints, and no window satisfies all three:

| constraint | source |
|---|---|
| holdout LOCKED to `2025-05-05 -> 2026-05-05` | SS0, owner 2026-08-09 |
| no 2022-23 data, even for exit selection | SS10.1, owner 2026-08-17 |
| Step 1 must not rank on the holdout | `S6-B1605c`, owner 2026-08-17 (*"undo"*) |

**The obvious compromise is measurably self-defeating.** A Step-1 window of
`2024-05-05 -> 2025-05-05` honours all three by construction, but MEASURED on the four existing
cubes it keeps only **50-56 pct of entries**:

```
cfg1              330 entries  ->  183 (55.5pct) before the holdout boundary
cfg2              420          ->  236 (56.2pct)
w1_sw20_span21    320          ->  167 (52.2pct)
w1_sw20_span50    302          ->  152 (50.3pct)
```

**At the FULL sample, `--min-n 10` still leaves 32-60 pct of the grid `NO_EXIT_SELECTABLE`.** Halving
the sample pushes most of it back to unanswerable, so the window fix destroys the search it is meant
to make trustworthy.

**Therefore `S6-B1605c` and `S6-B1696c` are ONE decision, not two.** Restoring the sample at a
holdout-respecting window needs the universe lever - 100 -> ~200 tickers, roughly doubling fires at
~2x runtime (`S6-B1696c` option (a)). **That is the only path that satisfies every constraint; it
pays in runtime rather than in correctness or data policy.**

## 0. HOLDOUT POLICY — SETTLED BY OWNER (2026-08-09)

**RULING: the holdout window is LOCKED to R5's dates. `2025-05-05 -> 2026-05-05`, 1 year, unchanged.**
Owner: *"We do not change the dates and duration of the holdout period. they remain the same as in
r5. this is to ensure comparibility. No logic changing that even if its been graded 9 times on
pre-optimized gates."*

**Option A (re-partition) is REJECTED. Option B (extend forward) is unavailable.**

**The rationale is sound and worth recording:** moving the holdout would make the optimised roster
incomparable to the R5 baseline, the R6b result, and every measurement taken this session. A
programme whose purpose is to show that optimisation improves on R5 cannot be graded on a different
window than R5 was. **Comparability is the point of a fixed holdout, and it outranks the marginal
statistical benefit of a fresher one.**

### This does NOT conflict with Option C — C is now the operative design
Option C (nested cross-validation inside the IS folds, holdout read exactly ONCE at the end)
**never proposed changing the holdout's dates.** It governs how many TIMES the fixed window is read,
not where it sits. So the owner's ruling and Option C are complementary, and C is now the design:

- **The holdout window is fixed** (owner ruling)
- **Phase 1 reads it exactly once**, on the final <=41-config candidate set (Option C)
- **All intermediate optimisation happens inside F1/F2/F3**, which the holdout ruling does not touch

### Moderating the L351 concern — the owner's distinction is correct
L351 counted ~9 holdout regrades and treated them as accumulated selection pressure. The owner's
phrase **"pre-optimized gates"** identifies a real distinction I understated:

| what those 9 reads did | what they did NOT do |
|---|---|
| calibrated a handful of GLOBAL gate parameters (Sharpe 0.5 -> 1.0; `min_trades` 100 -> 25/100) | select among strategies on holdout performance |
| effective search space: ~3-5 distinct gate configurations | 41 x 20 strategy-specific configs |

Tuning a few global thresholds is a far smaller multiple-testing spend than cherry-picking
strategies, and the Sharpe bar in particular was chosen **on principle** ("0.5 is too weak"), from a
sensitivity curve presented before the choice -- not by scanning for whichever value produced the
nicest roster. That is materially different from optimisation.

**The spend is real but small.** L351 stands as a discipline (count holdout reads project-wide) with
its magnitude corrected: the prior reads consumed little, and the reason to adopt Option C is
FORWARD-LOOKING -- Phase 1's 820 candidate configs are the genuine threat, not the 9 that happened.

## 1. GOVERNING CONSTRAINTS (bind both phases)

1. **The holdout is read ONCE per phase, at the end, on the final candidate set.** Not per
   strategy, not per iteration, not to "check how it's going".
2. **Pre-registration.** The search space -- which signals, which thresholds, which objective -- is
   written to `EXECUTION_QUEUE.md` and committed BEFORE any score is computed. A grid chosen after
   seeing results is not a grid, it is a story.
3. **FDR budget is declared up front.** Every config tested counts toward the family. If Phase 1
   tests 41 strategies x 20 configs, the family is 820 and BH-FDR is applied at that m -- not at the
   number that happened to survive.
4. **Selection statistics never touch the grading window.** The B1452 retraction and the B1454
   de-dup correction are both instances of this being violated in mild forms.
5. **Every reported number ships with its diagnostics** -- sensitivity curve, leave-one-out
   contribution, churn (in/out), and effective breadth (CHECKLIST #175, #176).
6. **There is NO usable prior for this population.** *(Corrected 2026-08-09 - owner: "The R6b prior
   is the base rate - this is incorrect especially for the untouched strategies.")* R6b was a
   **LOOSENING** experiment on **14 already-examined** strategies and graded 4 held / 9 failed
   (p=0.954). Phase 1 is **TIGHTENING** on **41 mostly-never-touched** strategies. Different
   operation, different population - citing it as the base rate was a category error. R6b remains
   relevant as evidence that *IS-fitted changes can fail on holdout*, i.e. as motivation for the
   discipline, but **not as a numerical expectation.** Phase 1 has no prior; that is itself a reason
   to run it.

---

## 2. PHASE 1 — TIGHTENING (offline for SUBSET-SAFE params only — see §2.3a)

### 2.1 Why tightening is cheap and loosening is not
`trade_log.csv` carries a `signals_at_entry` column: the **complete producer signal dict at the
entry bar**, ~22 KB per trade (verified B1497: `{"pivot": 158.6, "cpr_narrow": true, "cam_r4":
161.79, ...}`). Therefore:

- **TIGHTENING is exact and free.** A tighter threshold selects a strict SUBSET of trades that
  already exist, with known outcomes. Recomputing any subset's statistics needs no engine.
- **LOOSENING is impossible offline.** A looser threshold admits trades that were never generated.
  No amount of replay conjures them.

### 2.2 Population — 41 strategies (n > 300)  🔴 SUPERSEDED, see §0a #2

> **CORRECTION B1502.** The band assignments below were never validated against measured holdout n.
> The first strategy examined, `smc_breaker_block_long`, was treated as n>300; its MEASURED holdout
> n is **147** (full-period 352), which places it MID-BAND. **Re-derive every band from measured n
> before Phase 1 is scoped (S6-B1502a).** The counts below are retained for lineage only.


| band | strategies | in Phase 1? |
|---|---|---|
| **n > 300** | **41** | **YES — Phase 1.1 / 1.2** |
| 100 < n <= 300 | 58 | Phase 1.3, only after 1.1 validates (n-floor risk) |
| n <= 100 | 45 | NO — Phase 2 |
| no gradable cell | 63 | NO — Phase 2 |

**Why n > 300 first:** in that band neither `min_trades` leg can bind, so the search has no
n-floor interaction and tightening cannot starve a cell into failing a different gate. It is the
clean test of whether the method works at all.

### 2.3 Method — six steps

**Step 1 — EXTRACT.** Parse `signals_at_entry` per strategy into a feature matrix, IS rows only
(`2022-05-05 -> 2025-05-05`). Chunked parsing; ~22 KB/trade means a strategy with 1,200 IS trades
is ~26 MB of JSON. Holdout rows extracted to a **separate sealed file** that the optimiser cannot
read (enforced by a path the Phase-1 code has no reference to).

**Step 2 — PRE-REGISTER THE GRID.** Per strategy:
- **Which signals:** ONLY those the strategy's source actually consumes, read from the gate
  expression via `inspect.getsource` -- never guessed from names (L279: a name-based inference
  wrongly excused a mirror because B1194 had made the name stale).
- **Which thresholds:** fixed quantiles of the observed IS distribution (deciles), so the grid is
  data-defined but *rule*-defined, not cherry-picked.
- **Cap: ARBITRARY-PENDING-JUSTIFICATION.** *(Owner: "why 41 x 20?")* **41 is measured** -- the
  n>300 population. **20 was arbitrary** -- I wrote it without a basis, which violates CHECKLIST
  #165 (every selection rule must be justified on a measured basis or explicitly labelled
  arbitrary). Labelling it now rather than defending it. The cap should be DERIVED, and the honest
  way is: cap = the number of decile thresholds x the number of consumed numeric signals, computed
  PER STRATEGY from its actual gate expression. A strategy gating on one numeric signal has ~9
  candidate thresholds; one gating on three has ~27. **The real family size is therefore the sum of
  per-strategy grids, not 41 x a round number** -- and it must be counted before scoring, not
  estimated. S6-B1499a.
- Committed to the queue BEFORE any scoring.

**Step 3 — SCORE ON IS FOLDS SEPARATELY.**
*(Owner challenge 2026-08-09: "is this step really necessary? Holdout is the only one that should
matter and not these folds? same for step 4?")*

**The folds are not a grading mechanism. They are where SELECTION happens.** Every config must be
chosen somewhere, and there are only two places:
- **On the holdout** -- this is the B1452 lookahead, retracted. With 20 configs per strategy a
  maximum-over-20 on the graded window almost always "passes", and the number means nothing.
- **On the IS** -- the config is chosen blind to the holdout, then graded once.

So Step 3's existence is not optional; the holdout *is* the only thing that decides, and Step 3 is
what keeps it able to decide.

**Step 4 — FOLD-STABILITY FILTER. This one IS optional, and here is the honest trade-off.**

| | select on POOLED IS (skip Step 4) | require all 3 folds (Step 4) |
|---|---|---|
| candidates reaching the holdout | more | far fewer |
| protection against IS overfit | none beyond the holdout itself | strong -- a config must work in 2022-23 AND 2023-24 AND 2024-25 |
| cost | some holdout tests wasted on IS-noise winners | **kills real candidates that happen to be fold-uneven** |

**Recommendation: keep Step 4, but as a REPORTED TAG rather than a hard filter.** Score every config
on pooled IS *and* record its fold-stability; select the pooled-IS winner but carry
`fold_stable: true/false` into the holdout grade. That way:
- nothing real is silently killed before it reaches the holdout (the owner's concern), and
- if fold-unstable configs systematically fail the holdout, that is measured evidence for
  hard-filtering in Phase 2 rather than an assumption imposed now.

This is strictly more informative than either extreme and costs nothing.

**Step 5 — ONE CONFIG PER STRATEGY, and why the FDR family is 41 not 820.**
*(Owner: "explain")*

BH-FDR controls false discoveries among **hypotheses tested on the grading data**. The 820 IS scores
are not hypotheses tested on the holdout -- **they never touch it**. The holdout sees exactly one
hypothesis per strategy: *"does this strategy's chosen config have positive edge out of sample?"*
That is <= 41 tests, so m = 41 + 2 incumbents.

**This is only valid if the IS/holdout separation is airtight.** If any holdout information leaks
into the choice of config, the 820 become real holdout tests and m must be 820.

**CORRECTED B1820 (`S6-B1705c`, owner: *"major and unforgivable"*).** This paragraph previously
claimed the separation was *"enforced mechanically ... a file path containing IS rows only and no
reference to the holdout file"*. **NO SUCH FILE PATH EXISTS** - the grader is handed the full cube
and slices it itself. **The separation is nonetheless real, by two mechanisms this document never
named:**

| mechanism | where | verified |
|---|---|---|
| `select_exit` slices `in_sample()` ITSELF, so the EXIT choice cannot see the holdout | `roster_core.py:241` | `test_b1800_step1_exit_selection_is_is_only` - a holdout-only frame yields NO exit, with a live control proving the fixture can select |
| Step 1 ranks on **`is_sharpe`**, not `sharpe`; `rankable` REQUIRES a non-null IS Sharpe | `tighten_breaker_block.py:376` | B1718 P0-2, owner-approved |

**A claimed mechanism that does not exist is worse than an acknowledged gap**, because it stops
anyone looking. Both real mechanisms are code-level and testable; the promised one was neither.

**The conservative alternative is m = 820**, which would raise the BH threshold roughly 20x tighter
and almost certainly admit nothing. Both readings are defensible; the choice is owner decision #4.

**Step 6 — GRADE ONCE.** The <= 41 chosen configs are graded on the holdout in a single pass, with
BH-FDR across that family plus the 2 incumbents. **This is the only holdout read in Phase 1.**

### 2.3a RESIMULATION — the rule is SUBSET-SAFETY, not "tightening"  🔴 CORRECTED B1508

*(Owner concern: "we would need to resimulate on the entire cube. thus the best strategy x exit cell
post optimization and rerun may change after tightening.")*

**The original answer — "tightening never needs the engine" — was too broad.** The correct
criterion is whether a parameter can only REMOVE fires or can also ADD them.

| | parameter class | cube-gradable? | why |
|---|---|---|---|
| ✅ | **SUBSET-SAFE** — can only remove fires | **YES, free and exact** | every surviving trade already exists in the cube under all 26 exits, so grading is a lookup |
| 🔴 | **FIRE-ADDING** — can change WHICH bars fire | **NO — needs the engine** | produces `(ticker, date)` pairs R5 never took; the cube holds no P&L for them |

A parameter is fire-adding whenever it changes the producer's own detection (e.g. `swing_length`
rebuilds the order-block set) or swaps one leg of the gate for a different signal (e.g. EMA span
200 -> 50). **Neither is "loosening" in the ordinary sense, and both were mis-classified as free
under the original wording.**

VERIFIED B1499: for `macd_crossover|long`, all 202 sampled `(ticker, entry_date)` trades carry
**26 distinct `exit_method` rows each**. So the subset-safe half is genuinely exact — the best exit
CAN change when the population changes, and Step 3 re-selects it, but no simulation is involved.

**Cost consequence (L371).** The run count is the product of the FIRE-ADDING bands alone; every
subset-safe combination then derives offline from each run. For the worked example: 4,000
combinations, but **20 engine runs** (4 `swing_length` x 5 EMA `span`), with all 200 subset-safe
combinations free inside each. Costing by combinations would have overstated the workload 200x.

### 2.4 Error checks (each one closes a defect this session actually produced)

| check | guards against | lineage |
|---|---|---|
| Assert the optimiser has no holdout path in scope | accidental leakage | L276 (B1452) |
| Assert `full_period_n` is passed wherever the gate is evaluated | a silently no-op gate leg | B1492 |
| Positive control: a config identical to the current gates must reproduce the current result | extractor/replay bugs | L323 |
| Negative control: a deliberately absurd threshold must produce zero trades | silent no-op filters | L322 |
| Assert every scored config's trade count > 0 before scoring | vacuous passes | L325 |
| Re-derive every published count from the artifact, never from a running tally | count drift | L298 |
| Run `audit_registration_redundancy.py` after the phase | tightening collapsing two strategies together | CHECKLIST #169 |
| Report churn (in/out), never only the net | direction assumed rather than measured | L291 |

### 2.5 Standards
- Every number in the report carries its funnel stage (L295).
- Sensitivity curve published for any threshold that ends up chosen (L288 / #175).
- Effective breadth (`N_eff`) reported for the resulting roster, not just the count (#175).
- PROVISIONAL/ROBUST status applied against the measured selection-noise floor (S6-B1467c).
- Any strategy whose tightened config differs from its shipped gates is a **strategy change** and
  needs owner approval before it is written to `screener.py`.

### 2.6 Expected outcome, stated honestly
The R6b base rate is 4/13. Steps 2 and 4 are designed to beat it, but **the realistic expectation is
that a minority of the 41 convert** -- and at the Sharpe >= 1.0 bar, possibly very few. If Phase 1
delivers 3-5 additional ROBUST cells that is a doubling of the roster and a success. If it delivers
zero, that is also an answer: it says the library's edges are not recoverable by threshold tuning,
and Phase 2 or a new strategy class is required.

---

## 3. PHASE 2 — LOOSENING (requires engine runs)

### 3.1 Population — 108 strategies
45 with n <= 100, plus 63 with no gradable cell at all. These cannot be tightened -- they do not
fire enough to have a subset worth selecting.

### 3.2 The structural choice
| approach | cost | notes |
|---|---|---|
| **Per-strategy loosening runs** | N engine runs | infeasible: multi-hour each |
| **ONE permissive superset run** | 1 engine run | loosen gates broadly, generate a superset, then optimise offline by subset selection exactly as Phase 1 |

**Recommendation: the superset run.** One expensive run converts all subsequent loosening
optimisation into the same free offline problem Phase 1 solves. It is the only approach that scales
to 108 strategies.

### 3.3 Pre-spend requirements (B1335 Rule 1, and the S6-B1465c precedent)
Before any engine run: a `run_manifest.json` pinning code SHA, isolation mode, calendar, universe,
**and a wall-clock projection derived from a timed smoke** -- the field my B1465c manifest initially
omitted (L333). Plus the written answer to *"what could make this run obsolete?"*, and
`prelaunch_gate.py --manifest` passing in LOCAL mode (B1488).

**Explicitly: do not launch Phase 2's superset run until Phase 1 has reported.** If threshold
optimisation cannot rescue strategies that already fire 300+ times, it is unlikely to rescue ones
that barely fire, and that result should change Phase 2's design before it is paid for.

---

## 4. KILL CRITERIA

State these now, so the programme can be stopped on evidence rather than fatigue:

1. **Phase 1 kills itself** if fold-stability (Step 4) eliminates >95% of configs AND the survivors
   fail holdout FDR. That is the R6b result repeating with better instrumentation, and it means
   threshold tuning is not the lever.
2. **Phase 2 is not launched** if Phase 1 converts zero strategies.
3. **The programme kills itself** if the resulting roster's `N_eff` stays below ~3 regardless of
   cell count -- a book of correlated cells is not diversified no matter how many pass.

---

## 5. OWNER DECISIONS REQUIRED BEFORE ANY WORK  (superseded by §8 — live list)

1. ~~Holdout strategy A/B/C~~ — **SETTLED 2026-08-09.** Window LOCKED to R5 dates for
   comparability; Option C (read it once, optimise inside the IS folds) is the operative design.
2. **Mid-band (58 strategies at 100 < n <= 300): in Phase 1 or deferred?**
3. **Do the 3 AUTO-FAIL screens get implemented against the IS/full-period series (S6-B1495a)
   before Phase 1 grades?** They currently return `None` on a 1-year holdout.
4. **FDR family size:** 41 (one config per strategy) or 820 (every config tested)? The conservative
   reading is 820; the pre-registration + one-winner-per-strategy design is what makes 41 defensible.

---

## 6. LOCKED REPORTING STANDARD — CHECKLIST #183 (owner-locked B1510)

Every strategy entering S6-OPT-196 is reported through `scripts/producer_variant_table.py` as ONE
artifact in three sections. Adding a strategy = adding a `SPECS` entry (formula + params); the
renderer is strategy-agnostic. **Regenerate, never hand-edit** — a hand-edited copy is reverted by
the next generation (L286).

### 6.1 Section 1 — BOOLEAN FORMULA (REQUIRED; a SPEC without it is rejected)

Header must state the formula is READ from source, never recalled. Two layers:

```
=============================== PRODUCER LAYER ===============================

P1  swings  =  swing_highs_lows( ohlc, swing_length = 20 )
                   -> a bar is a swing high if its high is the highest
                      across swing_length bars BEFORE and AFTER it
                   PARAMETER: swing_length = 20   (library default is 50)

P2  ob_df   =  ob( ohlc, swings, close_mitigation = False )
                   -> emits, per detected block:  OB (+1 bull / -1 bear),
                      Top, Bottom, MitigatedIndex
                   PARAMETER: close_mitigation = False
                      False -> a block counts as mitigated when the HIGH/LOW
                               pierces it
                      True  -> only when the CLOSE pierces it  (stricter)

P3  events  =  ob_df[ OB != 0 ].tail( 20 )
                   PARAMETER: tail N = 20     (hardcoded literal, not an argument)

P4  per event e:   e.is_mitigated = ( MitigatedIndex > 0 )
                                    AND ( MitigatedIndex < today_index )
                   -> no parameter; derived from P2's MitigatedIndex

P5  per event e:   e.broken_up    = ( close > e.Top )
                   -> no parameter; strict inequality, zero buffer

P6  ema_50_200 =  compute_ema_sma( df )      # pairs (9,21),(20,50),(50,200)
       price_above_ema_200  =  close > EMA(close, span = 200)
                   PARAMETER: span = 200, emitted only from the (50,200) pair

=============================== STRATEGY LAYER ===============================

breaker_bullish  =  AT LEAST ONE event e in P3 satisfies ALL of:
                        ( e.OB == -1 )          <- bearish block      [from P2]
                        AND ( e.is_mitigated )                        [from P4]
                        AND ( e.broken_up )                           [from P5]

fires            =  ( breaker_bullish )  AND  ( price_above_ema_200 ) [from P6]
```

**Rules the format enforces.** Every producer gets a `Pn` id, its call signature with the LIVE
production value inline, a plain-language note on what it emits, and an explicit `PARAMETER:` line
— or `no parameter` where none exists. The STRATEGY LAYER spells out `AT LEAST ONE ... ALL OF`
rather than symbolic OR/AND, and tags every clause with the `Pn` it came from, so a reader can walk
from any gate back to the producer that computes it.

**Why Section 1 exists at all:** at B1500 a strategy was called untunable because its gate read as
two booleans. Forcing the producer layer to be written first makes that error unwritable — those
booleans had six parameters behind them (L355).

### 6.2 Section 2 — TABLE A, parameter inventory

One row per `Pn`. Required fields, all test-pinned by `test_b1510_producer_artifact_standard`:

| field | meaning |
|---|---|
| `id` | `Pn`, matching Section 1 |
| `producer` | the function or expression that computes it |
| `param` | parameter name, or `-` if none exists |
| `production` | the LIVE value today |
| `band` | every value to be tested |
| `subset_safe` | `True` = cube-gradable free, `False` = needs engine resim, `None` = no parameter |
| `status` | `TESTED` / `UNTESTED` / `PENDING` (tested but never gradable) / `N/A` |
| `derivation` | **WHY this band holds these values** — must cite a measurement or a stated rule |
| `evidence` | source `file:line`. **Never inference.** |

`derivation` and `evidence` exist because at B1507 a band was silently narrowed from 5 values to 2
on an unstated economic hunch (L369). With those fields required, the narrowing cannot be written
down without exposing that it has no basis.

### 6.3 Section 3 — TABLE B, combination results

15 columns in three groups, taken from `roster_core.evaluate()`'s return dict — **what it emits,
never a wishlist:**

- **GATED (6) — decide PASS/FAIL:** `pooled_sharpe` >= 1.0, `profit_factor` >= 1.3,
  `sortino` >= 0.7, `psr` >= 0.95, `min_trades_holdout` >= 25, `min_trades_full_period` > 100
- **DIAGNOSTIC (5) — reported, not gated:** `win_rate` (demoted B1387), `payoff`, `expectancy`,
  `p` (one-sided, H0: SR<=0), `ci_lo` (Sharpe CI lower bound)
- **CONTEXT (4):** fires, holdout n, full-period n, exit chosen IN-SAMPLE

**Known gap (S6-B1509a):** `max_drawdown`, `calmar` and `deflated_sharpe` were demoted to
DIAGNOSTIC at B1436/B1437, but `roster_core.evaluate()` computes none of them — so "diagnostic" has
meant ABSENT rather than reported-not-gated. `metrics.py` has all three (L374).

**Why all 15 and not just Sharpe (L373):** reporting Sharpe alone hid that the worked example's
`ci_lo` is **-0.034** — its 95% Sharpe lower bound sits below zero. Omitting cheap metrics is not
brevity, it is suppressing the interval around the headline.

### 6.4 Computed, never hand-written

The generator derives and prints: the **CHECKLIST #182 denominator** ("N of M combinations passed,
across X of Y applicable producers"), **FULL FACTORIAL**, combinations run, **percent covered**, and
the **free-vs-resim split**. Hand-counting reintroduced the exact error #182 exists to prevent
(L368: my "3 of 6" was really "3 of 5").

### 6.5 Drift guard

`validate_spec()` **blocks generation** when a `Pn` appears in Section 1 but has no Table A row, or
vice versa, and rejects any SPEC lacking a formula. Section 1 and Table A are two views of one
inventory, and a hand-maintained pair diverges. Verified against three drift modes and in BOTH
directions, per the B1504 lesson that a gate exercised one way may block everything (L375).

---

## 7. WORKED EXAMPLE — `smc_breaker_block_long` (B1500-B1510)

The first strategy taken end-to-end. Recorded because the method's failure modes only became
visible by running it.

### 7.1 What was found

**The gate looked untunable and had 6 producer parameters behind it.** `fires = breaker_bullish AND
price_above_ema_200` — two booleans, no numbers. Following each to its producer surfaced
`swing_length`, `close_mitigation`, `tail N`, OB-age recency, the break test, and EMA `span`.

**The signal was saturated.** `smc_breaker_block_bullish` fired on **124 of 124 bars** on AAPL.
Instrumenting the QUALIFYING EVENT rather than the aggregate rate explained why: it is an `OR` over
the last 20 order blocks with **no time limit**, so one block aged 294-469 bars, with price 7.5-60%
away, latches TRUE forever. `tail(20)` is a COUNT window where a TIME window was intended
(S6-B1500a). Same class as B654 `cpr_narrow` (87% True) and B655 `supertrend_bullish` (99.19%).

**Two populations, cleanly separable.** Across 5 tickers: latches at 17-54% distance and 343-407
bars old; true retests at 0.8-0.9% and 49-133 bars. An empty gap on BOTH axes (distance 3-7%, age
134-294), and the axes agree on which bars are which — that gap is what set the bands.

**The tightening DIRECTION was backwards.** A breaker block is a RETEST, so the lever is an UPPER
bound on distance, not a lower one. The original framing would have selected harder for the latches
(L359).

### 7.2 Result

**0 of 200 combinations passed, across 3 of 6 applicable producers.**
24 gradable, 164 NO_EXIT_SELECTABLE, 12 BELOW_POWER_FLOOR.

| knob | effect |
|---|---|
| OB-age cap <=180 | 352 -> 109 fires, Sharpe **0.473 -> 0.563** — the filter genuinely works |
| `close_mitigation=True` | helps in **12 of 12** matched cells, median **+0.005**, best **+0.059** |
| `tail N` | **inert** — the qualifying event is always among the newest 3 |
| `break_pct_max` (owner-approved NEW-GATE) | **0 of 160 combinations gradable** — economically the cleanest discriminator, statistically unusable at n=352 |

**All 24 gradable cells fail on `pooled_sharpe` alone**; the other five gates pass everywhere. The
best cell reaches 0.617 and then fails TWO gates, because the filtering that lifted the ratio cut
holdout n to 115 and PSR reads sample size.

**The decisive number is not Sharpe.** The R5 baseline's `ci_lo` is **-0.034**. Since a subset
cannot have a tighter confidence interval than its parent, no tightening can produce a subset whose
interval excludes zero. That is a stronger argument than the Sharpe gap because it concerns sample,
not effect size (S6-B1509b).

### 7.3 Cost model, measured

| quantity | value |
|---|---|
| full factorial | **4,000** |
| subset-safe subspace (derives free per run) | 200 |
| **distinct engine runs** | **20** (4 `swing_length` x 5 EMA `span`) |
| **measured: 1 ticker x 1 config, full window** | **~35 min** (2.11 s/sim-day x 1,003 days) |
| 20 configs at ONE ticker | ~12 h |
| multi-ticker slope | **UNVERIFIED — S6-B1508a** |

**Deliberately not extrapolated to 161 or 503 tickers.** An earlier producer-only estimate came in
**9x light** against the first real engine measurement (L367); per-sim-day cost may amortise across
tickers rather than scale linearly, and a ~6-minute run at 10 tickers settles it.

### 7.4 Universe finding

The SP50 subset (top 50 by market cap; **50/50 reconciled against T1a, 50/50 with cached OHLCV**)
retains only **31 of 352 fires across 11 of 50 tickers**. All 40 combinations returned
NO_EXIT_SELECTABLE — not a bad result, NO result. **Measure the retention ratio BEFORE running under
any universe restriction, and halt below the gates' n-floor** (L365, S6-B1505c). Two disclosed
limits on the subset itself: only 249 of 503 T1a actives carry `market_cap`, so it is the top 50 of
249 rankable; and selection uses TODAY's cap over a 2022-2026 window, which is survivorship-
flavoured — acceptable for tuning, not for a verdict (S6-B1504a/b).

### 7.5 What this example changes about the method

1. **Start at the producer layer, always.** The gate expression is not the tunable surface.
2. **Instrument the qualifying event before tuning anything.** Saturation usually means a stale
   member of a disjunction is latching, not that a threshold is loose.
3. **Classify every parameter subset-safe vs fire-adding first.** It decides both the cost model
   and what can be graded offline.
4. **Check retention before restricting the universe.**
5. **A strategy can be un-rescuable for sample reasons rather than edge reasons** — `ci_lo` < 0 on
   the baseline is a stop sign that no amount of tightening addresses.

---

## 8. OPEN OWNER DECISIONS (live as of B1510)

| ticket | decision |
|---|---|
| **S6-B1508a** | 10-ticker timed run to establish the multi-ticker slope (~6 min). **Removes the last unknown from the cost model.** |
| **S6-B1507b** | Add EMA spans 100/250? They do NOT exist in `compute_ema_sma` — producer edit, NEW-GATE class. |
| **S6-B1505a** | Test-universe policy: SP50 vs R5-fired vs full T1a, with a retention-ratio precheck. |
| **S6-B1509a** | Wire `max_drawdown` / `calmar` / `deflated_sharpe` into `roster_core.evaluate()` as reported-not-gated. |
| **S6-B1502a** | Re-derive the whole band partition from MEASURED holdout n before Phase 1 is scoped. |
| **S6-B1505b** | Approve engine resimulation for P1/P6 — gated on S6-B1508a's number. |

**Standing rule (`feedback_ask_before_adding_gates_vs_threshold_only`):** whether optimisation may
ADD a gate or stays threshold-only is situational — **ask every time**. Label every knob
EXISTING-THRESHOLD or NEW-GATE before building any grid.


---

## 9. PER-STRATEGY EXECUTION CHECKLIST (B1520, owner-directed)

**Every strategy entering S6-OPT-196 runs this list in order.** Each item exists because it failed
on `smc_breaker_block_long`, the first strategy through - the L-number is the incident.

### 9.1 BEFORE any measurement

| # | gate | why (incident) |
|---|---|---|
| 1 | **Read the PRODUCER layer, not the gate expression.** Follow every consumed signal to the function that computes it and enumerate that function's parameters. | L355 - a gate reading as two booleans had **6** producer parameters; I called it untunable. |
| 2 | **Prove each parameter reaches the ENGINE.** Grep the engine's real call path. A parameter the producer accepts but the caller never passes is NOT tunable. | L387 - `screener` called `compute_smc_signals(df, ticker=ticker)`; a 20-config sweep would have produced 20 IDENTICAL cubes. |
| 3 | **Check whether a variant is ALREADY emitted** before editing a producer to emit it. | L389 - EMA spans 9/20/21/50/200 already existed; the fix was a one-line consumer change, not a producer edit. |
| 4 | **Label every knob EXISTING-THRESHOLD or NEW-GATE. Any NEW-GATE -> ASK THE OWNER.** | `feedback_ask_before_adding_gates_vs_threshold_only`; L361 - I invented `BREAK_PCT_MAX` and ran 80 out-of-scope combinations. |
| 5 | **Classify each parameter SUBSET-SAFE (only removes fires) or FIRE-ADDING.** Run count = product of the FIRE-ADDING bands ALONE. | L371 - 4,000 combinations needed **20** engine runs; costing by combinations overstates 200x. |

### 9.2 DERIVING the bands

| # | gate | why |
|---|---|---|
| 6 | **Instrument the QUALIFYING EVENT before tuning.** Record what actually satisfied the signal - age, distance, rank - not just the aggregate fire rate. | L360 - saturation (124/124 bars) was ONE stale order block latching, invisible at the aggregate level. |
| 7 | **Derive band values from the measured distribution.** Never percentile-by-reflex, never a round number. Anchor level 1 at the production value. **Then VERIFY the band against its own derivation text before running, and run `scripts/verify_grid_bands.py` on the grid AFTER — a level that changes nothing is a wasted dimension.** | L356 (deciles on an integer count), L369 (P6 band silently narrowed 5 -> 2), **L473 (P3 `tail_n` claimed to span rank 1-4 with a floor of 3; 10 -> 20 moved 0 of 50 groups and 72pct of cfg1's 200 combinations were redundant)**. |
| 8 | **State the economic event the signal captures, then check the threshold DIRECTION serves it.** | L359 - a breaker block is a RETEST, so the lever is an UPPER bound; my version selected harder for the noise. |
| 9 | **Terminate each band where holdout n < 25 or full-period n <= 100.** The gates set the last rung, not taste. | The strict end was untestable on every run - the sample, not the effect, is binding. |

### 9.3 BEFORE any run

| # | gate | why |
|---|---|---|
| 10 | **Write `run_manifest.json`, pass `prelaunch_gate.py`.** Pin frozen_sha, isolation, calendar, universe sha256, budget, and enumerate obsolescence risks each with a MECHANICAL gate. | B1335 Rule 1. It caught the P1/P6 blocker before ~14 h was spent. |
> **B1618 - THE BASELINE UNIVERSE IS 544. OWNER RULED 2026-08-17.** This document previously said
> **381** in eight places and **544** in section 10.1. `381` was the ABANDONED alphabetically-
> partitioned chunk (`r5_universe_381.txt`: 100pct A-C, zero mega-caps, 248 tickers the real R5
> never ran) - the artifact L445 was written about. MEASURED:
> `output_r5_merged_1_7/trade_exit_detail.csv` holds **544 tickers, 25pct A-C, NVDA/MSFT/TSLA/GOOGL
> present**. All references are now 544, with every DERIVED quantity RE-MEASURED rather than
> find-replaced (the exclusion count was 41-of-381 and is **22 of 544**; the 4-year cost estimate
> rescaled). **`scripts/build_sweep_100.py` still READ the 381 file** - the live `_sweep_100.txt`
> was correct only because it had been rebuilt by hand, and re-running the builder would have
> replaced it with a list sharing **31 of 100** tickers. Generator repointed (L479, CHECKLIST #199).

| 11 | **Derive the universe from the BASELINE ARTIFACT, not a roster CSV.** | L378 - R5 ran **544**; T1a has 503. Substituting the universe breaks comparability exactly as changing holdout dates would. |
| 12 | **Measure the RETENTION RATIO before restricting the universe. Halt below the gates' n-floor.** | L365 - SP50 retained 31 of 352 fires; all 40 combinations returned NO result. |
| 13 | **ARM THE MONITOR IN THE LAUNCH TURN**: hourly PushNotification while active + a */13 sentinel check + CronDelete on completion. **A run is not launched until its output path to the owner is armed.** | L385 - a sentinel tripped, halted the ladder, and reached no one until the owner asked. |
| 14 | **Classify each sentinel ERROR (invalidates -> re-run) or FINDING (result valid -> halt for a decision).** | L384 - treating every trip as failure would have discarded a valid rung and re-run it identically. |
| 15 | **Never extrapolate cost from one point.** Two measured points minimum before any projection. | L367 (9x light), L377 (23pct light), L383 (~100x heavy). Three in one session. |

### 9.4 REPORTING the result

| # | gate | why |
|---|---|---|
| 16 | **Use the locked 3-section artifact (SS6 / CHECKLIST #183).** Formula + Table A + Table B, generated, never hand-edited. | Hand-maintained views diverge. |
| 17 | **Report ALL metrics the evaluator emits**, not the headline. | L373 - Sharpe alone hid `ci_lo` = -0.034, below zero. |
| 18 | **The verdict MUST carry its denominator** - "N of M combinations across X of Y producers". Computed, never hand-counted. | CHECKLIST #182; L368 - hand-counting reproduced the error the rule exists to prevent. |
| 19 | **A small-universe PASS is an ARTIFACT until entries/ticker converges to the baseline rate.** | L382 - rung 5 passed all 6 gates at **26.63x** the R5 entry rate. |
| 20 | **A pin test must be BEHAVIOURAL, not textual.** Set the non-default, RUN the engine, assert the FIRE SET changes. | B1520 - my first "pin test" grepped source strings. That is the grep-found trap wearing a test's clothes. |
| 21 | **Before any differential test, assert the SUBJECT OCCURS in the chosen window.** A differential with n=0 on BOTH sides reports agreement and reads as a pass. | L393 - the behavioural pin test compared two EMPTY fire sets, because the short window excluded all six of the strategy's fire dates. |
| 22 | **When a targeted test comes back vacuous, check whether the same artifact answers at a coarser grain before re-running.** | L394 - the cubes I was about to discard already proved the knob works (13/76 vs 16/95 entries). |
| 23 | **The factorial is NEVER shown without the boolean producer formula.** Emit both from `producer_variant_table.py --factorial`, which cannot print one without the other. | B1523 owner directive - a bare "4,000 combinations" is unreadable without the formula that generates it, and invites debate about the number instead of the structure. |

### 9.5 Standing rules that bind every step

- **No silent misses.** Every scope item ends with a terminal disposition; a finding without a
  queue ticket does not exist.
- **Owner approval** for every threshold/gate/production-path change. Approval for one strategy is
  not approval for the next.
- **Pyramid green before every commit**; doc-sweep and queue entry in the same turn.

---

## 10. THE REPEATABLE WORKFLOW (B1548 — supersedes §2's method for all strategies)

Everything below is what the `smc_breaker_block_long` walkthrough actually cost us to learn. Run it
in order for every strategy. Each numbered gate cites the incident that produced it.

### 10.1 The four phases

| phase | scope | window | universe | produces |
|---|---|---|---|---|
| **0 INVENTORY** | build the SPECS entry | — | — | formula + Table A + factorial |
| **1 SEARCH** | all fire-adding configs | **1 year, 2024-05..2025-05** | **200** | ranked combinations |
| **2 VALIDATE** | top 10 | **2 years (owner 2026-08-17)** | **344 disjoint of 544** (was 444; Step 1 now takes 200) | gate verdicts |
| **3 ADMIT** | best 1 | 2 years | 544 | Phase 1B decision |

**Why no 2022-23 data (owner ruling 2026-08-17).** The market changed materially with AI
adoption, so 2022-23 is not wanted even for exit selection.

**AMENDED FOR STEP 1 ONLY (owner ruling 2026-08-21).** Step 1 now runs **1 year,
`2024-05-05 -> 2025-05-05`**, ending exactly at the holdout boundary, because running to
`2026-05-05` meant ranking on the holdout year Step 2 then judges (`S6-B1605c`). Step 2 is
unchanged. **Three standing constraints - locked holdout, no 2022-23 data, Step 1 off the holdout -
have no window that satisfies all three at 100 tickers**, so the UNIVERSE is the lever: 100 -> 200.

**Validation remains CROSS-SECTIONAL, not temporal**: Step 1 searches **200** tickers, Step 2
confirms on the **344 DISJOINT** tickers (was 444 - the disjoint pool shrinks by exactly what Step 1
takes). **Accepted limitation:** nothing tests whether an edge survives a regime change.

**COST, stated honestly.** I told the owner this lever costs ~2x runtime. **In ticker-years it is
approximately NEUTRAL** - 100 tickers x 2 years and 200 tickers x 1 year are both 200 ticker-years.
**Approximately, not exactly**: warmup and per-run fixed costs are not linear in ticker-days, so the
first config of the next wave is the measurement that settles it (`S6-B1831b`).

**STEP 1 PRODUCES A RANKING, NOT VERDICTS.** Gates are STEP 2's admission criteria. Step 1
emits a Sharpe-ranked list, excludes `NO_EXIT_SELECTABLE` (no exit with >=10 in-sample
trades), and hands the **top 10** forward. Step 1 can never produce a PASS - if it does,
it is doing Step 2's job (L471).

**Why 100 then 444?** The 444 are DISJOINT from the 100, so validation is genuine out-of-sample
across the ticker dimension — a combination selected by luck on 100 will not replicate. Appending
the two reconstructs 544 (valid because `--cube-isolation` bypasses the candidate cap, verified
`backtest.py:1763`; R5's cap bound on 1 of 972 days and isolation ignores it entirely).

**NO separate baseline run (L423).** All 6 gates are ABSOLUTE thresholds, so admission depends on a
candidate's own metrics. Production parameters are one of the configs anyway, so that number arrives
free if it ranks. Scoping a baseline run wasted 7.3 h of plan before this was caught.

### 10.2 Cost model — measured, not assumed

```
0.2613 s per ticker-day   (pool=10; two concordant points, 10pct apart:
                           0.2484 @ 50t x 4y, 0.2743 @ 20t x 2y)

per run  =  tickers x sim-days x 0.2613
100 tickers x  503 days (2y)  ~= 3.65 h      <- Phase 1, per config
100 tickers x 1003 days (4y)  ~= 7.3 h
544 tickers x 1003 days (4y)  ~= 39.7 h   <- 7.3 h x (544/100), rescaled B1618
```

**ALWAYS set `--screen-pool-workers`.** The default is **0 = SEQUENTIAL** (L407). On a 12-core box
`pool=10` measured **1.53x** like-for-like. It is not more because ~62pct of per-day work is serial.

**Run configs CONCURRENTLY, not the pool wider.** Amdahl caps in-run parallelism at ~1.6x; separate
configs are independent processes and scale far better.

**Never extrapolate from one point.** Five extrapolations were wrong this session: 9x light
(L367), 23pct light (L377), ~100x heavy (L383), flat-scaling read from noise (L401), and a
profiler-share mistaken for a wall-clock saving (L418). **Two concordant measurements minimum
before any projection.**

### 10.3 Engine settings for optimisation runs

| setting | value | why |
|---|---|---|
| `--cube-isolation` | ON | bypasses ALL cross-strategy gates (`backtest.py:134`) |
| `--screen-pool-workers` | 10 | default 0 is sequential (L407) |
| `--no-agents --no-news --no-git --no-walk-forward` | ON | not consumed by the 6 gates |
| `--max-run-hours` | set | the runner REFUSES to start without it |
| `OPTIMIZATION_MODE` | 1 | uncaps `max_cands` (no-op under isolation, L419) |
| `SMC_SWING_LENGTH` / `STRAT_EMA_SPAN` | per config | env-plumbed B1519; verify they reach the ENGINE |

**Isolation also bypasses TIER SIZING (B1545, owner-approved).** `TIER_POSITION_SIZE_PCT` maps
LOW/AVOID to **0.0**, and a zero size SKIPS the trade — so tier data was deciding which signals
became trades. Under isolation every valid signal opens at `CUBE_ISOLATION_SIZE_PCT`. Size cannot
affect any gate because the cube records `pnl_pct`, a PERCENTAGE.

**Do NOT skip `smart_money_score` (L418).** It looks like pure sizing, but tier gates ENTRY via
LOW→skip. A measured A/B showed 245/124 entry differences. The saving was 6.3pct, not the 14.3pct
profiler share.

### 10.4 Monitor arming — MANDATORY, MECHANICALLY ENFORCED

**A run is not launched until its reporting path is armed IN THE SAME TURN** (CHECKLIST #185).

The arming call must promise BOTH:
1. a **PERIODIC** report — "every hour" / "hourly"
2. that it is **UNCONDITIONAL** — "do not withhold", "silence is correct only when nothing is running"

**Exception-only alerting does NOT satisfy this.** It was armed wrongly FOUR times (L385 wrote only
to a log; L392 exception-only; L420 no monitor at all; L424 exception-only again — and #185's first
version PASSED that last one because it checked EXISTENCE, not CADENCE).

`scan_unmonitored_launch()` in `scripts/verify_turn_compliance.py` blocks the turn otherwise.
Pinned both directions by `test_b1545_monitor_armed_gate`.

Also required: **trip conditions** for non-zero exit, death-without-artifact, and overrun past 2x
projection; and **CronDelete on completion** so stale monitors do not train everyone to ignore alerts.

### 10.5 Completion is an ARTIFACT, never a percentage

A run is complete when `trade_exit_detail.csv` EXISTS. **A run once finished all 1,003 sim-days and
wrote no cube** (L410) — post-processing is a separate phase and died with the session. Checking
sim-day percentage would have reported 100pct.

Verify on completion: cube exists · every entry carries exactly 26 exits (#130) · entries/ticker vs
the baseline rate · gradability (how many combinations produced a verdict at all).

### 10.6 Interpreting results

- **A small-universe PASS is an ARTIFACT until entries/ticker converges** (L382). Rung 5 passed all
  6 gates at **26.63x** the R5 entry rate.
- **Report ALL 15 metrics**, never Sharpe alone (L373) — it hid a `ci_lo` of -0.034, below zero.
- **The verdict carries its denominator** (#182): "N of M combinations across X of Y producers",
  COMPUTED from Table A, never hand-counted.
- **`ci_lo < 0` on a baseline is a stop sign.** A subset cannot have a tighter interval than its
  parent, so no tightening fixes it.
- **Disabling `min_trades` during Phase 1 ranking is correct** — at 100 tickers the floor would
  reject candidates for sample size rather than quality. It is re-enabled for Phase 2 grading.

### 10.7 Standing owner rulings

| ruling | status |
|---|---|
| Holdout dates and duration NEVER change | LOCKED |
| Fewer configs to save time | **OUT OF QUESTION** — cost comes from speed or machine |
| Threshold-only vs adding a NEW gate | **ASK EVERY TIME** — no default |
| Universe 100 for search | approved; speed is key |
| Isolation bypasses tier sizing | approved, comparability loss accepted |
| Hourly updates while any run is active | STANDING |
| AWS | requires a REAL quote against the $50 CAD cap and typed approval |

### 10.8 Per-strategy checklist

Run §9's 23 items in order. The five that cost the most when skipped:

1. **Read the PRODUCER layer, not the gate expression** (L355) — a gate of two booleans had 6
   producer parameters behind it.
2. **Prove each parameter reaches the ENGINE** (L387) — `screener` called
   `compute_smc_signals(df, ticker=ticker)`; a 20-config sweep would have produced 20 IDENTICAL cubes.
3. **Classify subset-safe vs fire-adding FIRST** (L371) — run count is the product of the
   fire-ADDING bands alone; 4,000 combinations needed 20 runs, not 4,000.
4. **Harvest ALL strategies from every cube** (L404) — one run computes 128; reading one wastes 99.2pct.
5. **Pin tests must be BEHAVIOURAL** (L391, L393) — assert the ENGINE ARTIFACT changes, and verify
   the subject actually OCCURS in the window, or the test passes on two empty sets.

---

# 11. RUNBOOK — EXACT COMMANDS TO OPTIMISE ONE STRATEGY

§10 explains WHY. **This section is HOW.** Copy-paste, substitute `<STRATEGY>`, run in order.
Everything here is EXECUTED-verified on `smc_breaker_block_long` (B1546-B1558).

---

## STEP 0 — Build the SPECS entry (no run; ~1 hour of reading)

**0.1** Read the strategy's gate in `backtest/signals/screener.py`:
```bash
grep -n "def strat_<STRATEGY>" -A 12 backtest/signals/screener.py
```

**0.2** For EVERY signal in the gate, find its producer and that producer's parameters.
**Do not stop at the gate expression** — a gate of two booleans had 6 producer parameters (L355).
```bash
grep -rn "<signal_name>" backtest/signals/*.py | grep -v screener
```

**0.3** For every parameter, PROVE it reaches the engine, not just the producer (L387):
```bash
grep -n "compute_<producer>(" backtest/signals/screener.py     # is the arg PASSED?
```
A parameter the producer accepts but the caller never passes is **NOT tunable** — plumb it first
(pattern: `backtest/config.py` env-var + pass at the call site, see `SMC_SWING_LENGTH` B1519).

**0.4** Classify each parameter:
- **SUBSET-SAFE** — can only REMOVE fires -> derives offline from any cube, FREE
- **FIRE-ADDING** — changes WHICH bars fire -> needs its own engine run

**Engine runs = product of the FIRE-ADDING bands only.** Everything else is free (L371).

**0.5** Derive each band from MEASURED distributions, never round numbers (L356, L369).
Instrument the qualifying event first:
```bash
PYTHONPATH=. python scripts/instrument_breaker_block.py --ticker AAPL \
  --start 2022-05-05 --end 2026-05-05 --out output_audit/<STRATEGY>_instr.json
```

**0.6** Add the SPECS entry to `scripts/producer_variant_table.py` — `formula` + `params`, every row
citing `evidence` as `file:line`. Then verify:
```bash
PYTHONPATH=. python scripts/producer_variant_table.py --strategy <STRATEGY> --factorial
```
This BLOCKS if the formula and Table A disagree, and prints the factorial + engine-run count.

---

## STEP 1 — SEARCH: all fire-adding configs, 100 tickers, 2 years

### 1.0 PRE-LAUNCH GATE - run BEFORE building anything

**Each config costs ~3.3 h. These checks cost seconds and each one has already caught a
defect that would have wasted a full run.**

```bash
# (a) UNIVERSE PROVENANCE - is this the artifact you think it is?  (L445)
python scripts/verify_universe_artifact.py output_audit/_sweep_100.txt \
  --compare-cube output_r5_merged_1_7/trade_exit_detail.csv
```
Must print **"looks like a broad universe"**. A SLICE verdict means alphabetical skew, absent
mega-caps, or tickers the baseline never ran - the exact defect that made 2 configs search an
abandoned A-C chunk.

```bash
# (b) RAM CEILING - how many configs fit CONCURRENTLY?  (measured, not assumed)
powershell -c "$os=Get-CimInstance Win32_OperatingSystem; \
  'free_MB={0} total_MB={1}' -f [math]::Round($os.FreePhysicalMemory/1KB), \
  [math]::Round($os.TotalVisibleMemorySize/1KB)"
```
**PEAK per worker measured at 3,223 MB** (`PeakWorkingSet64`, NOT a spot reading - spot
readings understated it three times). Non-python baseline ~6.4 GB of 15.6 GB, so
**3 concurrent configs**, not 5-6. Exceeding it risks MemoryError mid-sweep.

**(c) CONFIRM THE SWEEP KNOBS DIFFER.** The engine does NOT log `SMC_SWING_LENGTH` /
`STRAT_EMA_SPAN` (S6-B1576b), so a sweep can silently run N identical configs. Assert distinct
values across concurrent launches before starting.

### 1.1 Build the input files

```bash
# ONE strategy only. This is the difference between a 4.6 h run and a 20 min run.
echo "<STRATEGY>" > output_audit/_subset_<STRATEGY>.txt

# THE SEARCH UNIVERSE IS SHARED BY EVERY STRATEGY.
# B1830 (owner ruling 2026-08-21): size is now 200, and the builder takes --n.
# This SUPERSEDES the 2026-08-14 "fixed at 100" ruling. _sweep_200.txt is a
# SUPERSET of _sweep_100.txt by construction (both are top-N of one ADV-sorted
# list), so earlier 100-ticker results stay interpretable as a subset.
# Rebuild ONLY if the 544-universe changes. Owner ruling 2026-08-14,
    # re-anchored to the CORRECT universe by owner ruling 2026-08-17 (B1618).
# Builder: scripts/build_sweep_100.py
```

#### CRITERION: top 100 by average dollar volume (ADV) over the WARMUP window

**Owner ruling 2026-08-14.** ONE fixed list, shared by every strategy.

**Why fixed, not per-strategy.** The previous builder ranked tickers by *that strategy's* R5 fire
count, so each strategy was searched on the 100 tickers where it had historically fired most. That
is **in-sample selection**: it inflates apparent edge, and by a different amount per strategy, so
cross-strategy comparisons are corrupted too. A fixed list costs statistical power for
rarely-firing strategies and buys an unbiased, comparable result.

**Why ADV.** The search phase exists to RANK combinations on 100 tickers such that the ranking
transfers to 544. Liquidity is strategy-neutral, stable, and matches what would actually be traded,
so fills and slippage stay realistic.

**Why the WARMUP window (2021-05-06 to 2022-05-05).** It precedes the locked backtest window
entirely, so universe selection carries no lookahead into the period being measured.

**TWO DISCLOSED BIASES — do not rediscover these later:**

1. **SPY is in the list** (ADV $37.2B, ~2.8x AAPL). It is a Tier-1 ETF and legitimately inside the
   544, but it is an index, not a single stock, and strategies behave differently on it.
2. **22 of 544 are excluded** (MEASURED B1618; the old 41-of-381 was the abandoned chunk's
   figure, wrong in both halves) for lacking 100 warmup bars, which means **every ticker that listed
   after 2021-05-06 is structurally ineligible** (ACLX, ALAB, AISP, AMLX, ...). Recent IPOs can
   never enter this SEARCH universe. They remain in the 544 used for Phase-2 VALIDATION, so no
   combination is ever *admitted* on the biased universe — but its RANKING is derived from one.

**The fixed 100 (ADV-ranked, highest first):**

**Source universe: `output_audit/r5_universe_544.txt`** (from `output_r5_merged_1_7`, the R5 baseline `PHASE_1B_ROSTER.md` cites). **NOT** the former `r5_universe_381.txt`, which came from an abandoned alphabetically-partitioned chunk - 380/381 tickers A-C, no MSFT/NVDA/GOOGL, 248 tickers R5 never ran (L445). Verify any universe file before use:
```
python scripts/verify_universe_artifact.py output_audit/_sweep_100.txt --compare-cube output_r5_merged_1_7/trade_exit_detail.csv
```

```
SPY  TSLA  AAPL  AMZN  NVDA  MSFT  AMD  GOOGL  GOOG  MRNA
NFLX  PYPL  BA  BAC  JPM  V  XOM  DIS  MU  PFE
CVX  INTC  CRM  MA  ADBE  QCOM  C  F  BRK-B  WFC
UNH  HD  T  JNJ  TWTR  COIN  PG  WMT  UBER  AVGO
VZ  CSCO  ABNB  COST  AMAT  GS  MRK  CMCSA  NKE  GM
KO  PLTR  MS  ABBV  CRWD  TXN  ORCL  OXY  BKNG  TGT
TMO  LRCX  LOW  INTU  BMY  FCX  NOW  CCL  SBUX  PEP
CAT  DHR  GE  LLY  CHTR  ACN  ATVI  UNP  ABT  AAL
PANW  MCD  DE  IBM  SPGI  NEE  AXP  LMT  AMGN  ADI
TMUS  HON  MDT  COP  FDX  UAL  UPS  DASH  LIN  CVS
```


### 1.2 ARM THE MONITOR — **BEFORE** the launch, in the SAME turn

**The Stop hook BLOCKS the turn otherwise** (CHECKLIST #185/#186). The CronCreate prompt MUST
contain a PERIODIC marker (`every hour` / `hourly`) AND an UNCONDITIONAL marker
(`do not withhold` / `silence is correct only when nothing is running`).
Exception-only alerting does NOT satisfy it — that was armed wrongly four times.

### 1.3 Launch one config

```bash
STRATEGY_SUBSET_FILE=output_audit/_subset_<STRATEGY>.txt \
OPTIMIZATION_MODE=1 \
SMC_SWING_LENGTH=<P1_value> STRAT_EMA_SPAN=<P6_value> \
PYTHONPATH=. python backtest/run_phase1a.py \
  --tickers-file output_audit/_sweep_200.txt \
  --phase 1a-beta --cube-isolation \
  --no-agents --no-news --no-git --no-walk-forward \
  --screen-pool-workers 3 \
  --start 2024-05-05 --end 2025-05-05 \
  --max-run-hours 4.0 \
  --output-dir output_<STRATEGY>_cfg<N>
```

**Every flag matters:**

| flag / env | why |
|---|---|
| `STRATEGY_SUBSET_FILE` | **MANDATORY — never optional.** Runs ONE strategy instead of 182 AND is the gate that enables demand pruning. Omitting it loses BOTH savings, **silently**, exactly as B1558 did (4.56 h, L432). Owner-agreed 2026-08-14 to make it non-optional in this command. **Never set it for Phase 1B / full-roster runs.** |
| `OPTIMIZATION_MODE=1` | uncaps `max_cands`; **no-op under `--cube-isolation`** (L419). Does NOT skip `smart_money_score` — that was tried and REVERTED (L418) |
| `SMC_SWING_LENGTH`, `STRAT_EMA_SPAN` | the FIRE-ADDING config; one run per combination of these |
| `DEMAND_PRUNING=0` | **only if a run dies with `SkippedSignalError`** — that means warmup missed a key some regime reads. Default `1`. Raise `DEMAND_PRUNING_WARMUP` (default 25) before disabling |
| `--cube-isolation` | bypasses ALL cross-strategy gates AND tier sizing (B1545) |
| `--screen-pool-workers` | **default is 0 = SEQUENTIAL** (L407). Use 0 for a clean timing measurement; ~3 per config when running several concurrently. **Total workers must never exceed 10 physical cores** |
| `--max-run-hours` | the runner REFUSES to start without it |
| `--start 2024-05-05 --end 2025-05-05` | **1-year SEARCH window that ENDS AT THE HOLDOUT BOUNDARY** (owner ruling 2026-08-21). Step 1 previously ran to `2026-05-05` and therefore ranked on the holdout year it is judged against - `S6-B1605c`. |

**RETRACTED 2026-08-22 (B1877) - THE SECTION BELOW BLAMED THE WRONG THING.** The note said demand
pruning can silently produce a zero-fire run. **It cannot.** MEASURED with one variable changed:

```
venv python, DEMAND_PRUNING=1  -> 10 trades
venv python, DEMAND_PRUNING=0  -> 10 trades       pruning changes NOTHING

subprocess + sys.executable (venv)  -> 3/33 producers kept, 10 trades
subprocess + bare "python" (system) -> 2/33 producers kept,  0 trades
```

**The cause is the INTERPRETER.** `subprocess.run(["python", ...])` from inside the venv resolves
to the SYSTEM python, which keeps 2 of 33 producers and fires nothing. The B1849 "causal test"
varied pruning AND the launch path at once and attributed the whole difference to pruning.

**What survives:** the Step-1 window at 200 tickers FIRES (29 of 29 screen-days) - that run went
through bash, i.e. the venv. **What does not:** every claim below about pruning zeroing a run.
**ALWAYS launch with an explicit interpreter path**, never a bare `python`, from any script.

**ORIGINAL NOTE, PRESERVED FOR LINEAGE AND KNOWN WRONG ON ITS CENTRAL CLAIM:**

**DEMAND PRUNING AND UNIVERSE SIZE - MEASURED 2026-08-21 (B1861).** Demand pruning can
silently produce a ZERO-FIRE run: exit 0, no `SkippedSignalError`, correct windows, and an empty
cube that passes every completion check. **It is a SMALL-UNIVERSE effect and Step 1 at 200 tickers
is clear:**

```
run          universe      demand-pruning ARMED    screen-days   days with >0 candidates
arm A        10 tickers    2/33 kept, 4 reads      249            0
fire-check   185 active    3/33 kept, 5 reads       29           29      (7..29 per day)
```

**Warmup observes what the active strategies READ. A wider universe reads more, so more producers
survive pruning.** Causally confirmed on the narrow side: same window and tickers with
`DEMAND_PRUNING=0` gave 20 trades and 75 files against 0 trades and 1 file.

**Consequence for the runbook: never diagnose a strategy on a 10-20 ticker slice.** A zero-fire
result there is as likely to be pruning as it is to be the strategy. `zero_output_runs()` in
`scripts/verify_postconfig_complete.py` detects the signature - `status=complete`, `trades=0`, no
`trade_log.csv` - independently of the post-config ledger.

**Denominator caution (L568):** the screener reports against the **PIT-ACTIVE** universe, not the
ticker file's line count - `/185`, not `/200`. A monitor grepping the file count matches nothing
and reads as silence.

**UNIVERSE ARTIFACT VERIFIED 2026-08-21 (B1846, `#193`).** `verify_universe_artifact.py
output_audit/_sweep_200.txt --compare-cube output_r5_merged_1_7/trade_exit_detail.csv`:

```
baseline cube      : output_r5_merged_1_7 (544 tickers)
overlap            : 200
in file, NOT cube  : 0            <- no orphan tickers
in cube, NOT file  : 344
VERDICT: looks like a broad universe
```

**This is the check two configs skipped once and paid 3.30 h each for** (`S6-B1576a` measured that
elapsed; L445) - they searched an abandoned A-C chunk because nobody looked at the ticker list.
`_sweep_200` is clean on both axes: every ticker exists in the baseline, and the spread is broad
rather than alphabetically partitioned.

**INTENTIONALLY NARROW (stated here because the verifier asks for it).** `_t10.txt` / `_t20.txt`
are `head -N` slices of `_sweep_200` used ONLY by the B1845 timing probe, and `_t10` flags
`SLICE / SUSPECT - 70pct alphabetical skew`. That is what a 10-line head produces and it is fine
for timing, **but it is a stated LIMITATION of that probe, not a clean bill** - see `S6-B1846c`.

| `--tickers-file _sweep_200.txt` | **200 tickers, not 100** (same ruling). Halving the window alone keeps only **50-56pct of entries** (MEASURED B1817) and pushes most of the grid back to `NO_EXIT_SELECTABLE`; widening the universe restores the sample. **Superset of `_sweep_100.txt` by construction**, so wave-1 results stay interpretable. |

### 1.4 Concurrency

Launch several configs as **separate processes**, each with `--screen-pool-workers 3`.
In-run parallelism caps at ~1.6x (Amdahl, ~62pct serial), so concurrency across configs scales
better. **Keep total workers <= cores.** Watch for `MemoryError` in the log — the 182-strategy
pilot hit it during cube replay; single-strategy cubes are ~1/182 the size, which is what makes
concurrency viable.

### 1.5 Completion is an ARTIFACT, never a percentage

```bash
ls -la output_<STRATEGY>_cfg<N>/trade_exit_detail.csv   # THIS is completion
```
A run once finished all 1,003 sim-days and wrote **no cube** (L410). Also expect the process to
hang after writing — the pool does not always exit. Verify the artifact, then kill if needed.

---

## STEP 2 — GRADE: derive the subset-safe combinations

```bash
PYTHONPATH=.:scripts python scripts/tighten_breaker_block.py \
  --cube output_<STRATEGY>_cfg<N>/trade_exit_detail.csv \
  --out output_audit/<STRATEGY>_cfg<N>_grid.json
```

Per combination this: filters the cube to surviving fires, selects the best exit **IN-SAMPLE ONLY**,
grades the holdout on all 6 gates via `roster_core` (identical bar to the Phase 1B roster), and
records all 15 metrics.

**Verdicts:** `PASS` · `FAIL` · `BELOW_POWER_FLOOR` (holdout n < 30) ·
`NO_EXIT_SELECTABLE` (too few IS trades to rank 26 exits) · `ZERO_FIRES`

**Generate the locked artifact:**
```bash
PYTHONPATH=. python scripts/producer_variant_table.py \
  --strategy <STRATEGY> \
  --results output_audit/<STRATEGY>_cfg<N>_grid.json \
  --keys close_mitigation,break_pct_max,age_bars_max,tail_n \
  --out output_audit/PRODUCER_VARIANT_TABLE_<STRATEGY>.md
```

---

## STEP 3 — VALIDATE the top 10 (4 years, disjoint tickers)

Rank all combinations by Sharpe with `min_trades` DISABLED (at 100 tickers the floor rejects on
sample size, not quality). Take the top 10 — they will span only a few distinct engine configs.

Re-run those configs on the **444 tickers NOT in the search set**, full 4-year window, then append
to the 100-ticker 4-year runs to reconstruct 544. Valid because `--cube-isolation` bypasses the
candidate cap (`backtest.py:1763`).

**NO separate baseline run is needed** (L423) — all 6 gates are ABSOLUTE thresholds, so admission
depends on a candidate's own 4-year metrics.

---

## STEP 4 — ADMIT

A combination enters Phase 1B only if it passes **all 6 gates on the 4-year holdout**:
`pooled_sharpe >= 1.0` · `profit_factor >= 1.3` · `sortino >= 0.7` · `psr >= 0.95` ·
`min_trades_holdout >= 25` · `min_trades_full_period > 100`

**Report the verdict WITH its denominator** (#182): *"N of M combinations passed, across X of Y
applicable producers"* — computed by the table generator, never hand-counted.

---

## REFERENCE — ENGINE CONTROLS (code-verified B1570, 2026-08-14)

**Every control on the optimisation path, what it does, and whether it is optimisation-only.**
Values below were read from `backtest/config.py` at cite time, not from memory.

| control | default | scope | what it does |
|---|---|---|---|
| `STRATEGY_SUBSET_FILE=<path>` | unset | **OPT-ONLY** | Newline-separated strategy names. `run_phase1a.py` REPLACES `ALL_STRATEGIES` with the matched subset, so only those strategies are evaluated. **Refuses to start if it resolves to zero** (`B1425 FATAL`), so a typo cannot silently become a full-roster run. **This is also the gate for demand pruning — without it, pruning is OFF.** |
| `DEMAND_PRUNING` | `1` (on) | **OPT-ONLY** | Kill switch for demand-driven signal pruning. Inert anyway unless `STRATEGY_SUBSET_FILE` is set. Set `0` to disable if a run dies with `SkippedSignalError`. |
| `DEMAND_PRUNING_WARMUP` | `25` bars | **OPT-ONLY** | Bars spent RECORDING which signal keys are read before pruning arms. Raise it if a strategy's branches are rare. |
| `OPTIMIZATION_MODE` | `0` | **OPT-ONLY** | Uncaps `max_candidates_per_day`. **No-op under `--cube-isolation`** (isolation already bypasses the cap, L419). Does NOT skip `smart_money_score` — that was tried and REVERTED (L418), because tier maps LOW→0.0 and a zero size SKIPS the trade, so tier GATES ENTRY. |
| `SMC_SWING_LENGTH` | `20` | sweep knob | Swing length for SMC primitives. FIRE-ADDING — each value needs its own engine run. |
| `STRAT_EMA_SPAN` | `200` | sweep knob | Which EMA span the trend leg reads. FIRE-ADDING. Built into the key at RUNTIME (`f"price_above_ema_{span}"`) — see the L437 trap below. |
| `STAGE2_NO_LIVE_FETCH` | `1` (on) | **ALWAYS-ON** | Raises on any OHLCV cache miss instead of degrading silently. Set `0` ONLY for prefetch/setup, never a backtest. |

#### Config assignments as RUN (S6-B1537b, recovered B1915)

The table above gives the sweep knobs and their DEFAULTS. It never recorded
which value each config actually ran, which is the fact `S6-B1537b` says must
never be re-asked. **Recovered from the run's own record,
`output_audit/b1576_par.log`** — not from a plan, a note, or memory:

| config | `SMC_SWING_LENGTH` | `STRAT_EMA_SPAN` | exit | cube rows | wall |
|---|---|---|---|---|---|
| `output_cfg1` | `20` | `200` | 0 | 8,581 | 11,891 s (198.2 min) |
| `output_cfg2` | `10` | `50` | 0 | 10,921 | 11,973 s (199.6 min) |

**`cfg1` is the production anchor** — both knobs at their defaults — so cfg1 vs
cfg2 moves BOTH knobs at once and is not a single-variable comparison. Two
later cubes, `output_w1_sw20_span21` and `output_w1_sw20_span50`, vary the span
alone against `sw=20`.

**Timing measured B1915 from `b1576_cfg1.log` / `b1576_cfg2.log`:** end-to-end
198.1 / 199.5 min, of which the day loop is 195.9 / 197.3 and post-processing
is **2.2 / 2.1 min — 1.1%**. Post-processing is NOT on the slow path, and
re-costing the 20-config sweep on end-to-end rather than day-loop moves it
**32.9 h → 33.3 h (1.2%)**. That costing assumes the **measured** 2-way
concurrency; **3-way and above is unvalidated pending the peak-RSS measurement
(`S6-B1552a`)** — a wall-clock that divides by N says nothing about N copies
fitting in RAM.

| `ENGINE_OUTPUT_DIR` | unset | infra | Output directory override. |

**Config flags (not env), current live values:**
`USE_PRECOMPUTED_SIGNALS=False` (B1563 — the cache is EMPTY; re-enabling needs a PIT audit first) ·
`USE_SMC_PANEL_CACHE=False` (**UNSAFE** — 11.5pct divergence measured, B1542) ·
`USE_PANEL_TECHNICAL_SIGNALS=True` · `SMC_PHASE='PRODUCTION'` (if not PRODUCTION, `compute_smc_signals`
returns `{}` and every SMC strategy silently dies) · `DATA_LOAD_START=2021-05-06` ·
`CUBE_ISOLATION_SIZE_PCT=0.01`.

---

## REFERENCE — WHAT GETS SKIPPED, AND WHEN

Demand pruning computes only the producers whose signal keys the ACTIVE strategies actually read.

**It arms in three stages.** Bars 1-25 compute EVERYTHING and RECORD reads. Then the skip set is
derived and pruning arms. From then on the signals dict is wrapped in `GuardedSignals`, so reading a
pruned-away key RAISES `SkippedSignalError` instead of returning `.get()`'s default.

**How the required-key set is built — BOTH methods, unioned (B1570):**
- **RUNTIME recording** catches keys built at runtime, e.g. `f"price_above_ema_{STRAT_EMA_SPAN}"`.
  A static scan sees only ONE of `smc_breaker_block_long`'s two keys (L437).
- **STATIC extraction** catches keys a boolean SHORT-CIRCUITED past. `smc_ote_long` is
  `s.get(zone) and (s.get(bos) or ...)`; if `zone` is False across all warmup bars the `and` never
  evaluates the right side, so the bos keys are never READ and `bos_choch` would be pruned (L444).

The two fail in COMPLEMENTARY directions. Union is strictly safer — it can only KEEP more producers.

**Measured effect on `smc_breaker_block_long` (1 strategy):**
- Technical: **32 of 33 producers skipped**, 512 → 46 keys, 95.8pct off `compute_all_signals`
- SMC: **3 of 6 primitives skipped** (`retracements` 46.7pct + `fvg` 28.1pct + `bos_choch` 18.1pct of
  SMC cost), 91.5pct off `compute_smc_signals`. `ob`, `liquidity`, `swings` always run.

**SMC redundancy is automatic.** 22 strategies read `smc_*` keys; each keeps exactly the primitives
it needs — verified on `smc_fvg_retest_long` (keeps fvg), `smc_ote_long` (keeps bos_choch +
retracements), `smc_bos_continuation` (keeps bos_choch).

### PHASE 1B IS DIFFERENT — pruning is INERT there by design
`STRATEGY_SUBSET_FILE` is an OPTIMISATION-ONLY device. Phase 1B simulates all passed strategies
together, where every producer is read anyway. With no subset file, `wrap()` returns **the same
object** (identity-pinned by test) and `smc_skip_primitives()` returns empty — **zero overhead, zero
behaviour change**. Never set the subset file for a Phase 1B or full-roster cube run.

---

## REFERENCE — MEASURED COSTS (and why a percentage alone is a lie)

| shape | measured |
|---|---|
| 182 strategies, 100 tickers, 2y, pool=10 | **4.56 h** (2.63 h day loop + 1.93 h post-processing) |
| 182 strategies, 20 tickers, 2y, pool=3 x3 concurrent | 3,696 s |
| **1 strategy, 5 tickers, 2y, pool=0, UNPRUNED, cold cache** | **1,920 s** (B1568) |
| **1 strategy, 5 tickers, 2y, pool=0, UNPRUNED, warm cache** | **703 s** (B1569b) |
| **1 strategy, 5 tickers, 2y, pool=0, PRUNED, warm cache** | **366 s** (B1569b) |
| Machine | 10 physical / 12 logical cores, 15.6 GB RAM |

**THE SAME UNPRUNED CONFIG TOOK 1,920 s AND 703 s — 2.7x apart, same machine, same code.** The only
difference was OS file-cache warmth. Consequences you must respect:

1. **Cross-session elapsed times are NOT comparable.** A/B arms must run BACK-TO-BACK in one session.
2. **A saving is a fraction OF A BASELINE, and the baseline's composition is not constant.** Pruning
   measured **14.64pct** against a cold baseline and **47.94pct** against a warm one — the cold
   baseline carries I/O that pruning cannot remove and dilutes the fraction. Quote the saving WITH
   its cache condition, never alone.
3. Comparing B1569b's pruned arm (366 s) to B1568's cold baseline (1,920 s) would report **81pct**,
   two-thirds of it filesystem cache. That is the trap re-running the baseline exists to avoid.

**Correctness bar for any optimisation claim:** the cube must be BIT-IDENTICAL, not merely
same-row-count. B1568 + B1569b cubes all hash to `615233dbab2756d0` (1,352 x 37).

---

## REFERENCE — PARALLELISM

- **Cores: 10 physical.** With `--screen-pool-workers 0` (sequential) each config is ~1 core.
- **RAM is the binding constraint, not cores.** A single worker measured **2.1-2.3 GB**; at 15.6 GB
  total that caps concurrency at roughly **5-6 configs**, not 10.
- **Run configs CONCURRENTLY rather than widening the pool.** In-run parallelism caps at ~1.6x
  (Amdahl, ~62pct serial); separate processes scale far better. B1558 measured 2.24x throughput at
  3-way.
- **Never let total workers exceed physical cores** — pool=60 on 1 ticker ran 11.6x SLOWER than
  sequential (L-pool).
- **Do NOT run a pyramid or any other CPU work during a timing A/B.** It inflates the arm in flight
  and biases the saving upward.

## SWEEP EXECUTION MODE - OPTION C (owner ruling 2026-08-17)

**Wave 1 is OWNER-GATED. Waves 2-9 run autonomously, subject to MECHANICAL HALTs.**

Wave 1 is gated because it is the first `--screen-pool-workers 3` measurement; the remaining 8
waves are re-costed from its ELAPSED before any of them starts. Autonomy after that is safe only
because the stop conditions are measured, not judged in the moment:

| HALT condition | why it is mechanical |
|---|---|
| cube sanity fails: not exactly 1 strategy, not exactly `[26]` exits/entry, or a mega-cap absent | step 1, already scripted |
| diagnosis loss > `--max-diag-loss`, or ANY ticker dropped | the grader ABORTS (B1623) |
| spot-check agreement < 100pct on any of the three legs | step 4 |
| a config's ELAPSED deviates > 2x from wave 1's measured figure | arithmetic on the log |
| `MemoryError`, or free RAM below one worker's PEAK (3,223 MB) | `Get-CimInstance` in the */15 check |
| the adversarial review produces a CONFIRMED finding | step 5 |

**On any HALT: stop the sweep, do not start the next wave, notify the owner with the evidence.**
Waves are never started to "keep the machine busy" - an unexplained result stops the sequence.

## MANDATORY POST-CONFIG ANALYSIS (owner directive - run after EVERY config, unprompted)

**This runs after every config completes. No prompt required. Skipping a step is a silent miss.**

### 1. Cube sanity - BEFORE trusting any number
```bash
python -c "
import pandas as pd; d=pd.read_csv('output_cfg<N>/trade_exit_detail.csv',low_memory=False)
ex=d.groupby(['ticker','entry_date']).exit_method.nunique()
print('strategies',d.strategy.nunique(),'| exits/entry',sorted(ex.unique()),'| entries',len(ex))
print('mega-caps',[t for t in ['NVDA','MSFT','TSLA'] if t in set(d.ticker)])"
```
PASS requires: exactly **1** strategy, exactly **[26]** exits/entry, mega-caps PRESENT
(their absence means the archived A-C chunk universe, L445).

### 2. Grade - with the CONFIG'S OWN parameters
```bash
PYTHONPATH=.:scripts python scripts/tighten_breaker_block.py   --cube output_cfg<N>/trade_exit_detail.csv   --swing-length <THE SW THIS CONFIG RAN> --min-n 10   --out output_audit/<batch>_cfg<N>_grid.json
```
**`--swing-length` MUST match the run.** The grader RE-DERIVES every fire; a mismatch silently
drops the fires that do not reproduce - cfg2 lost 167 of 420 that way (L454). The union
diagnosis-loss gate aborts above 2pct.

### 3. Outlier + discrepancy sweep - ALL of these, every time
| check | why |
|---|---|
| cube entries == grid max fires | catches silent diagnosis loss (L454) |
| verdict distribution | `NO_EXIT_SELECTABLE` is a SAMPLE-SIZE verdict, not exit quality |
| rank by `ci_lo`, NOT `sharpe` | the higher Sharpe can have a NEGATIVE lower bound (L455) |
| `exits_effective` vs 26 | duplicate exits collapse; "best of 26" is usually fewer (L461) |
| PASS rows with marginal `ci_lo` | 5 of 200 at `ci_lo` +0.08 is a WEAK positive, not a result |
| any PASS selecting `regime_flip` | **run `measure_degraded_exits(cube)`** - do not judge by date. It is a time stop in ALL FOUR existing cubes (owner-accepted 2026-08-21) and live in every config run after B1682 |
| **every swept LEVEL changes the outcome** | **a level that changes nothing is a wasted dimension (L473)** |
| **top-N holds N DISTINCT fire-sets** | **cfg2's top 10 was 4 real candidates wearing 10 rows (L473)** |
| **measure DEGRADED exits per cube** | `regime_flip` was a time stop in every pre-B1622 cube; measured, not assumed (L483) |
| **equivalence-class members keep the SAME FIRES** | a de-dup key of `(fires, exit, sharpe)` could merge different fire-sets that tie; verified 6 of 6 (B1612) |

```bash
python scripts/verify_grid_bands.py output_audit/<batch>_cfg<N>_grid.json --anchor tail_n=20
```
**This is the step that was missing.** The sweep above already carried a duplicate-collapse
lens - `exits_effective` vs 26 - and it found `26 exits -> 23 effective`. **The same question
was never asked of the PARAMETER axis**, so `tail_n` sat at `[3, 5, 10, 20]` through 400 graded
combinations with `10 -> 20` moving **0 of 50** cfg1 groups. A lens is defined by its QUESTION,
not by the axis it was first applied to (L474). `--anchor` exempts the production value, which
is carried for reproducibility, not to discriminate.

**ACCEPTED ASYMMETRY - RESTATED 2026-08-21 (owner ruling (b)).** The 2026-08-17 version of this
note said cfg1/cfg2 were degraded *"while the 18 remaining configs carry a live one"*. **That was
false, and the correction matters more than the acceptance.**

`exit_regime_flip` needs TWO inputs - `regime_by_date` and `regime_at_entry` - supplied in two
separate batches. MEASURED via `rc.measure_degraded_exits` on **all four existing cubes**:

```
output_cfg1              time_stop_20d == regime_flip     written Aug 15
output_cfg2              time_stop_20d == regime_flip     written Aug 15
output_w1_sw20_span21    time_stop_20d == regime_flip     written Aug 18 13:21
output_w1_sw20_span50    time_stop_20d == regime_flip     written Aug 18 13:21
```

**Wave 1 is degraded too**, because it ran hours BEFORE B1682 - whose own commit title reads
*"I fixed ONE OF THE TWO things the exit needed, and called it done"*. B1622 supplied the first
input; B1680 then found the fix had never run.

**OWNER RULING 2026-08-21: accept it.** Not re-running wave 1 (~5.8 h) or cfg1/cfg2 (~6.6 h).

**What this commits us to, stated so nobody re-derives it:**

- **All four existing cubes carry `regime_flip` as a 20-day time stop**, i.e. a duplicate of
  `time_stop_20d` under another name. Their effective exit family is **25, not 26**.
- **Every config run from now carries a LIVE `regime_flip`** - both inputs are in the code
  (`backtest.py:2650` sets the field, `:3106` passes it, `exit_strategies.py` injects both).
- **Therefore `regime_flip` is NOT comparable between the four existing cubes and any later one.**
  Rankings are unaffected - no `regime_flip` appears in either wave-1 top-10 - so what is lost is
  comparability on that one exit, not the identity of the winners.
- **Never quote "best of 26" for these four.** `roster_core.measure_degraded_exits(cube)` MEASURES
  it from any cube, so this needs no date bookkeeping:

```bash
python -c "import sys;sys.path.insert(0,'.');import scripts.roster_core as rc,pathlib; \
  print(rc.measure_degraded_exits(rc.load_cube(pathlib.Path('output_cfg<N>/trade_exit_detail.csv'))))"
```

MEASURED 2026-08-17 on cfg2: **3 collapsed pairs**, not one -
`atr_trail_mae_conditional`==`atr_trail_1x`, `reverse_signal`==`atr_trail_mae_conditional`,
`time_stop_20d`==`regime_flip`. That independently reproduces the known **26 exits -> 23
effective** (L460). **Never quote "best of 26" without running this first.**

### 4. Spot check 50 random trades - EVERY config
```bash
PYTHONPATH=. python scripts/spot_check_trades.py   --cube output_cfg<N>/trade_exit_detail.csv --n 50   --swing-length <SW> --ema-span <SPAN>
```
**SCOPE, verified against code (B1631):**

| leg | what it does | file |
|---|---|---|
| re-derivation | P1-P6 rebuilt from raw parquet under PIT, calling the vendored LIBRARY | `spot_check_trades.py:58` |
| **engine** | **`compute_smc_signals` called at the same bar with the config's own parameters** | **added B1631** |
| execution | entry is a real trading day, exit >= entry, `hold_days` matches the calendar distance, `pnl_pct` sign-consistent | `spot_check_trades.py:101` |

**OHLCV-only is CORRECT here, and not by luck.** `smc_breaker_block_long` has exactly two gates -
`smc_breaker_block_bullish` and `price_above_ema_{span}` - both OHLCV-derived, and under
`--cube-isolation` `backtest.py:2379-2380` sets `size_pct = CUBE_ISOLATION_SIZE_PCT`, bypassing
tier sizing. That matters because tier GATES ENTRY otherwise (LOW -> 0.0 size -> the trade is
SKIPPED, L418/B1544), which would make `smart_money_score` an unchecked entry input.
**At Phase 1B, with tier sizing live and the full roster running, OHLCV-only coverage is NOT
sufficient** - the smart-money leg re-enters the entry path and must be checked too.

**Two legs could only say THAT they disagreed.** Adding the engine makes it three-way, so a
disagreement localises: engine+cube agreeing against the re-derivation means the CHECKER is wrong
(L457); re-derivation+engine agreeing against the cube means the RUN is wrong.

**Expected: 100pct agreement on all three, 0 execution failures.** Anything less is a finding.

**FIRST, prove the check can verify the strategy at all (B1634, owner correction):**

```bash
PYTHONPATH=. python scripts/verify_spotcheck_coverage.py <strategy>
```

Step 4 is a STANDARD, not a check written for one strategy. OHLCV-only coverage is complete for
`smc_breaker_block_long` because it reads two price-derived signals - **a property of the STRATEGY,
not of the check.** The rest of the roster reads smart-money, news, earnings, short-interest,
index-event and filing signals, and an OHLCV-only re-derivation would certify those **without ever
reading the input that gates them**, producing output identical to a real verification.

MEASURED across the roster: **185 of 222 strategies have at least one input the spot check cannot
verify**; `smc_breaker_block_long` is in the 37 that pass, so THIS sweep is covered - proven, not
assumed. The gate is fail-CLOSED: an unclassified key counts as unverifiable, because an
unrecognised input is precisely the one nobody thought about.

**Before the spot check certifies any strategy, this must exit 0.**

### 5. ADVERSARIAL REVIEW - find bugs and logic errors (owner phrasing, verbatim)

> *"Do an adversarial review of the code and map for false positives and false negatives.
> Identify any or all bugs and add them to the execution queue."*
> *"It was broader than this - it was also about finding bugs and logic errors."*

**FP/FN is ONE lens, not the scope.** The scope is bugs and logic errors. The FP/FN lens alone
would have MISSED the largest finding of this session - identical exit methods are neither a false
positive nor a false negative, they are a LOSS OF INFORMATION.

Run every lens, every config:

| lens | question | example found |
|---|---|---|
| **False positive** | a trade/PASS recorded that should not exist? | - |
| **False negative** | a fire the engine missed, a PASS suppressed? | MIN_N=30 suppressed 5 real passes (L455) |
| **Silent degradation** | does anything FALL BACK without saying so? | `regime_flip` was a time stop in every cube (L461) |
| **Duplicate information** | are "distinct" columns byte-identical? **Ask this of EVERY axis - exits, parameters, tickers, dates - not only the one where it first paid off.** | 26 exits -> 23 effective (L460); `tail_n` 3 of 4 levels inert (L473) |
| **Units / scale** | do the units of every input match the constant? | 252 trading days over a CALENDAR hold (L458) |
| **Config blindness** | does a re-deriving component get the ORIGINATING params? | grader graded cfg2 at the wrong swing_length (L454) |
| **Provenance** | is the artifact the one you think it is? | universe was an abandoned A-C chunk (L445); the sweep BUILDER still read it (L479) |
| **Executability** | can the ENGINE apply what the search selected, or does the knob exist only in the grader? | 4 of 6 swept parameters were grader-only; the graded winner would have run as 420 fires at Sharpe 0.789 instead of 68 at 2.239 (L475) |
| **Fail-open** | when this component meets unexpected input, does it PASS? Every branch that `continue`s, defaults, or falls back is a candidate | a comment satisfying a code check, a missing key skipped by the band gate, a wrong file found by the grader, a dropped ticker vanishing, an exit falling back to a time stop, a gate scoring "unknown" above "known bad" (L482, L483, L484) |
| **Self-referential verification** | does this check compare code to REALITY, or to another piece of the same author's code? | the spot check re-implemented the producer and agreed 100/100 while 4 parameters did not exist in the engine; a pin test asserting a STRING passed for the whole inert life of a fix; the orphan gate keyword-matched three phrases and missed 4 of 4 (L476, L481, L485) |
| **Completion vs artifact** | did the work happen, or did the command merely return? | a smoke reported "PASSED" with no cube written; a killed child reported exit 0 at simulated day 25 of 504 (L486) |
| **Effective parameter** | a flag that was ACCEPTED - does changing it change the answer? Run it at two values and compare. Enforced by `scripts/verify_flag_binds.py` | `--min-n 10` was accepted and governed admission only, while `OOS_MIN_N=30` in another module decided which cells got a Sharpe - so `--min-n 10` and `--min-n 20` were byte-identical (S6-B1705b, fixed B1714) |

**The 4 lenses below the original 7 were added B1631 from THIS session's actual defects** - every
example is a defect that the original 7 did not name and that shipped anyway. A lens list that only
grows after a failure is working as designed; one that never grows is not being used.

**LENS 12 was added B1800 (S6-B1705f, owner-approved) and is the only one with a MECHANISM rather
than a question.** The other eleven are read and applied by judgment; this one runs:
`binds(fn, param, a, b, ...)` returns `BINDS` / `INERT ON THIS INPUT` / `RAISED`.

- **It proves BINDING, never CORRECTNESS.** A flag that binds to the wrong thing passes here - that
  is the EXECUTABILITY lens's question, and the two are deliberately kept apart.
- **It cannot prove inertness in general, only on the input given**, which is why the verdict says
  `ON THIS INPUT` and names the fixture. A flag inert on one fixture may bind on another.
- **Choose an input where the difference is observable.** `min_n` 10 vs 30 agrees for both n<10 and
  n>=30; only n between the floors measures anything. **A two-value probe on an input where both
  values must agree is a green result that means nothing** - the same shape as a differential test
  with n=0 on both sides (L393, S6-B1522a).

**Every finding gets an EXECUTION_QUEUE ticket the same turn.** A finding mentioned in prose and
not ticketed does not exist (#94). Causes go in only when TESTED - otherwise `UNKNOWN - RCA NEEDED`
(#189).

### 6. POST-FIX RE-CHECK - if this config-run cycle FIXED anything (CHECKLIST #196)

**A fix can invalidate a conclusion the defect itself left intact.** While the bug stood the
numbers were self-consistent; correcting it breaks that consistency for anything already shipped.

For every defect fixed during this cycle:
1. **GREP for the shipped conclusions that depended on the old behaviour** - grids, rosters, docs.
   Do not recall them.
2. **MEASURE the overlap.** Do not assume a fix is purely additive.
3. **Ticket each affected conclusion for re-derivation**, or state explicitly why it survives.

*Lineage:* the `regime_flip` fix landed on one of only TWO ROBUST Phase 1B roster cells, whose
numbers were `time_stop_20d`'s all along.

### 6b. CARRYING AN EQUIVALENCE CLASS IS FREE - FOR SUBSET-SAFE PARAMETERS ONLY

**MEASURED on the cfg2 cube (420 fires):**

```
FIXED   diagnosis of 420 fires, shared by ALL combinations : 3.5 s
MARGINAL per combination graded                            : 0.01 - 0.03 s
```

So carrying **21** combinations instead of 10 costs **~0.2 s**. The grading cost is dominated
by the FIXED diagnosis, which scales with FIRES (i.e. tickers), not with combinations. Step 2's
real cost is the **single ENGINE RUN** that produces its cube - hours - and that is completely
independent of how many candidates are carried, because every carried parameter is SUBSET-SAFE
and graded from the SAME cube.

**The calculus INVERTS for a FIRE-ADDING parameter.** `swing_length` (P1) and the EMA span (P6)
change which bars fire, so each distinct value needs its OWN engine run - hours each, not
milliseconds. **A fire-adding parameter must never be carried as an equivalence class**; its
values are the CONFIGS of the sweep, decided before launch and capped by budget. If one is ever
added to the graded grid, this section stops applying and the carry must be capped explicitly.

### 7. IMPLEMENT IN ENGINE - a winner the engine cannot apply is not a winner

```bash
python scripts/verify_engine_implemented.py
```

**The sweep grades SUBSET-SAFE parameters OFFLINE.** That is what makes 4,000 combinations
affordable, and it is also why the search space can contain gates **the engine cannot apply** -
the grader will happily simulate a filter that exists only inside itself.

**STATUS 2026-08-17 (B1617 re-verified): all 6 swept parameters REACH the engine.** When this
step was written, four did not - the history is kept because it is what the step exists to catch.

| | status | env knob |
|---|---|---|
| P1 `swing_length` | **IMPLEMENTED** | `SMC_SWING_LENGTH` |
| P2 `close_mitigation` | **IMPLEMENTED (B1616)** | `SMC_OB_CLOSE_MITIGATION` |
| P3 `tail_n` | **IMPLEMENTED (B1616)** | `SMC_OB_TAIL_N` |
| P4 `age_bars_max` | **IMPLEMENTED (B1616)** | `SMC_BREAKER_AGE_BARS_MAX` |
| P5 `break_pct_max` | **IMPLEMENTED (B1616)** | `SMC_BREAKER_BREAK_PCT_MAX` |
| P6 `ema span` | **IMPLEMENTED** | `STRAT_EMA_SPAN` |

*Until B1616 the last four existed ONLY in the offline grader. cfg2's graded winner - 68 fires at
Sharpe 2.239 - would have run live as 420 fires at Sharpe 0.789 with a different exit method,
because the engine applied neither cap. That is `regime_flip` (L461) moved from exits to entry
gates.*

**Because they are now real engine knobs, the remaining admission step is a REPRODUCTION CHECK
that was previously impossible:** re-run the config with the candidate's env knobs set, and confirm
the cube reproduces the graded fire set exactly. **Admission without it ships a backtest nobody has
executed.**

**BLAST RADIUS - set a knob and you move more than one strategy** (MEASURED B1617):
`SMC_OB_TAIL_N` and `SMC_OB_CLOSE_MITIGATION` reach **5** strategies (both breaker legs, both
mitigation-block legs, `strat_pre_rebalance_long`), `close_mitigation` also alters `ob_df` and so
`strat_smc_order_block_bounce`; the two breaker caps reach **2** (LONG and SHORT). Harmless while
the sweep runs ONE strategy under `--cube-isolation`; at Phase 1B, with the full roster in one run,
a knob tuned for the long leg would silently retune five other strategies. S6-B1617b.

### 8. Report the verdict WITH its denominators
Never a bare PASS count. State: N of M combinations, X of Y producers varied, `exits_effective`
of 26, and the `ci_lo` of every PASS. **Margin of error is part of the verdict, not a footnote.**

## FAILURE MODES — check these before believing a result

| symptom | cause | reference |
|---|---|---|
| all combinations `NO_EXIT_SELECTABLE` | too few IS trades to rank 26 exits | B1502 |
| a small universe PASSES all gates | entry-rate artifact, not edge | L382 (26.63x) |
| `ci_lo < 0` | edge indistinguishable from zero; no tightening fixes it | L373 |
| entry sets differ across runs | universe size or tier gating changed the population | L376, L418 |
| run completes, no cube | post-processing died; percentage lied | L410 |
| `MemoryError` in cube replay | cube too large; use the subset filter | B1552 |
| pyramid OOMs mid-run | an engine run holds RAM; commit BEFORE launching | L425 |
