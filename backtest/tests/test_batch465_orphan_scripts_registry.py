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
    "scripts/check_platform_determinism.py": (
        "c",
        "Batch 498 DET1 cross-platform-determinism diagnostic. Manual-run "
        "harness operator invokes on each target platform (Windows / Linux) "
        "to produce SHA-256 fingerprints of 9 indicators against seeded "
        "synthetic OHLCV. Output drives the queue row DET1 root-cause "
        "diff. Consumed by test_batch498_det1_platform_determinism.py "
        "(reads committed Windows fixture + future Linux fixture).",
    ),
    "scripts/analyst_overlay_from_trade_log.py": (
        "c",
        "Batch 499 item-7 analyst-overlay generator. Operator-run "
        "post-cube pass that reconstructs equity_curve + portfolio "
        "summary + strategy_regime_matrix from a merged trade_log.csv "
        "so dashboard Tabs 2 + 4 receive their JSON feeds. Consumed by "
        "test_batch499_analyst_overlay.py (unit tests on the math). "
        "Needs cron/launcher wiring before dashboard refresh automation.",
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
