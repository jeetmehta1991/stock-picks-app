"""Pin tests for scripts/build_fire_bar_matrix.py per Batch 756 +
B755-COUNCIL TIER 1 ticket S4-B755-COUNCIL-FIRE-BAR-SPARSE-MATRIX-PRECOMPUTE.

Locks in the schema + Jaccard / phi-correlation math + crash-fix
contract for surface_pattern_candidates (regression: empty similarity_df
returned dict was missing 'jaccard_threshold' / 'phi_threshold' keys).
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from scripts.build_fire_bar_matrix import (
    CLUSTER_A_STRATEGIES,
    SMOKE_STRATEGIES,
    compute_pairwise_similarity,
    surface_pattern_candidates,
)


# ---------------------------------------------------------------------------
# Pin 1: Cluster A strategy list is exactly 30 (per state table in
# STAGE_4_OSCILLATOR_MEAN_REVERSION_CLUSTER_WALKS.md)
# ---------------------------------------------------------------------------
def test_pin1_cluster_a_strategies_count_is_28():
    # B899 migration: 30 -> 28 post-B874 deletion of camarilla_rsi_obv
    # (dual) + camarilla_rsi_obv_short per Pattern W deterministic-duplicate
    # finding (S4-B754-A-19 council 5-lens option A2).
    assert len(CLUSTER_A_STRATEGIES) == 28, (
        f"Cluster A must list 28 strategies post-B874 (was 30 pre-B874); got "
        f"{len(CLUSTER_A_STRATEGIES)}"
    )


# ---------------------------------------------------------------------------
# Pin 2: All Cluster A strategies are unique (no double-listing)
# ---------------------------------------------------------------------------
def test_pin2_cluster_a_strategies_unique():
    assert len(set(CLUSTER_A_STRATEGIES)) == len(CLUSTER_A_STRATEGIES), (
        "Cluster A strategy list contains duplicates"
    )


# ---------------------------------------------------------------------------
# Pin 3: All Cluster A strategy names resolve in ALL_STRATEGIES registry
# (guards against typo / rename without script update)
# ---------------------------------------------------------------------------
def test_pin3_cluster_a_strategies_in_registry():
    from backtest.signals.screener import ALL_STRATEGIES
    missing = [s for s in CLUSTER_A_STRATEGIES if s not in ALL_STRATEGIES]
    assert not missing, (
        f"Cluster A strategies missing from ALL_STRATEGIES: {missing}"
    )


# ---------------------------------------------------------------------------
# Pin 4: Smoke strategies subset of Cluster A
# ---------------------------------------------------------------------------
def test_pin4_smoke_strategies_subset_of_cluster_a():
    for s in SMOKE_STRATEGIES:
        assert s in CLUSTER_A_STRATEGIES, (
            f"Smoke strategy {s} must be in CLUSTER_A_STRATEGIES"
        )


# ---------------------------------------------------------------------------
# Pin 5: surface_pattern_candidates returns 'jaccard_threshold' +
# 'phi_threshold' keys EVEN when similarity_df is empty
# (regression: B756 initial smoke crashed with KeyError on this path)
# ---------------------------------------------------------------------------
def test_pin5_surface_pattern_candidates_empty_df_returns_threshold_keys():
    empty_df = pd.DataFrame(columns=[
        "strategy_a", "strategy_b", "direction", "n_a", "n_b",
        "n_both", "jaccard", "phi_correlation",
    ])
    result = surface_pattern_candidates(empty_df)
    assert "jaccard_threshold" in result
    assert "phi_threshold" in result
    assert result["pattern_w_candidates"] == []
    assert result["pattern_j_candidates"] == []


# ---------------------------------------------------------------------------
# Pin 6: surface_pattern_candidates filters Pattern W candidates by Jaccard
# threshold (default 0.85)
# ---------------------------------------------------------------------------
def test_pin6_surface_pattern_w_jaccard_threshold_filtering():
    df = pd.DataFrame([
        {"strategy_a": "a", "strategy_b": "b", "direction": "long",
         "n_a": 100, "n_b": 100, "n_both": 90, "jaccard": 0.90,
         "phi_correlation": 0.50},
        {"strategy_a": "a", "strategy_b": "c", "direction": "long",
         "n_a": 100, "n_b": 100, "n_both": 50, "jaccard": 0.30,
         "phi_correlation": 0.20},
    ])
    result = surface_pattern_candidates(df, jaccard_threshold=0.85)
    assert len(result["pattern_w_candidates"]) == 1
    assert result["pattern_w_candidates"][0]["strategy_b"] == "b"


# ---------------------------------------------------------------------------
# Pin 7: surface_pattern_candidates filters Pattern J candidates by
# phi-correlation threshold (default 0.70)
# ---------------------------------------------------------------------------
def test_pin7_surface_pattern_j_phi_threshold_filtering():
    df = pd.DataFrame([
        {"strategy_a": "a", "strategy_b": "b", "direction": "long",
         "n_a": 100, "n_b": 100, "n_both": 80, "jaccard": 0.40,
         "phi_correlation": 0.75},
        {"strategy_a": "a", "strategy_b": "c", "direction": "long",
         "n_a": 100, "n_b": 100, "n_both": 50, "jaccard": 0.30,
         "phi_correlation": 0.30},
    ])
    result = surface_pattern_candidates(df, phi_threshold=0.70)
    assert len(result["pattern_j_candidates"]) == 1
    assert result["pattern_j_candidates"][0]["strategy_b"] == "b"


# ---------------------------------------------------------------------------
# Pin 8: compute_pairwise_similarity Jaccard math on synthetic data
# Two strategies that share 5 of 10 fires across a 1000-cell universe:
#   set_a = {(t1, d1) ... (t1, d10)}    # 10 fires
#   set_b = {(t1, d6) ... (t1, d15)}    # 10 fires
#   intersection = {(t1, d6) ... (t1, d10)} = 5
#   union = 15
#   jaccard = 5/15 = 0.333...
# ---------------------------------------------------------------------------
def test_pin8_jaccard_math_synthetic():
    rows = []
    for d in range(1, 11):
        rows.append({"strategy": "a", "ticker": "T1",
                     "bar_date": pd.Timestamp(f"2024-01-{d:02d}"),
                     "direction": "long", "fires": True})
    for d in range(6, 16):
        rows.append({"strategy": "b", "ticker": "T1",
                     "bar_date": pd.Timestamp(f"2024-01-{d:02d}"),
                     "direction": "long", "fires": True})
    rows_df = pd.DataFrame(rows)
    sim_df = compute_pairwise_similarity(rows_df, n_bars_total=1000)
    assert len(sim_df) == 1
    assert sim_df.iloc[0]["strategy_a"] == "a"
    assert sim_df.iloc[0]["strategy_b"] == "b"
    assert sim_df.iloc[0]["n_a"] == 10
    assert sim_df.iloc[0]["n_b"] == 10
    assert sim_df.iloc[0]["n_both"] == 5
    assert abs(sim_df.iloc[0]["jaccard"] - 5.0 / 15.0) < 1e-5


# ---------------------------------------------------------------------------
# Pin 9: phi-correlation math on the IDENTICAL-firing case (Pattern W
# HIGHEST CONFIDENCE example: A-19 vs A-18 SHORT). If two strategies fire
# on exactly the same set of bars, phi should be 1.0.
# ---------------------------------------------------------------------------
def test_pin9_phi_correlation_identical_firing_is_one():
    rows = []
    for d in range(1, 11):
        rows.append({"strategy": "identical_a", "ticker": "T1",
                     "bar_date": pd.Timestamp(f"2024-01-{d:02d}"),
                     "direction": "short", "fires": True})
        rows.append({"strategy": "identical_b", "ticker": "T1",
                     "bar_date": pd.Timestamp(f"2024-01-{d:02d}"),
                     "direction": "short", "fires": True})
    rows_df = pd.DataFrame(rows)
    sim_df = compute_pairwise_similarity(rows_df, n_bars_total=100)
    assert len(sim_df) == 1
    assert abs(sim_df.iloc[0]["jaccard"] - 1.0) < 1e-5
    assert abs(sim_df.iloc[0]["phi_correlation"] - 1.0) < 1e-5


# ---------------------------------------------------------------------------
# Pin 10: phi-correlation math on DISJOINT fire sets (no shared bars).
# Two strategies firing on completely different bars should give phi <= 0.
# ---------------------------------------------------------------------------
def test_pin10_phi_correlation_disjoint_firing_is_negative_or_zero():
    rows = []
    for d in range(1, 11):
        rows.append({"strategy": "disjoint_a", "ticker": "T1",
                     "bar_date": pd.Timestamp(f"2024-01-{d:02d}"),
                     "direction": "long", "fires": True})
    for d in range(15, 25):
        rows.append({"strategy": "disjoint_b", "ticker": "T1",
                     "bar_date": pd.Timestamp(f"2024-01-{d:02d}"),
                     "direction": "long", "fires": True})
    rows_df = pd.DataFrame(rows)
    sim_df = compute_pairwise_similarity(rows_df, n_bars_total=1000)
    assert len(sim_df) == 1
    assert sim_df.iloc[0]["n_both"] == 0
    assert sim_df.iloc[0]["jaccard"] == 0.0
    # Phi for disjoint events is slightly negative under contingency math
    # (we're observing that A and B never co-occur, which is anti-correlation)
    assert sim_df.iloc[0]["phi_correlation"] <= 0.0


# ---------------------------------------------------------------------------
# Pin 11: compute_pairwise_similarity only emits same-direction pairs
# (LONG vs LONG, SHORT vs SHORT; never LONG vs SHORT). This is intentional
# per the COUNCIL "orthogonal return stream" framing -- LONG and SHORT are
# different directional bets and should not be Jaccard-compared directly.
# ---------------------------------------------------------------------------
def test_pin11_similarity_emits_only_same_direction_pairs():
    rows = [
        {"strategy": "a", "ticker": "T1",
         "bar_date": pd.Timestamp("2024-01-01"),
         "direction": "long", "fires": True},
        {"strategy": "b", "ticker": "T1",
         "bar_date": pd.Timestamp("2024-01-01"),
         "direction": "long", "fires": True},
        {"strategy": "a", "ticker": "T1",
         "bar_date": pd.Timestamp("2024-01-02"),
         "direction": "short", "fires": True},
        {"strategy": "b", "ticker": "T1",
         "bar_date": pd.Timestamp("2024-01-02"),
         "direction": "short", "fires": True},
    ]
    rows_df = pd.DataFrame(rows)
    sim_df = compute_pairwise_similarity(rows_df, n_bars_total=100)
    # Expected: 2 rows total -- (a-long, b-long), (a-short, b-short).
    # NO row for (a-long, b-short) or (a-short, b-long) per design.
    assert len(sim_df) == 2
    directions = set(sim_df["direction"].tolist())
    assert directions == {"long", "short"}


# ---------------------------------------------------------------------------
# Pin 12: empty rows_df returns empty similarity_df (not a crash)
# ---------------------------------------------------------------------------
def test_pin12_empty_rows_df_returns_empty_similarity():
    rows_df = pd.DataFrame(columns=[
        "strategy", "ticker", "bar_date", "direction", "fires",
    ])
    sim_df = compute_pairwise_similarity(rows_df, n_bars_total=0)
    assert len(sim_df) == 0
    assert list(sim_df.columns) == [
        "strategy_a", "strategy_b", "direction", "n_a", "n_b",
        "n_both", "jaccard", "phi_correlation",
    ]
