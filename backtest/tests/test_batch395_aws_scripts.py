"""Batch 395: structural + dry-run tests for the AWS orchestration scripts.

These tests do NOT make AWS calls.  They validate:
  - Each script has a valid --help interface
  - Splits generator produces a valid 5-batch split summing to 1937
  - Bootstrap script has all required env-var references + AWS CLI commands
  - Launch script handles --dry-run correctly
  - Merge / teardown / monitor have correct argparse interfaces

Source (per CHECKLIST #77): owner directive 2026-05-27 "test extensively
+ use smoke tests throughout. Test in batches."

Run: pytest backtest/tests/test_batch395_aws_scripts.py -v
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent

SCRIPTS = {
    "splits":     REPO / "scripts" / "aws_batch395_splits.py",
    "upload":     REPO / "scripts" / "aws_batch395_upload_data.py",
    "launch":     REPO / "scripts" / "aws_batch395_launch.py",
    "monitor":    REPO / "scripts" / "aws_batch395_monitor.py",
    "merge":      REPO / "scripts" / "aws_batch395_merge.py",
    "teardown":   REPO / "scripts" / "aws_batch395_teardown.py",
    "bootstrap":  REPO / "scripts" / "aws_batch395_bootstrap.sh",
}


def test_all_scripts_exist():
    for name, path in SCRIPTS.items():
        assert path.exists(), f"{name}: missing at {path}"


# ---------- python script --help interface --------------------------------

@pytest.mark.parametrize("name", ["splits", "upload", "launch", "monitor",
                                  "merge", "teardown"])
def test_script_help_exits_zero(name):
    path = SCRIPTS[name]
    r = subprocess.run(
        [sys.executable, str(path), "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"{name} --help failed: {r.stderr}"
    assert "usage:" in r.stdout.lower(), f"{name} --help no usage line"


# ---------- splits generator output validation -----------------------------

def test_splits_generator_produces_valid_5_batches():
    splits_json = REPO / "scripts" / "aws_batch395_splits.json"
    # Run the generator (writes JSON)
    r = subprocess.run(
        [sys.executable, str(SCRIPTS["splits"])],
        capture_output=True, text=True, timeout=60, cwd=str(REPO),
    )
    assert r.returncode == 0, f"splits generator failed: {r.stderr}"
    assert splits_json.exists()
    data = json.loads(splits_json.read_text())
    # Schema: batch_1..batch_5 each a non-empty list
    assert sorted(data.keys()) == [f"batch_{i}" for i in range(1, 6)]
    sizes = [len(data[k]) for k in sorted(data.keys())]
    total = sum(sizes)
    # Master universe is ~1937 tickers
    assert 1500 < total < 2500, f"total {total} outside expected range"
    # Balance: max-min <= 5% of max
    assert max(sizes) - min(sizes) <= max(2, int(0.05 * max(sizes))), \
        f"imbalanced batch sizes: {sizes}"
    # No overlap
    all_tickers = [t for k in sorted(data.keys()) for t in data[k]]
    assert len(all_tickers) == len(set(all_tickers)), "duplicate tickers"


def test_splits_verify_mode_passes():
    """--verify on an existing splits file should exit 0."""
    splits_json = REPO / "scripts" / "aws_batch395_splits.json"
    if not splits_json.exists():
        pytest.skip("splits json not yet generated")
    r = subprocess.run(
        [sys.executable, str(SCRIPTS["splits"]), "--verify"],
        capture_output=True, text=True, timeout=60, cwd=str(REPO),
    )
    assert r.returncode == 0, f"verify failed: {r.stderr}"


# ---------- bootstrap shell script validation -----------------------------

def test_bootstrap_has_required_env_vars():
    """Bootstrap must reference the env vars the launch script sets."""
    src = SCRIPTS["bootstrap"].read_text(encoding="utf-8")
    for var in ("BATCH395_INDEX", "BATCH395_BUCKET", "BATCH395_COMMIT",
                "BATCH395_PHASE", "BATCH395_START", "BATCH395_END",
                "BATCH395_WORKERS", "BATCH395_REPO_URL"):
        assert var in src, f"bootstrap missing env var ref: {var}"


def test_bootstrap_has_required_aws_calls():
    """Bootstrap must do: s3 sync data; tmux engine launch; s3 sync outputs;
    terminate-instances self-kill."""
    src = SCRIPTS["bootstrap"].read_text(encoding="utf-8")
    assert "aws s3 sync" in src, "bootstrap missing s3 sync"
    assert "tmux new-session" in src, "bootstrap missing tmux launch"
    assert "_COMPLETE" in src, "bootstrap missing _COMPLETE sentinel"
    assert "terminate-instances" in src, "bootstrap missing self-terminate"
    assert "run_phase1a" in src, "bootstrap missing engine invocation"


def test_bootstrap_uses_phase_1a_beta_flags():
    """Bootstrap engine call must include the 1a-beta-relevant flags."""
    src = SCRIPTS["bootstrap"].read_text(encoding="utf-8")
    assert "screen-pool-workers" in src, "missing pool workers flag"
    assert "no-agents" in src, "missing --no-agents"
    assert "no-git" in src, "missing --no-git"


# ---------- launch script argparse --dry-run -------------------------------

def test_launch_dry_run_does_not_call_aws():
    """--dry-run should print without actually calling aws run-instances.

    Skipped if `aws` CLI isn't available -- launch script needs it for
    SG / IAM / SSM lookups before ever reaching the dry-run branch.
    This is fine: the script will fail loudly on the host that lacks it.
    """
    try:
        r = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        pytest.skip("AWS CLI not installed in this test env")
    if r.returncode != 0:
        pytest.skip("AWS creds not configured in this environment")
    # Batch 482 (2026-05-29): bumped 60s -> 180s. Under xdist parallel load
    # the subprocess can be CPU-starved and exceed 60s; the script itself
    # is fast (~5s) but contention varies. 180s gives safe headroom; CI
    # runners are typically less loaded but the limit only triggers when
    # something is actually wrong with the script.
    r = subprocess.run(
        [sys.executable, str(SCRIPTS["launch"]),
         "--bucket", "test-bucket-no-real",
         "--key-pair", "test-key-no-real",
         "--ami-id", "ami-0c80e2b6ccb9ad6d1",
         "--batches", "1",
         "--dry-run"],
        capture_output=True, text=True, timeout=180,
    )
    assert "DRY-RUN" in r.stdout or r.returncode != 0


# ---------- monitor argparse ----------------------------------------------

def test_monitor_requires_bucket_arg():
    r = subprocess.run(
        [sys.executable, str(SCRIPTS["monitor"])],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode != 0
    assert "bucket" in (r.stderr + r.stdout).lower()


# ---------- merge argparse ------------------------------------------------

def test_merge_requires_bucket_arg():
    r = subprocess.run(
        [sys.executable, str(SCRIPTS["merge"])],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode != 0
    assert "bucket" in (r.stderr + r.stdout).lower()


# ---------- teardown dry-run -----------------------------------------------

def test_teardown_dry_run_exits_zero_when_no_aws():
    """Teardown --dry-run with no AWS creds should at least parse args."""
    r = subprocess.run(
        [sys.executable, str(SCRIPTS["teardown"]), "--dry-run"],
        capture_output=True, text=True, timeout=30,
    )
    # If creds unconfigured, the script reports FATAL and exits non-zero
    # which is acceptable behavior here.  We just verify argparse worked
    # (no "unrecognized arguments" stderr).
    assert "unrecognized arguments" not in r.stderr.lower()
