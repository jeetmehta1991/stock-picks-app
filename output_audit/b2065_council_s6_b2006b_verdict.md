# Council verdict — S6-B2006b methodology decision (B2065, 2026-08-23)

Five advisors (Contrarian / First Principles / Expansionist / Outsider / Executor) spawned in
parallel per the llm-council protocol; anonymized peer review and chairman synthesis run inline.
Full advisor texts live in the session transcript; this file records the verdict the owner
sequenced ("once all these tickets are executed").

## Peer-review pass (anonymized before de-anonymizing)
- Strongest: the First-Principles response — converts the shared diagnosis into two levers
  (pool evidence across strategies; size the measurement to the question) and prices them.
- Biggest blind spot: the Expansionist's widen-the-funnel — more noise-floor-blind
  measurements multiply the multiple-testing bleed.
- Missed by ALL FIVE: the 0.333 noise floor is DESIGN-CONDITIONAL (measured for best-of-26
  selection at R5 shapes) — recompute it for the family-pooled shape before concluding
  anything; and the holdout-read budget is the scarcest resource in the program, absent from
  every advisor's accounting.

## Agreements (high confidence)
1. The INSTRUMENT, not the search algorithm, is the binding problem: best find +0.025 vs
   floor 0.333 (13x). All five, independently.
2. Bayesian optimisation: dead on arrival — no signal above noise to model (4/5).
3. Successive halving: likely violates the owner's no-fewer-configs rule (its mechanism IS
   config-reduction) and prunes on indistinguishable rankings (3/5).
4. Family-axis transfer is the one alternative with content — evidence POOLING, not search:
   EMA sweep serves 114 strategies, SMC 22 (both plumbed); volume 67 / pivots 58 / RSI 34 /
   MACD 22 await owner-approved plumbs (3/5).
5. Compute cost is trivial (EUR 1-18/unit post-hike); OWNER-APPROVAL BANDWIDTH, not cores,
   bounds throughput (4/5).

## Clashes
- More search vs no more search: resolves through measurement SHAPE — more configs at
  power-sized n is a different purchase than more configs at n=18.
- The premise itself: the Contrarian alone challenges "optimisation is the only path"; the
  pilot is consistent with effective breadth genuinely being ~3, in which case the lever is
  NEW STRATEGY CLASSES, not faster search. Surfaced for the owner, unresolved by the council.

## Recommendation (ranked — deliverable a)
1. FAMILY-AXIS TRANSFER as the spine: run the two plumbed family sweeps (EMA->114, SMC->22)
   at POWER-SIZED shapes, grade family-pooled; queue the four unplumbed-axis plumb approvals
   in parallel.
2. FACTORIAL kept — at family level and power-sized shapes (honest + subset-safe-cheap);
   stop purchasing per-strategy grids at n~18 shapes.
3. SUCCESSIVE HALVING only if the owner explicitly renegotiates the no-fewer-configs rule.
4. BAYESIAN rejected until any measurement clears the floor.

Runtime reduction (b): family amortisation (up to 114x/run), demand pruning (measured 47.9%
warm), concurrency by separate configs, cloud parallelism only after a reproduction benchmark.

Compute comparison, named prices (c) — searched 2026-08-23, post-June-2026 Hetzner hikes:
| option | price | per search config (200t x 1y) | note |
|---|---|---|---|
| local (10 cores, 15.6GB) | $0 | 3.64h, ~2 concurrent | default; RAM-capped (3,223MB/worker, plan:879) |
| Hetzner CCX33 8vCPU | EUR 0.2219/h | ~EUR 1.6 | post-hike |
| Hetzner CCX43 16vCPU | EUR 0.4423/h | ~EUR 1-2 | IF byte-identical reproduction benchmarks |
| Hetzner CCX63 | EUR 1.3678/h | similar total, more parallel | |
| AWS | quote-first | - | owner cap $50 CAD stands |
Sources: northflank.com/blog/hetzner-cloud-server-price-increases;
sparecores.com/server/hcloud/ccx33 and /ccx43; webhosting.today 2026-06-18.

## The one thing to do first (d)
Recompute the noise floor and required per-cell trade count for a FAMILY-POOLED EMA-axis
measurement — offline, $0, from existing cubes. It decides every subsequent run's shape and
whether any compute is worth buying.

## Owner decisions this verdict routes (none taken by the council)
- Adopt family-pooled design shapes (changes what Step 1 measures) — approval needed.
- The four axis plumbs (volume/pivots/RSI/MACD) — one approval each, B1519 pattern.
- Whether to renegotiate the no-fewer-configs rule to admit halving.
- The EUR ~2 Hetzner reproduction benchmark.
- The Contrarian's premise challenge: if pooled-power measurement still finds nothing, the
  program's own kill criterion (Phase 1 zero conversions) points at new strategy classes.
