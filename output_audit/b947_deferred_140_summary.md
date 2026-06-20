# Batch 947 (2026-06-20): 140 Deferred Strategy Classification
# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.8 + Council 51 UNANIMOUS hybrid epsilon verdict per CHECKLIST #77.

## Summary

Total deferred strategies: 140

## Bucket Distribution (priority-ordered V > IV > III > II > I)

| Bucket | Count | % | Next-step hint |
|---|---|---|---|
| V_walk_doc_mentioned | 140 | 100.0% | walk_doc_extractor_gap |
| IV_below_threshold_fire | 0 | 0.0% | - |
| III_lineage_tags_only | 0 | 0.0% | - |
| II_batch_markers_only | 0 | 0.0% | - |
| I_truly_deferred | 0 | 0.0% | - |

## Top-10 Examples per Bucket

### V_walk_doc_mentioned

- `52wh_break_retest` (first_commit=None): walk_docs=['STAGE_4_BREAKOUT_CLUSTER_WALKS.md'] | batches=['B162', 'B291', 'B589']
- `52wl_break_retest_short` (first_commit=None): walk_docs=['STAGE_4_BREAKOUT_CLUSTER_WALKS.md'] | batches=['B291', 'B605']
- `52w_high_breakout_pullback_long` (first_commit=None): walk_docs=['STAGE_4_BREAKOUT_CLUSTER_WALKS.md'] | batches=['B586']
- `52w_high_breakout_with_smart_money_long` (first_commit=None): walk_docs=['STAGE_4_BREAKOUT_CLUSTER_WALKS.md', 'STAGE_4_SMART_MONEY_CLUSTER_WALKS.md'] | batches=['B588', 'B589', 'B613']
- `52w_high_breakout_with_smart_money_vol_below_long` (first_commit=None): walk_docs=['STAGE_4_BREAKOUT_CLUSTER_WALKS.md', 'STAGE_4_SMART_MONEY_CLUSTER_WALKS.md'] | batches=['B613']
- `52w_low_breakdown` (first_commit=None): walk_docs=['STAGE_4_BREAKOUT_CLUSTER_WALKS.md'] | batches=['B582', 'B586', 'B587']
- `52w_low_breakdown_pullback_short` (first_commit=None): walk_docs=['STAGE_4_BREAKOUT_CLUSTER_WALKS.md'] | batches=['B586']
- `adx_initiation` (first_commit=2026-04-17): walk_docs=['STAGE_4_TREND_CLUSTER_WALKS.md']
- `avwap_20high_rejection_short` (first_commit=None): walk_docs=['STAGE_4_CLUSTER_WALKS_INDEX.md', 'STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS.md'] | batches=['B208']
- `avwap_252_breakout` (first_commit=None): walk_docs=['STAGE_4_CLUSTER_WALKS_INDEX.md', 'STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS.md'] | batches=['B208']

## Recommendation (Council 51 mandate: recommend-only; no auto-mutation)

### HONEST FINDING: Walk-doc cross-reference too permissive

140 of 140 (100.0%) strategies match Bucket V (walk_doc_mentioned). The walk-doc index includes ALL 219 strategies (every strategy is mentioned somewhere in a STAGE_4_*.md doc). This makes Bucket V's matching criterion trivially universal -- the bucket doesn't discriminate.

**Analogous failure mode to B945:** B945 had a parser gap (regex too narrow); B947 has a cross-reference gap (mention != walk verdict). Per Council 50 honest-finding pattern, surfacing this without iterating tighter parser mid-batch.

**Council 52 RECOMMENDED ACTIONS:**
- (i) Tighten walk-doc parser: require strategy mention within K-line proximity of 'walked', 'verdict', 'W##:', or 'S4-B###' keywords (NOT just any text mention)
- (ii) Build STAGE_4 walk-verdict ledger from B883 lineage (specific strategy -> walk verdict mapping; treat ledger as ground truth)
- (iii) Accept 140 deferred as-is; defer walk-doc parser improvement to separate B948 batch

Per Council 51 Outsider strict mandate: B947 ships honest finding; B948 (or Council 52) decides next step. No mid-batch iteration.


## B931 Appendix Flag

`institutional_persistent_holders_long` is in B906 MEASUREMENT_DISPUTED set + B931 MAY-REVERT tag pending B906 owner decision. Classification reflects current dossier state; no re-tag in this batch per Council 51 HARD RULE.

## B947 Compliance Statement

| Council 51 mandate | Status |
|---|---|
| ONE commit (B947) | OK |
| Read-only classifier (no dossier mutation) | OK |
| Priority-ordered disjoint buckets V > IV > III > II > I | OK |
| Recommend-only (no auto-mutation) | OK |
| B931 appendix-flagged | OK |
| B948 walk-doc extractor + B949 owner triage = separate downstream | OK |
