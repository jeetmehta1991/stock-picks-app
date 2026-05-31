"""Batch 501 (2026-05-31) -- entry-side threshold optimizer tests.

Source: per CHECKLIST #77.
Queue row: EXECUTION_QUEUE.md item #9 1A-alpha-gate fallback (entry-
side optimization).
Script: scripts/entry_side_threshold_optimizer.py.
"""
from __future__ import annotations

import pandas as pd
import pytest


def _make_trades(rows):
    return pd.DataFrame(rows, columns=[
        "ticker", "entry_date", "strategy", "regime",
        "smart_money_score", "macro_score", "sentiment_score",
        "confidence_tier", "days_to_earnings",
        "win", "pnl_pct",
    ])


# ---------------------------------------------------------------------------
# Sharpe approx primitive
# ---------------------------------------------------------------------------

def test_batch501_sharpe_approx_empty_returns_zero():
    from scripts.entry_side_threshold_optimizer import _sharpe_approx
    import numpy as np
    assert _sharpe_approx(np.array([])) == 0.0
    assert _sharpe_approx(np.array([1.0])) == 0.0  # n<2 -> 0


def test_batch501_sharpe_approx_zero_std_returns_zero():
    from scripts.entry_side_threshold_optimizer import _sharpe_approx
    import numpy as np
    assert _sharpe_approx(np.array([1.0, 1.0, 1.0])) == 0.0


def test_batch501_sharpe_approx_positive_for_positive_drift():
    from scripts.entry_side_threshold_optimizer import _sharpe_approx
    import numpy as np
    arr = np.array([1.5, 2.0, 1.0, 1.8, 1.2])
    s = _sharpe_approx(arr)
    assert s > 0


# ---------------------------------------------------------------------------
# Baseline computation
# ---------------------------------------------------------------------------

def test_batch501_baseline_per_strategy():
    from scripts.entry_side_threshold_optimizer import _baseline_per_strategy
    rows = [
        ("AAPL", "2024-01-02", "s1", "bull", 1, 0, 0, "HIGH", 10, 1, 2.0),
        ("MSFT", "2024-01-03", "s1", "bull", 0, 0, 0, "HIGH", 20, 1, 1.5),
        ("GOOG", "2024-01-04", "s2", "bear", 1, 1, 0, "LOW",  3,  0, -1.0),
    ]
    base = _baseline_per_strategy(_make_trades(rows))
    assert base["s1"]["n_baseline"] == 2
    assert base["s1"]["wr_baseline"] == pytest.approx(1.0)
    assert base["s2"]["n_baseline"] == 1
    assert base["s2"]["wr_baseline"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# optimize_entry_thresholds end-to-end
# ---------------------------------------------------------------------------

def _build_synthetic_trades_with_smart_money_edge(n_total=120):
    """Build trades where smart_money_score > 0 gives WR=80% and
    smart_money_score <= 0 gives WR=20%. The optimizer should rank
    sm_score_gt_0 with high positive lift."""
    rows = []
    for i in range(n_total):
        is_sm = i % 2 == 0  # half with sm, half without
        win = 1 if (is_sm and i % 5 != 4) else (1 if (not is_sm and i % 5 == 4) else 0)
        pnl = 2.0 if win else -1.0
        rows.append((
            f"T{i}", "2024-01-02", "s1", "bull",
            1 if is_sm else 0,  # smart_money_score
            0, 0, "HIGH", 10, win, pnl,
        ))
    return _make_trades(rows)


def test_batch501_optimizer_finds_smart_money_lift():
    from scripts.entry_side_threshold_optimizer import optimize_entry_thresholds
    trades = _build_synthetic_trades_with_smart_money_edge(120)
    df = optimize_entry_thresholds(trades, strategies=("s1",), min_n_post_filter=10)
    assert not df.empty
    sm_buckets = df[df["feature"] == "smart_money_score"]
    assert not sm_buckets.empty
    # sm_score_gt_0 should have higher Sharpe than baseline
    gt0 = sm_buckets[sm_buckets["bucket"] == "sm_score_gt_0"].iloc[0]
    assert gt0["lift"] > 0, f"expected positive lift, got {gt0['lift']}"
    assert gt0["wr_filtered"] > gt0["wr_baseline"]


def test_batch501_optimizer_skips_small_buckets():
    from scripts.entry_side_threshold_optimizer import optimize_entry_thresholds
    trades = _build_synthetic_trades_with_smart_money_edge(120)
    df = optimize_entry_thresholds(trades, strategies=("s1",),
                                     min_n_post_filter=200)  # too big
    # Should skip all buckets because n=60 per bucket < 200 threshold
    assert df.empty


def test_batch501_optimizer_returns_sorted_by_lift_desc():
    from scripts.entry_side_threshold_optimizer import optimize_entry_thresholds
    trades = _build_synthetic_trades_with_smart_money_edge(120)
    df = optimize_entry_thresholds(trades, strategies=("s1",),
                                     min_n_post_filter=10)
    lifts = df["lift"].tolist()
    assert lifts == sorted(lifts, reverse=True)


def test_batch501_optimizer_skips_unknown_strategy():
    from scripts.entry_side_threshold_optimizer import optimize_entry_thresholds
    trades = _build_synthetic_trades_with_smart_money_edge(120)
    df = optimize_entry_thresholds(trades, strategies=("does_not_exist",),
                                     min_n_post_filter=10)
    assert df.empty


def test_batch501_optimizer_handles_missing_feature_column():
    """Trade log without `macro_score` column shouldn't raise; just skip
    macro_score buckets."""
    from scripts.entry_side_threshold_optimizer import optimize_entry_thresholds
    rows = [
        ("AAPL", "2024-01-02", "s1", "bull", 1, 0, 0, "HIGH", 10, 1, 1.0)
        for _ in range(40)
    ]
    df = _make_trades(rows).drop(columns=["macro_score"])
    out = optimize_entry_thresholds(df, strategies=("s1",), min_n_post_filter=10)
    if not out.empty:
        # macro_score must not be present in the output
        assert "macro_score" not in out["feature"].unique()


def test_batch501_optimizer_handles_all_features_present():
    from scripts.entry_side_threshold_optimizer import optimize_entry_thresholds
    trades = _build_synthetic_trades_with_smart_money_edge(120)
    df = optimize_entry_thresholds(trades, strategies=("s1",),
                                     min_n_post_filter=10)
    features_seen = set(df["feature"].unique())
    # Should include at least these
    assert "smart_money_score" in features_seen
