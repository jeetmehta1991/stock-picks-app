"""B1072 PIVOT #40 Option F pyramid tests: active_tickers >= 1000 gate
on A1-PROMOTION HALT-CRITICAL.

# Source: Council 184 4/4 RECOMMEND Option F per owner directive
# 2026-06-29 'Approve all council this' + CHECKLIST #115 + #133 + #120 +
# #124 + #128 + feedback_phase_ladder_timing_validation + Phase 2 smoke
# false-positive lesson (B1071 60 of 88 strategies silent at 10-ticker
# Phase 2 scale -> HALT-CRITICAL was real B1019 logic but wrong
# attribution: small-universe noise, not engine bug).

PIVOT #40: A1-PROMOTION HALT-CRITICAL now triple-gated:
  - a1_anom > 0.5 * a1_expected (B1067 FIX 2)
  - current_day >= 200             (B1070 F-9.2)
  - active_tickers >= 1000         (B1072 PIVOT #40 NEW)

Below 1000 active_tickers: WARN-HIGH retained for visibility, no HALT.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MONITOR_PATH = REPO / "scripts" / "b1019_phase_1_runtime_monitor.py"


def _load_monitor():
    spec = importlib.util.spec_from_file_location("monitor", MONITOR_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _mass_anomaly_inputs():
    """A1 mass-anomaly fixture: 60 of 88 expected-firing strategies
    anomalous (68pct, exceeds 50pct B1067 mass-anomaly threshold)."""
    a1 = {"anomaly_count": 60, "expected_firing_count": 88,
          "silent_with_expectation": 60}
    b2 = {"violations": [], "status": "OK"}
    d1 = {"cells_completed": 100, "total_cells": 5694, "pct_cells": 0.018,
          "eta_min": 0, "runtime_min": 10}
    e_new = {"halt": False}
    f_new = {"regime_gaps": 0}
    return a1, b2, d1, e_new, f_new


# =========== Core PIVOT #40 trio: small-vs-large universe at sim_day >= 200 ==

def test_b1072_pivot40_a1_no_halt_below_1000_tickers():
    """B1072 PIVOT #40: A1 mass-anomaly at sim_day 250 + active_tickers=1
    must NOT HALT (Phase 1 NVDA-only scale; too-small universe for
    88-strategy fire-rate baseline to be statistically actionable)."""
    mod = _load_monitor()
    a1, b2, d1, e_new, f_new = _mass_anomaly_inputs()
    tier = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                              current_day=250, active_tickers=1)
    assert tier == "WARN-HIGH", (
        f"B1072 PIVOT #40 REGRESSION: A1 mass-anomaly at sim_day 250 + "
        f"active_tickers=1 must WARN-HIGH (Phase 1 small-universe noise, "
        f"not HALT), got {tier}"
    )


def test_b1072_pivot40_a1_halts_at_1929_tickers_master_scale():
    """B1072 PIVOT #40: A1 mass-anomaly at sim_day 250 + active_tickers=1929
    (Master 1929 ops intersection) MUST HALT-CRITICAL."""
    mod = _load_monitor()
    a1, b2, d1, e_new, f_new = _mass_anomaly_inputs()
    tier = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                              current_day=250, active_tickers=1929)
    assert tier == "HALT-CRITICAL", (
        f"B1072 PIVOT #40: A1 mass-anomaly at sim_day 250 + "
        f"active_tickers=1929 (Master scale) must HALT-CRITICAL, got {tier}"
    )


def test_b1072_pivot40_boundary_active_tickers_999_vs_1000():
    """B1072 PIVOT #40 boundary: active_tickers=999 WARN, =1000 HALT."""
    mod = _load_monitor()
    a1, b2, d1, e_new, f_new = _mass_anomaly_inputs()
    tier_999 = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                                  current_day=250, active_tickers=999)
    tier_1000 = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                                   current_day=250, active_tickers=1000)
    assert tier_999 == "WARN-HIGH", (
        f"B1072 PIVOT #40: active_tickers=999 must WARN-HIGH, got {tier_999}"
    )
    assert tier_1000 == "HALT-CRITICAL", (
        f"B1072 PIVOT #40: active_tickers=1000 must HALT-CRITICAL, "
        f"got {tier_1000}"
    )


# =========== Phase-scale specific (Phase 2 = 10, Phase 3 = 50) ==============

def test_b1072_pivot40_phase_2_smoke_false_positive_now_warns():
    """B1072 PIVOT #40: replays the B1071 Phase 2 false-positive scenario
    (10 tickers, sim_day 250, 60 of 88 silent strategies) and asserts the
    fix turns the false HALT into a WARN-HIGH."""
    mod = _load_monitor()
    a1, b2, d1, e_new, f_new = _mass_anomaly_inputs()
    tier = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                              current_day=250, active_tickers=10)
    assert tier == "WARN-HIGH", (
        f"B1072 PIVOT #40: Phase 2 false-positive scenario (10 tickers, "
        f"sim_day 250, 60/88 silent) must WARN (not HALT) post-fix; "
        f"got {tier}"
    )


def test_b1072_pivot40_phase_3_50_tickers_below_floor():
    """B1072 PIVOT #40: Phase 3 (50 tickers) also below 1000-ticker floor;
    A1 mass-anomaly stays WARN, does NOT HALT."""
    mod = _load_monitor()
    a1, b2, d1, e_new, f_new = _mass_anomaly_inputs()
    tier = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                              current_day=250, active_tickers=50)
    assert tier == "WARN-HIGH", (
        f"B1072 PIVOT #40: Phase 3 (50 tickers) must WARN-HIGH (not HALT), "
        f"got {tier}"
    )


# =========== Composition with B1070 F-9.2 sim_day gate ======================

def test_b1072_pivot40_pre_day_200_master_scale_still_warns():
    """B1072 PIVOT #40 + B1070 F-9.2 composition: even at 1929 tickers, if
    sim_day < 200 the F-9.2 gate keeps HALT suppressed -- WARN-HIGH."""
    mod = _load_monitor()
    a1, b2, d1, e_new, f_new = _mass_anomaly_inputs()
    tier = mod._classify_tier(a1, b2, d1, e_new=e_new, f_new=f_new,
                              current_day=100, active_tickers=1929)
    assert tier == "WARN-HIGH", (
        f"B1072 PIVOT #40 + F-9.2 composition: sim_day 100 + 1929 tickers "
        f"must WARN-HIGH (sim_day gate suppresses), got {tier}"
    )


def test_b1072_pivot40_b2_violation_still_halts_regardless_of_active_tickers():
    """B1072 PIVOT #40 + B1067 FIX 2 (B2 priority): B2 schema violation
    HALTs regardless of active_tickers value (data-integrity supersedes
    A1 statistical-actionability)."""
    mod = _load_monitor()
    a1, b2, d1, e_new, f_new = _mass_anomaly_inputs()
    b2_violation = {"violations": ["missing_column_exit_reason"],
                    "status": "VIOLATION"}
    tier = mod._classify_tier(a1, b2_violation, d1, e_new=e_new,
                              f_new=f_new, current_day=50,
                              active_tickers=1)
    assert tier == "HALT-CRITICAL", (
        f"B1072 PIVOT #40: B2 violation must HALT regardless of "
        f"active_tickers (data-integrity priority), got {tier}"
    )


# =========== Lineage assertions =============================================

def test_b1072_pivot40_lineage_in_monitor():
    """B1072 PIVOT #40: lineage comment + active_tickers param documented."""
    content = MONITOR_PATH.read_text()
    assert "B1072 PIVOT #40" in content, (
        "B1072 PIVOT #40: lineage comment required in monitor.py"
    )
    assert "active_tickers >= 1000" in content, (
        "B1072 PIVOT #40: 1000-ticker gate must be documented in monitor.py"
    )
    assert "Council 184" in content, (
        "B1072 PIVOT #40: Council 184 attribution missing"
    )


def test_b1072_pivot40_active_tickers_threaded_through_call_site():
    """B1072 PIVOT #40: main() must pass active_tickers=args.total_tickers
    _active into _classify_tier call site."""
    content = MONITOR_PATH.read_text()
    # The call site at main()'s _classify_tier invocation
    assert "active_tickers=args.total_tickers_active" in content, (
        "B1072 PIVOT #40: main() must thread args.total_tickers_active "
        "into _classify_tier(active_tickers=...) call site"
    )


def test_b1072_pivot40_classify_tier_signature_has_active_tickers():
    """B1072 PIVOT #40: _classify_tier function signature must accept
    active_tickers kwarg with default 0."""
    mod = _load_monitor()
    import inspect
    sig = inspect.signature(mod._classify_tier)
    assert "active_tickers" in sig.parameters, (
        "B1072 PIVOT #40: _classify_tier must accept active_tickers kwarg"
    )
    param = sig.parameters["active_tickers"]
    assert param.default == 0, (
        f"B1072 PIVOT #40: active_tickers default must be 0 (defensive "
        f"backward-compat); got {param.default}"
    )
