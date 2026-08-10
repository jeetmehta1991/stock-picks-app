<!-- B1497 (2026-08-09). Owner-requested optimisation plan for the 207-strategy population.
     STATUS: PROPOSAL. Nothing here is implemented. Owner approval required per phase. -->

# Strategy Optimisation Plan — Phase 1 (tightening) and Phase 2 (loosening)

**Population:** 207 strategies (`222 registered - 3 Phase-1B roster - 12 disabled`).
**Current roster:** 2 cells / 3 strategies, ROBUST 2 / PROVISIONAL 0.
**Purpose of this programme:** the roster is 2 cells. Optimisation is not an enhancement; it is the
only remaining path to a deployable Phase 1B.

---

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
6. **The R6b prior is the base rate.** The last IS-fitted change set graded **4 held / 9 failed,
   binomial p=0.954**. Any Phase-1 result must beat that, and the design below exists specifically
   to beat it.

---

## 2. PHASE 1 — TIGHTENING (offline, zero engine runs)

### 2.1 Why tightening is cheap and loosening is not
`trade_log.csv` carries a `signals_at_entry` column: the **complete producer signal dict at the
entry bar**, ~22 KB per trade (verified B1497: `{"pivot": 158.6, "cpr_narrow": true, "cam_r4":
161.79, ...}`). Therefore:

- **TIGHTENING is exact and free.** A tighter threshold selects a strict SUBSET of trades that
  already exist, with known outcomes. Recomputing any subset's statistics needs no engine.
- **LOOSENING is impossible offline.** A looser threshold admits trades that were never generated.
  No amount of replay conjures them.

### 2.2 Population — 41 strategies (n > 300)

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
- **Cap:** <= 20 configs per strategy. 41 x 20 = **820 tests**, the declared FDR family.
- Committed to the queue BEFORE any scoring.

**Step 3 — SCORE ON IS FOLDS SEPARATELY.** For each config: surviving subset -> re-run exit
selection on that subset (the best exit can change when the trade population changes) -> compute
the 6 live gates on **F1, F2 and F3 independently**.

**Step 4 — STABILITY FILTER (the anti-R6b mechanism).** Keep a config ONLY if it clears the gates
in **all three folds**, not in the pooled IS. R6b's failure was that pooled-IS winners were
fold-specific noise. A config that works in 2022-23, 2023-24 AND 2024-25 is a materially different
claim from one that works on average. **Expect this to eliminate most candidates. That is the
point.**

**Step 5 — ONE CONFIG PER STRATEGY.** Among fold-stable survivors, select by argmax gates-cleared,
tie-break IS Sharpe (the owner's B1451 objective). One winner per strategy, so the holdout family
is at most 41 -- not 820.

**Step 6 — GRADE ONCE.** The <= 41 chosen configs are graded on the holdout in a single pass, with
BH-FDR across that family plus the 2 incumbents. **This is the only holdout read in Phase 1.**

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

## 5. OWNER DECISIONS REQUIRED BEFORE ANY WORK

1. ~~Holdout strategy A/B/C~~ — **SETTLED 2026-08-09.** Window LOCKED to R5 dates for
   comparability; Option C (read it once, optimise inside the IS folds) is the operative design.
2. **Mid-band (58 strategies at 100 < n <= 300): in Phase 1 or deferred?**
3. **Do the 3 AUTO-FAIL screens get implemented against the IS/full-period series (S6-B1495a)
   before Phase 1 grades?** They currently return `None` on a 1-year holdout.
4. **FDR family size:** 41 (one config per strategy) or 820 (every config tested)? The conservative
   reading is 820; the pre-registration + one-winner-per-strategy design is what makes 41 defensible.
