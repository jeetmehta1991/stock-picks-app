"""B1073 PIVOT #42 pin tests: active_tickers >= 1000 gate on E-NEW
silent-strategy floor HALT-CRITICAL.

# Source: Council 185 4/4 RECOMMEND Option 2 COMPREHENSIVE-MONITOR-AUDIT
# per owner directive 2026-06-29 'Approve all council this' +
# CHECKLIST #115 + #128 (PASS-PATH-OUTPUT-VERIFICATION) + #133 +
# feedback_writer_reader_schema_contract_pin_test +
# feedback_monitor_baseline_must_scale_with_active_universe +
# feedback_designed_vs_verified_requires_evidence_artifact.

PIVOT #42 (companion to B1072 PIVOT #40 A1-PROMOTION gate):
  E-NEW silent_floor HALT-CRITICAL now triple-gated:
    - current_day >= silent_floor_day (default 500)   [B1067 FIX 3]
    - silent_pct > silent_pct_threshold (default 0.5) [B1067 FIX 3]
    - active_tickers >= 1000                           [B1073 PIVOT #42 NEW]

Same bug class as A1-PROMOTION (PIVOT #40 in B1072): cross-sectional
strategies (relative-strength, sector-rank, breadth) structurally cannot
fire on N=1/10/50 tickers; silent_pct hits 50%+ floor naturally at
small-universe phases regardless of engine health.

Comprehensive monitor audit (Council 185) confirmed E-NEW was the ONLY
remaining small-ticker false-positive HALT site in _classify_tier after
B1072 fixed A1-PROMOTION. Bug class is now fully closed.
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


def _silent_floor_a1_inputs():
    """A1 fixture with mass-silent state: 80 of 88 expected-firing
    strategies silent (91pct, exceeds 50pct E-NEW silent_pct_threshold)."""
    return {
        "anomaly_count": 80,
        "expected_firing_count": 88,
        "silent_with_expectation": 80,
    }


# =========== Core PIVOT #42 trio: small-vs-large universe at sim_day >= 500 ==

def test_b1073_pivot42_e_new_no_halt_below_1000_tickers():
    """B1073 PIVOT #42: E-NEW silent_floor at sim_day 600 + 91pct silent +
    active_tickers=1 must NOT HALT (Phase 1 NVDA-only structural silence
    on cross-sectional strategies, not engine bug)."""
    mod = _load_monitor()
    a1 = _silent_floor_a1_inputs()
    e_new = mod._check_e_new_silent_floor(
        a1, current_day=600, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=1
    )
    assert e_new["halt"] is False, (
        "B1073 PIVOT #42 REGRESSION: E-NEW silent_floor at sim_day 600 + "
        "91pct silent + active_tickers=1 must NOT HALT (small-universe "
        f"structural silence), got halt={e_new['halt']}"
    )
    assert e_new["status"] == "GATED-small-universe", (
        f"B1073 PIVOT #42: status must indicate gate-suppression for "
        f"observability, got status={e_new['status']}"
    )


def test_b1073_pivot42_e_new_halts_at_1929_tickers_master_scale():
    """B1073 PIVOT #42: E-NEW silent_floor at sim_day 600 + 91pct silent +
    active_tickers=1929 (Master 1929 ops intersection) MUST HALT."""
    mod = _load_monitor()
    a1 = _silent_floor_a1_inputs()
    e_new = mod._check_e_new_silent_floor(
        a1, current_day=600, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=1929
    )
    assert e_new["halt"] is True, (
        "B1073 PIVOT #42: E-NEW silent_floor at sim_day 600 + 91pct silent + "
        "active_tickers=1929 (Master scale) must HALT, "
        f"got halt={e_new['halt']}"
    )
    assert e_new["status"] == "HALT", (
        f"B1073 PIVOT #42: status must be HALT at Master scale, "
        f"got status={e_new['status']}"
    )


def test_b1073_pivot42_boundary_active_tickers_999_vs_1000():
    """B1073 PIVOT #42 boundary: active_tickers=999 gated, =1000 HALTs."""
    mod = _load_monitor()
    a1 = _silent_floor_a1_inputs()
    e_999 = mod._check_e_new_silent_floor(
        a1, current_day=600, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=999
    )
    e_1000 = mod._check_e_new_silent_floor(
        a1, current_day=600, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=1000
    )
    assert e_999["halt"] is False, (
        f"B1073 PIVOT #42: active_tickers=999 must be gated (no HALT), "
        f"got halt={e_999['halt']}"
    )
    assert e_1000["halt"] is True, (
        f"B1073 PIVOT #42: active_tickers=1000 must HALT, "
        f"got halt={e_1000['halt']}"
    )


# =========== Phase-scale specific (Phase 1 = 1, Phase 2 = 10, Phase 3 = 50) ==

def test_b1073_pivot42_phase_1_smoke_false_positive_now_passes():
    """B1073 PIVOT #42: replays B1073 Phase 1 false-positive scenario
    (1 ticker NVDA, sim_day 500+, ~91pct silent) and asserts fix turns
    false HALT into gated-OK."""
    mod = _load_monitor()
    a1 = _silent_floor_a1_inputs()
    e_new = mod._check_e_new_silent_floor(
        a1, current_day=550, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=1
    )
    assert e_new["halt"] is False, (
        f"B1073 PIVOT #42: Phase 1 NVDA-only false-positive scenario "
        f"(1 ticker, sim_day 550, 80/88 silent) must NOT HALT post-fix; "
        f"got halt={e_new['halt']}"
    )


def test_b1073_pivot42_phase_2_10_tickers_below_floor():
    """B1073 PIVOT #42: Phase 2 (10 tickers) below 1000-ticker floor;
    E-NEW silent_floor stays gated, does NOT HALT."""
    mod = _load_monitor()
    a1 = _silent_floor_a1_inputs()
    e_new = mod._check_e_new_silent_floor(
        a1, current_day=550, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=10
    )
    assert e_new["halt"] is False, (
        f"B1073 PIVOT #42: Phase 2 (10 tickers) must NOT HALT, "
        f"got halt={e_new['halt']}"
    )


def test_b1073_pivot42_phase_3_50_tickers_below_floor():
    """B1073 PIVOT #42: Phase 3 (50 tickers) below 1000-ticker floor;
    E-NEW silent_floor stays gated, does NOT HALT."""
    mod = _load_monitor()
    a1 = _silent_floor_a1_inputs()
    e_new = mod._check_e_new_silent_floor(
        a1, current_day=550, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=50
    )
    assert e_new["halt"] is False, (
        f"B1073 PIVOT #42: Phase 3 (50 tickers) must NOT HALT, "
        f"got halt={e_new['halt']}"
    )


# =========== Composition with B1067 FIX 3 sim_day + silent_pct gates ========

def test_b1073_pivot42_pre_day_500_master_scale_still_ok():
    """B1073 PIVOT #42 + B1067 FIX 3 composition: even at 1929 tickers, if
    sim_day < 500 the silent_floor_day gate keeps HALT suppressed."""
    mod = _load_monitor()
    a1 = _silent_floor_a1_inputs()
    e_new = mod._check_e_new_silent_floor(
        a1, current_day=400, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=1929
    )
    assert e_new["halt"] is False, (
        f"B1073 PIVOT #42 + B1067 FIX 3 composition: sim_day 400 + "
        f"1929 tickers must NOT HALT (sim_day gate suppresses), "
        f"got halt={e_new['halt']}"
    )


def test_b1073_pivot42_silent_pct_below_threshold_no_halt():
    """B1073 PIVOT #42 + B1067 FIX 3: silent_pct below 50pct threshold,
    even at 1929 tickers + sim_day 600, must NOT HALT."""
    mod = _load_monitor()
    a1 = {"anomaly_count": 30, "expected_firing_count": 88,
          "silent_with_expectation": 30}  # 34pct silent < 50pct
    e_new = mod._check_e_new_silent_floor(
        a1, current_day=600, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=1929
    )
    assert e_new["halt"] is False, (
        f"B1073 PIVOT #42: silent_pct 34pct < 50pct threshold must NOT "
        f"HALT even at Master scale, got halt={e_new['halt']}"
    )


# =========== _classify_tier integration (E-NEW halt feeds into tier) ========

def test_b1073_pivot42_classify_tier_no_halt_when_e_new_gated():
    """B1073 PIVOT #42: _classify_tier must NOT HALT when E-NEW is
    gate-suppressed even though silent_pct triggers structurally."""
    mod = _load_monitor()
    a1 = _silent_floor_a1_inputs()
    e_new = mod._check_e_new_silent_floor(
        a1, current_day=600, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=1  # GATED
    )
    b2 = {"violations": [], "status": "OK"}
    d1 = {"cells_completed": 100, "total_cells": 5694, "pct_cells": 0.018,
          "eta_min": 0, "runtime_min": 50}
    f_new = {"regime_gaps": 0}
    tier = mod._classify_tier(
        a1, b2, d1, e_new=e_new, f_new=f_new,
        current_day=600, active_tickers=1
    )
    # a1_anom=80 >= 5 + a1 not gated (separate gate at 200/1000) -> WARN-HIGH
    assert tier != "HALT-CRITICAL", (
        f"B1073 PIVOT #42: _classify_tier must NOT HALT when E-NEW gated "
        f"at small universe + A1 also gated; got {tier}"
    )


def test_b1073_pivot42_classify_tier_halts_when_e_new_armed_at_master():
    """B1073 PIVOT #42: _classify_tier must HALT at Master scale when
    E-NEW gate engages (universe is large enough for floor to be valid)."""
    mod = _load_monitor()
    a1 = _silent_floor_a1_inputs()
    e_new = mod._check_e_new_silent_floor(
        a1, current_day=600, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=1929  # ARMED
    )
    b2 = {"violations": [], "status": "OK"}
    d1 = {"cells_completed": 100, "total_cells": 5694, "pct_cells": 0.018,
          "eta_min": 0, "runtime_min": 50}
    f_new = {"regime_gaps": 0}
    tier = mod._classify_tier(
        a1, b2, d1, e_new=e_new, f_new=f_new,
        current_day=600, active_tickers=1929
    )
    assert tier == "HALT-CRITICAL", (
        f"B1073 PIVOT #42: _classify_tier must HALT when E-NEW engages at "
        f"Master scale (1929 tickers, sim_day 600, 91pct silent), "
        f"got {tier}"
    )


# =========== Lineage + signature assertions =================================

def test_b1073_pivot42_lineage_in_monitor():
    """B1073 PIVOT #42: lineage comment + 1000-ticker gate documented."""
    content = MONITOR_PATH.read_text()
    assert "B1073 PIVOT #42" in content, (
        "B1073 PIVOT #42: lineage comment required in monitor.py"
    )
    assert "Council 185" in content, (
        "B1073 PIVOT #42: Council 185 attribution missing"
    )
    # Must document active_tickers gate in E-NEW context specifically
    assert "_check_e_new_silent_floor" in content, (
        "B1073 PIVOT #42: _check_e_new_silent_floor must remain present"
    )


def test_b1073_pivot42_active_tickers_threaded_through_call_site():
    """B1073 PIVOT #42: main() must pass active_tickers=args.total_tickers
    _active into _check_e_new_silent_floor call site."""
    content = MONITOR_PATH.read_text()
    # Must occur twice: once in _classify_tier (B1072) call site, once in
    # _check_e_new_silent_floor (B1073) call site
    occurrences = content.count("active_tickers=args.total_tickers_active")
    assert occurrences >= 2, (
        f"B1073 PIVOT #42: args.total_tickers_active must be threaded into "
        f"both _classify_tier AND _check_e_new_silent_floor call sites; "
        f"found {occurrences} occurrence(s)"
    )


def test_b1073_pivot42_e_new_signature_has_active_tickers():
    """B1073 PIVOT #42: _check_e_new_silent_floor signature must accept
    active_tickers kwarg with default 0 (defensive backward-compat)."""
    mod = _load_monitor()
    import inspect
    sig = inspect.signature(mod._check_e_new_silent_floor)
    assert "active_tickers" in sig.parameters, (
        "B1073 PIVOT #42: _check_e_new_silent_floor must accept "
        "active_tickers kwarg"
    )
    param = sig.parameters["active_tickers"]
    assert param.default == 0, (
        f"B1073 PIVOT #42: active_tickers default must be 0 (defensive "
        f"backward-compat preserving pre-fix call sites); got {param.default}"
    )


def test_b1073_pivot42_e_new_result_includes_active_tickers_field():
    """B1073 PIVOT #42: E-NEW result dict must include active_tickers
    field for downstream observability + post-mortem replay."""
    mod = _load_monitor()
    a1 = _silent_floor_a1_inputs()
    e_new = mod._check_e_new_silent_floor(
        a1, current_day=600, silent_floor_day=500,
        silent_pct_threshold=0.5, active_tickers=42
    )
    assert "active_tickers" in e_new, (
        "B1073 PIVOT #42: E-NEW result must include active_tickers field "
        "for observability"
    )
    assert e_new["active_tickers"] == 42, (
        f"B1073 PIVOT #42: active_tickers field must round-trip input "
        f"value; got {e_new['active_tickers']}"
    )
