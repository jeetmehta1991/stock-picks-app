"""backtest/tests/pyramid_tiers.py (B1470, ticket S6-B1467a -- owner-approved 2026-08-06)

THE PROBLEM THIS REPLACES
`backtest/tests/` holds 431 test files. The command treated as "the pyramid" -- in CLAUDE.md, in
the execution-discipline skill, and enforced by the C6 pre-commit stamp -- runs TWO of them and
reports `894 passed`. A full run reports **172 failed / 5,470 passed / 11 errors** (B1468). So the
gate covered ~14% of the suite's assertions while ~3% of the suite was red with no owner, and the
two red pins found at B1465 were found by grepping strategy names, not by any gate.

Worse, two failures live INSIDE the gate: `test_integration.py`'s BUG-30 and BUG-232 tests pass in
isolation (0.74s) and fail in a full run, so the gate's green was ORDER-DEPENDENT -- it certified
"these pass when nothing else has run" (L313). Tracked as S6-B1468a; the polluter is confirmed
cross-file and not yet identified.

WHAT THIS FILE DOES
Makes the gate's scope an explicit, greppable fact instead of a habit. Three tiers:

  GATE        what every commit must pass. Currently the two files C6 already enforces, so
              adopting this manifest changes NO commit behaviour on day one -- it only writes
              down what was already true.
  QUARANTINE  files with known failures as of the B1468 full run. NOT deleted: quarantine is an
              admission that their status is unknown-and-unowned, and each needs triage into
              "real defect -> fix" or "artifact-dependent -> skip cleanly". 45 of the 172 are one
              dashboard file and 11 are engine-parity errors; both look artifact-dependent.
  EXTENDED    everything else -- passing in the B1468 full run but outside the commit gate.
              These are the files a periodic full run protects.

THE RULE THAT MAKES IT MEAN SOMETHING (CHECKLIST #170)
A tiered manifest alone would inherit the exact blind spot it was written to fix, because a subset
that never runs inside the whole suite cannot detect order-dependence. So GATE must be re-validated
INSIDE a full run periodically; until S6-B1468a closes, GATE's green is known to be order-dependent
and that is recorded here rather than assumed away.

Counts are derived, never hand-maintained: EXTENDED is computed as (all files - GATE - QUARANTINE),
so a new test file lands in EXTENDED automatically and cannot silently vanish.
"""
from __future__ import annotations

from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent

# Every commit must pass these. Matches what C6 already enforces.
GATE: tuple[str, ...] = (
    "test_unit.py",
    "test_integration.py",
)

# Known-red in the B1468 full run (2026-08-06). Each needs triage; see S6-B1467a.
QUARANTINE: tuple[str, ...] = (
    "test_b1042_engine_state_emit.py",
    "test_b936_section_09b_extractor.py",
    "test_b970_stream_v_reproducibility.py",
    "test_b985_section_01_fstring_detection_extension.py",
    "test_batch394_cube_pool_parity.py",
    "test_batch419_dashboard_tabs.py",
    "test_batch464_writer_outputs_registry.py",
    "test_batch465_orphan_scripts_registry.py",
    "test_batch467_news_p10.py",
    "test_batch519_p15_sleeves_wireup.py",
    "test_batch522_p17_sleeve_scaffolds.py",
    "test_batch523_verification_matrix_regen_drift.py",
    "test_batch557_phase1a_beta_classification_cluster_verdict.py",
    "test_batch558_phase1a_beta_institutional_cluster_verdict.py",
    "test_batch561_sector_history_2023_expansion.py",
    "test_batch572_doji_at_resistance_short.py",
    "test_batch574_narrow_scope_doji_wide_bands.py",
    "test_batch584_donchian_bug_fix.py",
    "test_batch586_52w_high_walk.py",
    "test_batch589_52w_threshold_tweaks.py",
    "test_batch590_pullback_redesign.py",
    "test_batch591_donchian_walk.py",
    "test_batch595_donchian_tight_pair_walk.py",
    "test_batch596_donchian_retest_pair_walk.py",
    "test_batch597_volume_spike_breakout_walk.py",
    "test_batch598_avwap_symmetry.py",
    "test_batch603_news_strategies_walk.py",
    "test_batch606_r1_break_retest_walk.py",
    "test_batch607_flag_break_retest_walk.py",
    "test_batch608_break_retest_volume_walk.py",
    "test_batch609_break_retest_confluence_walk.py",
    "test_batch610_institutional_breakout_walk.py",
    "test_batch612_silent_gap_refactors.py",
    "test_batch613_52w_high_sm_rewalk.py",
    "test_batch614_news_reversal_walk.py",
    "test_batch615_squeeze_setup_walk.py",
    "test_batch616_low_priority_refactor.py",
    "test_batch617_critique_corrections.py",
    "test_batch621_fire_count_audit.py",
    "test_batch623_direction_disagg_audit.py",
    "test_batch625_walk_commit_fire_count_pin.py",
    "test_batch626_force_index_walk.py",
    "test_batch627_family_bug_sweep_not_s_get_ema_20.py",
    "test_batch628_obv_bullish_family_sweep.py",
    "test_batch629_cmf_family_sweep.py",
    "test_batch630_mega_sweep_E.py",
    "test_batch631_ultimate_oscillator_walk.py",
    "test_batch633_tier3_complete_sweep.py",
    "test_batch639_morning_star_reversal_walk.py",
    "test_batch641_tier1_walk_bundle_followups.py",
    "test_batch643_w5_capitulation_redesign.py",
    "test_batch645_w5_mirror.py",
    "test_batch657_t8_ichimoku_cloud_default_true_fix.py",
    "test_batch659_silent_gap_unify.py",
    "test_batch670_sm9_sm23_deletion_and_replacement.py",
    "test_batch671_borrow_trap_central_gate_plus_threshold_tighten.py",
    "test_batch682_b680_self_critique_actions.py",
    "test_batch686_inverted_cup_and_handle.py",
    "test_batch688_macd_docstring_honesty.py",
    "test_batch697_br1_score_loosen.py",
    "test_batch698_br1_anti_fakeout_producers.py",
    "test_batch721_simple_below_ema_50_short_state_to_event.py",
    "test_batch722_hull_event_plus_deletions.py",
    "test_batch728_breakout_retest_strong_close.py",
    "test_batch730_double_bottom_long_cp2_reviewer_spec.py",
    "test_batch741_b718b_second_chunk_explicit_borrow_gate.py",
    "test_batch743_b718b_strat3_second_chunk_explicit_borrow_gate.py",
    "test_batch744_borrow_gate_lint.py",
    "test_batch748b_dead_producer_disposition.py",
    "test_batch748c_walkback_plus_new_exploratory.py",
    "test_dec491_492_493_sprint2.py",
    "test_engine_optimization_parity.py",
    "test_schema_contracts.py",
    "test_silent_gap_pyramid.py",
    "test_sprint2_acceptance.py",
)


def all_test_files() -> list[str]:
    return sorted(p.name for p in TESTS_DIR.glob("test_*.py"))


def extended() -> list[str]:
    """Passing in the last full run, but outside the commit gate. DERIVED, not maintained."""
    known = set(GATE) | set(QUARANTINE)
    return [f for f in all_test_files() if f not in known]


def summary() -> dict:
    return {"total": len(all_test_files()), "gate": len(GATE),
            "quarantine": len(QUARANTINE), "extended": len(extended())}


if __name__ == "__main__":
    s = summary()
    print(f"  total test files   {s['total']}")
    print(f"  GATE               {s['gate']}   (enforced every commit)")
    print(f"  QUARANTINE         {s['quarantine']}   (known red, awaiting triage)")
    print(f"  EXTENDED           {s['extended']}   (passing, outside the gate)")
    assert s["gate"] + s["quarantine"] + s["extended"] == s["total"], "tiers must partition"
    print("  partition OK")
