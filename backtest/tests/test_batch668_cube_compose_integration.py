"""Batch 668 (2026-06-09) -- Stage-D cube replay integration of the
COMPOSE multi-testing correction layer per MULTIPLE_TESTING_METHODOLOGY.md
6 owner-approved decisions.

Pins:

cube_compose_verdict aggregation (decisions 3 + 5 wire-in):
  (1)  compute_cube_compose_verdict returns empty on empty df
  (2)  compute_cube_compose_verdict returns empty when strategy column
       missing
  (3)  compute_cube_compose_verdict aggregates per-strategy per-regime +
       overall (regime=None aggregation across all regimes)
  (4)  direction column from df_trades flows into the result's direction
       column (per-direction families per Decision 5)

EXPLORATORY non-penalization in cube path (Decision 4):
  (5)  EXPLORATORY strategy (pivot_s3_capitulation) appears in output
       with results but does NOT change deployable family size

CSV emission wiring (writer integration):
  (6)  emit_cube_compose_verdict_csv writes the CSV when df_trades has
       data + returns summary dict with n_cells / n_passes / etc.
  (7)  emit_cube_compose_verdict_csv handles empty df gracefully
       (returns written=False, no exception)

Discrepancy diagnostic (per methodology BH-vs-COMPOSE sanity check):
  (8)  discrepancy_count is the count of cells where BH-FDR significance
       != COMPOSE pass (raw diagnostic; not a verdict by itself)

Writer integration (smoke):
  (9)  writer.py imports + calls emit_cube_compose_verdict_csv without
       crashing on a simulated multi-strategy trade log
"""
from __future__ import annotations

import pandas as pd


# ============ Aggregation pins ============

def test_batch668_empty_df_returns_empty_result():
    """Pin (1): empty df -> empty DataFrame result."""
    from backtest.results.cube_compose_verdict import compute_cube_compose_verdict
    result = compute_cube_compose_verdict(pd.DataFrame())
    assert result.empty


def test_batch668_missing_strategy_column_returns_empty():
    """Pin (2): df without strategy column -> empty."""
    from backtest.results.cube_compose_verdict import compute_cube_compose_verdict
    df = pd.DataFrame({"pnl_pct": [0.01, 0.02, 0.03]})
    result = compute_cube_compose_verdict(df)
    assert result.empty


def test_batch668_per_regime_and_overall_aggregation():
    """Pin (3): per-strategy per-regime aggregation + overall regime=None."""
    from backtest.results.cube_compose_verdict import compute_cube_compose_verdict
    df = pd.DataFrame({
        "strategy": ["A"] * 60 + ["B"] * 60,
        "regime_at_entry": (["bull"] * 30 + ["bear"] * 30) * 2,
        "direction": ["long"] * 120,
        "pnl_pct": [0.01] * 60 + [0.02] * 60,
    })
    result = compute_cube_compose_verdict(
        df, spa_bootstrap_iters=10,  # fast smoke
    )
    # Per-regime: A_bull, A_bear, B_bull, B_bear = 4
    # Overall: A_overall, B_overall = 2
    # Total 6 cells
    strategies = set(result["strategy"].unique())
    regimes = set(result["regime"].unique())
    assert "A" in strategies and "B" in strategies
    assert "bull" in regimes and "bear" in regimes and "overall" in regimes
    assert len(result) == 6


def test_batch668_direction_flows_through():
    """Pin (4): direction column from df_trades flows to result."""
    from backtest.results.cube_compose_verdict import compute_cube_compose_verdict
    df = pd.DataFrame({
        "strategy": ["long_strat"] * 30 + ["short_strat"] * 30,
        "direction": ["long"] * 30 + ["short"] * 30,
        "pnl_pct": [0.01] * 30 + [0.01] * 30,
    })
    result = compute_cube_compose_verdict(
        df, spa_bootstrap_iters=10,
    )
    long_rows = result[result["strategy"] == "long_strat"]
    short_rows = result[result["strategy"] == "short_strat"]
    assert (long_rows["direction"] == "long").all()
    assert (short_rows["direction"] == "short").all()


# ============ EXPLORATORY non-penalization (Decision 4) ============

def test_batch668_exploratory_does_not_inflate_deployable_family_size():
    """Pin (5): EXPLORATORY strategy in trade log appears in output but
    does NOT change deployable strategies' deflated Sharpe.

    Two trade logs identical except one adds an EXPLORATORY strategy.
    The deployable strategies' deflated_sharpe values MUST match across
    the two runs (Decision 4 critique #7 circularity resolution)."""
    from backtest.results.cube_compose_verdict import compute_cube_compose_verdict
    # Trade log A: 3 deployable strategies
    df_a = pd.DataFrame({
        "strategy": ["deploy_1"] * 30 + ["deploy_2"] * 30 + ["deploy_3"] * 30,
        "direction": ["long"] * 90,
        "pnl_pct": [0.01] * 90,
    })
    # Trade log B: same 3 deployable + 1 EXPLORATORY (pivot_s3_capitulation)
    df_b = pd.DataFrame({
        "strategy": (
            ["deploy_1"] * 30 + ["deploy_2"] * 30 + ["deploy_3"] * 30
            + ["pivot_s3_capitulation"] * 30
        ),
        "direction": ["long"] * 120,
        "pnl_pct": [0.01] * 120,
    })

    result_a = compute_cube_compose_verdict(df_a, spa_bootstrap_iters=10)
    result_b = compute_cube_compose_verdict(df_b, spa_bootstrap_iters=10)

    # Filter to deployable strategies + overall regime
    def deployable_overall(df):
        return df[
            (df["strategy"].isin(["deploy_1", "deploy_2", "deploy_3"]))
            & (df["regime"] == "overall")
        ].sort_values("strategy").reset_index(drop=True)

    a_deploy = deployable_overall(result_a)
    b_deploy = deployable_overall(result_b)
    assert len(a_deploy) == 3 and len(b_deploy) == 3
    # Deflated Sharpe must match across runs (EXPLORATORY didn't inflate N)
    for col in ("deflated_sharpe", "deflated_sharpe_pvalue"):
        a_vals = a_deploy[col].tolist()
        b_vals = b_deploy[col].tolist()
        for av, bv in zip(a_vals, b_vals):
            assert abs(av - bv) < 1e-6, (
                f"Decision 4 violation: EXPLORATORY presence changed "
                f"deployable {col}: A={av}, B={bv}"
            )


# ============ CSV emission ============

def test_batch668_csv_emission_writes_file(tmp_path):
    """Pin (6): emit_cube_compose_verdict_csv writes the file + returns
    summary dict."""
    from backtest.results.cube_compose_verdict import emit_cube_compose_verdict_csv
    df = pd.DataFrame({
        "strategy": ["A"] * 30 + ["B"] * 30,
        "direction": ["long"] * 60,
        "pnl_pct": [0.01] * 30 + [0.02] * 30,
    })
    csv_path = tmp_path / "cube_compose_verdict.csv"
    summary = emit_cube_compose_verdict_csv(
        df, csv_path, spa_bootstrap_iters=10,
    )
    assert summary.get("written") is True
    assert csv_path.exists()
    written_df = pd.read_csv(csv_path)
    assert len(written_df) > 0
    assert "deflated_sharpe" in written_df.columns
    assert "spa_pvalue" in written_df.columns
    assert "passes_compose" in written_df.columns


def test_batch668_csv_emission_empty_df_no_crash(tmp_path):
    """Pin (7): empty df returns written=False without crashing."""
    from backtest.results.cube_compose_verdict import emit_cube_compose_verdict_csv
    csv_path = tmp_path / "cube_compose_verdict.csv"
    summary = emit_cube_compose_verdict_csv(
        pd.DataFrame(), csv_path,
    )
    assert summary.get("written") is False
    assert not csv_path.exists()


# ============ Discrepancy diagnostic ============

def test_batch668_discrepancy_count_is_diagnostic_only():
    """Pin (8): discrepancy_count counts cells where BH != COMPOSE.

    Not a verdict by itself per methodology -- this is the sanity-check
    diagnostic. Owner reviews discrepancies; high count flags
    methodology disagreement that may need re-evaluation."""
    from backtest.results.cube_compose_verdict import emit_cube_compose_verdict_csv
    import tempfile
    from pathlib import Path
    # Construct a trade log where some strategies will likely pass BH but
    # not COMPOSE (weak positive signal). Exact ratio depends on bootstrap
    # so we just verify the field is present + non-negative.
    df = pd.DataFrame({
        "strategy": [f"s_{i}" for i in range(10) for _ in range(30)],
        "direction": ["long"] * 300,
        "pnl_pct": [0.005 + 0.001 * i for i in range(10) for _ in range(30)],
    })
    with tempfile.TemporaryDirectory() as td:
        csv_path = Path(td) / "test.csv"
        summary = emit_cube_compose_verdict_csv(
            df, csv_path, spa_bootstrap_iters=50,
        )
        assert "discrepancy_count" in summary
        assert summary["discrepancy_count"] >= 0


# ============ Writer integration smoke ============

def test_batch668_writer_integration_smoke(tmp_path):
    """Pin (9): writer.py path imports + calls emit_cube_compose_verdict
    on a simulated trade log without crashing.

    Smoke verifies the wiring path is intact. The actual writer.py runs
    in an end-to-end backtest harness; this pin tests the module-level
    integration only."""
    # Build trade log mirroring what writer.py would pass
    df = pd.DataFrame({
        "strategy": ["insider_cluster_long"] * 40 + ["rsi_oversold"] * 40,
        "regime_at_entry": (["bull"] * 20 + ["bear"] * 20) * 2,
        "direction": ["long"] * 80,
        "pnl_pct": [0.01] * 40 + [-0.005] * 40,
    })
    # Direct call to the wrapper (writer.py uses identical path)
    from backtest.results.cube_compose_verdict import emit_cube_compose_verdict_csv
    csv_path = tmp_path / "cube_compose_verdict.csv"
    summary = emit_cube_compose_verdict_csv(
        df, csv_path, spa_bootstrap_iters=10,
    )
    assert summary["written"] is True
    # Sanity: both strategies should appear; overall + per-regime cells
    written_df = pd.read_csv(csv_path)
    strategies = set(written_df["strategy"].unique())
    assert "insider_cluster_long" in strategies
    assert "rsi_oversold" in strategies
