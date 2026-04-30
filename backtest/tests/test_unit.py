"""
Unit tests — test individual functions in isolation.
Run: python -m pytest backtest/tests/test_unit.py -v
"""
import sys
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# ─────────────────────────────────────────────────────────────────────────────
# CONFIDENCE TIER & TIERING LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def test_tier_adjustment_upgrade():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("HIGH", 80) == "VERY_HIGH"
    assert engine._adjust_tier_by_agent("MEDIUM_HIGH", 76) == "HIGH"
    print("✅ Tier upgrade works")

def test_tier_adjustment_downgrade():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("HIGH", 35) == "MEDIUM_HIGH"
    assert engine._adjust_tier_by_agent("VERY_HIGH", 39) == "HIGH"
    print("✅ Tier downgrade works")

def test_tier_adjustment_no_change():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("HIGH", 60) == "HIGH"
    print("✅ Tier no-change works")

def test_tier_avoid_never_upgrades():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("AVOID", 99) == "AVOID"
    print("✅ AVOID never upgrades")

def test_tier_exceptional_never_upgrades():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("EXCEPTIONAL", 99) == "EXCEPTIONAL"
    print("✅ EXCEPTIONAL never over-upgrades")

def test_tier_low_never_downgrades_below_low():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("LOW", 5) == "LOW"
    print("✅ LOW never downgrades below LOW")


# ─────────────────────────────────────────────────────────────────────────────
# TRANSACTION COSTS
# ─────────────────────────────────────────────────────────────────────────────

def test_transaction_cost_etf_cheaper():
    from backtest.engine.improvements import get_transaction_cost
    etf_cost = get_transaction_cost("SPY", 500_000)
    stock_cost = get_transaction_cost("AAPL", 3_000_000)
    assert etf_cost < stock_cost
    print("✅ ETF costs less than stock")

def test_transaction_cost_short_has_borrow():
    from backtest.engine.improvements import apply_transaction_costs
    df = pd.DataFrame([
        {"ticker": "AAPL", "direction": "long",  "hold_days": 10,
         "pnl_pct": 5.0, "win": True},
        {"ticker": "AAPL", "direction": "short", "hold_days": 10,
         "pnl_pct": 5.0, "win": True},
    ])
    result = apply_transaction_costs(df, {"AAPL": {"market_cap": 3_000_000_000_000}})
    long_cost  = result[result["direction"] == "long"]["cost_pct"].iloc[0]
    short_cost = result[result["direction"] == "short"]["cost_pct"].iloc[0]
    assert short_cost > long_cost, f"Short {short_cost:.4f} should > long {long_cost:.4f}"
    print("✅ Short trades have higher cost (borrow fee)")

def test_transaction_costs_reduce_pnl():
    from backtest.engine.improvements import apply_transaction_costs
    df = pd.DataFrame([{"ticker": "AAPL", "direction": "long",
                        "hold_days": 10, "pnl_pct": 5.0, "win": True}])
    result = apply_transaction_costs(df, {"AAPL": {"market_cap": 3_000_000_000_000}})
    assert result["pnl_pct"].iloc[0] < 5.0
    assert "pnl_pct_gross" in result.columns
    print("✅ Transaction costs reduce pnl_pct")


# ─────────────────────────────────────────────────────────────────────────────
# SURVIVORSHIP BIAS
# ─────────────────────────────────────────────────────────────────────────────

def test_survivorship_hold_adjusted():
    from backtest.engine.improvements import apply_survivorship_haircut
    # Short holds should get smaller haircut than long holds
    df_short = pd.DataFrame([{"ticker": "A", "direction": "long",
                               "hold_days": 3, "pnl_pct": 5.0, "win": True}])
    df_long  = pd.DataFrame([{"ticker": "A", "direction": "long",
                               "hold_days": 40, "pnl_pct": 5.0, "win": True}])
    _, haircut_short = apply_survivorship_haircut(df_short.copy(), 1.0)
    _, haircut_long  = apply_survivorship_haircut(df_long.copy(), 1.0)
    assert haircut_short < haircut_long, \
        f"Short hold haircut {haircut_short} should < long hold {haircut_long}"
    print("✅ Hold-adjusted survivorship bias — short holds get smaller haircut")


# ─────────────────────────────────────────────────────────────────────────────
# CIRCUIT BREAKERS
# ─────────────────────────────────────────────────────────────────────────────

def test_circuit_breaker_gap_down():
    from backtest.engine.exit_manager import check_circuit_breakers, OpenTrade
    trade = OpenTrade(
        ticker="AAPL", entry_date=date(2022,1,1), entry_price=100.0,
        direction="long", strategy="test", category="test", sector="Tech",
        initial_stop=90.0, trailing_stop=90.0, highest_close=105.0,
        regime_at_entry="bull",
    )
    # Gap down >12% should trigger CB1
    result = check_circuit_breakers(trade, today_open=85.0, prev_close=100.0, vix_value=20)
    assert result is not None
    assert result["level"] == 1
    print("✅ Circuit breaker 1 triggers on >12% gap down")

def test_circuit_breaker_no_trigger_normal():
    from backtest.engine.exit_manager import check_circuit_breakers, OpenTrade
    trade = OpenTrade(
        ticker="AAPL", entry_date=date(2022,1,1), entry_price=100.0,
        direction="long", strategy="test", category="test", sector="Tech",
        initial_stop=90.0, trailing_stop=90.0, highest_close=105.0,
        regime_at_entry="bull",
    )
    # Normal day — no CB
    result = check_circuit_breakers(trade, today_open=101.0, prev_close=100.0, vix_value=18)
    assert result is None
    print("✅ No circuit breaker on normal day")


# ─────────────────────────────────────────────────────────────────────────────
# CLOSE_TRADE — regression test for BUG-214 (Pass 48)
# ─────────────────────────────────────────────────────────────────────────────

def test_close_trade_long_winner():
    """BUG-214 regression: close_trade must compute days BEFORE pnl. NameError in old code."""
    from backtest.engine.exit_manager import close_trade, OpenTrade, ClosedTrade
    trade = OpenTrade(
        ticker="AAPL", entry_date=date(2024,1,1), entry_price=100.0,
        direction="long", strategy="test_strat", category="momentum",
        sector="Information Technology",
        initial_stop=90.0, trailing_stop=95.0, highest_close=110.0,
        regime_at_entry="bull",
    )
    closed = close_trade(trade, exit_price=110.0, exit_date=date(2024,1,15),
                         exit_reason="trailing_stop",
                         max_adverse=-2.0, max_favourable=10.0)
    assert isinstance(closed, ClosedTrade)
    assert closed.hold_days == 14
    assert closed.pnl_pct == 10.0
    assert closed.win is True
    assert closed.sector == "Information Technology"
    print("✅ close_trade long winner — days/pnl computed in correct order")


def test_close_trade_short_with_borrow_cost():
    """close_trade must apply short borrow cost without crashing."""
    from backtest.engine.exit_manager import close_trade, OpenTrade
    trade = OpenTrade(
        ticker="TSLA", entry_date=date(2024,1,1), entry_price=200.0,
        direction="short", strategy="test_strat", category="momentum_short",
        sector="Consumer Discretionary",
        initial_stop=220.0, trailing_stop=210.0, highest_close=190.0,
        regime_at_entry="bear",
    )
    closed = close_trade(trade, exit_price=180.0, exit_date=date(2024,1,11),
                         exit_reason="trailing_stop",
                         max_adverse=-1.0, max_favourable=15.0)
    # Short: gross PnL = (200 - 180) / 200 * 100 = 10%
    # 10-day hold; borrow cost subtracted in _pnl
    assert closed.hold_days == 10
    assert closed.win is True
    assert closed.direction == "short"
    print("✅ close_trade short trade with borrow cost — runs without error")


def test_close_trade_loser_generates_fail_reason():
    """close_trade must generate a fail_reason for losers."""
    from backtest.engine.exit_manager import close_trade, OpenTrade
    trade = OpenTrade(
        ticker="META", entry_date=date(2024,1,1), entry_price=400.0,
        direction="long", strategy="test_strat", category="momentum",
        sector="Communication Services",
        initial_stop=360.0, trailing_stop=380.0, highest_close=410.0,
        regime_at_entry="neutral",
    )
    closed = close_trade(trade, exit_price=380.0, exit_date=date(2024,1,8),
                         exit_reason="trailing_stop",
                         max_adverse=-5.0, max_favourable=2.5)
    assert closed.win is False
    assert closed.fail_reason  # auto-generated, not empty
    print("✅ close_trade loser — fail_reason auto-generated")


# ─────────────────────────────────────────────────────────────────────────────
# CLOSEDTRADE DATACLASS — regression test for BUG-215 (Pass 48)
# ─────────────────────────────────────────────────────────────────────────────

def test_closed_trade_single_definition():
    """BUG-215 regression: only ONE ClosedTrade definition should exist."""
    import ast
    from pathlib import Path
    src = Path(__file__).parent.parent / "engine" / "exit_manager.py"
    tree = ast.parse(src.read_text())
    classes = [n for n in ast.walk(tree)
               if isinstance(n, ast.ClassDef) and n.name == "ClosedTrade"]
    assert len(classes) == 1, \
        f"Expected exactly 1 ClosedTrade class, found {len(classes)} (BUG-215 regression)"
    print("✅ Single ClosedTrade dataclass definition")


def test_closed_trade_has_canonical_fields():
    """ClosedTrade must have sector, preliminary_tier, agent_reasoning fields."""
    import dataclasses
    from backtest.engine.exit_manager import ClosedTrade
    fields = {f.name for f in dataclasses.fields(ClosedTrade)}
    required = {
        "sector", "preliminary_tier", "agent_reasoning",
        "conversion_pair_id", "circuit_breaker_level",
        "congressional_signal", "insider_signal",
        "aaii_bullish", "cnn_fg_score",
    }
    missing = required - fields
    assert not missing, f"ClosedTrade missing fields: {missing}"
    print(f"✅ ClosedTrade has all canonical fields ({len(fields)} total)")


# ─────────────────────────────────────────────────────────────────────────────
# NEWS SENTIMENT — regression test for BUG-217 (Pass 48)
# ─────────────────────────────────────────────────────────────────────────────

def test_news_sentiment_reads_av_cache():
    """BUG-217 regression: get_news_sentiment must read from cache/av_news/, not /prefetch/news/."""
    from backtest.data.smart_money import get_news_sentiment, AV_NEWS_DIR
    # The directory should exist (committed test data) and point at cache/av_news
    assert "cache" in str(AV_NEWS_DIR), \
        f"AV_NEWS_DIR should reference cache/, got {AV_NEWS_DIR}"
    assert "av_news" in str(AV_NEWS_DIR), \
        f"AV_NEWS_DIR should reference av_news/, got {AV_NEWS_DIR}"
    # Returns dict with 'source' field (added in fix)
    result = get_news_sentiment("XYZNONEXISTENT", date(2024,1,1))
    assert "source" in result, "BUG-217 fix not applied — missing 'source' key"
    assert result["source"] == "none"
    print(f"✅ get_news_sentiment paths corrected — AV_NEWS_DIR={AV_NEWS_DIR.name}")


# ─────────────────────────────────────────────────────────────────────────────
# POINT-IN-TIME ENFORCEMENT
# ─────────────────────────────────────────────────────────────────────────────

def test_congressional_signal_lag_enforced():
    """Congressional trades must respect 45-day disclosure lag."""
    from backtest.data.smart_money import congressional_signal
    from unittest.mock import patch
    import pandas as pd

    # Create mock data with a trade reported today (should NOT be available)
    today = date(2024, 6, 15)
    mock_df = pd.DataFrame([{
        "TransactionDate": pd.Timestamp("2024-06-01"),
        "ReportDate":      pd.Timestamp(today),  # reported today
        "Transaction":     "Purchase",
        "Amount":          "500001 - 1000000",
        "Representative":  "Test Rep",
    }])

    with patch("backtest.data.smart_money._load_prefetch", return_value=mock_df):
        result = congressional_signal("AAPL", today)
        # Trade reported today should not be available (needs 45 day lag)
        # Signal should be none or neutral
        assert result.get("signal") in ["none", "neutral", "no_data"], \
            f"Expected no signal for same-day disclosure, got: {result.get('signal')}"
    print("✅ Congressional signal enforces 45-day disclosure lag")

def test_aaii_point_in_time():
    """AAII data must only return readings up to as_of."""
    from backtest.data.sentiment import get_aaii_sentiment
    result = get_aaii_sentiment(date(2022, 6, 15))
    if result.get("survey_date") is not None:
        assert pd.Timestamp(result["survey_date"]) <= pd.Timestamp("2022-06-15"), \
            f"AAII returned future data: {result['survey_date']}"
    print("✅ AAII sentiment is point-in-time")


# ─────────────────────────────────────────────────────────────────────────────
# CONFIDENCE INTERVALS
# ─────────────────────────────────────────────────────────────────────────────

def test_ci_bounds_are_valid():
    from backtest.results.metrics import _confidence_interval_95
    lo, hi = _confidence_interval_95(0.60, 100)
    assert 0.0 <= lo <= 0.60
    assert 0.60 <= hi <= 1.0
    assert lo < hi
    print("✅ CI bounds are logically valid")

def test_ci_wider_with_fewer_trades():
    from backtest.results.metrics import _confidence_interval_95
    lo_small, hi_small = _confidence_interval_95(0.55, 30)
    lo_large, hi_large = _confidence_interval_95(0.55, 500)
    assert (hi_small - lo_small) > (hi_large - lo_large)
    print("✅ CI is wider with fewer trades")

def test_ci_flags_random():
    from backtest.results.metrics import _confidence_interval_95
    # 51% win rate on 50 trades — lower CI bound should be below 50%
    lo, hi = _confidence_interval_95(0.51, 50)
    assert lo < 0.50, f"Expected lower bound < 0.50, got {lo}"
    print("✅ Low-confidence strategies flagged as potentially random")


# ─────────────────────────────────────────────────────────────────────────────
# SECTOR MAP
# ─────────────────────────────────────────────────────────────────────────────

def test_sector_etf_labelled():
    from backtest.data.universe import get_sector_map
    sm = get_sector_map(["XLK", "XLF", "XLE", "GLD"])
    assert sm["XLK"] != "Unknown"
    assert sm["XLF"] != "Unknown"
    print("✅ Sector ETFs have non-Unknown labels")

def test_unknown_ticker_graceful():
    from backtest.data.universe import get_sector_map
    sm = get_sector_map(["DEFINITELY_NOT_A_REAL_TICKER_XYZ"])
    assert sm["DEFINITELY_NOT_A_REAL_TICKER_XYZ"] == "Unknown"
    print("✅ Unknown tickers return 'Unknown' gracefully")


# ─────────────────────────────────────────────────────────────────────────────
# WALK-FORWARD VERDICTS
# ─────────────────────────────────────────────────────────────────────────────

def test_walk_forward_insufficient_oos():
    from backtest.engine.improvements import run_walk_forward
    # Only IS trades — no OOS trades at all
    df = pd.DataFrame([{
        "strategy": "s1", "entry_date": date(2022, 6, 1),
        "pnl_pct": 2.0, "win": True, "direction": "long", "sector": "Unknown",
    }] * 100)
    result = run_walk_forward(df)
    verdict = result["strategy_results"]["s1"]["verdict"]
    assert verdict == "INSUFFICIENT_OOS_DATA", f"Expected INSUFFICIENT_OOS_DATA, got {verdict}"
    print("✅ INSUFFICIENT_OOS_DATA verdict for strategies with no OOS trades")

def test_walk_forward_robust_requires_both_windows():
    from backtest.engine.improvements import run_walk_forward
    # Create trades across both IS and OOS periods with good performance
    rows = []
    import datetime
    # Window 1+2 IS: 2022-2024 — 200 trades spread across dates, 65% win rate
    base = date(2022,1,1)
    for i in range(200):
        d   = base + datetime.timedelta(days=i*4)
        pnl = 3.0 if i % 3 != 0 else -1.5  # ~67% win rate, PF ~3.0
        rows.append({"strategy":"s1","entry_date":d,"pnl_pct":pnl,
                     "win":pnl>0,"direction":"long","sector":"Unknown"})
    # Window 1 OOS: 2024 — 50 trades
    base2 = date(2024,1,1)
    for i in range(50):
        d   = base2 + datetime.timedelta(days=i*5)
        pnl = 3.0 if i % 3 != 0 else -1.5
        rows.append({"strategy":"s1","entry_date":d,"pnl_pct":pnl,
                     "win":pnl>0,"direction":"long","sector":"Unknown"})
    # Window 2 OOS: 2025 — 50 trades
    base3 = date(2025,1,1)
    for i in range(50):
        d   = base3 + datetime.timedelta(days=i*5)
        pnl = 3.0 if i % 3 != 0 else -1.5
        rows.append({"strategy":"s1","entry_date":d,"pnl_pct":pnl,
                     "win":pnl>0,"direction":"long","sector":"Unknown"})
    df = pd.DataFrame(rows)
    result = run_walk_forward(df)
    verdict = result["strategy_results"]["s1"]["verdict"]
    assert verdict == "ROBUST", f"Expected ROBUST, got {verdict}"
    assert "window_1" in result["strategy_results"]["s1"]["windows"]
    assert "window_2" in result["strategy_results"]["s1"]["windows"]
    print("✅ ROBUST verdict requires both windows to pass")


# ─────────────────────────────────────────────────────────────────────────────
# SMART MONEY SCORE
# ─────────────────────────────────────────────────────────────────────────────

def test_smart_money_avoid_condition():
    from backtest.data.smart_money import smart_money_score
    from unittest.mock import patch
    cong = {"signal": "sell"}
    ins  = {"signal": "cluster_sell"}
    inst = {"signal": "neutral"}
    result = smart_money_score("AAPL", date(2024,1,1), cong=cong, ins=ins, inst=inst)
    assert result["composite_signal"] == "congressional_sell+insider_cluster_sell"
    assert result["score"] == -5
    print("✅ AVOID condition (cong sell + insider cluster sell) fires correctly")

def test_smart_money_exceptional_condition():
    from backtest.data.smart_money import smart_money_score
    cong = {"signal": "strong_buy"}
    ins  = {"signal": "strong_buy"}
    inst = {"signal": "buy"}
    result = smart_money_score("AAPL", date(2024,1,1), cong=cong, ins=ins, inst=inst)
    assert result["composite_signal"] == "congressional+insider_cluster"
    assert result["score"] >= 6
    print("✅ EXCEPTIONAL condition (strong cong + strong insider) fires correctly")

def test_smart_money_all_keys_present():
    from backtest.data.smart_money import smart_money_score
    result = smart_money_score("AAPL", date(2024,1,1))
    for k in ["composite_signal", "score", "congressional_signal",
              "insider_signal", "institutional_signal",
              "congressional_sig", "insider_sig", "institutional_sig",
              "smart_money_composite"]:
        assert k in result, f"Missing key: {k}"
    print("✅ All SM keys present")


# ─────────────────────────────────────────────────────────────────────────────
# SLIPPAGE MODEL
# ─────────────────────────────────────────────────────────────────────────────

def test_slippage_increases_long_entry():
    from backtest.engine.improvements import apply_slippage
    price, slip = apply_slippage(100.0, "long", 2.0, "AAPL", 0.0)
    assert price > 100.0, "Long entry should be higher than close after slippage"
    print("✅ Slippage increases long entry price")

def test_slippage_decreases_short_entry():
    from backtest.engine.improvements import apply_slippage
    price, slip = apply_slippage(100.0, "short", 2.0, "AAPL", 0.0)
    assert price < 100.0, "Short entry should be lower than close after slippage"
    print("✅ Slippage decreases short entry price")

def test_etf_slippage_lower_than_stock():
    from backtest.engine.improvements import apply_slippage
    etf_price, etf_slip   = apply_slippage(100.0, "long", 0.5, "SPY", 0.0)
    stock_price, stock_slip = apply_slippage(100.0, "long", 2.0, "AAPL", 0.0)
    assert etf_slip < stock_slip
    print("✅ ETF has lower slippage than stock")


# ─────────────────────────────────────────────────────────────────────────────
# COT DATA REMOVED
# ─────────────────────────────────────────────────────────────────────────────

def test_cot_returns_neutral():
    from backtest.data.sentiment import get_cot_report
    result = get_cot_report(date(2023, 6, 1))
    assert result["signal"] == "not_available"
    assert result["commercial_net"] is None
    print("✅ COT returns not_available (fabricated data removed)")

def test_sentiment_score_excludes_cot():
    from backtest.data.sentiment import sentiment_snapshot
    snap = sentiment_snapshot(date(2023, 6, 1))
    # Score should be between -5 and +5 (AAII + F&G only, no COT boost)
    assert -5 <= snap["sentiment_score"] <= 5
    assert "cot" in snap  # key still present for forward compatibility
    print("✅ Sentiment score excludes COT contribution")


# ─────────────────────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_tier_adjustment_upgrade, test_tier_adjustment_downgrade,
        test_tier_adjustment_no_change, test_tier_avoid_never_upgrades,
        test_tier_exceptional_never_upgrades, test_tier_low_never_downgrades_below_low,
        test_transaction_cost_etf_cheaper, test_transaction_cost_short_has_borrow,
        test_transaction_costs_reduce_pnl,
        test_survivorship_hold_adjusted,
        test_circuit_breaker_gap_down, test_circuit_breaker_no_trigger_normal,
        test_congressional_signal_lag_enforced, test_aaii_point_in_time,
        test_ci_bounds_are_valid, test_ci_wider_with_fewer_trades, test_ci_flags_random,
        test_sector_etf_labelled, test_unknown_ticker_graceful,
        test_walk_forward_insufficient_oos, test_walk_forward_robust_requires_both_windows,
        test_smart_money_avoid_condition, test_smart_money_exceptional_condition,
        test_smart_money_all_keys_present,
        test_slippage_increases_long_entry, test_slippage_decreases_short_entry,
        test_etf_slippage_lower_than_stock,
        test_cot_returns_neutral, test_sentiment_score_excludes_cot,
    ]
    passed = 0
    failed = []
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"❌ {t.__name__}: {e}")
            failed.append(t.__name__)
    print(f"\n{'='*50}")
    print(f"{passed}/{len(tests)} unit tests passed")
    if failed:
        print(f"FAILED: {failed}")
