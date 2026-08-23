# A1 family-pooled Step-1 design (B2079, S6-B2074a — DRAFT-THEN-APPROVE)

Owner-adopted 2026-08-23 (A1); this draft is the design deliverable. Nothing below runs
until the owner approves this document. Sources: B2068 measurement
(output_audit/b2068_family_pooled_noise_floor.json), the B2065 council verdict, the B2038
cost table (b2031 elaborations addendum), STRATEGY_OPTIMISATION_PLAN.md section 10.

## 1. What changes

Step-1 SEARCH stops buying per-strategy grids at n≈18–50 (measured replication floors
1.31–1.82 Sharpe at those sizes — b2068 artifact) and instead sweeps ONE producer axis per
family, grading each axis level on the family's POOLED trades (floor 0.088 at the 62,064-trade
EMA pool; best-of-5 selection lift +0.099). The ruled Step-1 shape is unchanged: 200 tickers
(output_audit/_sweep_200.txt), window 2024-05-05 → 2025-05-05, holdout untouched.

## 2. The first two waves (axes already plumbed)

| wave | axis | family size | levels (K) | engine runs | projected wall |
|---|---|---|---|---|---|
| W-A | EMA span via EMA_PAIRS + STRAT_EMA_SPAN (B2016/B1519) | 114 consumers | 5 (9/20/21/50/200 — the emitted set) | 5 | 5 × 3.64 h = 18.2 h; ×1.75 overrun factor → **plan 32 h** |
| W-B | SMC_SWING_LENGTH (B1616; +4 breaker knobs held at defaults) | 22 consumers | 5 (5/10/20/30/50 — the E1-proven band) | 5 | same basis → **plan 32 h** |

The 1.75× factor is the S6-B1680a measured wave-1 overrun (5 h 46 min vs 3.30 h projected),
carried per that ticket's closure — projections in this program have under-run once and it was
by 1.75×.

Grading: offline from each run's cube via the ONE selector (roster_core.select_exit, B2078) —
per axis level: family-pooled IS Sharpe + ci_lo, plus the per-strategy breakdown table so a
level that helps the pool by hurting a minority is visible. Ranking key: pooled IS ci_lo
(D4 lineage). STEP 1 PRODUCES A RANKING, NOT VERDICTS (plan section 10.1 stands).

## 3. The obligations this design carries by name (from S6-B2074a)

- **(a) The S6-B1503d within-strategy interaction question.** The B1619 variant machinery
  (suffixed breaker signals) rides every W-B run at zero extra engine cost; per-strategy
  interaction grades offline from the same cubes. The question is answered at Step-2 scale
  for whatever W-B carries forward — not dropped, not bought as a 127.4 h per-strategy grid.
- **(b) The 1.75× projection-overrun factor** — applied to every wall-clock cell above.
- **(c) The correlation-aware noise floor.** The b2068 floor is iid bootstrap — an idealized
  bound; family members share entry days, so effective N < 62,064. BEFORE any admission
  decision: recompute the floor with an entry-date BLOCK bootstrap (resample days, not
  trades) from the same cube, $0 offline. If the block floor at pooled N exceeds the
  candidate margins, the design returns here before Step 2 spends anything.
- **(d) A2 plumb sequencing** — by family size: volume (67) → pivots (58) → RSI (34) →
  MACD (22). One B1519-pattern config plumb each, its own batch with pins, byte-identical
  defaults. Each joins the wave queue as W-C…W-F when its plumb lands.
- **(e) Where A3 halving enters.** Not in W-A/W-B (K=5 — halving saves under 40% of runs and
  costs rank stability at 50t). It enters at CROSS-AXIS waves (axis × axis combinations,
  K≥15): rung 1 all combos at 50t×1y, halve on pooled ci_lo, rung 2 survivors at 100t,
  finish top quartile at the full 200t shape. The renegotiated rule permits this; each
  halving rung's cut list is reported with denominators before the next rung runs.
- **(f) The A4 Hetzner benchmark** — before any cloud parallelism enters a cost table:
  one CCX33 (EUR 0.2219/h post-hike, per the B2065 verdict's sourced table) runs one
  50t×1y config from the same SHA; PASS = byte-identical trade_exit_detail.csv vs the
  local run. Cost ≈ EUR 2. Requires owner-provisioned Hetzner access; local remains the
  default until PASS.

## 4. The breaker-leg conversion (decision point folded from LEVER3/B2077)

strat_smc_breaker_block_long/short still gate on the breaker POSITION-STATE. The
thesis-faithful EVENT is the zone RETEST (the B2076 tap pattern applied to the flipped
zone). **Recommended: convert BEFORE W-B's baseline** so the sweep measures the gate that
will be deployed; the alternative (sweep the STATE gate, convert after) buys measurements
of a gate already scheduled for replacement. Conversion ships as its own batch with pins
(the B2076 template), variant machinery untouched.
**Contrarian case against:** converting first breaks comparability with every prior breaker
measurement (E1 pilot, the b1576 pair), so the W-B baseline cannot be sanity-checked against
any historical number — if W-B's results look wrong, there will be no unconverted reference
to diff against. Mitigation if approved: one 50t×1y STATE-gate reference run (0.91 h) at the
W-B config before converting.

## 5. Launch discipline (unchanged, restated)

Every wave run: launch_sweep.py wrapper (S6-B1704c, approved option c — built before W-A
launches) carrying prelaunch_gate + manifest; #185 unconditional periodic monitors; solo or
N=2 concurrency per the measured RAM ceiling; verdicts require cube rows + fires (L566).

## 6. What the owner approves here

1. This design as Step-1's operating shape (W-A, W-B as specified).
2. The breaker conversion timing (section 4 — recommended pre-W-B, with the reference-run
   mitigation).
3. The four A2 plumbs proceeding as W-C…W-F feeders (each still ships owner-visible).
4. Nothing launches until (c)'s block-bootstrap floor is computed and reported — it is $0
   and next in the queue.
