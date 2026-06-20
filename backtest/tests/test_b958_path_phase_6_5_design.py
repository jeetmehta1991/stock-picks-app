"""B958 (2026-06-20): pyramid tests for PATH doc Phase 6.5 design.

# Source: PATH_TO_PHASE_1B_ALPHA.md Section 13.15 + 13.16 + Council 63 UNANIMOUS
# verdict per owner directive 2026-06-20 'C then B' per CHECKLIST #77.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parent.parent.parent
PATH_DOC = REPO / "PATH_TO_PHASE_1B_ALPHA.md"


def _read_path_doc() -> str:
    return PATH_DOC.read_text(encoding="utf-8", errors="ignore")


def test_b958_path_doc_exists():
    """B958 contract: PATH doc still exists."""
    assert PATH_DOC.exists()


def test_b958_phase_table_has_8_rows():
    """B958: Section13.2 phase table extended from 7 rows (P0-P6) to 8 rows (P0-P6.5 + P7).

    Counts table rows containing 'P0', 'P1', ..., 'P6', 'P6.5', 'P7' markers.
    """
    text = _read_path_doc()
    # Find the phase table section
    section_start = text.find("### 13.2 The 7 Phases")
    if section_start == -1:
        section_start = text.find("13.2 The 7 Phases")
    assert section_start != -1, "Section 13.2 phase table missing"
    # Slice next 4000 chars
    section_text = text[section_start:section_start + 4000]
    # Phase markers required (8 rows now: P0-P6 + P6.5 + P7)
    required_phases = ["**P0**", "**P1**", "**P2**", "**P3**", "**P4**", "**P5**", "**P6**", "**P6.5**", "**P7**"]
    for phase in required_phases:
        assert phase in section_text, f"Phase marker {phase} missing from Section13.2 table"


def test_b958_dec_5_amended_with_n_effective_5874():
    """B958: DEC #5 amended to pre-register N_effective = 5,874 post-P6.5."""
    text = _read_path_doc()
    # DEC #5 mention
    dec_5_idx = text.find("DEC #5")
    assert dec_5_idx != -1
    # Should mention N_effective = 5,874 in some form
    dec_5_window = text[dec_5_idx:dec_5_idx + 2000]
    assert "5,874" in dec_5_window or "5874" in dec_5_window, (
        "DEC #5 amendment for N_effective = 5,874 missing"
    )


def test_b958_section_13_15_phase_6_5_design_exists():
    """B958: NEW Section13.15 'Phase 6.5 Design' section added."""
    text = _read_path_doc()
    assert "### 13.15 Phase 6.5 Design" in text, "Section13.15 Phase 6.5 Design section missing"


def test_b958_section_13_16_dec_phase_6_5_reset_exists():
    """B958: NEW Section13.16 'DEC-PHASE-6.5-RESET' section added."""
    text = _read_path_doc()
    assert "### 13.16 DEC-PHASE-6.5-RESET" in text, "Section13.16 DEC-PHASE-6.5-RESET section missing"


def test_b958_phase_6_5_trial_budget_180_cap():
    """B958: Phase 6.5 trial budget hard cap of 180 (120 Type 1 + 60 Type 2 Track B)."""
    text = _read_path_doc()
    section_start = text.find("### 13.15 Phase 6.5 Design")
    assert section_start != -1
    section_window = text[section_start:section_start + 10000]
    assert "180" in section_window
    assert "120" in section_window  # Type 1 cap
    assert "60" in section_window   # Type 2 Track B cap


def test_b958_track_b_qualifier_four_gates():
    """B958: Track B qualifier requires ALL 4 GATES (Contrarian 3 + Outsider edge signal)."""
    text = _read_path_doc()
    section_start = text.find("### 13.15 Phase 6.5 Design")
    assert section_start != -1
    section_window = text[section_start:section_start + 10000]
    # Must reference Bonferroni Sharpe band [0.55, 0.70]
    assert "0.55" in section_window and "0.70" in section_window
    # Must reference raw t-stat >= 2.0
    assert "2.0" in section_window
    # Must reference OOS quartile >= 2
    assert re.search(r"oos.*quartile|quartile.*rank", section_window, re.IGNORECASE)


def test_b958_oos_carve_out_2026_q2():
    """B958: 2026-Q2+ OOS carve-out preservation method documented."""
    text = _read_path_doc()
    assert "2026-Q2" in text or "Q2+" in text
    # Reference in Section13.15 or Section13.16
    section_start = text.find("### 13.15 Phase 6.5 Design")
    if section_start != -1:
        section_window = text[section_start:section_start + 10000]
        assert "Q2" in section_window or "2026-Q2" in section_window


def test_b958_phase_6_5_entry_gates_added_to_13_7():
    """B958: R5 launch gates Section13.7 extended with P6.5 entry gates 16-20."""
    text = _read_path_doc()
    section_start = text.find("### 13.7 R5 Launch Gates")
    assert section_start != -1
    section_window = text[section_start:section_start + 5000]
    # 5 new entry gates 16-20 added (Council 63 mandate)
    for gate_num in ("16.", "17.", "18.", "19.", "20."):
        assert gate_num in section_window, f"P6.5 entry gate {gate_num} missing from Section13.7"


def test_b958_council_7_reset_acknowledged():
    """B958: Council 7 binding 'R5 -> no changes' explicitly reset in Section13.16."""
    text = _read_path_doc()
    section_start = text.find("### 13.16 DEC-PHASE-6.5-RESET")
    assert section_start != -1
    section_window = text[section_start:section_start + 5000]
    # Must mention Council 7 binding
    assert "Council 7" in section_window
    # Must use word 'reset' or 'lifted'
    assert re.search(r"reset|lifted|LIFTED", section_window)


def test_b958_failure_modes_p6_5_specific_added():
    """B958: Section13.13 failure modes table extended with P6.5-specific failures."""
    text = _read_path_doc()
    section_start = text.find("### 13.13 Failure Modes")
    assert section_start != -1
    section_window = text[section_start:section_start + 6000]
    # 4 new failure-mode rows added (Council 63 + Contrarian)
    p6_5_failure_keywords = [
        "trial-budget overrun",
        "OOS-seal-bleed",
        "qualifier-creep",
        "natural range",
    ]
    for kw in p6_5_failure_keywords:
        assert kw in section_window, f"P6.5 failure mode keyword '{kw}' missing from Section13.13"


def test_b958_p2_reclassification_absorbs_track_a_consolidation():
    """B958: Section13.2 P2 description amended to absorb Type 2 Track A consolidation."""
    text = _read_path_doc()
    section_start = text.find("### 13.2 The 7 Phases")
    if section_start == -1:
        section_start = text.find("13.2 The 7 Phases")
    assert section_start != -1
    section_text = text[section_start:section_start + 5000]
    # P2 row should mention Track A absorption + redundancy_phi_matrix
    assert "P2" in section_text
    assert "Track A" in section_text or "redundancy_phi_matrix" in section_text
    assert "B705" in section_text or "no_prior_edge" in section_text
