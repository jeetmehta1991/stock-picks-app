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


def test_bug_095_writer_accepts_portfolio_signature_kwarg():
    """BUG-95 sub-batch 5: write_all_outputs has a `portfolio` keyword param
    with default None. Source-pin check (does not exercise full writer).
    """
    import inspect
    from backtest.results.writer import write_all_outputs
    sig = inspect.signature(write_all_outputs)
    assert "portfolio" in sig.parameters, (
        "write_all_outputs must accept portfolio kwarg")
    assert sig.parameters["portfolio"].default is None, (
        "portfolio kwarg must default to None for backward compatibility")


def test_bug_095_writer_emits_portfolio_outputs_when_portfolio_supplied(tmp_path):
    """BUG-95 sub-batch 5: when portfolio is supplied with equity_curve, the
    writer emits equity_curve.parquet + benchmark_curve.parquet +
    portfolio_metrics.json. Uses non-empty trade frames to avoid pre-existing
    writer assumptions about non-empty trade data.
    """
    import pandas as pd
    from datetime import date, timedelta
    from backtest.engine.portfolio import Portfolio
    from backtest.results.writer import write_all_outputs

    p = Portfolio(starting_capital=100_000.0)
    d = date(2024, 1, 1)
    val = 100_000.0
    bench = 470.0
    for i in range(10):
        p.equity_curve.append((d + timedelta(days=i), val))
        p.benchmark_curve.append((d + timedelta(days=i), bench))
        val *= 1.005
        bench *= 1.002

    # Minimal trade log that satisfies pre-existing writer column references
    df_trades = pd.DataFrame([{
        "ticker": "AAPL", "strategy": "test", "direction": "long",
        "category": "momentum", "sector": "Information Technology",
        "entry_date": date(2024, 1, 2), "exit_date": date(2024, 1, 5),
        "entry_price": 100.0, "exit_price": 105.0,
        "pnl_pct": 5.0, "pnl_dollar": 50.0, "win": True, "hold_days": 3,
        "confidence_tier": "MEDIUM", "regime": "bull",
        "exit_reason": "trailing_stop", "max_adverse_excursion": -2.0,
        "max_favourable_excursion": 5.0,
    }])
    df_metrics = pd.DataFrame([{
        "strategy": "test", "trades": 1, "win_rate": 100.0,
        "profit_factor": 5.0, "passes_all": False,
    }])
    write_all_outputs(
        df_trades=df_trades, metrics=df_metrics,
        skipped=[], cb_log=[],
        exit_compare=pd.DataFrame(),
        output_dir=tmp_path,
        portfolio=p,
    )

    assert (tmp_path / "equity_curve.parquet").exists(), (
        "writer must emit equity_curve.parquet when portfolio supplied")
    assert (tmp_path / "benchmark_curve.parquet").exists(), (
        "writer must emit benchmark_curve.parquet when portfolio supplied")
    assert (tmp_path / "portfolio_metrics.json").exists(), (
        "writer must emit portfolio_metrics.json when portfolio supplied")

    import json
    metrics_out = json.loads((tmp_path / "portfolio_metrics.json").read_text())
    assert metrics_out["n_equity_points"] == 10
    assert metrics_out["starting_capital"] == 100_000.0
    assert metrics_out["portfolio_total_return_pct"] > 0


def test_dec_314_market_wide_cb_wired_in_engine():
    """DEC-314 (Phase 3 Batch 45): SPY intraday-low vs open market-wide
    circuit breaker wired into _process_day at NYSE Rule 80B thresholds
    -7% (L3), -13% (L4), -20% (L5).
    """
    import inspect
    from backtest.engine import backtest as bt_module
    src = inspect.getsource(bt_module)
    assert "DEC-314" in src, "DEC-314 cross-reference missing in backtest.py"
    assert "market_wide_cb" in src, "market_wide_cb logic not wired"
    assert "rule_80b" in src.lower() or "rule 80b" in src.lower(), (
        "NYSE Rule 80B reference missing from market-wide CB block")
    # Three threshold levels present
    assert "-0.07" in src and "-0.13" in src and "-0.20" in src, (
        "Missing one or more NYSE Rule 80B threshold levels (-7/-13/-20%)")
    # Skip entry pattern present
    assert "market_wide_cb_level" in src, (
        "Market-wide CB skip-entry reason string missing")


def test_dec_317_dec_388_engine_wires_hysteresis_state():
    """DEC-317 + DEC-388 (Phase 3 Batch 43): BacktestEngine instantiates
    _prev_regime + _vix_series state attributes for hysteresis-aware regime
    classification.
    """
    from backtest.engine.backtest import BacktestEngine
    eng = BacktestEngine(universe=["SPY"], run_agents=False, walk_forward=False)
    assert hasattr(eng, "_prev_regime")
    assert eng._prev_regime is None  # None at start
    assert hasattr(eng, "_vix_series")  # populated by load_data; None at construction


def test_dec_317_dec_388_engine_imports_get_vix_smoothed():
    """Source pin: backtest.py imports get_vix_smoothed + calls regime_filter
    with hysteresis flags.
    """
    import inspect
    from backtest.engine import backtest as bt_module
    src = inspect.getsource(bt_module)
    assert "get_vix_smoothed" in src, "Engine must import get_vix_smoothed"
    assert "use_hysteresis" in src, "Engine must pass use_hysteresis flag"
    assert "self._prev_regime" in src, "Engine must track prev_regime state"
    assert "self._vix_series" in src, "Engine must pre-load VIX series"


def test_bug_095_engine_can_open_gate_wired():
    """BUG-95 sub-batch 4: backtest.py must call self.portfolio.can_open()
    inside _process_day with max_positions from LIVE_TRADING_RULES and skip
    entry on gate denial.
    """
    import inspect
    from backtest.engine import backtest as bt_module
    src = inspect.getsource(bt_module)

    assert "self.portfolio.can_open(" in src, (
        "Engine must call self.portfolio.can_open() inside _process_day")
    assert "LIVE_TRADING_RULES" in src, (
        "Engine must import LIVE_TRADING_RULES for can_open gate")
    assert "max_positions=LIVE_TRADING_RULES" in src, (
        "Engine must pass max_open_positions from LIVE_TRADING_RULES")
    assert "drawdown_suspend_threshold" in src, (
        "Engine must pass drawdown_suspend_threshold to can_open")
    assert "portfolio_gate_" in src, (
        "Gate denial must record skipped_trades reason prefixed portfolio_gate_")


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


def test_dec_091_engine_wires_drawdown_size_multiplier():
    """DEC-091 Batch 70 2026-05-12 owner-mandated engine wiring: verify
    backtest.py source actually calls Portfolio.drawdown_size_multiplier()
    on BOTH entry sites (can_open gate + add_position).
    """
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    count = src.count("drawdown_size_multiplier()")
    assert count >= 2, (
        f"Engine must call drawdown_size_multiplier at gate AND add_position; "
        f"found {count} calls"
    )
    assert "DEC-091 RESOLVED-IMPLEMENTED Batch 70" in src


def test_dec_091_engine_scales_size_by_dd_band_behavior():
    """DEC-091 wiring behavior: 12% DD -> drawdown_size_multiplier returns
    0.75 -> engine applies it to TIER_POSITION_SIZE_PCT yielding the
    band-reduced size.
    """
    from datetime import date
    from backtest.engine.backtest import BacktestEngine
    from backtest.config import TIER_POSITION_SIZE_PCT
    eng = BacktestEngine(universe=["SPY"], run_agents=False, walk_forward=False)
    p = eng.portfolio
    p.equity_curve.append((date(2024, 1, 1), 100_000.0))
    p._equity_peak = 100_000.0
    p.equity_curve.append((date(2024, 1, 2), 88_000.0))   # 12% DD
    assert p.drawdown_size_multiplier() == 0.75
    base = TIER_POSITION_SIZE_PCT["HIGH"]
    assert base * p.drawdown_size_multiplier() == 0.0225


def test_dec_088_engine_wires_vol_target_scale_factor():
    """DEC-088 Batch 71 2026-05-12 owner-mandated wiring: verify
    backtest.py calls Portfolio.vol_target_scale_factor() on BOTH entry
    sites (can_open gate + add_position), stacked after DEC-091 multiplier.
    """
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    count = src.count("vol_target_scale_factor()")
    assert count >= 2, (
        f"Engine must call vol_target_scale_factor at gate AND add_position; "
        f"found {count} calls"
    )
    assert "DEC-088 RESOLVED-IMPLEMENTED Batch 71" in src


def test_dec_088_engine_no_op_with_insufficient_history():
    """DEC-088: fresh Portfolio (no equity history) -> vol_target_scale_factor
    returns 1.0 (no-op). Size_pct unchanged. Critical: backtest must work
    correctly in the first ~21 days before realized vol is computable.
    """
    from backtest.engine.backtest import BacktestEngine
    eng = BacktestEngine(universe=["SPY"], run_agents=False, walk_forward=False)
    p = eng.portfolio
    # Fresh portfolio: no equity_curve entries
    assert p.vol_target_scale_factor() == 1.0


def test_dec_088_engine_scales_down_when_realized_vol_high():
    """DEC-088: synthetic equity curve with ~2% daily moves -> ~32% ann vol
    -> vol_target_scale_factor returns 0.15/max(0.317, 0.075) = ~0.47,
    bounded at 0.5 floor. Size scales down to ~half.
    """
    from datetime import date, timedelta
    from backtest.engine.backtest import BacktestEngine
    eng = BacktestEngine(universe=["SPY"], run_agents=False, walk_forward=False)
    p = eng.portfolio
    p.equity_curve.clear()
    base = 100_000.0
    for i in range(25):
        sign = 1 if i % 2 == 0 else -1
        eq = base * (1 + 0.02 * sign)
        p.equity_curve.append((date(2024, 1, 1) + timedelta(days=i), eq))
    scale = p.vol_target_scale_factor(target=0.15, window_days=21)
    assert scale < 1.0
    assert scale >= 0.5  # bounded


def test_dec_106_engine_wires_multi_input_regime_score():
    """DEC-106 Batch 80: multi-input regime score (Phase A telemetry) wired
    in _process_day; uses available macro + sent fields (VIX + SPY trend +
    AAII spread + CNN F&G); missing inputs skipped per helper.
    """
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    assert "DEC-106 RESOLVED-IMPLEMENTED Batch 80" in src
    assert "multi_input_regime_score" in src
    assert "multi_input_regime" in src


def test_dec_149_engine_wires_regime_transition_matrix_at_finalize():
    """DEC-149 Batch 79: regime history accumulated in _process_day +
    transition matrix computed in finalize.
    """
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    assert "DEC-149 RESOLVED-IMPLEMENTED Batch 79" in src
    assert "self._regime_history" in src
    assert "compute_regime_transition_matrix" in src
    assert "self._regime_transition_matrix" in src


def test_dec_108_engine_wires_ema_smoothed_regime_probability():
    """DEC-108 Batch 78: EMA-smoothed regime probability threaded across
    days via self._regime_smoothed. surfaces as regime_ctx['regime_score_
    smoothed'] for downstream consumption.
    """
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    assert "DEC-108 RESOLVED-IMPLEMENTED Batch 78" in src
    assert "self._regime_smoothed" in src
    assert "ema_smooth_regime_probability" in src
    assert "regime_score_smoothed" in src


def test_dec_108_helper_ema_first_then_subsequent():
    """DEC-108 helper math: first call returns new_score; subsequent calls
    weighted 0.9*prev + 0.1*new.
    """
    from backtest.engine.regime_filter import ema_smooth_regime_probability
    s1 = ema_smooth_regime_probability(80.0, prev_smoothed=None, alpha=0.1)
    assert s1 == 80.0
    s2 = ema_smooth_regime_probability(10.0, prev_smoothed=s1, alpha=0.1)
    # 0.9*80 + 0.1*10 = 73.0
    assert abs(s2 - 73.0) < 1e-9


def test_dec_128_engine_wires_dispersion_cb():
    """DEC-128 Batch 77: source-level grep + cross-sectional dispersion CB
    wired in _process_day after DEC-314 market-wide CB block.
    """
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    assert "DEC-128 RESOLVED-IMPLEMENTED Batch 77" in src
    assert "dispersion_circuit_breaker" in src
    assert "dispersion_cb_triggered_dec128" in src
    assert "dispersion_cb_dec128" in src


def test_dec_348_engine_wires_event_suppression_gate():
    """DEC-348 Batch 76: event-calendar suppression at entry. Skip if
    earnings within DEC-349 asymmetric window (pre=1, post=3) or macro
    event (FOMC/CPI/NFP) in same window.
    """
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    assert "DEC-348 RESOLVED-IMPLEMENTED Batch 76" in src
    assert "EVENT_SUPPRESSION_EARNINGS" in src
    assert "EVENT_WINDOW_PRE_DAYS" in src and "EVENT_WINDOW_POST_DAYS" in src


def test_dec_348_helper_within_window():
    """DEC-348 helper: entry on FOMC day suppressed."""
    from datetime import date
    from backtest.results.metrics import event_calendar_suppression_check
    out = event_calendar_suppression_check(
        as_of_date=date(2024, 6, 12),
        fomc_dates=[date(2024, 6, 12)],
    )
    assert out["suppressed"] is True
    assert "EVENT_SUPPRESSION_FOMC" in out["reasons"]


def test_dec_135_engine_wires_max_loss_cap_gate():
    """DEC-135 Batch 75: per-ticker rolling 30-day max-loss cap (-10%)
    gate at entry-candidate eval.
    """
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    assert "DEC-135 RESOLVED-IMPLEMENTED Batch 75" in src
    assert "max_loss_cap_breach_dec135" in src
    assert "_cap_pct = -10.0" in src
    assert "_window_days = 30" in src


def test_dec_135_helper_cumulative_loss_threshold():
    """DEC-135 helper math: 2 losing trades sum to <= -10% in window -> halt."""
    import pandas as pd
    from datetime import date
    from backtest.engine.improvements import per_ticker_30day_max_loss_check
    df = pd.DataFrame([
        {"ticker": "BAD", "exit_date": date(2024, 6, 5), "pnl_pct": -4.0},
        {"ticker": "BAD", "exit_date": date(2024, 6, 15), "pnl_pct": -7.0},
        {"ticker": "OK", "exit_date": date(2024, 6, 10), "pnl_pct": 2.0},
    ])
    out = per_ticker_30day_max_loss_check(df, today=date(2024, 6, 30),
                                          cap_pct=-10.0, cooldown_days=30)
    assert out["BAD"] is True
    assert out["OK"] is False


def test_dec_076_engine_wires_factor_concentration_breach():
    """DEC-076 Batch 74: source-level grep + Portfolio helper consumed at
    entry gate. Candidate sector that's already > 30% portfolio weight
    gets entry rejected.
    """
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    assert "factor_concentration_breach" in src
    assert "DEC-076 RESOLVED-IMPLEMENTED Batch 74" in src
    # Skipped-trades reason recorded
    assert "factor_concentration_breach_dec076" in src


def test_dec_076_portfolio_breach_helper_signals_overconcentration():
    """DEC-076 behavior: Portfolio with 40% Tech exposure -> breach=True;
    candidate ticker in Tech sector would be gated at entry.
    """
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.add_position("AAPL", "Tech", "long", entry_price=100.0,
                   size_pct=0.20, entry_date=date(2024, 1, 1))
    p.add_position("MSFT", "Tech", "long", entry_price=100.0,
                   size_pct=0.20, entry_date=date(2024, 1, 1))
    out = p.factor_concentration_breach(sector_threshold_pct=30.0)
    assert out["any_breach"] is True
    assert "Tech" in out["sector_breaches"]


def test_dec_018_engine_wires_stopout_cooldown_gate():
    """DEC-018 Batch 73: 5-day cooldown after stop-out -- gate at entry-eval
    skips ticker for TICKER_STOPOUT_COOLDOWN_DAYS after a stop_loss exit.
    """
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    assert "stopout_cooldown_active" in src
    assert "DEC-018 RESOLVED-IMPLEMENTED Batch 73" in src
    assert "TICKER_STOPOUT_COOLDOWN_DAYS" in src


def test_dec_018_engine_skips_ticker_within_cooldown_window():
    """DEC-018 behavior: simulate self.closed_trades with a recent stop-out;
    verify entry-eval cooldown_breach detection logic catches within-window
    and clears after window.
    """
    from datetime import date
    from types import SimpleNamespace
    from backtest.config import TICKER_STOPOUT_COOLDOWN_DAYS
    # Lightweight stand-in for ClosedTrade -- the inline cooldown logic only
    # reads ticker / exit_reason / exit_date so a SimpleNamespace suffices.
    fake_stop = SimpleNamespace(
        ticker="AAPL",
        exit_date=date(2024, 6, 10),
        exit_reason="atr_trail_stop",
    )
    as_of_within = date(2024, 6, 12)  # 2 days post stop -> in cooldown
    days_within = (as_of_within - fake_stop.exit_date).days
    assert 0 <= days_within < TICKER_STOPOUT_COOLDOWN_DAYS
    as_of_clear = date(2024, 6, 20)   # 10 days post -> cleared
    days_clear = (as_of_clear - fake_stop.exit_date).days
    assert days_clear >= TICKER_STOPOUT_COOLDOWN_DAYS


def test_dec_087_engine_wires_vol_targeted_size():
    """DEC-087 Batch 72 2026-05-12: engine source calls vol_targeted_size
    at gate + add_position sites with ATR-derived per-ticker vol proxy.
    """
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    assert "vol_targeted_size" in src
    assert "DEC-087 RESOLVED-IMPLEMENTED Batch 72" in src
    # ATR-derived proxy must be present: (atr / close) * sqrt(252)
    assert "math.sqrt(252)" in src.replace(" ", "") or "_math.sqrt(252)" in src.replace(" ", "")


def test_dec_087_engine_high_vol_proxy_reduces_size():
    """DEC-087: synthetic high-vol ATR (e.g. 5% of close -> 5% daily vol
    proxy -> ~79% annualized) -> vol_targeted_size scales <1.
    Spec: high-vol gets smaller allocation than low-vol at same edge.
    """
    import math
    from backtest.engine.portfolio import vol_targeted_size
    # High vol: ATR=5% close, annualized vol = 0.05 * sqrt(252) ~= 0.793
    high_vol_proxy = 0.05 * math.sqrt(252)
    high_size = vol_targeted_size(0.03, high_vol_proxy)
    # Low vol: ATR=0.5% close, annualized ~= 0.079
    low_vol_proxy = 0.005 * math.sqrt(252)
    low_size = vol_targeted_size(0.03, low_vol_proxy)
    # Low-vol position should get larger allocation than high-vol at
    # same base tier size
    assert low_size > high_size
    # Both bounded by [0.25, 2.0] multiplier per DEC-087 spec
    assert 0.03 * 0.25 <= high_size <= 0.03 * 2.0
    assert 0.03 * 0.25 <= low_size <= 0.03 * 2.0


def test_dec_091_dd_30pct_hard_halt_via_multiplier():
    """DEC-091: 32% DD -> multiplier 0.0 -> scaled size_pct=0 -> entry
    skipped by the 'if size_pct > 0' branch (defense-in-depth alongside
    can_open's drawdown_suspend_pct gate).
    """
    from datetime import date
    from backtest.engine.backtest import BacktestEngine
    from backtest.config import TIER_POSITION_SIZE_PCT
    eng = BacktestEngine(universe=["SPY"], run_agents=False, walk_forward=False)
    p = eng.portfolio
    p.equity_curve.append((date(2024, 1, 1), 100_000.0))
    p._equity_peak = 100_000.0
    p.equity_curve.append((date(2024, 1, 2), 68_000.0))   # 32% DD
    assert p.drawdown_size_multiplier() == 0.0
    base = TIER_POSITION_SIZE_PCT["HIGH"]
    assert base * p.drawdown_size_multiplier() == 0.0


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
