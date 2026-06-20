"""B956 (2026-06-20): pyramid tests for findings triage queue.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13 + Council 60 UNANIMOUS 4/4
# strategic pivot per owner challenge 2026-06-20.
"""
from __future__ import annotations

import pytest


def test_b956_script_importable():
    """B956 contract: findings triage script importable."""
    from scripts import b956_build_findings_triage_queue as mod
    assert hasattr(mod, "main")
    assert hasattr(mod, "_classify_findings_for_dossier")


def test_b956_classify_fire_starved_finding():
    """B956: dossier with Section 7 verdict=FAIL_FIRE_STARVED produces FIRE_STARVED finding."""
    from scripts.b956_build_findings_triage_queue import _classify_findings_for_dossier
    dossier = {
        "sections": {
            "section_07_temporal_coverage_probe": {
                "verdict": "FAIL_FIRE_STARVED",
                "passes_min_trades_floor_either": False,
                "fires_per_year_long": 5.0,
                "fires_per_year_short": 0.0,
            }
        }
    }
    findings = _classify_findings_for_dossier("test_strategy", dossier)
    assert any(f["finding_type"] == "FIRE_STARVED" for f in findings)
    fire_starved = [f for f in findings if f["finding_type"] == "FIRE_STARVED"][0]
    assert fire_starved["severity"] == "HIGH"


def test_b956_classify_inverse_unsafe_finding():
    """B956: dossier with Section 8 mechanical_inverse_unsafe=True produces INVERSE_UNSAFE finding."""
    from scripts.b956_build_findings_triage_queue import _classify_findings_for_dossier
    dossier = {
        "sections": {
            "section_08_data_source_asymmetry": {
                "mechanical_inverse_unsafe": True,
                "asymmetric_sources": ["13F"],
                "signals_triggering_classification": {"13F": ["13f_signal"]},
            }
        }
    }
    findings = _classify_findings_for_dossier("test_strategy", dossier)
    assert any(f["finding_type"] == "INVERSE_UNSAFE_CHECK_NEEDED" for f in findings)


def test_b956_classify_signal_orphan_finding():
    """B956: dossier with Section 1 n_signals_orphan > 0 produces SIGNAL_ORPHAN finding."""
    from scripts.b956_build_findings_triage_queue import _classify_findings_for_dossier
    dossier = {
        "sections": {
            "section_01_wiring_trace_coverage": {
                "n_signals_orphan": 3,
                "signals_orphan": ["sig_a", "sig_b", "sig_c"],
                "wiring_coverage_pct": 70.0,
            }
        }
    }
    findings = _classify_findings_for_dossier("test_strategy", dossier)
    assert any(f["finding_type"] == "SIGNAL_ORPHAN" for f in findings)


def test_b956_classify_deferred_finding():
    """B956: dossier with r5_inclusion_criterion=deferred produces DEFERRED_OWNER_TRIAGE."""
    from scripts.b956_build_findings_triage_queue import _classify_findings_for_dossier
    dossier = {
        "sections": {},
        "r5_inclusion_criterion": "deferred",
    }
    findings = _classify_findings_for_dossier("test_strategy", dossier)
    assert any(f["finding_type"] == "DEFERRED_OWNER_TRIAGE" for f in findings)
    deferred = [f for f in findings if f["finding_type"] == "DEFERRED_OWNER_TRIAGE"][0]
    assert deferred["severity"] == "HIGH"


def test_b956_classify_earnings_blackout_lookahead_finding():
    """B956: dossier with Section 13 best_exit=earnings_blackout produces LOOKAHEAD_RISK."""
    from scripts.b956_build_findings_triage_queue import _classify_findings_for_dossier
    dossier = {
        "sections": {
            "section_13_exit_axis_best_26": {
                "in_r4_cube": True,
                "best_exit_method": "earnings_blackout",
                "best_exit_total_pnl_pct": 1000.0,
                "best_exit_n_trades": 500,
            }
        }
    }
    findings = _classify_findings_for_dossier("test_strategy", dossier)
    assert any(f["finding_type"] == "EARNINGS_BLACKOUT_LOOKAHEAD_RISK" for f in findings)


def test_b956_no_findings_for_clean_dossier():
    """B956: clean dossier (no problematic sections) produces 0 findings."""
    from scripts.b956_build_findings_triage_queue import _classify_findings_for_dossier
    dossier = {
        "sections": {
            "section_07_temporal_coverage_probe": {
                "verdict": "PASS_CUBE",
                "passes_min_trades_floor_either": True,
            },
            "section_08_data_source_asymmetry": {
                "mechanical_inverse_unsafe": False,
            },
            "section_01_wiring_trace_coverage": {
                "n_signals_orphan": 0,
            },
        },
        "r5_inclusion_criterion": "pre_cube_evidence_sufficient",
    }
    findings = _classify_findings_for_dossier("test_strategy", dossier)
    # No findings of HIGH/MEDIUM severity expected
    high_med = [f for f in findings if f["severity"] in ("HIGH", "MEDIUM")]
    assert high_med == []
