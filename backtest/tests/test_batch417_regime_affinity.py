"""Batch 417 (2026-05-28 owner-approved): test-pin the 14 NEW
STRATEGY_REGIME_AFFINITY entries derived from the post-AWS Phase 1A-beta
cube run.

Source attribution (per CHECKLIST #77):
  Cube data: output_batch395_final/trade_exit_detail.csv x trade_log.csv
  Computation: per-(strategy x regime) Sharpe + n>=30 filter from the
  ad-hoc analysis in 2026-05-28 conversation log; regimes INCLUDED iff
  sharpe > 0 AND n >= 30.
  Owner approved "14 NEW only" scope: do NOT override the existing 113
  curated entries (from Batches 203/293/370 + literature) even where
  cube empirical disagrees. The 15 OVERRIDE candidates are deferred to
  per-strategy approval in a later batch.

These entries pin the cube-derived regime affinity for 14 strategies that
had NO prior entry. Test fails if any entry drifts (e.g., someone
silently reverts) or if the count drops below the expected floor.
"""
from __future__ import annotations

import pytest

from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY


# Batch 417 cube-empirical affinity (regime set per strategy)
#
# B617 update (2026-06-07 external-AI critique on B608/B609/B610 walks):
# 4 of the 14 B417 entries were REMOVED by the family audit because the
# strategies are dual (_strat3) and the explicit single-bucket regime entry
# was mis-regimed for one of the two directions:
#   - break_retest_confluence (B609 F1 removal)
#   - break_retest_volume (B608 F1 removal)
#   - cpr_narrow_momentum (B617 family audit)
#   - hull_rsi (B617 family audit)
# These now get the Batch 291 direction-aware default (LONG -> {bull,
# neutral}; SHORT -> {bear, crisis, neutral}). The cube data was
# direction-agnostic, so a single-bucket entry applied to a dual
# constrained both directions identically - the Batch 271 family-bug
# signature. Direction-disaggregated cube validation pending.
BATCH_417_NEW_ENTRIES_ACTIVE = {
    "awesome_oscillator":              {"bear"},
    "institutional_buy_momentum_long": {"bull"},
    "institutional_cluster_long":      {"bear"},
    "macd_fast_crossover":             {"bull"},
    # B639 (Stage 4 morning_star walk option a 2026-06-09): F3 family-
    # bug fix removed morning_star regime affinity entry. B822 removes
    # from B417 ACTIVE list.
    "parabolic_sar_flip":              {"bear"},
    "ppo_crossover":                   {"bear"},
    "tema_dema":                       {"bear"},
    "three_white_soldiers":            {"bear", "bull"},
    "williams_stoch_dual":             {"bear"},
}

BATCH_417_REMOVED_BY_FAMILY_AUDIT = {
    "break_retest_confluence",   # B609 F1
    "break_retest_volume",       # B608 F1
    "cpr_narrow_momentum",       # B617 family audit
    "hull_rsi",                  # B617 family audit
    "morning_star",              # B639 F3 family-bug fix
}


@pytest.mark.parametrize("strategy,expected_regimes",
                          sorted(BATCH_417_NEW_ENTRIES_ACTIVE.items()))
def test_batch417_strategy_regime_affinity_entry(strategy, expected_regimes):
    """Each Batch 417 NEW entry STILL ACTIVE post-B617 must be present +
    match cube-derived set."""
    assert strategy in STRATEGY_REGIME_AFFINITY, (
        f"{strategy} missing from STRATEGY_REGIME_AFFINITY - Batch 417 "
        f"not applied or silently reverted")
    actual = STRATEGY_REGIME_AFFINITY[strategy]
    assert actual == expected_regimes, (
        f"{strategy}: STRATEGY_REGIME_AFFINITY = {actual!r}, expected "
        f"{expected_regimes!r} (Batch 417 cube-empirical)")


@pytest.mark.parametrize("strategy", sorted(BATCH_417_REMOVED_BY_FAMILY_AUDIT))
def test_batch417_removed_by_family_audit(strategy):
    """B617 family audit: 4 of the 14 B417 entries removed because dual
    strategy with explicit single-bucket regime entry mis-regimed one of
    the two directions. Direction-disaggregated cube validation pending."""
    assert strategy not in STRATEGY_REGIME_AFFINITY, (
        f"{strategy} should be REMOVED from STRATEGY_REGIME_AFFINITY by "
        f"B617 family audit (was Batch 417 cube-derived but applied to a "
        f"dual _strat3 strategy direction-agnostically). Falls back to "
        f"Batch 291 direction-aware default.")


def test_batch417_strategy_regime_affinity_count_floor():
    """STRATEGY_REGIME_AFFINITY entries post-B617 + B639 family audits.

    Floor trajectory (each lowering documented with rationale):
      127 -> 105 (B617): removed 19 Class A entries (dual strategies
        with single-direction regime entries that mis-regimed the
        opposite direction); 3-entry margin for upcoming B639 work.
      105 -> 100 (B822/B825): B639 morning_star removal + later family-
        bug-fix batches dropped 4 more entries (current=101). Floor
        lowered to 100 with 1-entry margin. NEXT removal MUST be
        documented in this floor with explicit batch+reason BEFORE
        lowering further; silent lowering is the regression-guard
        failure mode this test exists to prevent.

    Per Council audit B825: this floor is a regression-guard. Lowering
    it without surfacing the cause defeats its purpose. Future lowering
    requires (a) which batch removed entries, (b) why, (c) explicit
    floor update in same batch."""
    # 101 -> 78 (B3139q-r79): S6-B1248-SHORT-REGIME-AFFINITY (owner ruled
    # 2026-10-20, recommendation (a) - no regime policy for shorts) removed
    # the 23 explicit pure-short entries that copied the blanket short
    # policy (Batch 203 / Batch 271); test_b1248_shorts_carry_no_regime_policy
    # names them. Floor = the new count, no margin.
    # 78 -> 72 (B3139q-r171): S6-B3405 (owner Lane-1 approval 2026-11-01)
    # removed the 6 ORPHAN keys whose strategies were deleted
    # (buyback_8k_recent_long B682, camarilla_rsi_obv_short B874,
    # dxy_headwind_multinational_short B1189, hull_rsi_short +
    # po3_htf_aligned_long + po3_htf_aligned_short B722) - no registered
    # strategy could look them up; test_b3392c names each in REMOVED.
    assert len(STRATEGY_REGIME_AFFINITY) >= 72, (
        f"STRATEGY_REGIME_AFFINITY has {len(STRATEGY_REGIME_AFFINITY)} "
        f"entries, expected >= 72 (post-B617 -19 -> 105; post-B639 + "
        f"family audits -> 101; B3139q-r79 -23 policy copies -> 78; "
        f"B3139q-r171 -6 orphans -> 72)")


# Batch 418 (2026-05-28 owner-approved "proceed"): 15 OVERRIDES of existing
# curated entries where cube empirical disagrees. Supersedes the prior
# test_batch417 "override-not-applied" guards; those entries are now the
# cube-derived values pinned below.
BATCH_418_OVERRIDES = {
    "adx_initiation":               {"bear"},
    "avwap_252_breakout":           {"bear", "neutral"},
    "bollinger_tight":              {"bull"},
    "cmf_flip":                     {"bear", "neutral"},
    "pairs_mean_reversion_long":    {"bear"},
    "pead_long":                    {"bear", "bull"},
    "po3_bullish":                  {"bull"},
    "pre_fomc_long_sleeve":         {"bear", "neutral"},
    "prev_day_high_break":          {"bear"},
    "supertrend_macd":              {"bull"},
    "ultimate_oscillator":          {"bull"},
    "xs_low_beta_long":             {"bear", "bull"},
    "xs_momentum_top_decile":       {"bull"},
    "xs_quality_top_quintile_long": {"bear"},
}

# B3139q-r171 (S6-B3405, owner Lane-1 approval 2026-11-01): po3_htf_aligned_long
# was a Batch-418 override whose STRATEGY was deleted at B722 - the entry was an
# orphan no registered strategy could look up, removed with the other five
# (test_b3392c names each in REMOVED). Kept here so the 29-entry cube-derivation
# arithmetic stays whole.
BATCH_418_REMOVED_ORPHANS = {
    "po3_htf_aligned_long": "S6-B3405 (strategy deleted B722)",
}


@pytest.mark.parametrize("strategy,expected_regimes",
                          sorted(BATCH_418_OVERRIDES.items()))
def test_batch418_strategy_regime_affinity_override(strategy, expected_regimes):
    """Each Batch 418 OVERRIDE must be present + match cube-derived set.
    These supersede prior Batch 203/293/370 curation per
    project_no_apriori_strategy_pruning (cube empirical supersedes literature).
    """
    assert strategy in STRATEGY_REGIME_AFFINITY, (
        f"{strategy} missing from STRATEGY_REGIME_AFFINITY - Batch 418 "
        f"override not applied or silently reverted")
    actual = STRATEGY_REGIME_AFFINITY[strategy]
    assert actual == expected_regimes, (
        f"{strategy}: STRATEGY_REGIME_AFFINITY = {actual!r}, expected "
        f"{expected_regimes!r} (Batch 418 cube-empirical override)")


def test_batch418_total_cube_derived_entries():
    """Total entries with explicit cube-derivation = 14 (Batch 417 NEW) + 15
    (Batch 418 OVERRIDES) = 29 distinct strategies. B617 family audit
    removed 4 of the 14 B417 entries (dual strategies; direction-disagg
    cube validation pending) -> 10 B417 active + 15 B418 = 25 active
    cube-derived entries."""
    cube_derived_count = (len(BATCH_417_NEW_ENTRIES_ACTIVE)
                          + len(BATCH_417_REMOVED_BY_FAMILY_AUDIT)
                          + len(BATCH_418_OVERRIDES)
                          + len(BATCH_418_REMOVED_ORPHANS))
    assert cube_derived_count == 29, (
        f"Expected 14 + 15 = 29 cube-derived entries (incl B617-removed and "
        f"the B3139q-r171 orphan); got {cube_derived_count}")
    # No collision between the two sets (Batch 417 NEW were not-prior-entries;
    # Batch 418 OVERRIDES were prior-entries being changed):
    all_417 = set(BATCH_417_NEW_ENTRIES_ACTIVE) | BATCH_417_REMOVED_BY_FAMILY_AUDIT
    all_418 = set(BATCH_418_OVERRIDES) | set(BATCH_418_REMOVED_ORPHANS)
    overlap = all_417 & all_418
    assert not overlap, (
        f"Batch 417 NEW and Batch 418 OVERRIDE sets must be disjoint; "
        f"overlap = {overlap}")
    # the removed orphan stays removed
    assert all(k not in STRATEGY_REGIME_AFFINITY for k in BATCH_418_REMOVED_ORPHANS)
