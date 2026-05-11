"""
Integration tests  -  catch key wiring and data coherency bugs.
Run before every Phase 1B run: python -m pytest backtest/tests/ -v

These tests specifically target bugs found in audits:
- L44: smart_money_score key mismatch
- Trailing stop direction
- Sector map loading
- Walk-forward two-window structure
- Agent pipeline key coherency
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_smart_money_score_keys():
    """L44 regression: smart_money_score must return all keys used by pipeline and engine."""
    from backtest.data.smart_money import smart_money_score
    result = smart_money_score("AAPL", date(2024, 1, 15))

    # Pipeline keys
    pipeline_keys = ["institutional_sig", "insider_sig",
                     "congressional_sig", "smart_money_composite"]
    for k in pipeline_keys:
        assert k in result, f"Pipeline key missing: {k}"
        assert isinstance(result[k], dict), f"{k} should be dict, got {type(result[k])}"

    # Engine keys
    engine_keys = ["composite_signal", "score",
                   "congressional_signal", "insider_signal", "institutional_signal"]
    for k in engine_keys:
        assert k in result, f"Engine key missing: {k}"

    print("[ok] smart_money_score keys correct")


def test_trailing_stop_uses_low_not_close():
    """D5 regression: trailing stop must trigger on intraday low, not close."""
    from backtest.engine.exit_manager import check_trailing_stop_hit, OpenTrade
    from dataclasses import field

    trade = OpenTrade(
        ticker="TEST", entry_date=date(2022,1,1), entry_price=100.0,
        direction="long", strategy="test", category="test", sector="Unknown",
        initial_stop=90.0, trailing_stop=95.0, highest_close=105.0,
        regime_at_entry="bull",
    )

    # Low dips below stop, close above stop  -  should EXIT
    result = check_trailing_stop_hit(trade, today_low=94.0, today_high=101.0, today_close=97.0)
    assert result == 95.0, f"Expected exit at 95.0, got {result}"

    # Low above stop  -  should NOT exit
    result2 = check_trailing_stop_hit(trade, today_low=96.0, today_high=101.0, today_close=99.0)
    assert result2 is None, f"Expected None, got {result2}"

    print("[ok] Trailing stop uses intraday low correctly")


def test_avoid_tier_returned():
    """A9 regression: AVOID tier must be returned when SM signals negative."""
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}

    sm_avoid = {"composite_signal": "congressional_sell+insider_cluster_sell", "score": -5}
    tier = engine._assign_confidence_tier(3, sm_avoid, {}, {})
    assert tier == "AVOID", f"Expected AVOID, got {tier}"

    sm_except = {"composite_signal": "congressional+insider_cluster", "score": 6}
    tier2 = engine._assign_confidence_tier(3, sm_except, {}, {})
    assert tier2 == "EXCEPTIONAL", f"Expected EXCEPTIONAL, got {tier2}"

    print("[ok] Confidence tier AVOID returned correctly")


def test_sector_map_loads_from_csv():
    """Sector map must load from CSV without network calls."""
    from backtest.data.universe import get_sector_map
    sm = get_sector_map(["AAPL", "XOM", "KO", "SPY", "UNKNOWN_TICKER"])
    assert sm["AAPL"] == "Information Technology"
    assert sm["XOM"] == "Energy"
    assert sm["KO"] == "Consumer Staples"
    assert sm["SPY"] == "Broad Market"
    assert sm["UNKNOWN_TICKER"] == "Unknown"
    print("[ok] Sector map loads from CSV")


def test_walk_forward_two_windows():
    """B1 regression: walk-forward must compute 4 folds per DEC-505.

    Pass 53 Day-9 v2 update (2026-05-07): replaced legacy 2-window expectation
    with DEC-505 4-fold expanding-window per WF-1 owner-approved migration.
    Test name retained for git-blame stability; assertions updated.
    """
    import pandas as pd
    import numpy as np
    from backtest.engine.improvements import run_walk_forward

    # Create synthetic trade log spanning 2021-05 -> 2026-05 per DEC-505 window
    n = 500
    dates = pd.date_range("2021-05-05", periods=n, freq="5B")
    df = pd.DataFrame({
        "strategy":   ["test_strat"] * n,
        "entry_date": [d.date() for d in dates],
        "pnl_pct":    np.random.normal(0.8, 3, n),
        "direction":  ["long"] * n,
        "sector":     ["Information Technology"] * n,
    })
    df["win"] = df["pnl_pct"] > 0

    result = run_walk_forward(df)
    assert "strategy_results" in result
    strat = result["strategy_results"].get("test_strat", {})
    assert "windows" in strat, "windows key missing"
    # DEC-505 4-fold: assert all 4 fold names present
    assert "fold_1" in strat["windows"], "fold_1 missing (DEC-505 4-fold)"
    assert "fold_4" in strat["windows"], "fold_4 missing (DEC-505 4-fold)"
    assert len(strat["windows"]) == 4, f"expected 4 folds, got {len(strat['windows'])}"
    assert "verdict" in strat
    assert strat["verdict"] in ["ROBUST", "WEAK", "OVERFIT",
                                 "FAILS_BOTH", "INSUFFICIENT_OOS_DATA"]
    print("[ok] Walk-forward computes 4 folds per DEC-505")


def test_confidence_intervals():
    """A30 regression: confidence intervals must be computed correctly."""
    from backtest.results.metrics import _confidence_interval_95
    lo, hi = _confidence_interval_95(0.55, 200)
    assert 0.48 < lo < 0.55, f"Lower CI bound {lo} unexpected"
    assert 0.55 < hi < 0.62, f"Upper CI bound {hi} unexpected"

    # Low trade count should give wide CI
    lo2, hi2 = _confidence_interval_95(0.55, 30)
    assert hi2 - lo2 > hi - lo, "Low count should give wider CI"
    print("[ok] Confidence intervals computed correctly")


def test_sector_adjusted_criteria():
    """Sector-adjusted criteria must differ by sector."""
    from backtest.config import get_sector_criteria
    energy = get_sector_criteria("Energy")
    staples = get_sector_criteria("Consumer Staples")
    assert energy["min_win_rate"] < staples["min_win_rate"]
    assert energy["max_drawdown"] > staples["max_drawdown"]
    print("[ok] Sector-adjusted criteria differ correctly")


def test_bug_095_engine_instantiates_portfolio():
    """BUG-95 sub-batch 2: BacktestEngine must instantiate self.portfolio."""
    from backtest.engine.backtest import BacktestEngine
    from backtest.engine.portfolio import Portfolio
    from backtest.config import STARTING_CAPITAL
    eng = BacktestEngine(universe=["SPY"], run_agents=False, walk_forward=False)
    assert hasattr(eng, "portfolio")
    assert isinstance(eng.portfolio, Portfolio)
    assert eng.portfolio.starting_capital == STARTING_CAPITAL
    assert eng.portfolio.cash == STARTING_CAPITAL


def test_bug_095_engine_imports_portfolio_module():
    """BUG-95 sub-batch 2 source pin: backtest.py must import Portfolio +
    STARTING_CAPITAL + TIER_POSITION_SIZE_PCT and call mark_to_market /
    add_position / remove_position in the daily lifecycle.
    """
    import inspect
    from backtest.engine import backtest as bt_module
    src = inspect.getsource(bt_module)

    assert "BUG-95" in src, "BUG-95 cross-reference must exist in backtest.py"
    assert "from backtest.engine.portfolio import Portfolio" in src, (
        "backtest.py must import Portfolio class")
    assert "STARTING_CAPITAL" in src, (
        "backtest.py must reference STARTING_CAPITAL config constant")
    assert "TIER_POSITION_SIZE_PCT" in src, (
        "backtest.py must reference TIER_POSITION_SIZE_PCT config constant")
    assert "self.portfolio = Portfolio(starting_capital=" in src, (
        "Engine must instantiate self.portfolio in __init__")
    assert "self.portfolio.mark_to_market(" in src, (
        "Engine must call mark_to_market each day")
    assert "self.portfolio.add_position(" in src, (
        "Engine must call add_position when a trade enters")
    assert "self.portfolio.remove_position(" in src, (
        "Engine must call remove_position when a trade exits")


def test_bug_095_engine_portfolio_lifecycle_minimal():
    """BUG-95 sub-batch 2 lifecycle pin: simulating add+remove on the engine's
    portfolio mirrors what _process_day does.
    """
    from datetime import date
    from backtest.engine.backtest import BacktestEngine
    eng = BacktestEngine(universe=["SPY"], run_agents=False, walk_forward=False)
    p = eng.portfolio
    initial_cash = p.cash

    p.add_position("AAPL", "IT", "long", entry_price=100.0,
                   size_pct=0.03, entry_date=date(2024, 1, 1))
    assert p.num_open == 1
    assert p.cash < initial_cash

    p.mark_to_market({"AAPL": 110.0}, date(2024, 1, 2))
    assert len(p.equity_curve) == 1
    assert p.equity_curve[0][1] > initial_cash

    realised = p.remove_position("AAPL", exit_price=110.0)
    assert realised > 0
    assert p.num_open == 0
    assert p.cash > initial_cash


if __name__ == "__main__":
    tests = [
        test_smart_money_score_keys,
        test_trailing_stop_uses_low_not_close,
        test_avoid_tier_returned,
        test_sector_map_loads_from_csv,
        test_walk_forward_two_windows,
        test_confidence_intervals,
        test_sector_adjusted_criteria,
        test_bug_095_engine_instantiates_portfolio,
        test_bug_095_engine_imports_portfolio_module,
        test_bug_095_engine_portfolio_lifecycle_minimal,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
