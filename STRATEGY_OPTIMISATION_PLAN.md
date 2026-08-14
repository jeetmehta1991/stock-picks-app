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
into the choice of config, the 820 become real holdout tests and m must be 820. The separation is
therefore enforced mechanically, not by intention: the Phase-1 optimiser is given a file path
containing IS rows only and has no reference to the holdout file (Step 1).

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
| 7 | **Derive band values from the measured distribution.** Never percentile-by-reflex, never a round number. Anchor level 1 at the production value. | L356 (deciles on an integer count), L369 (P6 band silently narrowed 5 -> 2). |
| 8 | **State the economic event the signal captures, then check the threshold DIRECTION serves it.** | L359 - a breaker block is a RETEST, so the lever is an UPPER bound; my version selected harder for the noise. |
| 9 | **Terminate each band where holdout n < 25 or full-period n <= 100.** The gates set the last rung, not taste. | The strict end was untestable on every run - the sample, not the effect, is binding. |

### 9.3 BEFORE any run

| # | gate | why |
|---|---|---|
| 10 | **Write `run_manifest.json`, pass `prelaunch_gate.py`.** Pin frozen_sha, isolation, calendar, universe sha256, budget, and enumerate obsolescence risks each with a MECHANICAL gate. | B1335 Rule 1. It caught the P1/P6 blocker before ~14 h was spent. |
| 11 | **Derive the universe from the BASELINE ARTIFACT, not a roster CSV.** | L378 - R5 ran **381**; T1a has 503. Substituting the universe breaks comparability exactly as changing holdout dates would. |
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
| **1 SEARCH** | all fire-adding configs | **2 years** | **100** | ranked combinations |
| **2 VALIDATE** | top 10 | **4 years** | **281 disjoint + 100 append = 381** | gate verdicts |
| **3 ADMIT** | best 1 | 4 years | 381 | Phase 1B decision |

**Why 2 years in Phase 1?** Ranking needs only relative ordering. Grading needs the locked
IS(3y)+holdout(1y) split, which a 2-year window cannot provide. Search cheap, grade properly.

**Why 100 then 281?** The 281 are DISJOINT from the 100, so validation is genuine out-of-sample
across the ticker dimension — a combination selected by luck on 100 will not replicate. Appending
the two reconstructs 381 (valid because `--cube-isolation` bypasses the candidate cap, verified
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
381 tickers x 1003 days (4y)  ~= 27.7 h
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

### 1.1 Build the input files

```bash
# ONE strategy only. This is the difference between a 4.6 h run and a 20 min run.
echo "<STRATEGY>" > output_audit/_subset_<STRATEGY>.txt

# 100 tickers, ordered by R5 fire-count for THIS strategy so small runs carry signal
PYTHONPATH=. python - <<'PY'
import pandas as pd
S="<STRATEGY>"
c=pd.read_csv('output_r5_rung4_chunk1/trade_exit_detail.csv',low_memory=False,
              usecols=['strategy','ticker','entry_date'])
uni=sorted(c.ticker.unique())
g=c[c.strategy==S]
fires=g.groupby('ticker').apply(lambda d: d.groupby('entry_date').ngroups,
                                include_groups=False) if len(g) else {}
order=sorted(uni,key=lambda t:(-int(fires.get(t,0)),t))
open('output_audit/_sweep_100.txt','w').write('\n'.join(order[:100])+'\n')
print('wrote 100 tickers; top 5:',order[:5])
PY
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
  --tickers-file output_audit/_sweep_100.txt \
  --phase 1a-beta --cube-isolation \
  --no-agents --no-news --no-git --no-walk-forward \
  --screen-pool-workers 3 \
  --start 2024-05-05 --end 2026-05-05 \
  --max-run-hours 4.0 \
  --output-dir output_<STRATEGY>_cfg<N>
```

**Every flag matters:**

| flag / env | why |
|---|---|
| `STRATEGY_SUBSET_FILE` | **runs ONE strategy instead of 182.** Omitting it cost a 4.56 h run (L432) |
| `OPTIMIZATION_MODE=1` | uncaps `max_cands` |
| `SMC_SWING_LENGTH`, `STRAT_EMA_SPAN` | the FIRE-ADDING config; one run per combination of these |
| `--cube-isolation` | bypasses ALL cross-strategy gates AND tier sizing (B1545) |
| `--screen-pool-workers 3` | **default is 0 = SEQUENTIAL** (L407). Use ~3 per concurrent config |
| `--max-run-hours` | the runner REFUSES to start without it |
| `--start 2024-05-05` | 2-year SEARCH window; ranking only |

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

Re-run those configs on the **281 tickers NOT in the search set**, full 4-year window, then append
to the 100-ticker 4-year runs to reconstruct 381. Valid because `--cube-isolation` bypasses the
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

## REFERENCE — measured costs

| shape | measured |
|---|---|
| 182 strategies, 100 tickers, 2y | **4.56 h** (2.63 h day loop + 1.93 h post-processing) |
| 182 strategies, 20 tickers, 2y | 2,759 s |
| per ticker-day (pool=10) | 0.2613 s |
| post-processing share | **42pct of every run** |

**Single-strategy costs are being measured now (B1558).** Until that lands, do NOT project — five
projections were wrong this session (L367, L377, L383, L401, L418).

---

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
