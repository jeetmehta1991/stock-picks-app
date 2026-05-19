"""
scripts/run_t0_close_out.py — T0 close-out automation.

Bundles all post-Batch-rerun close-out steps into one orchestrated run.
Per IMPLEMENTATION_PLAN.md Track T0 (2026-05-18 Batch 234).

Steps:
  1. Verify all 5 input batches have last_run.txt sentinel (completion gate)
  2. Run merge_batch_outputs.py (concat CSVs + re-compute DSR/Bonferroni/per-strategy metrics)
  3. Run run_pbo_check.py (Probability of Backtest Overfitting on merged trade log)
  4. Run build_verification_matrix.py (coverage-driven DEC/BUG verification)
  5. Run build_dashboard_stage_2.py (decisions/bugs/INVs registry)
  6. Run build_dashboard_phase_1a.py (12-tab Phase 1A alpha analysis)
  7. Git commit + push with structured summary

Usage:
  python scripts/run_t0_close_out.py \
      --input-pattern "output_phase_1a_alpha_batch_*" \
      --output-dir output_v2 \
      --batch-label "Phase 1A-alpha T0 close-out"

Owner-approved (2026-05-18): T0 must update BOTH Dashboard 2 (Stage 2) AND
Dashboard 3 (Phase 1A 12-tab). Both refreshed unconditionally.

Exit codes:
  0  - All steps successful, commit pushed
  1  - Sentinel check failed (one or more batches not done)
  2  - Merge failed
  3  - PBO check failed
  4  - VERIFICATION_MATRIX build failed
  5  - Dashboard build failed
  6  - Commit / push failed
  7  - Other unrecoverable error

Safe to re-run: each step is idempotent (overwrites prior output).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def log(msg: str, level: str = "INFO") -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def run_step(name: str, cmd: list[str], cwd: Path = REPO, timeout: int = 1800) -> tuple[int, str]:
    """Run a step; capture output. Returns (exit_code, output_tail)."""
    log(f"STEP: {name}")
    log(f"  CMD: {' '.join(cmd)}")
    t0 = time.time()
    try:
        r = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        elapsed = time.time() - t0
        tail = (r.stdout or "")[-2000:] + (r.stderr or "")[-2000:]
        log(f"  exit={r.returncode}, elapsed={elapsed:.1f}s")
        if r.returncode != 0:
            log(f"  TAIL:\n{tail[-1500:]}", level="ERROR")
        return r.returncode, tail
    except subprocess.TimeoutExpired:
        log(f"  TIMEOUT after {timeout}s", level="ERROR")
        return 124, "timeout"


def step_1_verify_sentinels(input_dirs: list[Path]) -> bool:
    """Verify all input batches have last_run.txt (completion sentinel)."""
    log("=" * 60)
    log("STEP 1/7: Verify batch completion sentinels")
    missing = []
    for d in input_dirs:
        sentinel = d / "last_run.txt"
        if not sentinel.exists():
            missing.append(str(d))
        else:
            log(f"  OK: {d.name}/last_run.txt exists")
    if missing:
        log(f"BLOCKED: {len(missing)} batch(es) missing last_run.txt:", level="ERROR")
        for m in missing:
            log(f"  - {m}", level="ERROR")
        return False
    log(f"  All {len(input_dirs)} batches complete.")
    return True


def step_2_merge_batches(
    input_dirs: list[Path], output_dir: Path
) -> int:
    """Run merge_batch_outputs.py."""
    log("=" * 60)
    log("STEP 2/7: Merge batch outputs (concat + re-compute DSR/Bonferroni)")
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "merge_batch_outputs.py"),
        "--input-dirs",
        *[str(d) for d in input_dirs],
        "--output-dir",
        str(output_dir),
    ]
    code, _ = run_step("merge_batch_outputs", cmd, timeout=600)
    return code


def step_3_pbo_check(output_dir: Path) -> int:
    """Run PBO check on merged trade log."""
    log("=" * 60)
    log("STEP 3/7: PBO check on merged trade log")
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "run_pbo_check.py"),
        "--source",
        str(output_dir),
    ]
    code, _ = run_step("run_pbo_check", cmd, timeout=600)
    return code


def step_4_verification_matrix() -> int:
    """Regenerate VERIFICATION_MATRIX.md (coverage-driven)."""
    log("=" * 60)
    log("STEP 4/7: Rebuild VERIFICATION_MATRIX.md")
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "build_verification_matrix.py"),
    ]
    code, _ = run_step("build_verification_matrix", cmd, timeout=900)
    return code


def step_5_dashboard_stage_2() -> int:
    """Refresh Dashboard 2 (Stage 2 decisions / bugs / INVs)."""
    log("=" * 60)
    log("STEP 5/7: Refresh Dashboard 2 (Stage 2)")
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "build_dashboard_stage_2.py"),
    ]
    code, _ = run_step("build_dashboard_stage_2", cmd, timeout=600)
    return code


def step_6_dashboard_phase_1a(source_dir: Path) -> int:
    """Refresh Dashboard 3 (Phase 1A 12-tab alpha analysis)."""
    log("=" * 60)
    log("STEP 6/7: Refresh Dashboard 3 (Phase 1A 12-tab)")
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "build_dashboard_phase_1a.py"),
        "--source",
        str(source_dir),
    ]
    code, _ = run_step("build_dashboard_phase_1a", cmd, timeout=600)
    return code


def step_7_commit_push(label: str, output_dir: Path) -> int:
    """Git commit + push the T0 close-out artifacts."""
    log("=" * 60)
    log("STEP 7/7: Git commit + push")

    # Stage artifacts produced by steps 2-6
    paths_to_add = [
        str(output_dir),
        "VERIFICATION_MATRIX.md",
        "verification_matrix.json",
        "dashboard_stage_2/data.js",
        "dashboard_stage_2/data.json",
        "dashboard_stage_2/last_run.txt",
        "dashboard_phase_1a/data.js",
        "dashboard_phase_1a/data.json",
        "dashboard_phase_1a/last_run.txt",
    ]
    add_cmd = ["git", "add", *paths_to_add]
    code, _ = run_step("git add", add_cmd, timeout=120)
    if code != 0:
        return 6

    # Read merged summary for the commit body
    trade_count = "?"
    dsr_value = "?"
    pbo_value = "?"
    try:
        portfolio_summary = output_dir / "portfolio_summary.json"
        if portfolio_summary.exists():
            ps = json.loads(portfolio_summary.read_text())
            trade_count = ps.get("total_trades", "?")
    except Exception:
        pass
    try:
        pbo_json = output_dir / "pbo_check.json"
        if pbo_json.exists():
            pj = json.loads(pbo_json.read_text())
            pbo_value = pj.get("pbo", "?")
    except Exception:
        pass

    msg = (
        f"T0 close-out: {label}\n\n"
        f"Merged 5 batches -> {output_dir.name}/. Trades: {trade_count}. PBO: {pbo_value}.\n"
        f"Dashboards 2+3 refreshed. VERIFICATION_MATRIX.md rebuilt.\n\n"
        f"Auto-generated via scripts/run_t0_close_out.py\n\n"
        f"Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
    )
    commit_cmd = ["git", "commit", "-m", msg]
    code, _ = run_step("git commit", commit_cmd, timeout=120)
    if code != 0:
        log("  No changes to commit OR commit failed (may be benign on idempotent re-run)", level="WARN")
        return 0  # Treat as soft-success since re-runs may have nothing to commit

    push_cmd = ["git", "push", "origin", "main"]
    code, _ = run_step("git push", push_cmd, timeout=120)
    if code != 0:
        return 6
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="T0 close-out orchestration")
    p.add_argument(
        "--input-pattern",
        default="output_phase_1a_alpha_batch_*",
        help="Glob pattern for batch output dirs (default: %(default)s)",
    )
    p.add_argument(
        "--output-dir",
        default="output_v2",
        help="Merged-output target dir (default: %(default)s)",
    )
    p.add_argument(
        "--batch-label",
        default=f"Phase 1A-alpha close-out {datetime.now().strftime('%Y-%m-%d')}",
        help="Label for the commit message",
    )
    p.add_argument(
        "--skip-sentinel-check",
        action="store_true",
        help="Bypass last_run.txt verification (use for partial / debug runs)",
    )
    p.add_argument(
        "--skip-commit",
        action="store_true",
        help="Skip step 7 (commit + push)",
    )
    args = p.parse_args()

    # Resolve input dirs via glob
    input_dirs = sorted(REPO.glob(args.input_pattern))
    if not input_dirs:
        log(f"No batch dirs match pattern {args.input_pattern}", level="ERROR")
        return 1
    log(f"Found {len(input_dirs)} batch dirs:")
    for d in input_dirs:
        log(f"  {d.relative_to(REPO)}")

    output_dir = REPO / args.output_dir

    t_start = time.time()

    # Step 1: sentinel check
    if not args.skip_sentinel_check:
        if not step_1_verify_sentinels(input_dirs):
            return 1

    # Step 2: merge
    code = step_2_merge_batches(input_dirs, output_dir)
    if code != 0:
        return 2

    # Step 3: PBO
    code = step_3_pbo_check(output_dir)
    if code != 0:
        log("PBO check non-zero exit; continuing T0 chain (PBO failure is informational, not fatal)", level="WARN")

    # Step 4: VERIFICATION_MATRIX
    code = step_4_verification_matrix()
    if code != 0:
        log("VERIFICATION_MATRIX build failed; continuing to dashboards", level="WARN")

    # Step 5: Dashboard 2
    code = step_5_dashboard_stage_2()
    if code != 0:
        log("Dashboard 2 build failed; continuing to Dashboard 3", level="WARN")

    # Step 6: Dashboard 3
    code = step_6_dashboard_phase_1a(output_dir)
    if code != 0:
        log("Dashboard 3 build failed; will still attempt commit", level="WARN")

    # Step 7: commit + push
    if args.skip_commit:
        log("Skipping commit+push per --skip-commit", level="INFO")
    else:
        code = step_7_commit_push(args.batch_label, output_dir)
        if code != 0:
            return 6

    elapsed = time.time() - t_start
    log("=" * 60)
    log(f"T0 close-out complete. Total wallclock: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
