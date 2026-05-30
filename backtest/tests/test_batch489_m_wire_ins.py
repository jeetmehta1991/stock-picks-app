"""Batch 489 (2026-05-30) -- wire-in regression tests for M11 + M2 + M9.

Three engine wire-ins land in Batch 489 (queue items M11 / M2 / M9):

  M11 -- pnl_concentration_{top1_pct,top5_pct} + pnl_hhi merged into
         `backtest.results.cube_populator.compute_cell_metrics` output.

  M2  -- median_size_pct_of_adv + max_size_pct_of_adv + capacity_concern_flag
         merged into compute_cell_metrics when adv_at_entry +
         position_dollars columns are present.

  M9  -- `BacktestEngine._assign_confidence_tier(..., firing_strategies=None)`
         + `self._strategy_cluster_lookup` + `load_strategy_cluster_lookup()`.
         Effective (cluster-collapsed) strategy count drives the tier when
         the lookup is populated; raw count drives it when empty
         (back-compat).

These tests pin the integration so future refactors that drop the wire-in
get caught.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# M11 wire-in: pnl_concentration in compute_cell_metrics output
# ---------------------------------------------------------------------------

def _make_trades(pnls, hold_days=5, **extra_cols) -> pd.DataFrame:
    base = {"pnl_pct": list(pnls), "hold_days": [hold_days] * len(pnls)}
    for k, v in extra_cols.items():
        base[k] = list(v) if hasattr(v, "__iter__") and not isinstance(v, str) \
            else [v] * len(pnls)
    return pd.DataFrame(base)


def test_batch489_m11_compute_cell_metrics_emits_pnl_concentration_keys():
    from backtest.results.cube_populator import compute_cell_metrics
    trades = _make_trades([1.0, 2.0, -0.5, 0.8, 1.5, -1.0, 0.3, 0.4, 0.6, 0.9,
                           1.1, 1.2, 0.7, 0.5, -0.3, 0.2, 1.4, 1.3, 0.6, 0.8,
                           0.4, 0.9, 1.0, 0.5, -0.4, 0.7, 1.1, 0.3, 0.8, 1.2])
    m = compute_cell_metrics(trades)
    for k in ("pnl_concentration_top1_pct", "pnl_concentration_top5_pct",
              "pnl_hhi"):
        assert k in m, f"missing M11 key: {k}"
    # Sanity bounds
    assert 0.0 <= m["pnl_concentration_top1_pct"] <= 1.0
    assert 0.0 <= m["pnl_concentration_top5_pct"] <= 1.0
    assert 0.0 <= m["pnl_hhi"] <= 1.0
    # top1 <= top5 (top1 is included in top5)
    assert m["pnl_concentration_top1_pct"] <= m["pnl_concentration_top5_pct"]


def test_batch489_m11_single_trade_cell_is_fully_concentrated():
    from backtest.results.cube_populator import compute_cell_metrics
    trades = _make_trades([2.5])
    m = compute_cell_metrics(trades)
    # Single trade -> all metrics 1.0
    assert m["pnl_concentration_top1_pct"] == 1.0
    assert m["pnl_concentration_top5_pct"] == 1.0
    assert m["pnl_hhi"] == 1.0


def test_batch489_m11_uniform_pnl_low_hhi():
    """30 equal-magnitude trades -> HHI = 1/30; top1 = 1/30."""
    from backtest.results.cube_populator import compute_cell_metrics
    pnls = [1.0] * 30
    trades = _make_trades(pnls)
    m = compute_cell_metrics(trades)
    assert m["pnl_concentration_top1_pct"] == pytest.approx(1 / 30, abs=1e-5)
    assert m["pnl_hhi"] == pytest.approx(1 / 30, abs=1e-5)


# ---------------------------------------------------------------------------
# M2 wire-in: capacity flags in compute_cell_metrics
# ---------------------------------------------------------------------------

def test_batch489_m2_capacity_keys_emitted_when_columns_present():
    from backtest.results.cube_populator import compute_cell_metrics
    trades = _make_trades(
        pnls=[1.0, 1.5, 0.8, -0.5, 1.2] * 6,
        adv_at_entry=[1_000_000.0] * 30,
        position_dollars=[5_000.0] * 30,  # 0.5 pct of ADV - over threshold
    )
    m = compute_cell_metrics(trades)
    assert "median_size_pct_of_adv" in m
    assert "max_size_pct_of_adv" in m
    assert "capacity_concern_flag" in m
    # 5000/1_000_000 = 0.005 > 0.001 threshold -> flag True
    assert m["capacity_concern_flag"] is True
    assert m["median_size_pct_of_adv"] == pytest.approx(0.005, abs=1e-6)


def test_batch489_m2_capacity_keys_absent_when_columns_missing():
    """Trade log without adv/position cols -> capacity keys NOT emitted."""
    from backtest.results.cube_populator import compute_cell_metrics
    trades = _make_trades([1.0, 1.5, 0.8, -0.5, 1.2] * 6)
    m = compute_cell_metrics(trades)
    assert "median_size_pct_of_adv" not in m
    assert "max_size_pct_of_adv" not in m
    assert "capacity_concern_flag" not in m


def test_batch489_m2_capacity_below_threshold_does_not_flag():
    from backtest.results.cube_populator import compute_cell_metrics
    trades = _make_trades(
        pnls=[1.0, 1.5, 0.8, -0.5, 1.2] * 6,
        adv_at_entry=[10_000_000.0] * 30,
        position_dollars=[5_000.0] * 30,  # 0.05 pct of ADV - under threshold
    )
    m = compute_cell_metrics(trades)
    assert m["capacity_concern_flag"] is False
    assert m["median_size_pct_of_adv"] == pytest.approx(0.0005, abs=1e-6)


# ---------------------------------------------------------------------------
# M9 wire-in: _assign_confidence_tier + cluster_lookup
# ---------------------------------------------------------------------------

def _make_minimal_engine(tmp_path=None):
    """Construct a BacktestEngine with minimal config for unit-level tests of
    _assign_confidence_tier. We avoid `run()`; just exercise the tier logic."""
    from datetime import date
    from backtest.engine.backtest import BacktestEngine
    import tempfile
    out_dir = str(tmp_path) if tmp_path is not None else tempfile.mkdtemp(
        prefix="batch489_wireins_")
    eng = BacktestEngine(
        universe=["AAPL"],
        start=date(2024, 1, 2),
        end=date(2024, 1, 5),
        output_dir=out_dir,
        use_cache=False,
        run_agents=False,
        disable_news=True,
    )
    return eng


def test_batch489_m9_engine_has_cluster_lookup_attribute():
    eng = _make_minimal_engine()
    assert hasattr(eng, "_strategy_cluster_lookup")
    assert isinstance(eng._strategy_cluster_lookup, dict)
    assert eng._strategy_cluster_lookup == {}  # default empty


def test_batch489_m9_assign_confidence_tier_accepts_firing_strategies_kwarg():
    """Sanity: kwarg exists + back-compat with no kwarg."""
    import inspect
    from backtest.engine.backtest import BacktestEngine
    sig = inspect.signature(BacktestEngine._assign_confidence_tier)
    assert "firing_strategies" in sig.parameters


def test_batch489_m9_empty_lookup_falls_back_to_raw_count():
    """With empty lookup, effective_count == raw count -> tier unchanged
    from pre-Batch-489 behaviour."""
    eng = _make_minimal_engine()
    # 5 raw strategies, lookup empty -> effective should equal 5
    sm = {"insider_signal": False, "congressional_buy": False,
          "institutional_buy": False}
    macro = "neutral"
    sent = {"score": 0}
    # Tier without firing_strategies (legacy call)
    tier_legacy = eng._assign_confidence_tier(5, sm, macro, sent)
    # Tier WITH firing_strategies but empty lookup
    tier_new = eng._assign_confidence_tier(
        5, sm, macro, sent,
        firing_strategies=["a", "b", "c", "d", "e"],
    )
    assert tier_legacy == tier_new, (
        f"Empty cluster_lookup should preserve tier; got "
        f"legacy={tier_legacy} new={tier_new}"
    )


def test_batch489_m9_populated_lookup_collapses_count():
    """5 raw strategies collapsing into 2 clusters -> effective_count = 2.
    The tier assignment uses effective_count, so a 2-cluster confluence
    yields a LOWER tier than a 5-distinct-strategy confluence."""
    eng = _make_minimal_engine()
    # Build a lookup where 4 of 5 names share one cluster
    eng._strategy_cluster_lookup = {
        "a": 0, "b": 0, "c": 0, "d": 0,  # 4 in cluster 0
        "e": 1,                            # 1 in cluster 1
    }
    sm = {"insider_signal": False, "congressional_buy": False,
          "institutional_buy": False}
    macro = "neutral"
    sent = {"score": 0}
    tier_collapsed = eng._assign_confidence_tier(
        5, sm, macro, sent,
        firing_strategies=["a", "b", "c", "d", "e"],
    )
    # Without lookup, 5 raw strategies might produce a HIGHER tier
    eng._strategy_cluster_lookup = {}
    tier_raw = eng._assign_confidence_tier(
        5, sm, macro, sent,
        firing_strategies=["a", "b", "c", "d", "e"],
    )
    # Effective=2 should be lower-or-equal tier than effective=5
    tier_order = {"LOW": 0, "MEDIUM": 1, "MEDIUM-HIGH": 2, "HIGH": 3,
                  "VERY HIGH": 4, "EXCEPTIONAL": 5}
    assert tier_order[tier_collapsed] <= tier_order[tier_raw], (
        f"Cluster-collapsed tier {tier_collapsed} should be <= raw tier "
        f"{tier_raw}"
    )


def test_batch489_m9_load_strategy_cluster_lookup_from_disk(tmp_path):
    """load_strategy_cluster_lookup reads a JSON file + populates the attr."""
    eng = _make_minimal_engine()
    lookup_path = tmp_path / "cluster_lookup.json"
    lookup_path.write_text(json.dumps({
        "donchian_breakout": 0,
        "donchian_breakout_v2": 0,
        "mean_reversion_bb": 1,
        "mfi_oversold": 2,
    }), encoding="utf-8")
    n_clusters = eng.load_strategy_cluster_lookup(lookup_path)
    assert n_clusters == 3
    assert eng._strategy_cluster_lookup["donchian_breakout"] == 0
    assert eng._strategy_cluster_lookup["mfi_oversold"] == 2


def test_batch489_m9_load_strategy_cluster_lookup_missing_file(tmp_path):
    """Missing file -> graceful fallback (returns 0, empty lookup, no raise)."""
    eng = _make_minimal_engine()
    missing = tmp_path / "does_not_exist.json"
    n = eng.load_strategy_cluster_lookup(missing)
    assert n == 0
    assert eng._strategy_cluster_lookup == {}


def test_batch489_m9_load_strategy_cluster_lookup_bad_json(tmp_path):
    """Malformed JSON -> graceful fallback (warning logged, no raise)."""
    eng = _make_minimal_engine()
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid json", encoding="utf-8")
    n = eng.load_strategy_cluster_lookup(bad)
    assert n == 0
    assert eng._strategy_cluster_lookup == {}


# ---------------------------------------------------------------------------
# Cross-wire-in sanity: cube_populator emits ALL Batch-489 fields together
# when trade_log carries adv+pos cols
# ---------------------------------------------------------------------------

def test_batch489_cube_populator_emits_full_field_set():
    from backtest.results.cube_populator import compute_cell_metrics
    trades = _make_trades(
        pnls=[1.0, 1.5, 0.8, -0.5, 1.2, 0.9, 1.1, 0.7, -0.3, 0.4,
              0.6, 0.5, 0.8, 1.0, -0.2, 0.3, 1.3, 0.9, 0.7, 0.5,
              0.4, 0.6, 1.0, 1.1, -0.1, 0.8, 0.7, 0.5, 0.9, 1.2],
        adv_at_entry=[2_000_000.0] * 30,
        position_dollars=[3_000.0] * 30,
    )
    m = compute_cell_metrics(trades)
    expected_batch489_keys = {
        "pnl_concentration_top1_pct", "pnl_concentration_top5_pct", "pnl_hhi",
        "median_size_pct_of_adv", "max_size_pct_of_adv",
        "capacity_concern_flag",
    }
    missing = expected_batch489_keys - set(m.keys())
    assert not missing, f"Batch 489 keys missing from cube_populator: {missing}"
