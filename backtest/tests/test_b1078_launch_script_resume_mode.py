"""B1078 Council 194 Option 1: launch_r5_master_4y_v2.sh resume-mode tests.

Source: Council 194 RECOMMEND Option 1 MODIFY-LAUNCH-SCRIPT-RESUME-MODE
post-B1077 2nd consecutive spot interruption. First REAL use of B1076
resume infra.

Tests verify launch script wiring:
- RESUME_FROM_RUN_ID env var threaded through user-data
- SKIP_PHASES env var threaded through user-data
- run_phase function gates skip-mode on PHASE_N_PASS sentinel existence
- run_phase function downloads checkpoint when prior status='running'
- --resume-from-checkpoint passed to engine when checkpoint present
- Defensive: no skip if sentinel missing (falls through to fresh run)
- Backward compat: empty resume vars = original B1075 behavior
"""
from __future__ import annotations

from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
LAUNCH_SCRIPT = REPO / "scripts" / "launch_r5_master_4y_v2.sh"


def test_b1078_resume_env_vars_in_user_data():
    """B1078: RESUME_FROM_RUN_ID + SKIP_PHASES must be threaded into
    user-data so AWS instance sees them."""
    content = LAUNCH_SCRIPT.read_text()
    assert 'RESUME_FROM_RUN_ID="${RESUME_FROM_RUN_ID:-}"' in content, (
        "B1078: RESUME_FROM_RUN_ID env var must be threaded into user-data"
    )
    assert 'SKIP_PHASES="${SKIP_PHASES:-}"' in content, (
        "B1078: SKIP_PHASES env var must be threaded into user-data"
    )
    assert 'export RESUME_FROM_RUN_ID SKIP_PHASES' in content, (
        "B1078: both env vars must be exported for run_phase function"
    )


def test_b1078_skip_phases_logic_gated_on_pass_sentinel():
    """B1078 defensive: skip phase ONLY if prior PHASE_N_PASS sentinel
    exists in RESUME_FROM_RUN_ID S3 prefix."""
    content = LAUNCH_SCRIPT.read_text()
    # Look for the defensive sentinel check before skip
    assert 'aws s3 ls "s3://\\${BUCKET}/\\${RESUME_FROM_RUN_ID}/PHASE_\\${PHASE_NUM}_PASS"' in content, (
        "B1078: SKIP_PHASES must verify PHASE_N_PASS sentinel exists "
        "before skipping (defensive per memory rule)"
    )


def test_b1078_skip_phases_syncs_prior_output_dir():
    """B1078: when phase skipped, must sync prior output_phase_N/ to
    local PHASE_DIR so downstream phases can read it."""
    content = LAUNCH_SCRIPT.read_text()
    assert 'aws s3 sync "s3://\\${BUCKET}/\\${RESUME_FROM_RUN_ID}/\\${PHASE_DIR}/" "\\${PHASE_DIR}/"' in content, (
        "B1078: skipped phase must sync prior S3 output_phase_N/ to local "
        "PHASE_DIR (downstream phases depend on artifacts)"
    )


def test_b1078_resume_checkpoint_status_running_check():
    """B1078: resume-checkpoint mode triggers ONLY if prior
    engine_state.status='running' (NOT 'complete')."""
    content = LAUNCH_SCRIPT.read_text()
    assert '"status": "running"' in content, (
        "B1078: resume mode must check status='running' (not complete)"
    )
    assert 'PRIOR_STATE_JSON' in content, (
        "B1078: must inspect prior engine_state.json before resume"
    )


def test_b1078_resume_arg_passed_to_engine():
    """B1078: --resume-from-checkpoint must be threaded to run_phase1a
    invocation when checkpoint detected."""
    content = LAUNCH_SCRIPT.read_text()
    assert 'RESUME_ARG="--resume-from-checkpoint \\${PHASE_DIR}"' in content, (
        "B1078: RESUME_ARG must format --resume-from-checkpoint with "
        "PHASE_DIR path"
    )
    # Must be in the python invocation line
    assert '\\${RESUME_ARG}' in content, (
        "B1078: \\${RESUME_ARG} must be passed to python invocation"
    )


def test_b1078_resume_arg_in_setsid_invocation():
    """B1078: RESUME_ARG variable must appear in the setsid python
    run_phase1a line."""
    content = LAUNCH_SCRIPT.read_text()
    # Find the setsid python line and assert RESUME_ARG appears
    for line in content.splitlines():
        if 'setsid python -m backtest.run_phase1a' in line:
            assert '\\${RESUME_ARG}' in line, (
                "B1078: setsid python run_phase1a line must include "
                f"\\${{RESUME_ARG}}; got: {line[:200]}"
            )
            return
    raise AssertionError(
        "B1078: setsid python -m backtest.run_phase1a invocation not found"
    )


def test_b1078_skip_phases_emits_pass_sentinel():
    """B1078: skipped phase must emit PHASE_N_PASS sentinel locally so
    downstream phases + monitor see PASS state."""
    content = LAUNCH_SCRIPT.read_text()
    assert 'PHASE_\\${PHASE_NUM}_PASS \\$(date -u +%Y-%m-%dT%H:%M:%SZ) skipped=B1078_resume' in content, (
        "B1078: skipped phase must emit PHASE_N_PASS sentinel with "
        "skipped=B1078_resume marker"
    )


def test_b1078_resume_mode_args_sentinel_emitted():
    """B1078: when resume-from-checkpoint engaged, emit
    PHASE_N_RESUME_ARGS sentinel for observability."""
    content = LAUNCH_SCRIPT.read_text()
    assert 'PHASE_\\${PHASE_NUM}_RESUME_ARGS' in content, (
        "B1078: resume-engaged phase must emit PHASE_N_RESUME_ARGS sentinel"
    )


def test_b1078_backward_compat_no_resume_vars():
    """B1078: empty RESUME_FROM_RUN_ID + SKIP_PHASES => original B1075
    behavior preserved (no resume logic engages)."""
    content = LAUNCH_SCRIPT.read_text()
    # The skip-mode block must gate on BOTH vars being non-empty
    assert 'if [ -n "\\${SKIP_PHASES:-}" ] && [ -n "\\${RESUME_FROM_RUN_ID:-}" ]' in content, (
        "B1078: skip-mode must require BOTH SKIP_PHASES + RESUME_FROM_RUN_ID "
        "non-empty (backward-compat when neither set)"
    )
    # Resume-checkpoint block must gate on RESUME_FROM_RUN_ID non-empty
    assert 'if [ -n "\\${RESUME_FROM_RUN_ID:-}" ] && \\\\' in content, (
        "B1078: resume-checkpoint mode must require RESUME_FROM_RUN_ID "
        "non-empty (backward-compat when not set)"
    )


def test_b1078_skip_falls_through_on_sentinel_missing():
    """B1078: if SKIP_PHASES requested but PHASE_N_PASS missing in
    RESUME_FROM_RUN_ID, fall through to fresh run (do NOT halt or skip
    incorrectly)."""
    content = LAUNCH_SCRIPT.read_text()
    assert 'PHASE_\\${PHASE_NUM}_SKIP_SENTINEL_MISSING' in content, (
        "B1078: must log skip-fallback when PHASE_N_PASS sentinel missing"
    )
    assert 'running fresh' in content, (
        "B1078: must indicate fresh-run fallback on skip sentinel miss"
    )


def test_b1078_lineage_documented():
    """B1078: Council 194 + Option 1 lineage in script."""
    content = LAUNCH_SCRIPT.read_text()
    assert 'B1078' in content, "B1078 batch lineage must be referenced"
    assert 'Council 194' in content, "Council 194 must be referenced"
    assert 'Option 1' in content, "Council 194 Option 1 designator required"
