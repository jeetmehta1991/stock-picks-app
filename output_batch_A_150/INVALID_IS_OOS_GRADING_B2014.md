# IS/OOS GRADINGS FROM THIS CUBE ARE INVALID (B2014 / D7, owner-approved 2026-08-22)

This cube's window spans 2025-02-06, the date `signals_at_entry` began
persisting. Before it, `next_pivot_target` silently fell back on 100 percent
of trades for eleven quarters; after it, on 20-40 percent (L526, measured at
B1771). The exit therefore has a DIFFERENT IDENTITY on each side of the
boundary, and any in-sample-vs-holdout comparison graded through it inside
this cube compares two different exits wearing one name.

- The TRADE DATA remains valid; single-side analyses remain valid.
- Any IS/OOS RANKING or grading built on this cube across 2025-02-06 is
  superseded and must be re-derived on an R5-era cube.
- Basis: L526; the B1770 decomposition and its B1991 validation (within-exit
  rho -0.740 concentrated in next_pivot_target, n=68 combinations).
