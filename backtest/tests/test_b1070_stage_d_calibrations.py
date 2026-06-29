"""B1070 Stage D Sub-B 2 HIGH calibrations pyramid tests.

# Source: Council 172/175/179 Sub-B per CHECKLIST #77 + #115 + owner
# directive 2026-06-29 'Proceed council this'.

F-9.2: A1-PROMOTION HALT-CRITICAL gated on current_day >= 200 to avoid
  spurious false positives in first 200 sim_days
F-8.1: --baseline-window-start/end + --phase-window-start/end args +
  regime-mix drift warning when >2 years
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MONITOR_PATH = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"
LAUNCH_SCRIPT = REPO / "scripts" / "launch_r5_master_4y_v2.sh"


def _load_monitor():
    spec = importlib.util.spec_from_file_location("monitor", MONITOR_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================ F-9.2 sim_day gate ===========================

def test_b1070_f_9_2_a1_promotion_no_halt_below_sim_day_200():
    """B1070 F-9.2: A1 mass-anomaly (60 of 88 = 68pct) at sim_day 100
    must NOT HALT (premature; strategies haven't accumulated fires)."""
    mod = _load_monitor()
    a1 = {"anomaly_count": 60, "expected_firing_count": 88,
          "silent_with_expectation": 60}
    b2 = {"violations": [], "status": "OK"}
    d1 = {"cells_completed": 50, "total_cells": 5694, "pct_cells": 0.009,
          "eta_min": 0, "runtime_min": 2}
    e_new = {"halt": False}
    f_new = {"regime_gaps": 0}
    tier = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                              current_day=100)
    assert tier == "WARN-HIGH", (
        f"B1070 F-9.2 REGRESSION: A1 mass-anomaly at sim_day 100 (<200) "
        f"must WARN-HIGH (not HALT-CRITICAL), got {tier}"
    )


def test_b1070_f_9_2_a1_promotion_halt_at_sim_day_200():
    """B1070 F-9.2: A1 mass-anomaly at sim_day >= 200 must HALT.

    B1072 PIVOT #40 update: also requires active_tickers >= 1000;
    fixture pins Master-scale (1929) to isolate F-9.2 gate semantics."""
    mod = _load_monitor()
    a1 = {"anomaly_count": 60, "expected_firing_count": 88,
          "silent_with_expectation": 60}
    b2 = {"violations": [], "status": "OK"}
    d1 = {"cells_completed": 100, "total_cells": 5694, "pct_cells": 0.018,
          "eta_min": 0, "runtime_min": 10}
    e_new = {"halt": False}
    f_new = {"regime_gaps": 0}
    tier = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                              current_day=250, active_tickers=1929)
    assert tier == "HALT-CRITICAL", (
        f"B1070 F-9.2: A1 mass-anomaly at sim_day 250 (>=200) + "
        f"active_tickers=1929 (Master scale) must HALT-CRITICAL, got {tier}"
    )


def test_b1070_f_9_2_a1_promotion_boundary_at_sim_day_199():
    """B1070 F-9.2 boundary: sim_day 199 still WARN, sim_day 200 HALT.

    B1072 PIVOT #40 update: pin active_tickers=1929 (Master scale) to
    isolate F-9.2 sim_day gate semantics from F-40 universe-size gate."""
    mod = _load_monitor()
    a1 = {"anomaly_count": 60, "expected_firing_count": 88,
          "silent_with_expectation": 60}
    b2 = {"violations": [], "status": "OK"}
    d1 = {"cells_completed": 100, "total_cells": 5694, "pct_cells": 0.018,
          "eta_min": 0, "runtime_min": 10}
    e_new = {"halt": False}
    f_new = {"regime_gaps": 0}
    tier_199 = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                                  current_day=199, active_tickers=1929)
    tier_200 = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                                  current_day=200, active_tickers=1929)
    assert tier_199 == "WARN-HIGH", f"sim_day 199 must WARN, got {tier_199}"
    assert tier_200 == "HALT-CRITICAL", f"sim_day 200 must HALT, got {tier_200}"


def test_b1070_f_9_2_lineage_documented():
    """B1070 F-9.2: lineage in monitor.py."""
    content = MONITOR_PATH.read_text()
    assert "B1070 F-9.2 FIX" in content, (
        "B1070 F-9.2: lineage comment required in monitor.py"
    )
    assert "current_day >= 200" in content, (
        "B1070 F-9.2: sim_day 200 gate must be in monitor.py"
    )


# ============================ F-8.1 regime-drift args ======================

def test_b1070_f_8_1_baseline_window_args_present():
    """B1070 F-8.1: --baseline-window-start/end args must be added."""
    content = MONITOR_PATH.read_text()
    assert "--baseline-window-start" in content, (
        "B1070 F-8.1: monitor must accept --baseline-window-start arg"
    )
    assert "--baseline-window-end" in content, (
        "B1070 F-8.1: monitor must accept --baseline-window-end arg"
    )
    assert "--phase-window-start" in content, (
        "B1070 F-8.1: monitor must accept --phase-window-start arg"
    )
    assert "--phase-window-end" in content, (
        "B1070 F-8.1: monitor must accept --phase-window-end arg"
    )


def test_b1070_f_8_1_regime_drift_warning_string_present():
    """B1070 F-8.1: regime-drift warning string + B1072 deferral
    documented."""
    content = MONITOR_PATH.read_text()
    assert "DEFER-IF-MIXED-REGIME" in content, (
        "B1070 F-8.1: regime-drift warning string DEFER-IF-MIXED-REGIME "
        "must be present"
    )
    assert "B1072" in content, (
        "B1070 F-8.1: warning must reference B1072 re-measurement deferral"
    )


def test_b1070_f_8_1_launch_script_passes_window_args():
    """B1070 F-8.1: launch script must pass --baseline-window-start/end +
    --phase-window-start/end to monitor."""
    content = LAUNCH_SCRIPT.read_text()
    assert "--baseline-window-start 2020-01-01" in content, (
        "B1070 F-8.1: launch script must pass --baseline-window-start"
    )
    assert "--phase-window-start" in content, (
        "B1070 F-8.1: launch script must pass --phase-window-start"
    )


def test_b1070_f_8_1_drift_warning_emits_runtime():
    """B1070 F-8.1: invoke monitor with Phase window differing by >2yr
    and assert WARNING emitted. Monitor enters poll loop; capture early
    stdout via timeout-with-capture."""
    try:
        result = subprocess.run(
            [sys.executable, str(MONITOR_PATH),
             "--engine-state", "/nonexistent/path.json",
             "--trade-log", "/nonexistent/path.csv",
             "--baseline-window-start", "2018-01-01",
             "--baseline-window-end", "2024-01-01",
             "--phase-window-start", "2022-05-05",
             "--phase-window-end", "2026-05-05",
             "--poll-seconds", "1"],
            capture_output=True, text=True, timeout=5,
        )
        combined = result.stdout + result.stderr
    except subprocess.TimeoutExpired as e:
        # Expected: monitor entered poll loop; capture what was printed
        # before timeout (the drift warning prints at startup).
        # text=True means stdout/stderr are str (not bytes); no decode needed.
        combined = (e.stdout or "") + (e.stderr or "")
    assert "DEFER-IF-MIXED-REGIME" in combined or "B1070 F-8.1" in combined, (
        f"B1070 F-8.1: regime-drift warning must emit when windows differ "
        f">2yr. Captured: {combined[:1000]!r}"
    )


def test_b1070_stage_d_lineage():
    """B1070 Stage D: both F-9.2 + F-8.1 lineage comments present."""
    content = MONITOR_PATH.read_text()
    assert "B1070 F-9.2 FIX" in content, "F-9.2 lineage missing"
    assert "B1070 F-8.1 FIX" in content, "F-8.1 lineage missing"
    assert "Council 179" in content, "Council 179 attribution missing"
