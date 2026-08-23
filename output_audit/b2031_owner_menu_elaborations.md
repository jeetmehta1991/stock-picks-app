# B2031 — Elaborations 4 and 5 (owner rulings 2026-08-23: "elaborate")

## Item 4 — "archive = move": what it means and what would move

**The ambiguity.** The 2026-08-22 H ruling reads: *"output_r5_merged_1_7 CONFIRMED the final
R5 dir, archive = move."* Two readings:

- **(i) Method ruling** — whenever archiving happens, MOVE directories (don't copy-then-keep).
  Nothing is ordered now. H is then fully complete.
- **(ii) Ordered action** — archive the superseded run dirs now, by moving them under
  `archive/`. Then a named list is required, because moving data dirs on an unstated list
  violates do-not-assume.

**The population, measured (76 `output_*` dirs at repo root; sizes MEASURED via du this
batch):** the movable mass is dominated by the superseded R5 chunk dirs - chunk17 5.0 GB,
chunk18 3.6, chunk14 2.9, chunk16 2.4, chunk13 1.5, chunk12 0.6, chunk11 0.3 (~16.3 GB for
the lineage), plus sweep_pilot 1.9 GB, r6b_cube_14 1.0 GB, the batch395 family ~2.8 GB,
optmode pair ~0.9 GB, pool_test 0.5 GB. Reading (ii) frees roughly 25 GB from repo root.
(KEEP set for reference: output_r5_merged_1_7 is 7.4 GB, output_audit 0.9 GB.)

| category | count | dirs | proposed disposition under reading (ii) |
|---|---|---|---|
| KEEP — live / baseline / referenced | 13 | `output_r5_merged_1_7` (the confirmed R5 baseline), `output_b2016_e1*` ×6 (active E1 sequence incl. the running span arm), `output_audit` (artifact store, not a run), `output_cfg1`, `output_cfg2`, `output_w1_sw20_span21`, `output_w1_sw20_span50` (the four sweep cubes still cited by live grids/ledger), `output_batch_A_150` (cited by the D6 ruling) | stay |
| Self-labeled DISCARD | 14 | `output_b1845_*_DISCARD` ×6, `output_b1856_firecheck_200t_DISCARD`, `output_b1874_*_DISCARD` ×3, `output_b1875_*_DISCARD` ×2, `output_b1876_*_DISCARD` ×2 | move first — they were named discardable at creation |
| Superseded R5 lineage | 15 | `output_chunk11-14,16-18` ×7, `output_merge_*` ×7 (A/B/dryrun/dryrun2/test/test2/test3/test4 — 8 actually), `output_batch394_parity_seq` | move — merged into `output_r5_merged_1_7` |
| R4/Batch-395 era | 7 | `output_batch395_batch_1-5`, `output_batch395_final`, `output_batches` | move — pre-R5 historical |
| R6 era | 7 | `output_r6_local_150`, `output_r6_probe`, `output_r6_probe25`, `output_r6b_cube_14`, `output_r6c_group1_3`, `output_optimization_candidates_r6_is_only`, `output_optimization_candidates_R4_2026_06_16` | move — R6 concluded |
| Probes / scratch | 20 | `output_smoke_test`, `output_smoke_cloud`, `output_pool_test`, `output_parity_tmp`, `output_profile_lever_c`, `output_coverage_smoke_local`, `output_ladder_5/10`, `output_scale_t50/t5rep`, `output_optmode_on/off`, `output_pin_sw20/50`, `output_pin2_sw20/50`, `output_sweep_pilot`, `output_b1506_engine_timing`, `output_optimization_candidates_2026_07_25` | move — one-shot probes with ledger records |

**Recommendation:** reading (i) is the more natural parse of the ruling's grammar, and nothing
breaks if nothing moves. If you intend (ii), approve the table's move set (or edit it) and I'll
execute it as its own batch with a manifest of moves (post-config ledger paths updated where
they reference moved dirs — `verify_postconfig_complete.py` globs `output_*`, so moving dirs
OUT of root also shrinks its scan surface, a small win). **Against my own recommendation:** if
disk pressure or root-dir clutter is the actual motivation, (ii) is worth doing regardless of
the original intent — say "execute the table" and it happens.

## Item 5 — the BLOCKED design menu, elaborated with recommendations

Grouped; each row: what it is → cost → my recommendation with the tradeoff. Approving a group
approves its members unless you strike some. Every item is a strategy/exit/gate change, so
nothing ships without your word.

### Group A — exit design (cube evidence exists)

1. **BREAKEVEN-1R-BUFFER (P2).** `break_even_at_1r` moves the stop to breakeven at exactly
   1R; measured 8.4% median win rate because the stop sits at the max-touch level. Proposal:
   +0.2–0.3R buffer. Cost: config change + cube re-grade (offline). **Recommend: approve at
   +0.25R** — the exit is near-unusable as-is; tradeoff: slightly later protection.
2. **LEVER9-EXIT-SUITE (P1).** Three new exits (Connors sma5-cross, opposite-band, k*ATR
   target+time pair), two re-tunes, and the 6 dead-trail deprecation decision. Cost: exit
   roster changes + a cube iteration to grade them. **Recommend: defer the NEW exits until the
   current 26-exit family's collapse problem is fixed** (3 pairs byte-identical, effective ~23;
   adding exits to a family that can't distinguish its members adds noise) — but approve the
   deprecation DECISION now: 6 dead trails that never win any cell are pure grading overhead.
3. **LEVER10-MAE-FITTED-STOPS (P3).** Per-strategy initial stops from
   `per_strategy_mae_75th_pct_of_winners()`. **Recommend: hold until Phase 1B** — it's a
   portfolio-level risk design, and the isolation cube can't evaluate it fairly.
4. **ENG9-FILL-DATE (P2, OPEN but yours).** Add a `fill_date` field so time-stops stop being
   1-day biased (entry_date = signal date vs next-bar fill). Writer-reader schema addition
   with its own contract pin. **Recommend: approve** — cheap, additive, removes a known bias
   from every future cube; tradeoff: a schema migration touch on the trade log.

### Group B — entry gates (ask-every-time class)

5. **HNS-NECKLINE-GATE (P2).** `head_and_shoulders_top_short` fires on pattern-DETECTED
   without a neckline-BREAK. Pattern-detected ≠ pattern-completed (Edwards & Magee).
   **Recommend: approve the gate** — it's the canonical definition of the pattern completing;
   tradeoff: fewer fires on an already-thin strategy.
6. **LEVER6-RETEST-INTEGRITY (P2).** Level-held qualifier (close back above/below + 1–2 bar
   persistence) for 8 retest strategies. **Recommend: approve for the 2 retest strategies with
   the worst cube PF first, not all 8** — per-strategy walks beat a blanket gate (blast-radius
   discipline); expand on evidence.
7. **LEVER4-GATE-BUDGET (P2).** k-of-m scoring for the top-25 gate-stacked strategies.
   **Recommend: defer** — it's a redesign of the strategy formalism itself; the optimisation
   program's tightening/loosening machinery should finish first, since k-of-m would invalidate
   the SPECS model mid-program.

### Group C — STATE→EVENT conversions and pair symmetry

8. **LEVER3-STATE-EVENT-SWEEP (P1).** Six volume-bleeders still gate on latching STATE
   signals (incl. `smc_breaker_block_long/short`). **Recommend: approve for the four NON-E1
   strategies now; hold the two breaker legs until the E1 sequence closes** — converting the
   swept strategy mid-sweep forks the config.
9. **SUPERTREND-SHORT-STATE-EVENT (P1, OPEN but yours).** The short still gates on
   `supertrend_bearish`, measured 99.19% True (near-no-op), while the long was
   EVENT-converted at B655 — and the long's docstring already *claims* the short mirrors it
   (S6-B2024a). **Recommend: approve the swap to `supertrend_flip_recent_short_5d`** — it
   completes an owner-approved conversion the pair half-received; tradeoff: the short's fire
   count drops to event-anchored levels.
10. **ICHI-BREAKDOWN-ASYMMETRY (P3).** Long and short built from different STATE/EVENT
    mixes. **Recommend: fold into the same ruling as #9** (one pair-symmetry decision), lowest
    priority.
11. **STALE-NAME-SWEEP (P2).** Four strategy names describe pre-loosening gates
    (`macd_ichimoku` etc.). Rename (touches CSVs/tests/roster) vs docstring-annotate.
    **Recommend: docstring-annotate** — renames churn every downstream artifact for zero
    behavioral gain; tradeoff: names stay historically misleading, mitigated by the annotation.

### Group D — new strategies and structural decisions

12. **NEW-STRATEGIES-M1-M15 (P1).** Fifteen candidates; tranche A (six trivial-producer,
    cached-data: RS-line-vs-sector, earnings-anchored AVWAP, pocket-pivot, gap-and-go,
    failed-breakout-2B, consecutive-down-days) is cheap to wire. **Recommend: approve tranche
    A only, wired EXPLORATORY** per the Class 7 protocol; hold tranches B/C (parser/producer
    builds) until the optimisation program answers whether the existing library's edges are
    recoverable — 15 new strategies before that answer risks widening a book we can't yet grade.
13. **F23-F24-DECISIONS (P2).** F23: consolidate the 10 classification-change strategies to 1.
    F24: pairs hedge-leg — implement dollar-neutral or re-scope EXPLORATORY. **Recommend: F23
    consolidate (the 10 are near-duplicates by construction); F24 re-scope EXPLORATORY** —
    dollar-neutral execution is Stage-3+ machinery we shouldn't build inside Stage 2.
14. **OR-ARM-ATTRIBUTION (P3).** Analysis of which OR-arm fires; input is the Batch B trade
    log, and Batch B launch remains owner-gated. **Recommend: leave BLOCKED** — it resolves
    itself if/when Batch B runs.

**One decision cuts across all of this:** every approval above lands in the optimisation
program's TIGHTENING/LOOSENING partitions and gets graded by the same cube machinery — so
approvals are cheap to absorb incrementally, and the highest-leverage rulings are #1, #5, #9,
and #12-tranche-A.

## Addendum (B2038) — the universe ladder as a COST table, measured rates

Per-config engine cost at the canonical 0.2613 s/ticker-day (B2021 re-confirmed 0.257–0.282
end-to-end at a different concurrency shape):

| shape | ticker-years | per-config hours |
|---|---|---|
| SP50 × 1y (E1 shape) | 50 | 0.91 |
| sweep-100 × 1y | 100 | 1.82 |
| sweep-200 × 1y (ruled Step-1 shape) | 200 | 3.64 |
| 100 × 2y (old Step-1) | 200 | 3.64 |
| **344 disjoint × 2y (STEP-2 VALIDATE)** | **688** | **12.53** |
| 544 × 2y | 1088 | 19.82 |
| 544 × 4y (full R5 shape) | 2176 | 39.64 |

Two consequences: (1) the ruled 200t×1y Step-1 shape and the old 100t×2y are the SAME
ticker-years — the S6-B1831b neutrality, now visible in the arithmetic (nonlinearity term
still owed one empirical config); (2) **STEP-2 for the complete E1 candidate set is ONE
engine run** — every carried combination is subset-safe and grades offline from the single
344×2y cube — so the decision is 12.5 h local at $0, or an AWS quote under the E4 ruling.
