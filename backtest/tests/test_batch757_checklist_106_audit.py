"""Pin tests for scripts/checklist_106_cluster_a_producer_audit.py per
Batch 757 + B755-COUNCIL TIER 1.2 ticket.

# Source: scripts/checklist_106_cluster_a_producer_audit.py (B757 build)
# per CHECKLIST #77 + #106 (data-consumption audit discipline)

Locks in the audit contract: declared-signals gathering, Pattern F-class
detection, temporal-gap detection, and KNOWN-EVENT probe correctness.
"""
from __future__ import annotations

import pandas as pd
import pytest

from scripts.checklist_106_cluster_a_producer_audit import (
    KNOWN_EVENT_PROBES,
    _detect_pattern_f_candidates,
    _detect_temporal_gaps,
    _gather_declared_signals,
)
from scripts.build_fire_bar_matrix import CLUSTER_A_STRATEGIES


# ---------------------------------------------------------------------------
# Pin 1: KNOWN_EVENT_PROBES populated with at least 1 entry per axis (e)
# ---------------------------------------------------------------------------
def test_pin1_known_event_probes_nonempty():
    assert len(KNOWN_EVENT_PROBES) >= 1, (
        "KNOWN-EVENT probes required per CHECKLIST #106(e)"
    )
    for p in KNOWN_EVENT_PROBES:
        assert "ticker" in p and "date" in p and "signal" in p
        assert "expected" in p
        # Date format YYYY-MM-DD
        from datetime import datetime
        datetime.strptime(p["date"], "%Y-%m-%d")


# ---------------------------------------------------------------------------
# Pin 2: _gather_declared_signals returns non-empty for Cluster A
# (every strategy returns at least 1 signal in signals_used; sanity check
# the inventory aggregation)
# ---------------------------------------------------------------------------
def test_pin2_gather_declared_signals_nonempty():
    declared = _gather_declared_signals(CLUSTER_A_STRATEGIES)
    assert len(declared) > 0, (
        "Cluster A declared-signals inventory must be non-empty"
    )
    # Each entry must be {signal_name -> [list of strategies]}
    for sig, strats in declared.items():
        assert isinstance(sig, str)
        assert isinstance(strats, list)
        assert all(isinstance(s, str) for s in strats)


# ---------------------------------------------------------------------------
# Pin 3: _gather_declared_signals captures expected signals for RSI family
# (rsi_oversold + rsi_overbought_short + rsi21_slow etc. all reference
# RSI-class signals)
# ---------------------------------------------------------------------------
def test_pin3_declared_signals_includes_rsi_family():
    declared = _gather_declared_signals(["rsi_oversold", "rsi21_slow"])
    # Expect rsi-related signals to appear
    rsi_signals = [s for s in declared if "rsi" in s.lower()]
    assert len(rsi_signals) > 0, (
        f"RSI strategies should declare RSI signals; got {list(declared.keys())}"
    )


# ---------------------------------------------------------------------------
# Pin 4: Pattern F detection -- declared but never emitted
# Synthetic: declare 'fake_signal' used by 2 strategies; signal_coverage shows
# 0 tickers emitting -> Pattern F candidate
# ---------------------------------------------------------------------------
def test_pin4_pattern_f_declared_but_never_emitted():
    declared = {"fake_signal": ["strat_a", "strat_b"]}
    coverage = {}  # fake_signal not in coverage = never emitted
    candidates = _detect_pattern_f_candidates(declared, coverage, n_tickers_probed=50)
    assert len(candidates) == 1
    assert candidates[0]["signal"] == "fake_signal"
    assert candidates[0]["issue"] == "declared_but_never_emitted"
    assert candidates[0]["severity"] == "HIGH"  # 2 strategies => HIGH


# ---------------------------------------------------------------------------
# Pin 5: Pattern F detection -- emitted but always False (silent-no-op)
# ---------------------------------------------------------------------------
def test_pin5_pattern_f_emitted_but_always_false():
    declared = {"always_false_signal": ["strat_x"]}
    coverage = {
        "always_false_signal": {
            "n_tickers_emitting": 50,
            "n_tickers_with_True": 0,   # always False
            "n_observations": 12000,
            "n_True_observations": 0,
            "by_year": {},
        }
    }
    candidates = _detect_pattern_f_candidates(declared, coverage, n_tickers_probed=50)
    assert len(candidates) == 1
    assert candidates[0]["signal"] == "always_false_signal"
    assert candidates[0]["issue"] == "emitted_but_always_False"


# ---------------------------------------------------------------------------
# Pin 6: Temporal-gap detection -- signal emission rate < threshold
# ---------------------------------------------------------------------------
def test_pin6_temporal_gap_below_threshold():
    declared = {"sparse_signal": ["strat_q"]}
    coverage = {
        "sparse_signal": {
            "n_tickers_emitting": 50,
            "n_tickers_with_True": 50,
            "n_observations": 12000,
            "n_True_observations": 12,  # ~0.1% overall
            "by_year": {
                "2024": {"n_observations": 6000, "n_True": 12},  # 0.2% -- above threshold
                "2025": {"n_observations": 6000, "n_True": 0},   # 0% -- gap
            },
        }
    }
    gaps = _detect_temporal_gaps(coverage, declared, min_rate_threshold=0.001)
    # 2025 should be flagged (rate 0/6000 < 0.001)
    assert any(g["year"] == "2025" and g["signal"] == "sparse_signal" for g in gaps), (
        f"Temporal gap should flag 2025 0%-emission year; got {gaps}"
    )


# ---------------------------------------------------------------------------
# Pin 7: Temporal-gap detection does NOT flag undeclared signals
# (only declared signals matter for the audit)
# ---------------------------------------------------------------------------
def test_pin7_temporal_gap_ignores_undeclared_signals():
    declared = {"declared_a": ["strat_x"]}
    coverage = {
        "declared_a": {
            "n_tickers_emitting": 50,
            "n_tickers_with_True": 50,
            "n_observations": 100,
            "n_True_observations": 50,
            "by_year": {"2024": {"n_observations": 100, "n_True": 50}},
        },
        "undeclared_b": {  # not in declared set; should be skipped
            "n_tickers_emitting": 50,
            "n_tickers_with_True": 0,
            "n_observations": 100,
            "n_True_observations": 0,
            "by_year": {"2024": {"n_observations": 100, "n_True": 0}},
        },
    }
    gaps = _detect_temporal_gaps(coverage, declared, min_rate_threshold=0.01)
    # undeclared_b should NOT appear in gaps
    assert all(g["signal"] != "undeclared_b" for g in gaps)


# ---------------------------------------------------------------------------
# Pin 8: Pattern F candidate severity tagging
# - 2+ strategies declaring a missing signal => HIGH severity
# - 1 strategy declaring a missing signal => MEDIUM severity
# ---------------------------------------------------------------------------
def test_pin8_pattern_f_severity_tagging():
    declared = {
        "multi_strat_signal": ["strat_a", "strat_b", "strat_c"],
        "single_strat_signal": ["strat_d"],
    }
    coverage = {}  # nothing emitted
    candidates = _detect_pattern_f_candidates(declared, coverage, n_tickers_probed=50)
    sev_map = {c["signal"]: c["severity"] for c in candidates}
    assert sev_map["multi_strat_signal"] == "HIGH"
    assert sev_map["single_strat_signal"] == "MEDIUM"


# ---------------------------------------------------------------------------
# Pin 9: KNOWN_EVENT_PROBES includes a March 2020 COVID-crash entry per
# CHECKLIST #106(e). This is the canonical RSI oversold event in the
# 2020-2026 backtest window.
# ---------------------------------------------------------------------------
def test_pin9_known_event_probes_includes_march_2020():
    march_2020_probes = [
        p for p in KNOWN_EVENT_PROBES
        if p["date"].startswith("2020-03")
    ]
    assert len(march_2020_probes) >= 1, (
        "March 2020 COVID-crash RSI-oversold probe required per CHECKLIST #106(e)"
    )


# ---------------------------------------------------------------------------
# Pin 10: All Cluster A strategies surveyable (smoke-test the gather loop)
# ---------------------------------------------------------------------------
def test_pin10_all_cluster_a_strategies_surveyable():
    declared = _gather_declared_signals(CLUSTER_A_STRATEGIES)
    # Every Cluster A strategy should appear in at least one signal's
    # strategies-list (otherwise the strategy declared no signals -- bug).
    all_strats_in_declared = set()
    for sig, strats in declared.items():
        all_strats_in_declared.update(strats)
    missing = [s for s in CLUSTER_A_STRATEGIES if s not in all_strats_in_declared]
    assert not missing, (
        f"Strategies with no declared signals: {missing}"
    )
