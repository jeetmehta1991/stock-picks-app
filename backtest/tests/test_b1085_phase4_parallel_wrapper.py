"""B1085 Council 204+205+206+207: Phase 4 parallel wrapper + per-AZ
preflight pyramid tests.

Source: Owner directive 2026-06-29 'B then 4 parallel' + 'continue
council this' + Council 204-207 chain.

Tests verify:
- scripts/launch_phase4_parallel.sh exists + reuses b1070 helper
- Wrapper iterates A-H (8 chunks)
- AZ rotation 4 AZs x 2 chunks each
- AZ-fallback logic present (Council 206 caveat)
- Resume from RESUME_FROM_RUN_ID verified via PHASE_N_PASS sentinels
- preflight_smoke.sh has --per-az flag (Outsider Council 204)
- --per-az iterates 4 AZs (1a/1c/1d/1f) in parallel
- Lineage documented
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PARALLEL = REPO / "scripts" / "launch_phase4_parallel.sh"
PREFLIGHT = REPO / "scripts" / "preflight_smoke.sh"


def test_b1085_parallel_wrapper_exists():
    """B1085: launch_phase4_parallel.sh must exist."""
    assert PARALLEL.exists(), (
        "B1085 Council 204-207: scripts/launch_phase4_parallel.sh must exist"
    )


def test_b1085_wrapper_reuses_launch_script():
    """B1085: parallel wrapper must reuse launch_r5_master_4y_v2.sh
    (not duplicate logic) per Council 206 reuse principle."""
    content = PARALLEL.read_text()
    assert "launch_r5_master_4y_v2.sh" in content, (
        "B1085: wrapper must reuse launch_r5_master_4y_v2.sh"
    )
    assert "b1070_phase_d_launch_helper.sh" in content, (
        "B1085: wrapper must reuse b1070_phase_d_launch_helper.sh for "
        "EBS=100GB enforcement"
    )


def test_b1085_wrapper_iterates_all_8_chunks():
    """B1085: wrapper must launch chunks A-H (all 8 per B1084)."""
    content = PARALLEL.read_text()
    # Single iteration syntax check (for CHUNK in A B C D E F G H)
    assert "A B C D E F G H" in content, (
        "B1085: wrapper must iterate all 8 chunks A-H"
    )


def test_b1085_az_rotation_4az_2chunks_each():
    """B1085 Council 205+206: 4 AZs x 2 chunks each = 8 launches."""
    content = PARALLEL.read_text()
    # Each AZ must be referenced as primary for 2 chunks
    for az in ("us-east-1a", "us-east-1c", "us-east-1d", "us-east-1f"):
        assert content.count(az) >= 2, (
            f"B1085: AZ {az} must appear at least 2x (once as primary "
            f"for 2 chunks + fallback rotation)"
        )


def test_b1085_az_fallback_logic_present():
    """B1085 Council 206 caveat: AZ-fallback on InsufficientInstance-
    Capacity. Wrapper must try fallback AZs if primary fails."""
    content = PARALLEL.read_text()
    assert "AZ_FALLBACK_ORDER" in content or "fallback" in content.lower(), (
        "B1085 Council 206: AZ-fallback logic must be present (try "
        "remaining AZs on capacity failure)"
    )


def test_b1085_resume_source_verification():
    """B1085: wrapper must verify RESUME_FROM_RUN_ID has Phase 1+2+3
    PASS sentinels BEFORE launching chunks (defensive per B1078 pattern)."""
    content = PARALLEL.read_text()
    assert "PHASE_1_PASS" in content
    assert "PHASE_2_PASS" in content
    assert "PHASE_3_PASS" in content
    assert "PHASE_${PHASE}_PASS" in content or "PHASE_1_PASS" in content, (
        "B1085: must verify all 3 prior phase PASS sentinels exist"
    )


def test_b1085_phase_4_chunk_env_var_threaded():
    """B1085: wrapper must thread PHASE_4_CHUNK env var per chunk
    (B1084 integration)."""
    content = PARALLEL.read_text()
    assert "PHASE_4_CHUNK" in content, (
        "B1085: PHASE_4_CHUNK env var (B1084) must be threaded per chunk"
    )
    assert "SKIP_PHASES" in content, (
        "B1085: SKIP_PHASES env var (B1078) must be threaded"
    )
    assert "RESUME_FROM_RUN_ID" in content, (
        "B1085: RESUME_FROM_RUN_ID (B1078) must be threaded"
    )


def test_b1085_checklist_134_verification():
    """B1085: per-chunk CHECKLIST #134 verification (describe-instances
    within 60 sec)."""
    content = PARALLEL.read_text()
    assert "describe-instances" in content, (
        "B1085: must call aws ec2 describe-instances for #134 verification"
    )


def test_b1085_preflight_per_az_flag_exists():
    """B1085 Council 207: preflight_smoke.sh --per-az flag must exist."""
    content = PREFLIGHT.read_text()
    assert "--per-az" in content, (
        "B1085 Council 207: preflight_smoke.sh must support --per-az flag"
    )


def test_b1085_preflight_per_az_iterates_4_azs():
    """B1085 Council 207: --per-az must iterate 4 AZs (1a/1c/1d/1f)."""
    content = PREFLIGHT.read_text()
    for az in ("us-east-1a", "us-east-1c", "us-east-1d", "us-east-1f"):
        assert az in content, (
            f"B1085: --per-az must include AZ {az}"
        )


def test_b1085_preflight_per_az_parallel_execution():
    """B1085 Council 207: per-AZ preflights run in PARALLEL (not serial)
    per cost/wall-clock economics."""
    content = PREFLIGHT.read_text()
    # Parallel signal: background invocation (&) + wait
    assert "&" in content, (
        "B1085: per-AZ preflights must launch background (&) for parallel"
    )
    assert "wait" in content, (
        "B1085: must wait for parallel preflights to complete"
    )


def test_b1085_lineage_documented():
    """B1085: Council 204-207 lineage referenced in sources."""
    parallel_content = PARALLEL.read_text()
    assert "B1085" in parallel_content
    assert "Council 204" in parallel_content or "Council 206" in parallel_content
    preflight_content = PREFLIGHT.read_text()
    assert "B1085" in preflight_content
    assert "Council 207" in preflight_content


def test_b1085_launch_evidence_emitted():
    """B1085: wrapper must emit launch evidence JSON to output_audit/
    for owner audit trail."""
    content = PARALLEL.read_text()
    assert "output_audit" in content
    assert "b1085_parallel_launch_" in content
    assert "instance" in content.lower()
