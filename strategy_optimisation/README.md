# strategy_optimisation/ - the Table A band charter

**Owner-directed 2026-09-16 (B2836).** This directory holds, per strategy, the
band inventory the optimisation workflows consume: **Table A (depth)** - the
strategy's own persisted gate magnitudes - and **Table A (breadth)** - every
relevant companion producer persisted on that strategy's own fires. Every
level is marked **OFFLINE** (a subset of recorded fires - zero engine hours)
or **RESIM** (an engine leg). The workflow that consumes these tables is
STRATEGY_OPTIMISATION_PLAN.md SS11.2t (W-T) / SS11.2l (W-L); this directory is
the T2/L2 "Table A rendered" artifact, pre-built.

**Shape (B2838, owner-caught conformance):** each file leads with the plan's
CANONICAL Table A - the SS6/#183 parameter inventory, one row per parameter
across BOTH layers (producer booleans WITH THEIR DEFINED BANDS in P<n>.x
rows - B2845, owner-corrected: a ready and FINAL Table A per strategy, no
pending placeholders - strategy numeric thresholds, helper gates, B-rows),
preceded by the Formula (Section 1) and followed by the MEASURED input
sections. The engine-spec (SPECS) entry in `producer_variant_table.py` is
built FROM these bands before any engine leg; `validate_spec` then owns
the formula <-> Table A cross-check.

**Generated, never hand-edited.** Regenerate with:

    python scripts/build_table_a.py --lane TIGHTEN                      # tighten/ (12 files)
    python scripts/build_table_a.py --lane BOTH --subdir tighten/both   # tighten/both/ (29 files, owner-directed placement)

Each file carries an L803/#309 build stamp (generator + cube + status build +
commit + timestamp). A file whose stamp is stale against HEAD is regenerated
before any campaign reads it (the SS11.2w freshness precondition).

## Division of labour (owner-ruled)

| Wave | Tables by | Execution by | Scope |
|---|---|---|---|
| 1 - `tighten/` (12 strategies) | Fable | **Fable, end to end** | offline legs FIRST; producer-band resim legs IN-MANDATE after them |
| 2 - `both/` (29 strategies) | Fable | **Opus** (per W-T/W-L, mechanical) | offline first, engine after |

**OFFLINE DESCRIBES A LEG'S COST, NEVER A STRATEGY'S SCOPE (owner-corrected
2026-09-16, B2843).** An earlier revision called wave 1 "entirely offline" -
that narrows the mandate, the exact class B2702/L785 forbids: the depth leg
covers ALL Table A producer bands, resim included, and an untested axis is
resim-scheduled or owner-waived in words, never silently dropped. Wave 1 runs
the free legs first because they cost nothing; the P1-band SIMULATIONS then
run as in-mandate engine legs, gated on three things: the T3 band words, the
actuator plumbing for DEFINED-NO-ACTUATOR knobs, and the engine approvals
(11.2c words; B2107 caps; venue ruling S6-B2107a precedes Step-1 launches).
A shared producer's resim runs the FULL OPEN consumer set and its one cube is
graded offline per consumer (11.2s) - simulation results are reused by
construction, and admitted strategies stay banked (B2731).

## What OFFLINE and RESIM mean here

- **DEPTH, tighter side = OFFLINE** by construction: a tighter level of a
  persisted gate magnitude selects a subset of the cube's recorded fires.
  These are the `free_band` levels (validate_spec's free side).
- **DEPTH, looser side = RESIM** by construction: a looser level admits bars
  the cube never recorded. Band from the SPECS entry (`producer_variant_table`),
  built at W-T T0/R1 where missing. Documented in every table, **not run** in
  the wave-1 offline campaigns without the owner's engine words (11.2c).
- **BREADTH = OFFLINE** where the companion key is persisted at coverage
  >= 0.98 on the strategy's fires (an AND-leg is subset selection); **every
  breadth row is a NEW-GATE** (standing owner rule 2026-08-10) - the T3 owner
  band review words the band before any grid runs.
- **BREADTH below the coverage floor, price-denominated keys (as ratios), and
  any producer with NO persisted key = RESIM / engine-side design work.**
  What `signals_at_entry` does not hold, no offline instrument can see
  (plan 11.2s: persistence exists only on taken trades).

## OFFLINE-ONLY STEP 2 (owner ruling 2026-09-16, verbatim intent)

For offline-only campaigns (the 12 tighten-lane strategies): **Step 2 runs
offline over the full cube - 544 tickers, the entire 4y window - with NO
pruning of combinations.** Step-1 pruning exists to cap ENGINE runtime in
Step 2; offline reads are free, so the full combination population is read.

**Statistical price of no-pruning, stated (the owner asked for counters):**

1. **The holdout is touched by every combination, not a pre-registered few.**
   Reading N combinations on the holdout and preferring the best is holdout
   mining unless the multiplicity machinery prices the FULL N. Therefore:
   the trials count for the multiplicity block (11.2b2d - permutation null,
   BH-FDR across the read population) is the FULL number of combinations
   read, never a post-hoc subset; PSR cannot substitute (it is
   single-candidate, blind to trials - B2376).
2. **One shot.** The read is still ONE pre-registered event on the owner's
   explicit Step-2 word (11.2c, breadth_step2_read.py is fail-closed on
   --ruling). After it, the holdout is SPENT for these objects (B2136);
   re-reads only on explicit owner override.
3. **Selection for admission is stated before the read** (which cells are
   candidates and on what IS evidence), so the full-population read is a
   verdict table, not a search. The no-pruning ruling changes what is
   READ, not what is pre-registered.

## Risks of offline-only runs (flagged, owner-requested)

- **Persistence bounds the grade (lower bound):** a gate leg reading an
  unpersisted key defaults False in replay - offline fire counts can
  undercount the engine's truth (conservative direction, but retention
  ratios can skew where persistence is selective).
- **Subset-only visibility:** offline sees recorded fire bars only. Exact
  for tightening (a subset is a subset; the cube's per-(entry, exit) rows
  cover all 24 exits), but nothing offline can say about behaviour at bars
  the base config never fired on.
- **Shared trades across combinations:** grid cells overlap heavily, so
  naive significance overstates - the permutation/cluster nulls are
  mandatory, not decorative.
- **Sample-size gates still bind:** min_trades_holdout 15 and
  min_trades_full_period 75 (4y) fail thin tightened cells by design.
- **Stale-cube exposure:** the cube is R5-era. Changed strategies are graded
  on their SURVIVING subset only (T1) - honest, but n shrinks (measured
  here: pairs_mean_reversion_short 5,698 -> 4,461; cmf_flip 2,994 -> 2,250).
- **Derived-field contamination class (L766/B2615):** offline re-scorers
  must reproduce the landed baseline before any level they report is
  believed; fields they cannot derive fail closed, never proxy.

## Mechanical enforcement map (verified by grep/read, 2026-09-16)

| Stage | Mechanism | Status |
|---|---|---|
| Engine config lands | `run_phase1a.py::_postconfig_landing_hook` (line 181, invoked line 713) -> B2520 battery, all nine steps; Stop-hook LANDING REPORT gate | WIRED (grep this batch) |
| Offline Step-1 grid | grader-internal fail-closed refusals (reproduction / coverage / join / truncation) + multiplicity block (`offline_level_sweep.py`, `breadth_step1_grid.py`) with `multiplicity.reconciles` required by the T4 gate | WIRED (in-process) |
| Step-2 read | `breadth_step2_read.py` REFUSES without `--ruling` (the 11.2c word recorded verbatim) | WIRED |
| Step-2 vs Step-1 multiplicity | `breadth_step2_read.require_multiplicity()` REFUSES an absent or non-reconciled Step-1 multiplicity block, before any frame is built (pin test_b2839) | WIRED (B2839 closed S6-B2836a) |

## Roster - wave 1 (12 TIGHTEN, from the stamped status view)

pairs_mean_reversion_long, pairs_mean_reversion_short, stochrsi_overbought_short,
williams_r_oversold, stochrsi_oversold, cmf_flip, naked_poc_retest_long,
cpr_narrow_momentum_short, three_black_crows_short, bollinger_lower,
three_white_soldiers, hull_rsi

(Membership is derived from the L803-stamped status view at generation time -
the per-file stamps say which build; counts live in the stamped view, never here.)
