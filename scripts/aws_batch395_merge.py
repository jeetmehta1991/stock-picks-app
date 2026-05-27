"""Batch 395: download 5 batch outputs from S3, merge, rebuild cube, validate.

Source (per CHECKLIST #77): owner directive 2026-05-27 Path 1.  After
all 5 EC2 instances signal `_COMPLETE` to S3, this script:

  1. Downloads s3://bucket/outputs/batch_{1..5}/ to local
  2. Runs scripts/merge_batch_outputs.py to combine into final trade_log
  3. Runs scripts/rebuild_cube_from_trade_log.py to materialize
     trade_exit_detail.csv from the merged trade log
  4. Runs Phase 7 (post-run validation) from scripts/pre_launch_validation.py
  5. Uploads the merged final outputs back to s3://bucket/final/

Usage:
    python scripts/aws_batch395_merge.py --bucket stock-picks-batch395-jm-7421

    # Custom local output dir:
    python scripts/aws_batch395_merge.py ... --output-dir output_batch395_final
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def s3_sync_down(bucket: str, prefix: str, local_dir: Path) -> int:
    """Sync s3://bucket/prefix/ down to local_dir/."""
    local_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "aws", "s3", "sync", f"s3://{bucket}/{prefix}/", str(local_dir),
        "--no-progress",
    ]
    return subprocess.call(cmd)


def s3_sync_up(bucket: str, prefix: str, local_dir: Path) -> int:
    cmd = [
        "aws", "s3", "sync", str(local_dir), f"s3://{bucket}/{prefix}/",
        "--no-progress",
    ]
    return subprocess.call(cmd)


def all_complete(bucket: str, n_batches: int) -> tuple[bool, list[int]]:
    """Check which batches have written the _COMPLETE sentinel.

    Returns (all_done, missing_batch_indices).
    """
    missing = []
    for i in range(1, n_batches + 1):
        cmd = [
            "aws", "s3api", "head-object", "--bucket", bucket,
            "--key", f"outputs/batch_{i}/_COMPLETE",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            missing.append(i)
    return (len(missing) == 0, missing)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--n-batches", type=int, default=5)
    ap.add_argument("--output-dir",
                    default=str(REPO / "output_batch395_final"))
    ap.add_argument("--local-batch-prefix",
                    default=str(REPO / "output_batch395_batch"),
                    help="prefix for per-batch local dirs (suffixed with _N)")
    ap.add_argument("--wait", action="store_true",
                    help="if some batches not complete, poll until all done "
                         "(timeout 8h)")
    ap.add_argument("--skip-cube-rebuild", action="store_true",
                    help="skip rebuild_cube_from_trade_log.py (cube already "
                         "in merged trade_exit_detail.csv from each batch)")
    ap.add_argument("--upload-final", action="store_true",
                    help="upload merged final outputs back to "
                         "s3://bucket/final/")
    args = ap.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Wait for all _COMPLETE sentinels
    if args.wait:
        deadline = time.time() + 8 * 3600
        while time.time() < deadline:
            all_done, missing = all_complete(args.bucket, args.n_batches)
            if all_done:
                print(f"[INFO] all {args.n_batches} batches complete")
                break
            print(f"[WAIT] missing _COMPLETE for batches {missing} -- "
                  f"sleeping 120s")
            time.sleep(120)
        else:
            print(f"[FATAL] timeout waiting for all batches complete; "
                  f"missing: {missing}")
            return 1
    else:
        all_done, missing = all_complete(args.bucket, args.n_batches)
        if not all_done:
            print(f"[WARN] missing _COMPLETE for batches {missing}; "
                  f"proceeding anyway (use --wait to block)")

    # Phase 1: download each batch
    print(f"\n[INIT] downloading {args.n_batches} batches from S3...")
    batch_dirs = []
    for i in range(1, args.n_batches + 1):
        local = Path(f"{args.local_batch_prefix}_{i}")
        prefix = f"outputs/batch_{i}"
        print(f"[SYNC] s3://{args.bucket}/{prefix}/ -> {local}/")
        rc = s3_sync_down(args.bucket, prefix, local)
        if rc != 0:
            print(f"[FAIL] sync rc={rc} for batch_{i}")
            continue
        batch_dirs.append(local)

    if len(batch_dirs) < args.n_batches:
        print(f"[WARN] only {len(batch_dirs)}/{args.n_batches} batches "
              f"downloaded; merge will be partial")

    # Phase 2: run existing merge_batch_outputs.py
    print(f"\n[MERGE] invoking merge_batch_outputs.py...")
    merge_cmd = [
        sys.executable, str(REPO / "scripts" / "merge_batch_outputs.py"),
        "--input-dirs", *[str(d) for d in batch_dirs],
        "--output-dir", str(output_dir),
    ]
    rc = subprocess.call(merge_cmd, cwd=str(REPO))
    if rc != 0:
        print(f"[FAIL] merge_batch_outputs.py rc={rc}")
        return 2

    # Phase 3: rebuild cube from merged trade log (if needed)
    if not args.skip_cube_rebuild:
        cube_csv = output_dir / "trade_exit_detail.csv"
        merged_log = output_dir / "trade_log.csv"
        if merged_log.exists() and (not cube_csv.exists() or cube_csv.stat().st_size < 1024):
            print(f"\n[CUBE] rebuilding trade_exit_detail.csv from merged "
                  f"trade_log...")
            rebuild_cmd = [
                sys.executable, str(REPO / "scripts" / "rebuild_cube_from_trade_log.py"),
                "--trade-log", str(merged_log),
                "--ohlcv-dir", str(REPO / "data_prefetch" / "polygon" / "ohlcv_daily"),
                "--output-dir", str(output_dir),
            ]
            rc = subprocess.call(rebuild_cmd, cwd=str(REPO))
            if rc != 0:
                print(f"[FAIL] rebuild_cube rc={rc}")
                return 3
        else:
            print(f"\n[CUBE] trade_exit_detail.csv already populated; "
                  f"skipping rebuild")

    # Phase 4: post-run validation (Phase 7 of pre_launch suite)
    print(f"\n[VALIDATE] running post-run validation on {output_dir}...")
    val_cmd = [
        sys.executable, "-c",
        f"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path('{REPO}').resolve()))
from scripts.pre_launch_validation import phase_7_post_run_validation
fails = phase_7_post_run_validation(Path('{output_dir}'))
if fails:
    print(f'[FAIL] post-run validation ({{len(fails)}} issue(s)):')
    for f in fails:
        print('  -', f)
    sys.exit(11)
print('[OK] post-run validation passed')
""",
    ]
    rc = subprocess.call(val_cmd)
    if rc != 0:
        print(f"[FAIL] post-run validation rc={rc}")
        # Do not return; uploads still valuable for forensics

    # Phase 5: upload final outputs (optional)
    if args.upload_final:
        print(f"\n[UPLOAD] {output_dir}/ -> s3://{args.bucket}/final/")
        rc = s3_sync_up(args.bucket, "final", output_dir)
        if rc != 0:
            print(f"[FAIL] upload rc={rc}")

    print(f"\n[DONE] merge complete -> {output_dir}/")
    print(f"       Next steps:")
    print(f"       - Inspect output_batch395_final/trade_log.csv "
          f"+ trade_exit_detail.csv")
    print(f"       - Run python scripts/aws_batch395_teardown.py --bucket "
          f"{args.bucket} to terminate any stragglers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
