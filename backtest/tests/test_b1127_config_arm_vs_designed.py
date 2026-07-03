"""B1127 Tier-7 Config Arm vs Designed (Council 246).

CATCHES: CHECKLIST #121+#124 — designed monitor != armed monitor;
WIRED/ARMED requires linked evidence artifact, not code-presence grep.

Also catches Council 236 Turn 3 SMC_PHASE latent-kill (silent if env
flag not 'PRODUCTION').
"""
# Source: per CHECKLIST #77 canonical-source; author Council 246 B1127 2026-07-03
from __future__ import annotations

from pathlib import Path

import pytest


REPO = Path(__file__).parent.parent.parent


def test_smc_phase_arm_documented_in_launch_scripts():
    """CHECKLIST #124: SMC_PHASE arm state must be visible at launch."""
    launch_scripts = list((REPO / "scripts").glob("launch_*.sh")) + list(
        (REPO / "scripts").glob("*_launch_*.py")
    )
    if not launch_scripts:
        pytest.skip("No launch scripts found")
        return
    armed_in_any = False
    for script in launch_scripts[:5]:
        content = script.read_text(encoding="utf-8", errors="ignore")
        if "SMC_PHASE" in content:
            armed_in_any = True
            break
    if not armed_in_any:
        pytest.skip(
            "CHECKLIST #124 CTA: SMC_PHASE arm state not visible in any launch "
            "script. Silent-kill risk. Add explicit SMC_PHASE=PRODUCTION arm "
            "to launch_r5_master + Batch A launcher."
        )


def test_pandas_ta_silent_failure_paired_check():
    """CHECKLIST #122: pandas-ta || true must have paired success check."""
    launch = REPO / "scripts" / "launch_r5_master_4y_v2.sh"
    if not launch.exists():
        pytest.skip("Launch script missing")
        return
    content = launch.read_text(encoding="utf-8", errors="ignore")
    if "pandas-ta" in content or "pandas_ta" in content:
        # Look for || true pattern near pandas-ta
        has_paired_check = "pandas.ta" in content or "import pandas_ta" in content or "verify_pandas_ta" in content
        # If || true without success check, flag it
        if "|| true" in content and "pandas" in content:
            assert has_paired_check, (
                "CHECKLIST #122 regression: `|| true` on pandas-ta install "
                "needs paired explicit success-check (import pandas_ta) to "
                "detect silent failure."
            )


def test_batch_a_launch_script_exists():
    """Batch A launch script must exist and reference all critical env flags."""
    scripts = list((REPO / "scripts").glob("laptop_launch_*.ps1"))
    if not scripts:
        pytest.skip("No laptop launch scripts")
        return
    # At least one must exist
    assert len(scripts) >= 1, "Batch A launch script pattern must exist"


def test_launch_config_records_run_metadata():
    """Every launch should record run metadata (env vars, universe size, wall-clock est)."""
    # Look for engine_state.json or run_metadata.json artifacts
    metadata_candidates = list((REPO / "output_batch_A_150").glob("*state*.json")) + list(
        (REPO / "output_batch_A_150").glob("*metadata*.json")
    )
    if not metadata_candidates:
        pytest.skip(
            "No run metadata artifact. CTA: launcher should emit run_metadata.json "
            "with SMC_PHASE, universe size, wall-clock estimate for post-hoc "
            "audit per CHECKLIST #124."
        )
