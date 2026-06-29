"""B1067 monitor 4-fix batch pyramid tests.

# Source: Council 167 RECOMMEND Option-4 OPTION-1 + Option-4 per
# CHECKLIST #77 + #115 + owner directive 2026-06-28 "1. Phase 3 blocked
# till the above resolved. 4 approved too" + meta-criticism on
# adversarial review gaps.

FIX 1 G-IMPL: monitor.py stdout line-buffering (was block-buffered ->
  0-byte monitor.log)
FIX 2 A1-PROMOTION: A1 mass-anomaly (>50pct expected-firing) now HALT
  (was WARN-only)
FIX 3 E-NEW: silent-strategy floor HALT at sim_day >= 500
FIX 4 F-NEW: per-strategy regime coverage LOG-MEDIUM
"""
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MONITOR_PATH = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"
LAUNCH_SCRIPT = REPO / "scripts" / "launch_r5_master_4y_v2.sh"


def _load_monitor():
    spec = importlib.util.spec_from_file_location("monitor", MONITOR_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_b1067_fix1_g_impl_reconfigure_line_buffering():
    """B1067 FIX 1 G-IMPL: monitor.py must call sys.stdout.reconfigure
    with line_buffering=True so prints flush incrementally."""
    content = MONITOR_PATH.read_text()
    assert "sys.stdout.reconfigure" in content, (
        "B1067 FIX 1: monitor.py must call sys.stdout.reconfigure for "
        "line-buffered output (avoids 0-byte log on PASS path)"
    )
    assert "line_buffering=True" in content, (
        "B1067 FIX 1: must pass line_buffering=True to reconfigure"
    )


def test_b1067_fix1_launch_script_uses_python_u():
    """B1067 FIX 1 G-IMPL: launch script must invoke monitor with -u
    (unbuffered) flag as belt-and-suspenders for the reconfigure."""
    content = LAUNCH_SCRIPT.read_text()
    assert "python -u scripts/b1019_phase_1_runtime_monitor.py" in content, (
        "B1067 FIX 1: launch script must use 'python -u' for monitor "
        "invocation (forces unbuffered stdio)"
    )


def test_b1067_fix2_a1_promotion_halt_threshold_in_classify_tier():
    """B1067 FIX 2 A1-PROMOTION: _classify_tier must HALT when
    a1_anom > 0.5 * expected_firing_count."""
    content = MONITOR_PATH.read_text()
    assert "0.5 * a1_expected" in content, (
        "B1067 FIX 2: _classify_tier must compute 50pct threshold of "
        "expected_firing_count for A1 mass-anomaly HALT"
    )
    assert "a1_expected = a1.get(" in content, (
        "B1067 FIX 2: must read expected_firing_count from a1 dict"
    )


def test_b1067_fix2_a1_check_emits_expected_firing_count():
    """B1067 FIX 2: _check_a1_fire_rate must emit expected_firing_count
    in its result dict so _classify_tier can compute mass-anomaly ratio."""
    content = MONITOR_PATH.read_text()
    assert 'result["expected_firing_count"]' in content, (
        "B1067 FIX 2: A1 check must populate expected_firing_count"
    )
    assert 'result["silent_with_expectation"]' in content, (
        "B1067 FIX 2: A1 check must populate silent_with_expectation"
    )


def test_b1067_fix3_e_new_silent_floor_function_exists():
    """B1067 FIX 3 E-NEW: _check_e_new_silent_floor function must exist."""
    mod = _load_monitor()
    assert hasattr(mod, "_check_e_new_silent_floor"), (
        "B1067 FIX 3: _check_e_new_silent_floor function must exist"
    )


def test_b1067_fix3_e_new_halts_above_threshold():
    """B1067 FIX 3 E-NEW: silent_pct > 50pct at sim_day >= 500 must HALT."""
    mod = _load_monitor()
    # Synthesize a1 dict with mass silence
    a1 = {"expected_firing_count": 88, "silent_with_expectation": 87}
    e_result = mod._check_e_new_silent_floor(
        a1, current_day=600, silent_floor_day=500,
        silent_pct_threshold=0.5
    )
    assert e_result["halt"] is True, (
        "B1067 FIX 3: 87/88 silent at sim_day 600 must HALT"
    )


def test_b1067_fix3_e_new_no_halt_below_floor():
    """B1067 FIX 3 E-NEW: same mass silence at sim_day < 500 must NOT HALT
    (engine may still be in early ticker rotation)."""
    mod = _load_monitor()
    a1 = {"expected_firing_count": 88, "silent_with_expectation": 87}
    e_result = mod._check_e_new_silent_floor(
        a1, current_day=400, silent_floor_day=500,
        silent_pct_threshold=0.5
    )
    assert e_result["halt"] is False, (
        "B1067 FIX 3: sim_day 400 < 500 floor must NOT HALT"
    )


def test_b1067_fix4_f_new_regime_coverage_function_exists():
    """B1067 FIX 4 F-NEW: _check_f_new_regime_coverage function exists."""
    mod = _load_monitor()
    assert hasattr(mod, "_check_f_new_regime_coverage"), (
        "B1067 FIX 4: _check_f_new_regime_coverage function must exist"
    )


def test_b1067_fix4_f_new_log_medium_only_no_halt():
    """B1067 FIX 4 F-NEW: regime coverage gaps must trigger LOG-MEDIUM
    not HALT (per owner LOW priority classification)."""
    mod = _load_monitor()
    a1 = {"anomaly_count": 0, "expected_firing_count": 0}
    b2 = {"violations": [], "status": "OK"}
    d1 = {"cells_completed": 0, "total_cells": 100, "pct_cells": 0,
          "eta_min": 0, "runtime_min": 0}
    f_with_gaps = {"regime_gaps": 5}
    tier = mod._classify_tier(a1, b2, d1, e_new={"halt": False},
                              f_new=f_with_gaps)
    assert tier == "LOG-MEDIUM", (
        f"B1067 FIX 4: regime gaps with no other issues must be LOG-MEDIUM, got {tier}"
    )


def test_b1067_format_checkpoint_includes_e_f_metrics():
    """B1067: _format_checkpoint_line must emit e_silent_pct + f_regime_gaps
    for monitor visibility."""
    content = MONITOR_PATH.read_text()
    assert "e_silent_pct=" in content, (
        "B1067: checkpoint line must include e_silent_pct metric"
    )
    assert "f_regime_gaps=" in content, (
        "B1067: checkpoint line must include f_regime_gaps metric"
    )
    assert "a1_expected_firing=" in content, (
        "B1067: checkpoint line must include a1_expected_firing metric"
    )


def test_b1067_lineage_documented():
    """B1067: PIVOT lineage + Council 167 referenced in monitor.py."""
    content = MONITOR_PATH.read_text()
    assert "B1067" in content, "B1067 batch lineage must be referenced"
    assert "Council 167" in content, "Council 167 must be referenced"
    assert "FIX 1 G-IMPL" in content, "FIX 1 G-IMPL must be lineage-tagged"
    assert "FIX 2 A1-PROMOTION" in content, "FIX 2 must be lineage-tagged"
    assert "FIX 3 E-NEW" in content, "FIX 3 must be lineage-tagged"
    assert "FIX 4 F-NEW" in content, "FIX 4 must be lineage-tagged"


def test_b1067_classify_tier_a1_mass_anomaly_halt_integration():
    """B1067 integration: A1 mass-anomaly (60 of 88 expected = 68pct) HALTs."""
    mod = _load_monitor()
    a1 = {"anomaly_count": 60, "expected_firing_count": 88,
          "silent_with_expectation": 60}
    b2 = {"violations": [], "status": "OK"}
    d1 = {"cells_completed": 100, "total_cells": 5694, "pct_cells": 0.018,
          "eta_min": 0, "runtime_min": 5}
    e_new = {"halt": False}
    f_new = {"regime_gaps": 0}
    # B1070 F-9.2 update: A1-PROMOTION HALT now gated on
    # current_day >= 200; pass sim_day=250 to assert HALT fires.
    # B1072 PIVOT #40 update: also requires active_tickers >= 1000;
    # pin Master-scale 1929 to isolate B1067 FIX 2 gate semantics.
    tier = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                              current_day=250, active_tickers=1929)
    assert tier == "HALT-CRITICAL", (
        f"B1067 FIX 2 (post-B1070 F-9.2 + B1072 PIVOT #40): 60/88 anomalies "
        f"(68pct > 50pct) at sim_day 250 + active_tickers 1929 must "
        f"HALT-CRITICAL, got {tier}"
    )


def test_b1067_classify_tier_a1_below_threshold_warn_not_halt():
    """B1067 FIX 2 boundary: 40 of 88 (45pct) anomalies = WARN not HALT."""
    mod = _load_monitor()
    a1 = {"anomaly_count": 40, "expected_firing_count": 88,
          "silent_with_expectation": 40}
    b2 = {"violations": [], "status": "OK"}
    d1 = {"cells_completed": 100, "total_cells": 5694, "pct_cells": 0.018,
          "eta_min": 0, "runtime_min": 5}
    e_new = {"halt": False}
    f_new = {"regime_gaps": 0}
    tier = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new)
    assert tier == "WARN-HIGH", (
        f"B1067 FIX 2: 40/88 (45pct < 50pct threshold) must WARN-HIGH, got {tier}"
    )
