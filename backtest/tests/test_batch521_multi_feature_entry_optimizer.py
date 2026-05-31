"""Batch 521 (2026-05-31) -- multi-feature entry-side optimizer tests.

Source: per CHECKLIST #77 + DET1-unblock autonomous-batch series.
Queue row: EXECUTION_QUEUE.md item #9 1a-alpha-gate fallback.

Pins:

  (1) `optimize_pairwise` correctly skips same-feature pairings
      (e.g. sm_score_gt_0 + sm_score_le_0 would always intersect to
       0 trades anyway, but the algorithm must not even emit the row)
  (2) min_n_post_filter is respected (rows below the threshold are
      dropped)
  (3) incremental_lift is correctly defined as min over the two
      single-feature lifts (this is what makes the metric
      multi-feature-meaningful)
  (4) sorting is descending by incremental_lift
  (5) the BATCH_414_STRATEGIES set is the same 9 as Batch 501 (so
      paper-trail consistency between the two optimizers holds)
  (6) the production output exists and is non-empty after the
      autonomous run on this branch
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from scripts.entry_side_multi_feature_optimizer import (
    BATCH_414_STRATEGIES,
    _sharpe_approx,
    optimize_pairwise,
)
from scripts.entry_side_threshold_optimizer import (
    BATCH_414_STRATEGIES as B501_STRATEGIES,
)


@pytest.fixture
def synthetic_trades() -> pd.DataFrame:
    """200-row synthetic trade log w/ controllable features."""
    rng = np.random.default_rng(seed=42)
    n = 200
    df = pd.DataFrame({
        "strategy":           ["bollinger_tight"] * n,
        "pnl_pct":            rng.normal(loc=0.01, scale=0.03, size=n),
        "win":                (rng.uniform(size=n) > 0.4).astype(int),
        "smart_money_score":  rng.choice([-1, 0, 1], size=n),
        "macro_score":        rng.choice([-1, 0, 1], size=n),
        "sentiment_score":    rng.choice([-1, 0, 1], size=n),
        "confidence_tier":    rng.choice(
            ["LOW", "MEDIUM", "HIGH"], size=n),
        "regime":             rng.choice(
            ["bull", "neutral", "bear"], size=n),
        "days_to_earnings":   rng.integers(0, 30, size=n),
    })
    return df


def test_batch521_batch_414_strategies_match_batch501():
    """Batch 521 + Batch 501 must score the SAME strategy set so the
    single vs multi-feature paper trail is comparable."""
    assert BATCH_414_STRATEGIES == B501_STRATEGIES, (
        "Strategy set drift between Batch 501 + Batch 521. The point "
        "of 521 is to extend 501's analysis; the strategy lists MUST "
        "match for that to hold."
    )


def test_batch521_no_same_feature_pairings(synthetic_trades):
    """Result must NEVER contain rows where feature_a == feature_b."""
    out = optimize_pairwise(synthetic_trades,
                             strategies=("bollinger_tight",),
                             min_n_post_filter=5)
    assert not out.empty, "synthetic data should produce some rows"
    same_feat = out[out["feature_a"] == out["feature_b"]]
    assert len(same_feat) == 0, (
        f"Found {len(same_feat)} rows with feature_a==feature_b: "
        f"{same_feat[['feature_a','feature_b']].head().to_dict()}"
    )


def test_batch521_min_n_post_filter_respected(synthetic_trades):
    """No row may have n_joint < min_n_post_filter."""
    min_n = 25
    out = optimize_pairwise(synthetic_trades,
                             strategies=("bollinger_tight",),
                             min_n_post_filter=min_n)
    if not out.empty:
        assert (out["n_joint"] >= min_n).all(), (
            f"Found rows with n_joint < {min_n}: "
            f"min n_joint = {out['n_joint'].min()}"
        )


def test_batch521_incremental_lift_is_min_of_singles(synthetic_trades):
    """incremental_lift must equal min(lift_vs_single_a, lift_vs_single_b)
    to row precision (4 decimals).
    """
    out = optimize_pairwise(synthetic_trades,
                             strategies=("bollinger_tight",),
                             min_n_post_filter=5)
    assert not out.empty
    computed = np.minimum(out["lift_vs_single_a"], out["lift_vs_single_b"])
    np.testing.assert_array_almost_equal(
        out["incremental_lift"].values, computed.values, decimal=4,
        err_msg="incremental_lift != min(lift_vs_a, lift_vs_b)",
    )


def test_batch521_sorted_by_incremental_lift_descending(synthetic_trades):
    out = optimize_pairwise(synthetic_trades,
                             strategies=("bollinger_tight",),
                             min_n_post_filter=5)
    if len(out) >= 2:
        diffs = out["incremental_lift"].diff().dropna()
        assert (diffs <= 1e-9).all(), (
            f"output not sorted descending by incremental_lift: "
            f"max upward diff = {diffs.max()}"
        )


def test_batch521_sharpe_approx_zero_for_constant_pnl():
    """Sentinel: zero std => zero Sharpe."""
    constant = np.array([0.01] * 50)
    assert _sharpe_approx(constant) == 0.0


def test_batch521_sharpe_approx_zero_for_singleton():
    """Sentinel: 1-element series can't compute Sharpe."""
    assert _sharpe_approx(np.array([0.05])) == 0.0


def test_batch521_production_output_exists_and_nontrivial():
    """The autonomous-run output must exist + carry the expected
    schema + carry a top-row incremental_lift > 0 (otherwise the
    optimizer surfaced nothing actionable and the batch is wasted).
    """
    out_path = (
        REPO / "output_batch395_final"
        / "entry_threshold_multifeature_candidates.csv"
    )
    if not out_path.exists():
        pytest.skip(
            f"Batch 521 production output absent at {out_path}; "
            f"re-run `scripts/entry_side_multi_feature_optimizer.py`."
        )
    df = pd.read_csv(out_path)
    required_cols = {
        "strategy", "feature_a", "bucket_a", "feature_b", "bucket_b",
        "n_joint", "sharpe_baseline", "sharpe_single_a",
        "sharpe_single_b", "sharpe_joint", "incremental_lift",
    }
    missing = required_cols - set(df.columns)
    assert not missing, f"schema regression -- missing cols: {missing}"
    assert len(df) > 0, "empty output -- nothing for owner to pick from"
    top = df.iloc[0]
    assert top["incremental_lift"] > 0, (
        f"top row has non-positive incremental_lift "
        f"({top['incremental_lift']}); no multi-feature gate beats "
        f"BOTH single-feature gates -- review optimizer logic or "
        f"buckets."
    )


def test_batch521_n_joint_le_min_single_counts(synthetic_trades):
    """n_joint must always be <= min(n_single_a, n_single_b) -- AND
    of two masks can never exceed either mask alone."""
    out = optimize_pairwise(synthetic_trades,
                             strategies=("bollinger_tight",),
                             min_n_post_filter=2)
    if not out.empty:
        violators = out[out["n_joint"] >
                         out[["n_single_a", "n_single_b"]].min(axis=1)]
        assert violators.empty, (
            f"n_joint > min(n_single) for {len(violators)} rows -- "
            f"intersection logic is broken."
        )
