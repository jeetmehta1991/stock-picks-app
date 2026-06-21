"""Batch 465 (2026-05-29) -- AU9 orphan-scripts registry.

QUEUE FRAMING WAS VERY STALE (queue: 21; actual: 3):
  The queue claimed 21 orphan scripts/*.py files (no reference anywhere
  in repo). A fresh whole-word scan across all .py / .md / .sh / .yml /
  .json (excluding tests/) shows the actual count is 3. The other 18
  named in the queue were archived, wired, or renamed across the
  intervening batches.

CURRENT ORPHANS (3):
  scripts/aws_batch395_upload_data.py     -- one-time S3 data upload
  scripts/fix_meta_ticker_corruption.py   -- Batch 275 META ticker fix
  scripts/phase_1b_canary_dashboard.py    -- Phase 1B canary dashboard

NO AUTONOMOUS DELETION:
  Per CLAUDE.md owner-approval rule, removing or archiving a script is
  a behavior change that needs owner sign-off. The registry surfaces
  the inventory + classifies each for owner-approved follow-up.

REGISTRY classification letters:
  a -- "intentional one-shot, archive candidate" : script ran once for
       a specific cleanup / migration / upload. Done; can move to
       archive/ with a brief note.
  b -- "ad-hoc data-fix script, retain in scripts/ for reference" :
       one-shot that captures a specific data corruption fix; useful
       to keep as documented procedure even if not re-run.
  c -- "active deliverable; needs caller wiring or doc reference" :
       script is part of an in-flight workflow but currently has no
       cron / launcher / doc pointer. Wire it or document the
       manual-trigger condition.

FOLLOW-UP:
  Each (a) is a candidate archive move; (b) stays in place; (c) needs
  a caller. This batch surfaces; owner decides.
"""
from __future__ import annotations

import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# CLASSIFICATION REGISTRY (one entry per orphan script)
# --------------------------------------------------------------------------
CLASSIFICATION: dict[str, tuple[str, str]] = {
    "scripts/aws_batch395_upload_data.py": (
        "a",
        "Batch 395 one-time S3 upload of data_prefetch + universe csvs; "
        "supposed to run before the first batch395 launch. Owner-approval "
        "needed to archive once the cube run completes.",
    ),
    "scripts/fix_meta_ticker_corruption.py": (
        "b",
        "Batch 275 META ticker corruption fix (Meta Materials -> Meta Platforms "
        "reassignment 2022-06-09). One-shot data fix; retain as documented "
        "procedure in case META.parquet is rebuilt from upstream Polygon data.",
    ),
    "scripts/phase_1b_canary_dashboard.py": (
        "c",
        "Batch 399 Sprint 7 Phase B canary dashboard. Consumer of "
        "canary_signals.parquet (produced by phase_1b_canary_compute.py). "
        "Currently no launcher / cron / doc reference; needs wiring before "
        "Phase 1B-alpha gate activates.",
    ),
    "scripts/audit_ohlcv_ticker_reassignments.py": (
        "b",
        "Batch 275 META ticker-reassignment audit (companion to "
        "fix_meta_ticker_corruption.py). Audits the OHLCV cache for "
        "ticker-reassignment discontinuities. Retain in scripts/ as a "
        "documented manual-run audit; run on demand when META-like "
        "reassignment incidents are suspected.",
    ),
    "scripts/run_phase_1a_beta_local.py": (
        "c",
        "Local Phase 1A-beta runner shim. Was a developer convenience "
        "before AWS-based launch was the canonical path. Either re-wire "
        "as the documented `pytest`-pre-AWS smoke runner or archive.",
    ),
    # Batch 517 hotfix (2026-05-31): scripts/check_platform_determinism.py
    # REMOVED from CLASSIFICATION because Batch 508 workflow
    # `.github/workflows/det1-platform-determinism.yml` now references
    # it -- it has a caller and is no longer orphan. AU9 scanner pin
    # would have flagged it on next regen; removed proactively.
    "scripts/analyst_overlay_from_trade_log.py": (
        "c",
        "Batch 499 item-7 analyst-overlay generator. Operator-run "
        "post-cube pass that reconstructs equity_curve + portfolio "
        "summary + strategy_regime_matrix from a merged trade_log.csv "
        "so dashboard Tabs 2 + 4 receive their JSON feeds. Consumed by "
        "test_batch499_analyst_overlay.py (unit tests on the math). "
        "Needs cron/launcher wiring before dashboard refresh automation.",
    ),
    # Batch 530 post-merge sync: scripts/entry_side_threshold_optimizer.py
    # REMOVED -- batch/521 multi-feature optimizer test now imports
    # BATCH_414_STRATEGIES from it -> no longer orphan per AU9 scanner.
    "scripts/entry_side_multi_feature_optimizer.py": (
        "c",
        "Batch 521 multi-feature entry-side optimizer (pairwise feature "
        "buckets). Operator-run post-cube companion to Batch 501 "
        "single-feature optimizer. Consumed by "
        "test_batch521_multi_feature_entry_optimizer.py only. Needs "
        "caller/cron wiring once R4 cube spec is owner-approved.",
    ),
    "scripts/validate_sec_edgar_decoded_completeness.py": (
        "c",
        "Batch 526 SEC EDGAR decoded-cache 6-gate validator (coverage / "
        "schema / min-rows / status-dist / spot-check / sample-sanity). "
        "Operator-run after P17a scoped extraction completes to gate "
        "the P17b/c/d/e sleeve wire-in batch. Consumed by "
        "test_batch526_sec_edgar_decoded_validator.py only.",
    ),
    # Batch 530 post-merge sync: scripts/diff_trade_logs.py REMOVED --
    # AU9 scanner sees a reference outside test/EXECUTION_QUEUE excluded
    # set (likely the script's own setup docs or another doc file).
    # Not orphan per scanner; registry agrees.
    "scripts/check_merge_train_conflicts.py": (
        "c",
        "Batch 529 merge-train conflict detector (git merge-tree "
        "simulation across batch/** branches). Operator-run before "
        "merging accumulated feature branches. Consumed by "
        "test_batch529_merge_train_conflict_detector.py only.",
    ),
    "scripts/verify_environment.py": (
        "c",
        "Batch 525 laptop-portable environment verifier (requirements.txt "
        "pin diff + cross-platform fingerprint diff). Operator-run on "
        "fresh machine after `pip install -r requirements.txt`. "
        "Documented in requirements.txt setup procedure.",
    ),
    # Batch 524 hotfix (2026-05-31): scripts/extract_sec_edgar_xml_pilot.py
    # REMOVED -- Batch 515 scoped wrapper imports it (pilot has caller now),
    # so AU9 scanner reports it as non-orphan. Registry must agree.
    "scripts/extract_sec_edgar_xml_scoped.py": (
        "c",
        "Batch 515 P17a full-universe SEC EDGAR extractor "
        "(~1722 tickers x 3 forms x 2020-2026). Calls "
        "extract_sec_edgar_xml_pilot via monkey-patched PILOT window. "
        "Operator-run after owner approves scaling beyond pilot. "
        "Consumed by manual trigger only -- no cron/launcher yet. "
        "Caller wiring TBD post-extraction completion + cube ingest.",
    ),
    "scripts/prefetch_finra_short_interest.py": (
        "c",
        "Batch 513 P15 FINRA biweekly short-interest prefetch fetcher. "
        "Pulls cdn.finra.org/equity/otcmarket/biweekly/shrtYYYYMMDD.csv "
        "(pipe-delimited despite .csv extension) for 1926 universe "
        "tickers; writes data_prefetch/finra/short_interest/*.parquet. "
        "Operator-run manually; biweekly cadence (15th + EOM) means "
        "the cron wiring is a separate batch decision (Sprint 5 "
        "refresh cadence). Consumed by Batch 519 P15 sleeves "
        "(strat_squeeze_setup_long + strat_short_borrow_trap_avoid).",
    ),
    # ----- Batch 836 (2026-06-16) AU9 23-entry expansion -----
    # Per owner directive 2026-06-16 'Gate 5 18 substantive pyramid items
    # execute'. B826 + B748e + B602-B748 batch wave created 23 new orphan
    # scripts. Classifying each per the AU9 (a/b/c) rubric.
    "scripts/aws_b660_launch.py": (
        "a",
        "Batch 660 launch script for full T1a x 2020-2026 fire-count "
        "measurement run on AWS. One-time launch for B660 background job; "
        "owner-approval to archive once B660 measurement set is locked.",
    ),
    "scripts/b748e_incremental_sc13d_decoder.py": (
        "a",
        "Batch 748e SC 13D incremental decoder. One-shot SEC EDGAR SC 13D "
        "extraction pass run during the B748 sec_edgar_decoded buildup. "
        "Documented in B748e commit; archive candidate after extractor "
        "becomes the canonical path.",
    ),
    "scripts/backfill_quiet_strategies.py": (
        "a",
        "One-time backfill of quiet-strategy producer-zero re-audit data. "
        "Archive candidate once Stage 3 producer_zero_reaudit.json is the "
        "primary surface.",
    ),
    "scripts/checklist_106_cluster_a_producer_audit.py": (
        "c",
        "Batch 757 CHECKLIST-106 producer-data audit for Cluster A. "
        "Recurring audit run during Stage 4 cluster walks. Consumed by "
        "B767 council pre-flight + ad-hoc producer-health probes. Needs "
        "cron/launcher wiring for systematic pre-cube audit cadence.",
    ),
    "scripts/cross_sectional_pit_audit.py": (
        "c",
        "Batch 746 cross_sectional PIT-invariance audit. Verdict-grade "
        "audit ran during B690-step-2. Recurring audit pattern for any "
        "factor-strategy PIT regression. Needs documented manual-trigger "
        "condition for re-runs.",
    ),
    "scripts/extract_proposed_changes.py": (
        "a",
        "Batch 566 Stage 4 step 1 of 4 change extractor (351 atomic rows "
        "from R4). One-shot extraction; archive candidate once Stage 4 "
        "per-change approval surface is finalized.",
    ),
    "scripts/fetch_flt_one_time_b561.py": (
        "a",
        "Batch 561 one-time FLT (FleetCor / Corpay) ticker data fetch for "
        "sector_history.csv 2023-03-17 IT->Industrials cohort. Explicit "
        "one-time in filename; archive after FLT inclusion in cache.",
    ),
    "scripts/init_approvals.py": (
        "a",
        "One-time initializer for approvals.json (Stage 4 per-change "
        "approval state). Archive after first owner-approval workflow "
        "cycle establishes the file lifecycle.",
    ),
    "scripts/mark_s4_reviewed.py": (
        "a",
        "Owner-utility to mark Stage 4 walk-doc strategies as reviewed. "
        "One-time / ad-hoc operator tool. Archive candidate; not part of "
        "automated workflow.",
    ),
    # B971 (2026-06-21) Council 74: scripts/mean_reversion_edge_prior_test.py
    # REMOVED -- now externally-referenced (no longer orphan per AU9 scanner).
    "scripts/mfi_obv_anti_selection_test.py": (
        "c",
        "Batch 789 MFI x OBV anti-selection conditional-add-test (B709-"
        "style 4-cell test on T1a OHLCV + forward 10d returns). Diagnostic "
        "test; consumed by B826 #67 full-T1a verdict. Operator-run; needs "
        "documented trigger condition for any new gate-modification audit.",
    ),
    "scripts/pattern_t_family_grep_audit.py": (
        "b",
        "Batch 763 Pattern T MA-cross + trend-gate collinearity family-"
        "grep audit. Documented procedure for cluster-wide redundancy "
        "audits. Retain in scripts/ as documented re-runnable audit when "
        "new Pattern T candidates surface.",
    ),
    "scripts/pit_universe_discipline_audit.py": (
        "b",
        "Batch 747 PIT-universe discipline audit (B690 revised step 3 per "
        "owner question 'why does there need to be any delisting?'). "
        "Documented audit procedure; retain in scripts/ for re-run when "
        "universe-construction discipline questions arise.",
    ),
    "scripts/preflight_cross_sweep.py": (
        "b",
        "Batch 568 preflight cross-sweep utility. Owner-approval cross-"
        "sweep tool per feedback_audit_recommendations_against_existing"
        "_directives. Documented procedure; retain.",
    ),
    "scripts/producer_collision_audit.py": (
        "b",
        "Batch 736 producer-collision auditor. Documented audit for "
        "detecting collision between TIER 1 / TIER 2 / TIER 3 producer "
        "signal key emissions. Retain in scripts/ for re-run when "
        "producer-side schema changes land.",
    ),
    "scripts/refactor_b718b_explicit_borrow_gate.py": (
        "a",
        "Batch 718b explicit borrow gate refactor (Pattern Y consolidation "
        "step 1). One-time refactor; archive after B742 strat3 chunk lands.",
    ),
    "scripts/refactor_b742_strat3_explicit_borrow_gate.py": (
        "a",
        "Batch 742 explicit borrow gate refactor (Pattern Y consolidation "
        "step 2; _strat3 SHORT branch). One-time refactor; archive after "
        "B744 borrow-gate lint test pins the post-refactor state.",
    ),
    "scripts/run_b693_sweeps.py": (
        "a",
        "Batch 693 sweep harness for entry-side multi-feature gate "
        "exploration. One-time sweep; outputs in batch's owner-approval "
        "candidates. Archive candidate after R5 cube iteration.",
    ),
    "scripts/run_b702_ev3_deletion_empirical_verify.py": (
        "a",
        "Batch 702 EV-3 deletion empirical verify script (phi correlation "
        "test that produced B709 EMPIRICAL-RESTORE verdict). One-time "
        "verification; archive after B709 restoration is locked.",
    ),
    "scripts/run_b737_confronting_tests.py": (
        "a",
        "Batch 737 confronting-tests runner. One-time adversarial-tests "
        "harness from B737 walk. Archive candidate.",
    ),
    "scripts/validate_pattern_w_candidates.py": (
        "b",
        "Batch 759 Pattern W validation consumer (post-B758 edge-prior "
        "test methodology). Documented validation procedure for Pattern W "
        "DELETE candidates per council methodology. Retain in scripts/.",
    ),
    "scripts/validate_smc_panel_cache_semantic.py": (
        "b",
        "Batch 555/560 SMC panel-cache semantic validation. Documented "
        "validation for USE_SMC_PANEL_CACHE flag flip decision (per-key "
        "bool divergence + per-key float divergence audit). Retain in "
        "scripts/ for re-run when flag-flip is owner-considered.",
    ),
    "scripts/validate_trigger_followthrough.py": (
        "b",
        "Batch 757/758 trigger-followthrough validation consumer (post-"
        "B756 fire-bar matrix smoke). Documented validation procedure for "
        "Pattern W candidate testing. Retain in scripts/.",
    ),
    # ------------------------------------------------------------------
    # B971 (2026-06-21) Council 74 A1-1 additions: 15 new orphan scripts
    # surfaced by AU9 scanner across B914-B970 session work.
    # ------------------------------------------------------------------
    "scripts/b914_cohort_audit_13f_fwd_returns.py": (
        "a",
        "Batch 914 13F cohort fwd-returns audit; one-shot pre-R5 "
        "diagnostic. Audited 13F holdings cohort vs forward-return "
        "distributions for archetype-1 dispose-before-diagnose check. "
        "Done; archive candidate once owner reviews findings.",
    ),
    "scripts/b916_archetype1_diagnose_before_dispose.py": (
        "a",
        "Batch 916 archetype-1 diagnose-before-dispose protocol script "
        "(Council 32-era audit). One-shot pre-R5 archetype investigation; "
        "owner-approved disposition methodology lives in B917+B918 outputs. "
        "Archive candidate.",
    ),
    "scripts/b917_coverage_map_rescue_retest.py": (
        "a",
        "Batch 917 coverage-map rescue-retest one-shot script. Archetype-1 "
        "broad-sample micropilot; output in output_audit/b917_*.json. "
        "Done; archive candidate.",
    ),
    "scripts/b918_arch1_per_gate_bottleneck.py": (
        "a",
        "Batch 918 archetype-1 per-gate bottleneck audit. One-shot pre-R5 "
        "diagnostic isolating which gate caused FAIL_FIRE_STARVED for arch-1 "
        "cohort. Output in output_audit/b918_*.json. Archive candidate.",
    ),
    "scripts/b949_investigate_evidence_source_buckets.py": (
        "a",
        "Batch 949 Council 53 evidence-source bucket investigation (D-only "
        "75/49.3% OVER-PERMISSIVE finding + 65 Bucket II parser gap). "
        "One-shot pre-R5 investigation; informed B950 ledger refinement. "
        "Archive candidate.",
    ),
    "scripts/b950_measure_counterfactuals.py": (
        "a",
        "Batch 950 Council 54 in-process counterfactual measurement "
        "(A-only/B-only/A+B distributions before ship-decision). One-shot "
        "ledger v2 calibration tool. Output informed Council 54 ship verdict. "
        "Archive candidate.",
    ),
    "scripts/b950_pre_build_audit_d_only.py": (
        "a",
        "Batch 950 Council 54 Contrarian pre-build audit on 75 D-only "
        "entries (23/75 = 30.7% with evidence = SHIP_INSTRUMENTED verdict). "
        "One-shot audit; informed Council 54 ship-conditional decision. "
        "Archive candidate.",
    ),
    "scripts/b956_build_findings_triage_queue.py": (
        "c",
        "Batch 956 Council 60 STRATEGIC PIVOT findings triage queue builder "
        "(scans 217 dossiers across 12 built sections; enumerates 6 finding "
        "types). RECURRING tool: re-run after each dossier population to "
        "refresh owner-triage queue. WIRED B975 (2026-06-21 Council 77 P1 "
        "Bucket A A9) as end-of-run hook in scripts/populate_all_dossiers.py "
        "(non-fatal try/except). Tests in test_b975_a9_b956_cron_wired.py.",
    ),
    "scripts/b957_audit_retrospective_trial_counts.py": (
        "a",
        "Batch 957 Council 61+62 retrospective trial-count audit "
        "(N_effective approx 5,894 = 1.04x baseline; DSR threshold inflation "
        "approx 1.002x NEGLIGIBLE). One-shot pre-R5 audit; informed "
        "Council 63 Phase 6.5 design. Archive candidate.",
    ),
    "scripts/build_walk_verdict_ledger.py": (
        "a",
        "Batch 948 Council 52 walk_verdict_ledger v1 builder (108 strategies; "
        "section-header pattern only). SUPERSEDED by build_walk_verdict_"
        "ledger_v2.py (B950 Council 54 added table-row pattern + verdict-"
        "strength scanner). Retain for now as v1 baseline; archive once v2 "
        "stable post-R5.",
    ),
    "scripts/build_walk_verdict_ledger_v2.py": (
        "c",
        "Batch 950 Council 54 walk_verdict_ledger v2 builder (125 strategies; "
        "section-header + table-row patterns + verdict-strength scanner). "
        "Output (walk_verdict_ledger_v2.json) consumed by r5_inclusion_"
        "criterion.py _load_walk_verdict_ledger() per B948+B950 wiring. "
        "RECURRING per-batch: re-run when STAGE_4_*CLUSTER_WALKS.md docs "
        "change. WIRED B976 (2026-06-21 Council 77 P1 Bucket A A8) as "
        "end-of-run hook in scripts/populate_all_dossiers.py (non-fatal "
        "try/except). Tests in test_b976_a6_a7_a8_wired.py.",
    ),
    "scripts/classify_deferred_140.py": (
        "a",
        "Batch 947 Council 51 deferred-140 classifier (priority-ordered "
        "disjoint buckets V > IV > III > II > I; HONEST FINDING: 140/140 = "
        "100% Bucket V walk-doc-mentioned cross-reference too permissive). "
        "SUPERSEDED by B948+B949+B950 ledger + criterion refinement. "
        "Archive candidate.",
    ),
    "scripts/dossier_self_test.py": (
        "c",
        "Batch 934 Council 45 dossier-build self-test framework (9 KNOWN-"
        "GOOD strategies validation). Pre-Stream-E-population sanity check. "
        "WIRED B976 (2026-06-21 Council 77 P1 Bucket A A6) as PRE-FLIGHT "
        "gate in scripts/populate_all_dossiers.py - runs BEFORE "
        "list_strategies_for_dossier per Council 38 Outsider mandate "
        "(non-fatal try/except - soft-gate). Tests in "
        "test_b976_a6_a7_a8_wired.py.",
    ),
    "scripts/refresh_sector_history.py": (
        "c",
        "Sector history refresh utility (monthly cadence likely). Currently "
        "no cron/scheduler reference. Needs documented monthly-trigger "
        "wiring (GH Actions or laptop cron per CLAUDE.md universe refresh "
        "pattern).",
    ),
    "scripts/stream_v_verify_reproducibility.py": (
        "c",
        "Batch 970 Council 72 Stream V reproducibility verifier (PATH "
        "Section 13.7 launch gate #14 satisfied; 70/70 bit-identical on 5 "
        "deterministic strategies x 14 Stream E extractors). WIRED B976 "
        "(2026-06-21 Council 77 P1 Bucket A A7) as post-Stream-E "
        "regression hook in scripts/populate_all_dossiers.py (runs AFTER "
        "populate loop; non-fatal try/except). Tests in "
        "test_b976_a6_a7_a8_wired.py.",
    ),
}


def _scan_orphan_scripts() -> list[str]:
    """Replicate the AU9 orphan scan: tracked scripts/*.py files with NO
    whole-word reference in any other non-test, non-generated file.

    Only TRACKED scripts (per `git ls-files`) are scanned -- untracked
    scratch files in scripts/ are out of scope by definition.

    "Orphan" here means: NO whole-word reference in any .py / .sh / .yml /
    .yaml / .md across the repo (caller files + documentation), EXCLUDING
    the self-referencer files EXECUTION_QUEUE.md and this registry test
    (which list orphans by name and would otherwise create a circular
    'documented therefore not orphan' loop). Tests/ directories are also
    excluded since test files reference many scripts in passing.

    Excluded directories (to keep scan stable across pyramid runs):
      - any directory whose name starts with `output_`, `tmp_`, `vm_`
      - logs/, archive/, .pytest_cache/, .venv/, node_modules/
      - tests/
    Excluded specific files:
      - EXECUTION_QUEUE.md (lists orphans by name -> circular)
      - this test file (lists orphans by name -> circular)
    """
    # Only tracked scripts (skip untracked scratch files)
    import subprocess
    try:
        result = subprocess.run(
            ["git", "ls-files", "scripts/*.py"],
            cwd=str(REPO), capture_output=True, text=True, check=True,
        )
        tracked_rel = [ln.strip() for ln in result.stdout.splitlines()
                       if ln.strip()]
        scripts = sorted(REPO / p for p in tracked_rel)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: glob (less strict but works without git)
        scripts = sorted((REPO / "scripts").rglob("*.py"))
    EXCLUDED_DIR_PREFIXES = ("output_", "tmp_", "vm_")
    EXCLUDED_DIRS = {
        "logs", "archive", ".pytest_cache", ".venv", "node_modules",
        "tests",
    }
    EXCLUDED_FILES_ABS = {
        (REPO / "EXECUTION_QUEUE.md").resolve(),
        (REPO / "backtest" / "tests"
         / "test_batch465_orphan_scripts_registry.py").resolve(),
    }
    EXCLUDED_FILENAMES: set[str] = set()

    patterns = ["*.py", "*.sh", "*.yml", "*.yaml", "*.md"]
    universe: list[Path] = []
    for pat in patterns:
        for p in REPO.rglob(pat):
            parts = p.parts
            if any(part.startswith(EXCLUDED_DIR_PREFIXES) for part in parts):
                continue
            if any(part in EXCLUDED_DIRS for part in parts):
                continue
            if p.name in EXCLUDED_FILENAMES:
                continue
            if p.resolve() in EXCLUDED_FILES_ABS:
                continue
            universe.append(p)

    orphans = []
    for s in scripts:
        name = s.stem
        needle = re.compile(rf"\b{re.escape(name)}\b")
        found_external = False
        for f in universe:
            if f.resolve() == s.resolve():
                continue
            try:
                t = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if needle.search(t):
                found_external = True
                break
        if not found_external:
            rel = str(s.relative_to(REPO)).replace("\\", "/")
            orphans.append(rel)
    return orphans


def test_registry_covers_all_orphan_scripts():
    """Drift guard: every actual orphan must have a CLASSIFICATION entry."""
    orphans = set(_scan_orphan_scripts())
    classified = set(CLASSIFICATION.keys())
    missing = sorted(orphans - classified)
    assert not missing, \
        f"{len(missing)} orphan scripts are not in CLASSIFICATION: " \
        f"{missing}. Add each to the registry with class letter + reason."


def test_registry_has_no_stale_entries():
    """Reverse guard: a registered orphan that is now referenced should
    be removed from CLASSIFICATION."""
    orphans = set(_scan_orphan_scripts())
    classified = set(CLASSIFICATION.keys())
    stale = sorted(classified - orphans)
    assert not stale, \
        f"{len(stale)} CLASSIFICATION entries are no longer orphan " \
        f"(remove): {stale}"


def test_every_class_letter_in_legal_set():
    """All classification letters must be a/b/c."""
    legal = {"a", "b", "c"}
    bad = {k: v for k, v in CLASSIFICATION.items() if v[0] not in legal}
    assert not bad, f"Illegal classification letters: {bad}"


def test_classification_distribution_matches_scan_size():
    """Registry total must equal the actual orphan count."""
    orphan_count = len(_scan_orphan_scripts())
    assert len(CLASSIFICATION) == orphan_count, \
        f"registry size {len(CLASSIFICATION)} != actual orphans {orphan_count}"
