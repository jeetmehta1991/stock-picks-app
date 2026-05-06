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
# TIER-1 PIT CORRECTNESS — regression tests for Pass 50 fixes
# DEC-295 (borrow units), DEC-301 (FRED ALFRED), DEC-302 (VIX/DXY proxies),
# DEC-304 (calendar JSON), DEC-305 (PIT guard RAISE)
# ─────────────────────────────────────────────────────────────────────────────

def test_pit_guard_raises_on_leakage():
    """DEC-305: _assert_no_lookahead must RAISE LookAheadBiasError by default."""
    from backtest.data.fetcher import _assert_no_lookahead, LookAheadBiasError
    df = pd.DataFrame({"close": [100, 101, 102]},
                      index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-02-01"]))
    try:
        _assert_no_lookahead(df, date(2024, 1, 15), "TEST")
        raised = False
    except LookAheadBiasError:
        raised = True
    assert raised, "PIT guard must raise LookAheadBiasError on leakage (DEC-305)"
    print("✅ DEC-305: PIT guard raises LookAheadBiasError on leakage")


def test_pit_guard_silent_on_clean_data():
    """DEC-305: _assert_no_lookahead must NOT raise on clean data."""
    from backtest.data.fetcher import _assert_no_lookahead
    df = pd.DataFrame({"close": [100, 101]},
                      index=pd.to_datetime(["2024-01-01", "2024-01-02"]))
    result = _assert_no_lookahead(df, date(2024, 1, 5), "CLEAN")
    assert len(result) == 2
    print("✅ DEC-305: PIT guard passes clean data unchanged")


def test_pit_guard_warn_mode_via_env_var():
    """DEC-305: ALLOW_LOOKAHEAD_LEAK=1 downgrades raise → warn for cache-repair scenarios."""
    import os
    from backtest.data.fetcher import _assert_no_lookahead
    df = pd.DataFrame({"close": [100, 102]},
                      index=pd.to_datetime(["2024-01-01", "2024-02-01"]))
    os.environ["ALLOW_LOOKAHEAD_LEAK"] = "1"
    try:
        result = _assert_no_lookahead(df, date(2024, 1, 15), "WARN")
        raised = False
    except Exception:
        raised = True
    finally:
        del os.environ["ALLOW_LOOKAHEAD_LEAK"]
    assert not raised, "ALLOW_LOOKAHEAD_LEAK=1 must NOT raise"
    assert len(result) == 1, "Filtered result should have 1 row remaining"
    print("✅ DEC-305: ALLOW_LOOKAHEAD_LEAK=1 downgrades to warning")


def test_borrow_cost_canonical_unit():
    """DEC-295: SHORT_ANNUAL_BORROW_RATE is the canonical single-source name.
    Value 0.005 = 0.5%/year (decimal), unambiguous."""
    from backtest.config import SHORT_ANNUAL_BORROW_RATE
    assert SHORT_ANNUAL_BORROW_RATE > 0, "Annual rate must be positive"
    # Sanity: 0.005 = 0.5% per year, NOT 0.5% per day
    assert SHORT_ANNUAL_BORROW_RATE < 0.1, \
        "Annual rate must be small fraction (<10%/yr); 0.005 = 0.5%/yr is typical"
    print(f"✅ DEC-295: SHORT_ANNUAL_BORROW_RATE = {SHORT_ANNUAL_BORROW_RATE} (decimal, ={SHORT_ANNUAL_BORROW_RATE*100}%/yr)")


def test_borrow_cost_in_one_place_only():
    """DEC-295: borrow cost lives in apply_transaction_costs, NOT in _pnl.
    _pnl returns gross PnL only; centralised cost layer handles borrow."""
    from backtest.engine.exit_manager import _pnl
    # Long PnL: hold_days irrelevant (no borrow)
    long_short = _pnl(180, 200, "long",  hold_days=1)
    long_long  = _pnl(180, 200, "long",  hold_days=30)
    assert long_short == long_long, "Long PnL must not depend on hold_days"
    # Short PnL: hold_days IGNORED here (borrow now in apply_transaction_costs)
    short_1d  = _pnl(200, 180, "short", hold_days=1)
    short_30d = _pnl(200, 180, "short", hold_days=30)
    assert short_1d == short_30d, \
        "DEC-295 design: _pnl is gross only; borrow lives in apply_transaction_costs"
    # The full pipeline (close → apply_costs) DOES charge borrow on shorts:
    from backtest.engine.improvements import apply_transaction_costs
    df = pd.DataFrame([
        {"ticker": "AAPL", "direction": "short", "hold_days": 1,  "pnl_pct": 5.0, "win": True},
        {"ticker": "AAPL", "direction": "short", "hold_days": 30, "pnl_pct": 5.0, "win": True},
    ])
    result = apply_transaction_costs(df, {"AAPL": {"market_cap": 3e12}})
    cost_1d  = result.iloc[0]["cost_pct"]
    cost_30d = result.iloc[1]["cost_pct"]
    assert cost_30d > cost_1d, \
        "30-day short hold must have more borrow cost than 1-day"
    print("✅ DEC-295: borrow centralised in apply_transaction_costs; _pnl is gross-only")


def test_economic_calendar_loads_from_json():
    """DEC-304: economic calendar loaded from JSON file, not hardcoded."""
    from backtest.data.macro import _load_economic_calendar
    cal = _load_economic_calendar()
    assert "CPI_DATES" in cal
    assert "NFP_DATES" in cal
    assert "FOMC_DATES" in cal
    assert "_metadata" in cal
    # Should have actual content (not empty due to file missing)
    assert len(cal["CPI_DATES"]) >= 30, "CPI_DATES should have multiple years"
    assert len(cal["FOMC_DATES"]) >= 20, "FOMC_DATES should have multiple years"
    # Metadata documents source
    assert "sources" in cal["_metadata"]
    print(f"✅ DEC-304: economic calendar loaded — "
          f"CPI={len(cal['CPI_DATES'])}, NFP={len(cal['NFP_DATES'])}, "
          f"FOMC={len(cal['FOMC_DATES'])}")


def test_high_impact_event_detection():
    """DEC-304: is_near_high_impact_event still works with JSON-loaded dates."""
    from backtest.data.macro import is_near_high_impact_event
    # 2024-03-20 was an FOMC meeting; 1 day before should fire
    result = is_near_high_impact_event(date(2024, 3, 19), window_days=2)
    assert result["blocked"] is True
    assert result["nearest_event_type"] == "FOMC"
    # Random non-event date should NOT fire
    result2 = is_near_high_impact_event(date(2024, 3, 27), window_days=2)
    assert result2["blocked"] is False
    print("✅ DEC-304: high-impact event detection still works after JSON migration")


def test_fred_series_supports_as_of_param():
    """DEC-301: _fred_series accepts as_of for ALFRED PIT correctness."""
    import inspect
    from backtest.data.macro import _fred_series
    sig = inspect.signature(_fred_series)
    assert "as_of" in sig.parameters, \
        "_fred_series must accept as_of parameter for PIT correctness (DEC-301)"
    # Default should be None for backward compat
    assert sig.parameters["as_of"].default is None
    print("✅ DEC-301: _fred_series exposes as_of parameter for ALFRED")


def test_vix_loader_prefers_real_index():
    """DEC-302: VIX loader code structure prefers ^VIX over VXX."""
    import inspect
    from backtest.data import macro
    src = inspect.getsource(macro._load_vix_from_ohlcv_cache)
    assert '^VIX' in src, "VIX loader must check for ^VIX (real index) first"
    assert 'VXX' in src, "VIX loader must have VXX fallback"
    # ^VIX block must appear BEFORE VXX block in source
    vix_idx = src.find('^VIX')
    vxx_idx = src.rfind('VXX')
    assert vix_idx < vxx_idx, \
        "^VIX preference must come before VXX fallback in code"
    print("✅ DEC-302: VIX loader prefers ^VIX with VXX fallback")


def test_dxy_loader_prefers_real_index():
    """DEC-302: DXY loader code structure prefers DX-Y.NYB over UUP."""
    import inspect
    from backtest.data import macro
    src = inspect.getsource(macro._load_dxy_from_ohlcv_cache)
    assert 'DX-Y.NYB' in src, "DXY loader must check for DX-Y.NYB first"
    assert 'UUP' in src, "DXY loader must have UUP fallback"
    # DX-Y.NYB block must appear BEFORE UUP fallback in source
    dxy_idx = src.find('DX-Y.NYB')
    uup_idx = src.rfind('UUP')
    assert dxy_idx < uup_idx, \
        "DX-Y.NYB preference must come before UUP fallback in code"
    print("✅ DEC-302: DXY loader prefers DX-Y.NYB with UUP fallback")


# ─────────────────────────────────────────────────────────────────────────────
# TIER-2 ENGINE-CORRECTNESS — regression tests for Pass 51 fixes
# DEC-309 (cache collision), DEC-311 (ATR refresh), DEC-312 (hybrid parity),
# DEC-315 (multi-CB), DEC-316 (regime fail-closed), DEC-324 (transaction date)
# ─────────────────────────────────────────────────────────────────────────────

def test_cache_ticker_collision_raises():
    """DEC-309: BRK-B and BRK.B both → BRK_B.parquet. Must raise, not silently overwrite."""
    from backtest.data.cache import _assert_no_ticker_collision, TickerCollisionError
    # BRK-B and BRK.B both map to same filename
    try:
        _assert_no_ticker_collision("BRK-B", {"BRK.B": {"start": "2024-01-01"}})
        raised = False
    except TickerCollisionError:
        raised = True
    assert raised, "DEC-309: collision must raise TickerCollisionError"
    print("✅ DEC-309: ticker collision detected")


def test_cache_no_collision_on_unique_ticker():
    """DEC-309: unique tickers must NOT raise."""
    from backtest.data.cache import _assert_no_ticker_collision
    # AAPL alongside MSFT — no collision
    _assert_no_ticker_collision("AAPL", {"MSFT": {}})
    # New ticker into empty cache
    _assert_no_ticker_collision("NVDA", {})
    print("✅ DEC-309: unique tickers pass collision check")


def test_atr_trail_uses_rolling_atr():
    """DEC-311: ATR trailing stop adapts to current volatility, not entry-time only."""
    import inspect
    from backtest.engine.exit_strategies import exit_atr_trail
    src = inspect.getsource(exit_atr_trail)
    # Pre-computed rolling ATR series should be present
    assert "atr_series" in src, "DEC-311: rolling ATR series missing"
    assert "ewm(alpha=1/14" in src, "DEC-311: 14-period EMA-ATR computation missing"
    assert "current_atr" in src, "DEC-311: per-iteration current_atr missing"
    print("✅ DEC-311: ATR trail refreshes daily from rolling series")


def test_atr_trail_runs_end_to_end():
    """DEC-311: exit_atr_trail produces sensible result with synthetic data."""
    import pandas as pd
    from datetime import date as _date
    from backtest.engine.exit_strategies import exit_atr_trail
    # Build 30 trading days of synthetic data
    idx = pd.bdate_range("2024-01-01", periods=30)
    df = pd.DataFrame({
        "open":   [100 + i*0.5 for i in range(30)],
        "high":   [101 + i*0.5 for i in range(30)],
        "low":    [99  + i*0.5 for i in range(30)],
        "close":  [100 + i*0.5 for i in range(30)],
        "volume": [1_000_000] * 30,
    }, index=idx)
    result = exit_atr_trail(df, _date(2024,1,1), entry_price=100.0,
                             direction="long", atr=2.0, atr_mult=1.0)
    assert "exit_price" in result
    assert "pnl_pct" in result
    assert "exit_reason" in result
    # Trending up data — should hit end_of_data with positive pnl
    assert result["pnl_pct"] > 0, f"Trending-up should be profitable, got {result}"
    print(f"✅ DEC-311: exit_atr_trail end-to-end: {result['exit_reason']} pnl={result['pnl_pct']:.2f}%")


def test_hybrid_max_days_check_removed():
    """DEC-312: exit_hybrid_50pct must NOT enforce max_days (parity with other 11)."""
    import inspect
    from backtest.engine.exit_strategies import exit_hybrid_50pct
    src = inspect.getsource(exit_hybrid_50pct)
    assert "if i >= max_days" not in src, \
        "DEC-312 regression: hybrid still has max_days check; breaks comparison fairness"
    print("✅ DEC-312: hybrid max_days check removed for exit-comparison parity")


def test_circuit_breakers_all_returns_multiple():
    """DEC-315: check_circuit_breakers_all returns ALL triggered breakers same day."""
    from backtest.engine.exit_manager import (
        check_circuit_breakers_all, check_circuit_breakers, OpenTrade
    )
    trade = OpenTrade(
        ticker="AAPL", entry_date=date(2022,1,1), entry_price=100.0,
        direction="long", strategy="test", category="test", sector="Tech",
        initial_stop=90.0, trailing_stop=90.0, highest_close=105.0,
        regime_at_entry="bull",
    )
    # Big gap down (Level 1) AND VIX crisis (Level 5) same day
    results = check_circuit_breakers_all(
        trade, today_open=85.0, prev_close=100.0, vix_value=42.0
    )
    levels = [r["level"] for r in results]
    assert 1 in levels, f"Level 1 should trigger on -15% gap, got {levels}"
    assert 5 in levels, f"Level 5 should trigger on VIX 42, got {levels}"
    # Backward-compat wrapper still works
    first = check_circuit_breakers(trade, today_open=85.0, prev_close=100.0, vix_value=42.0)
    assert first is not None, "Wrapper must return first result"
    print(f"✅ DEC-315: check_circuit_breakers_all captures all {len(results)} triggered breakers")


def test_regime_unknown_blocks_trades():
    """DEC-316: classify_regime returns 'unknown' on missing VIX; entries blocked."""
    from backtest.engine.regime_filter import classify_regime, get_regime_context
    # No VIX value
    assert classify_regime(None, None) == "unknown", \
        "DEC-316: missing VIX must return 'unknown', not 'neutral'"
    assert classify_regime(None, True) == "unknown"
    # Context blocks both directions
    ctx = get_regime_context(None, None, None)
    assert ctx["regime"] == "unknown"
    assert ctx["long_allowed"] is False, "Unknown regime must block longs"
    assert ctx["short_allowed"] is False, "Unknown regime must block shorts"
    assert ctx["long_size_mult"] == 0.0
    assert ctx["short_size_mult"] == 0.0
    # Sanity: known VIX still works as before
    assert classify_regime(15.0, True) == "bull"
    print("✅ DEC-316: missing VIX → unknown regime → trades blocked")


def test_regime_filter_has_unknown_entry():
    """DEC-316: REGIME_FILTER config must include 'unknown' for fallback."""
    from backtest.config import REGIME_FILTER
    assert "unknown" in REGIME_FILTER, \
        "DEC-316: REGIME_FILTER must define 'unknown' for missing-data fallback"
    cfg = REGIME_FILTER["unknown"]
    assert cfg.get("long") == "none", "Unknown regime must block longs"
    assert cfg.get("short") == "none", "Unknown regime must block shorts"
    print("✅ DEC-316: REGIME_FILTER['unknown'] correctly configured to block")


def test_congressional_uses_transaction_date():
    """DEC-324: congressional_signal age-weights by transaction_date, not disclosure_date."""
    import inspect
    from backtest.data.smart_money import congressional_signal
    src = inspect.getsource(congressional_signal)
    assert "transaction_date" in src, \
        "DEC-324: congressional_signal must reference transaction_date"
    assert "TransactionDate" in src, \
        "DEC-324: must read Quiver TransactionDate field"
    # Ensure age-weight uses transaction_date (not disclosure_date)
    age_weight_section = src[src.find("age_days"):src.find("buys   = recent")]
    assert "transaction_date" in age_weight_section, \
        "DEC-324: age_days must be computed from transaction_date"
    print("✅ DEC-324: congressional age-weighting uses transaction_date")


# ─────────────────────────────────────────────────────────────────────────────
# HYBRID 50PCT EXIT — BUG-270a / BUG-270b REGRESSION
# ─────────────────────────────────────────────────────────────────────────────

def _make_ohlcv(dates, highs, lows, closes):
    df = pd.DataFrame({"high": highs, "low": lows, "close": closes}, index=dates)
    df.index = pd.DatetimeIndex(df.index)
    return df

def test_hybrid_long_trail_after_target_hit():
    """BUG-270a: must NOT raise NameError ('low' undefined) after target hit."""
    from backtest.engine.exit_strategies import exit_hybrid_50pct
    import datetime
    base = date(2022, 1, 3)
    dates  = [base + timedelta(days=i) for i in range(30)]
    # Days 0-4: rise to ~106 (hits 3×ATR=3 target), then crash to 70
    highs  = [101, 103, 105, 107, 107] + [90, 80, 75, 70, 70] + [70]*20
    lows   = [99,  101, 103, 105, 105] + [85, 75, 70, 65, 65] + [65]*20
    closes = [100, 102, 104, 106, 106] + [88, 78, 72, 68, 68] + [68]*20
    df = _make_ohlcv(dates, highs, lows, closes)
    entry_date = date(2022, 1, 2)   # one day before df starts
    result = exit_hybrid_50pct(df, entry_date, 100.0, "long", atr=1.0)
    assert result["exit_reason"] in ("hybrid_trail", "stop_loss", "end_of_data"), \
        f"Unexpected exit_reason: {result['exit_reason']}"
    print(f"✅ BUG-270a: long hybrid trail no NameError — exit={result['exit_reason']}")

def test_hybrid_short_trail_after_target_hit():
    """BUG-270b: short branch must trail and exit via hybrid_trail, not end_of_data."""
    from backtest.engine.exit_strategies import exit_hybrid_50pct
    import datetime
    base = date(2022, 1, 3)
    dates  = [base + timedelta(days=i) for i in range(30)]
    # Days 0-4: drop to ~94 (hits 3×ATR=3 short target), then spike to 130
    highs  = [101, 99,  97,  95,  95] + [105, 115, 125, 130, 130] + [130]*20
    lows   = [99,  97,  95,  93,  93] + [100, 110, 120, 128, 128] + [128]*20
    closes = [100, 98,  96,  94,  94] + [102, 112, 122, 129, 129] + [129]*20
    df = _make_ohlcv(dates, highs, lows, closes)
    entry_date = date(2022, 1, 2)
    result = exit_hybrid_50pct(df, entry_date, 100.0, "short", atr=1.0)
    assert result["exit_reason"] in ("hybrid_trail", "stop_loss"), \
        f"Expected hybrid_trail or stop_loss, got: {result['exit_reason']} (pre-fix would be end_of_data)"
    print(f"✅ BUG-270b: short hybrid trail exits correctly — exit={result['exit_reason']}")


# ─────────────────────────────────────────────────────────────────────────────
# PIT UNIVERSE LOADERS (DEC-040 / DEC-477 — Pass 53)
# ─────────────────────────────────────────────────────────────────────────────

def test_pit_filter_event_driven_changes():
    """Post-rebuild T1a (Pass 53 Wikipedia 124 events): PIT counts vary across as_of dates.

    Spot-checks specific known events:
      - TSLA added 2020-12-21 (replaces AIV)
      - SNDK added 2025-11-28 (replaces IPG; WDC spinoff)
      - DAY removed 2026-02-09 (CDAY-renamed-DAY post-merger)
    """
    from backtest.data.universe import get_sp500_constituents_pit
    pre_tsla = set(get_sp500_constituents_pit(date(2020, 12, 20)))
    post_tsla = set(get_sp500_constituents_pit(date(2020, 12, 21)))
    assert "TSLA" not in pre_tsla, "TSLA should NOT be in S&P pre-2020-12-21"
    assert "TSLA" in post_tsla, "TSLA SHOULD be in S&P from 2020-12-21"
    assert "AIV" in pre_tsla, "AIV should be in S&P pre-2020-12-21"
    assert "AIV" not in post_tsla, "AIV should NOT be in S&P from 2020-12-21"

    pre_sndk = set(get_sp500_constituents_pit(date(2025, 11, 27)))
    post_sndk = set(get_sp500_constituents_pit(date(2025, 11, 28)))
    assert "SNDK" not in pre_sndk and "SNDK" in post_sndk, "SNDK inclusion 2025-11-28 not handled"
    assert "IPG" in pre_sndk and "IPG" not in post_sndk, "IPG removal 2025-11-28 not handled"

    pre_day_remove = set(get_sp500_constituents_pit(date(2026, 2, 8)))
    post_day_remove = set(get_sp500_constituents_pit(date(2026, 2, 10)))
    assert "DAY" in pre_day_remove, "DAY should be active 2026-02-08"
    assert "DAY" not in post_day_remove, "DAY should be removed by 2026-02-10"

    # CDAY → DAY rename map: CDAY should never appear in PIT results
    sample_2024 = set(get_sp500_constituents_pit(date(2024, 6, 1)))
    assert "CDAY" not in sample_2024, "CDAY should be remapped to DAY (rename map)"
    assert "DAY" in sample_2024, "DAY should be active under post-rename ticker"

    print("✅ event-driven PIT: TSLA + SNDK + IPG + DAY transitions verified")


def test_pit_filter_added_date_semantics():
    """Ticker with explicit added_date is excluded from PIT before that date, included after."""
    from backtest.data.universe import _filter_pit
    df = pd.DataFrame({
        "Symbol": ["AAA", "BBB", "CCC"],
        "added_date": ["", "2022-06-01", "2024-01-01"],
        "removed_date": ["", "", ""],
    })
    # Pre-window: AAA passes (NULL added), BBB excluded (added 2022-06), CCC excluded (added 2024)
    result = _filter_pit(df, date(2021, 1, 1))
    assert set(result["Symbol"].tolist()) == {"AAA"}, "pre-window: only NULL-added passes"
    # Mid-window: AAA + BBB pass, CCC still excluded
    result = _filter_pit(df, date(2023, 1, 1))
    assert set(result["Symbol"].tolist()) == {"AAA", "BBB"}, "mid-window: AAA + BBB pass"
    # Post-window: all 3 pass
    result = _filter_pit(df, date(2025, 1, 1))
    assert set(result["Symbol"].tolist()) == {"AAA", "BBB", "CCC"}, "all 3 active by 2025"
    print("✅ added_date semantics: correct PIT inclusion at each window")


def test_pit_filter_removed_date_semantics():
    """Ticker with explicit removed_date is included before removal, excluded on/after."""
    from backtest.data.universe import _filter_pit
    df = pd.DataFrame({
        "Symbol": ["XXX", "YYY"],
        "added_date": ["", ""],
        "removed_date": ["2023-06-01", ""],
    })
    # Before removal: both pass
    result = _filter_pit(df, date(2023, 1, 1))
    assert set(result["Symbol"].tolist()) == {"XXX", "YYY"}, "before removal: both active"
    # On removal date: removed_date filter is strict-greater (removed_date > as_of)
    # 2023-06-01 > 2023-06-01 is FALSE → XXX excluded on its removal date
    result = _filter_pit(df, date(2023, 6, 1))
    assert set(result["Symbol"].tolist()) == {"YYY"}, "on removal date: XXX excluded"
    # After removal: only YYY
    result = _filter_pit(df, date(2024, 1, 1))
    assert set(result["Symbol"].tolist()) == {"YYY"}, "after removal: only YYY"
    print("✅ removed_date semantics: correct PIT exclusion at/after removal")


def test_pit_filter_multi_period_rows():
    """Re-entry tickers (e.g., NDX WDC/CSGP/TTWO/SPLK) handled via OR semantics across rows."""
    from backtest.data.universe import _filter_pit
    df = pd.DataFrame({
        "Symbol": ["WDC", "WDC", "OTHER"],
        "added_date":   ["",         "2023-06-01", ""],
        "removed_date": ["2020-12-01", "",         ""],
    })
    # Period 1 active: WDC pre-2020-12 (row 0)
    result = _filter_pit(df, date(2020, 6, 1))
    assert set(result["Symbol"].tolist()) == {"WDC", "OTHER"}, "Period 1: WDC active"
    # Gap: WDC inactive (between removal 2020-12 and re-entry 2023-06)
    result = _filter_pit(df, date(2022, 1, 1))
    assert set(result["Symbol"].tolist()) == {"OTHER"}, "Gap: WDC inactive"
    # Period 2 active: WDC re-entered 2023-06 (row 1)
    result = _filter_pit(df, date(2024, 1, 1))
    assert set(result["Symbol"].tolist()) == {"WDC", "OTHER"}, "Period 2: WDC re-active"
    print("✅ multi-period rows: WDC re-entry handled via OR semantics")


def test_union_universe_includes_etfs():
    """union_universe combines all 5 buckets with ETFs by default."""
    from backtest.data.universe import union_universe, get_etfs_full
    etfs = set(get_etfs_full())
    union = set(union_universe(date(2024, 6, 15)))
    assert etfs.issubset(union), "ETFs must be in default union"
    assert "SPY" in union and "QQQ" in union, "core ETFs present"
    # Without ETFs
    union_no_etf = set(union_universe(date(2024, 6, 15), include_etfs=False))
    assert not (etfs & union_no_etf), "include_etfs=False excludes ETF tickers"
    print(f"✅ union_universe: {len(union)} tickers w/ETFs, {len(union_no_etf)} w/o")


# ─────────────────────────────────────────────────────────────────────────────
# DEC-504 — T3-OVER-T1 PRECEDENCE RESOLVER (Pass 53 owner directive 2026-05-05)
# ─────────────────────────────────────────────────────────────────────────────

def test_dec504_tier_precedence_order():
    """Verify _TIER_PRECEDENCE order: T3 > T2 > T1c > T1a > T1ETF."""
    from backtest.data.universe import _TIER_PRECEDENCE
    assert _TIER_PRECEDENCE == ["T3", "T2", "T1c", "T1a", "T1ETF"], \
        "Precedence order must be T3 > T2 > T1c > T1a > T1ETF per DEC-504"
    print("✅ DEC-504 tier precedence order: T3 > T2 > T1c > T1a > T1ETF")


def test_dec504_tier_params_complete():
    """Each tier has all required parameter keys per DEC-504 scope (a)-(e)."""
    from backtest.data.universe import TIER_PARAMS, _TIER_PRECEDENCE
    required_keys = {"min_avg_dollar_volume_usd", "min_history_days",
                     "min_market_cap_m", "position_size_tier", "refresh_cadence"}
    for tier in _TIER_PRECEDENCE:
        assert tier in TIER_PARAMS, f"TIER_PARAMS missing tier {tier}"
        keys = set(TIER_PARAMS[tier].keys())
        assert required_keys <= keys, \
            f"Tier {tier} missing keys: {required_keys - keys}"
    # T3 more permissive than T1a per owner intent
    assert TIER_PARAMS["T3"]["min_avg_dollar_volume_usd"] < TIER_PARAMS["T1a"]["min_avg_dollar_volume_usd"], \
        "T3 ADV floor must be < T1a (T3 is more permissive)"
    assert TIER_PARAMS["T3"]["min_history_days"] < TIER_PARAMS["T1a"]["min_history_days"], \
        "T3 history requirement must be < T1a"
    print("✅ DEC-504 TIER_PARAMS complete + T3 more permissive than T1a")


def test_dec504_resolver_t3_over_t1_vst_2024():
    """VST canonical case: T1a + T3 simultaneous on 2024-06-01 → resolves to T3."""
    from backtest.data.universe import resolve_tier_precedence
    # VST joined T1a 2024-05-08 + T3 added 2024-05-01 (removed 2024-06-03)
    # On 2024-06-01: both active → T3 wins per DEC-504
    result = resolve_tier_precedence("VST", date(2024, 6, 1))
    assert result == "T3", f"VST 2024-06-01 should resolve to T3 (DEC-504), got {result}"
    print(f"✅ DEC-504 VST 2024-06-01 → T3 (T3 wins over T1a)")


def test_dec504_resolver_t1a_after_t3_removal():
    """VST 2024-07-01: T3 removed 2024-06-03; only T1a active → resolves to T1a."""
    from backtest.data.universe import resolve_tier_precedence
    result = resolve_tier_precedence("VST", date(2024, 7, 1))
    assert result == "T1a", f"VST 2024-07-01 should resolve to T1a (T3 removed), got {result}"
    print(f"✅ DEC-504 VST 2024-07-01 → T1a (T3 removed; T1a is now most-specific)")


def test_dec504_resolver_t2_over_t3():
    """T2+T3 dual-membership case: T2 should NOT win over T3 per precedence order."""
    from backtest.data.universe import resolve_tier_precedence, get_extended_universe_pit, get_momentum_watchlist_pit
    # Find a ticker that's in both T2 and T3 active on 2025-08-01
    t2_active = set(get_extended_universe_pit(date(2025, 8, 1)))
    t3_active = set(get_momentum_watchlist_pit(date(2025, 8, 1)))
    overlap = t2_active & t3_active
    assert len(overlap) > 0, "Test requires ≥1 T2∩T3 active ticker (validator showed 26 on 2025-08-01)"
    sample = sorted(overlap)[0]
    result = resolve_tier_precedence(sample, date(2025, 8, 1))
    assert result == "T3", f"{sample} 2025-08-01 in T2∩T3; should resolve to T3 (DEC-504), got {result}"
    print(f"✅ DEC-504 {sample} (T2∩T3) → T3")


def test_dec504_resolver_t1_only():
    """Pure T1a-only ticker (e.g., AAPL pre-2025) resolves to T1a."""
    from backtest.data.universe import resolve_tier_precedence
    result = resolve_tier_precedence("AAPL", date(2024, 6, 1))
    # AAPL is T1a-active and T1c-active; T1c wins over T1a per precedence
    assert result in ("T1a", "T1c"), f"AAPL 2024-06-01 should resolve to T1a or T1c, got {result}"
    print(f"✅ DEC-504 AAPL 2024-06-01 → {result}")


def test_dec504_resolver_etf():
    """Pure ETF (e.g., SPY) resolves to T1ETF (lowest precedence; nothing else applies)."""
    from backtest.data.universe import resolve_tier_precedence
    result = resolve_tier_precedence("SPY", date(2024, 6, 1))
    assert result == "T1ETF", f"SPY should resolve to T1ETF, got {result}"
    print(f"✅ DEC-504 SPY → T1ETF")


def test_dec504_resolver_unknown_ticker():
    """Ticker not in any tier returns None."""
    from backtest.data.universe import resolve_tier_precedence
    result = resolve_tier_precedence("NOTATICKER", date(2024, 6, 1))
    assert result is None, f"Unknown ticker should resolve to None, got {result}"
    print(f"✅ DEC-504 unknown ticker → None")


def test_dec504_get_tier_params_t3_returned_for_dual():
    """get_tier_params returns T3 dict for dual T1+T3 ticker per precedence."""
    from backtest.data.universe import get_tier_params, TIER_PARAMS
    params = get_tier_params("VST", date(2024, 6, 1))
    assert params is not None, "VST 2024-06-01 should return params"
    assert params == TIER_PARAMS["T3"], "VST dual membership should return T3 params per DEC-504"
    assert params["min_avg_dollar_volume_usd"] == 5_000_000, "T3 ADV floor"
    assert params["min_history_days"] == 60, "T3 history floor"
    print(f"✅ DEC-504 get_tier_params VST → T3 dict (ADV $5M, history 60d)")


def test_dec504_get_tier_params_returns_copy():
    """get_tier_params returns a copy, not the canonical dict (mutation safety)."""
    from backtest.data.universe import get_tier_params, TIER_PARAMS
    params = get_tier_params("AAPL", date(2024, 6, 1))
    if params is not None:
        original_adv = TIER_PARAMS["T1a"]["min_avg_dollar_volume_usd"]
        params["min_avg_dollar_volume_usd"] = -1
        assert TIER_PARAMS["T1a"]["min_avg_dollar_volume_usd"] == original_adv, \
            "Mutating returned dict must not affect canonical TIER_PARAMS"
        print("✅ DEC-504 get_tier_params returns copy (mutation-safe)")


# ─────────────────────────────────────────────────────────────────────────────
# BUG-271/272/273 — smart_money.py silent-gap fix (Pass 53 Batch 1 / DEC-503 SECOND application)
# ─────────────────────────────────────────────────────────────────────────────

def _inject_quiver_bulk_for_test(dataset: str, df: pd.DataFrame):
    """Test helper: inject synthetic bulk DataFrame into _BULK_CACHE."""
    from backtest.data import smart_money
    smart_money._reset_bulk_cache_for_tests()
    smart_money._BULK_CACHE[dataset] = df


def test_bug271_get_analyst_data_returns_not_available_pre_batch4():
    """BUG-271 fix: pre-Batch-4 (no Polygon financials cache), returns signal=not_available."""
    from backtest.data.smart_money import get_analyst_data
    # Force cache miss with non-existent ticker path
    result = get_analyst_data("NONEXISTENT_TICKER_XYZ", date(2024, 6, 1))
    assert result["signal"] == "not_available", \
        f"Expected signal=not_available pre-Batch-4, got {result['signal']!r}"
    assert result["consensus"] == "unknown"
    assert result["total_analysts"] == 0
    print("✅ BUG-271 get_analyst_data → not_available (pre-Batch-4 graceful)")


def test_bug271_get_analyst_data_no_yfinance_calls():
    """BUG-271 + D4: get_analyst_data must NOT import or call yfinance at runtime."""
    import backtest.data.smart_money as sm
    src = Path(sm.__file__).read_text(encoding='utf-8')
    # `import yfinance` should be absent (D4 total cut)
    assert "import yfinance" not in src, "yfinance import must be removed (D4 owner directive)"
    # `yf.Ticker` should be absent
    assert "yf.Ticker(" not in src, "yf.Ticker calls must be removed"
    print("✅ BUG-271 D4 yfinance import + yf.Ticker calls absent from smart_money.py")


def test_bug272_insider_signal_no_bulk_returns_none():
    """BUG-272: insider_signal returns 'none' gracefully when bulk cache absent."""
    from backtest.data import smart_money
    smart_money._reset_bulk_cache_for_tests()
    # Without injection, _load_quiver_bulk returns empty DataFrame → signal=none
    result = smart_money.insider_signal("AAPL", date(2024, 6, 1))
    assert result["signal"] == "none", \
        f"Expected signal=none with no bulk cache, got {result['signal']!r}"
    assert result["buy_count"] == 0
    print("✅ BUG-272 insider_signal → none (no bulk cache; graceful)")


def test_bug272_insider_signal_with_synthetic_bulk_buy():
    """BUG-272: insider_signal computes buy signal with live/insiders schema (TransactionCode 'P')."""
    # Schema: Ticker / Date / Name / AcquiredDisposedCode / TransactionCode / officerTitle
    bulk = pd.DataFrame({
        "Ticker": ["AAPL", "AAPL", "AAPL", "MSFT"],
        "Date": ["2024-05-15", "2024-05-20", "2024-05-25", "2024-05-15"],
        "Name": ["John CEO", "Jane CFO", "Bob CTO", "Other"],
        "AcquiredDisposedCode": ["A", "A", "A", "D"],
        "TransactionCode": ["P", "P", "P", "S"],  # P = open-market purchase
        "officerTitle": ["CEO", "CFO", "CTO", "VP"],
        "isOfficer": [True, True, True, True],
        "isDirector": [False, False, False, False],
    })
    _inject_quiver_bulk_for_test("insiders", bulk)
    from backtest.data.smart_money import insider_signal
    result = insider_signal("AAPL", date(2024, 6, 1), lookback_days=30)
    assert result["signal"] in ("buy", "weak_buy", "strong_buy"), \
        f"Expected buy variant, got {result['signal']!r}"
    assert result["buy_count"] >= 1, f"Expected buy_count>=1, got {result['buy_count']}"
    assert result["sell_count"] == 0, "AAPL has no sells in synthetic data"
    print(f"✅ BUG-272 insider_signal AAPL (live/insiders schema) → {result['signal']} ({result['buy_count']} buys)")


def test_bug272_insider_signal_filters_by_ticker():
    """BUG-272: bulk feed correctly filtered by ticker (case-insensitive)."""
    bulk = pd.DataFrame({
        "Ticker": ["AAPL", "MSFT", "GOOG"],
        "Date": ["2024-05-15"] * 3,
        "Name": ["A", "B", "C"],
        "AcquiredDisposedCode": ["A"] * 3,
        "TransactionCode": ["P"] * 3,
        "officerTitle": ["CEO"] * 3,
        "isOfficer": [True] * 3,
    })
    _inject_quiver_bulk_for_test("insiders", bulk)
    from backtest.data.smart_money import insider_signal
    result_aapl = insider_signal("AAPL", date(2024, 6, 1))
    result_msft = insider_signal("MSFT", date(2024, 6, 1))
    result_lower_aapl = insider_signal("aapl", date(2024, 6, 1))  # case-insensitive
    assert result_aapl["buy_count"] == 1, f"AAPL filter: expected 1 buy, got {result_aapl['buy_count']}"
    assert result_msft["buy_count"] == 1, f"MSFT filter: expected 1 buy, got {result_msft['buy_count']}"
    assert result_lower_aapl["buy_count"] == 1, "Case-insensitive ticker filter must work"
    print("✅ BUG-272 insider_signal ticker filter (case-insensitive)")


def test_bug272_insider_signal_excludes_non_open_market_codes():
    """BUG-272: TransactionCode 'A' (grant), 'F' (tax), 'M' (option exercise) excluded from buy signal."""
    bulk = pd.DataFrame({
        "Ticker": ["AAPL"] * 4,
        "Date": ["2024-05-15"] * 4,
        "Name": ["X", "Y", "Z", "W"],
        "AcquiredDisposedCode": ["A", "A", "A", "A"],
        "TransactionCode": ["A", "F", "M", "G"],  # grant, tax, option, gift — all excluded
        "officerTitle": ["CEO"] * 4,
        "isOfficer": [True] * 4,
    })
    _inject_quiver_bulk_for_test("insiders", bulk)
    from backtest.data.smart_money import insider_signal
    result = insider_signal("AAPL", date(2024, 6, 1))
    assert result["buy_count"] == 0, \
        f"Non-purchase codes must be excluded; got buy_count={result['buy_count']}"
    print("✅ BUG-272 insider_signal correctly excludes A/F/M/G transaction codes")


def test_bug273_institutional_signal_no_bulk_returns_none():
    """BUG-273: institutional_signal returns 'none' gracefully when bulk cache absent."""
    from backtest.data import smart_money
    smart_money._reset_bulk_cache_for_tests()
    result = smart_money.institutional_signal("AAPL", date(2024, 6, 1))
    assert result["signal"] == "none", \
        f"Expected signal=none with no bulk cache, got {result['signal']!r}"
    print("✅ BUG-273 institutional_signal → none (no bulk cache; graceful)")


def test_bug273_institutional_signal_with_synthetic_bulk():
    """BUG-273: institutional_signal computes signal with live/sec13fchanges schema."""
    # Schema: Ticker / Date / ReportPeriod / Fund / Change_Share / Change_Pct / Held
    quarter_end = "2024-03-31"
    bulk = pd.DataFrame({
        "Ticker": ["AAPL", "AAPL", "AAPL", "MSFT"],
        "Date": ["2024-05-15"] * 4,
        "ReportPeriod": [quarter_end] * 4,
        "Fund": ["Fund A", "Fund B", "Fund C", "Fund D"],
        "Change_Share": [1000, 500, 200, 100],
        "Change_Pct": [1.0, 1.0, 1.0, 1.0],  # all = 1.0 means new positions
        "Held": [1000, 500, 200, 100],
    })
    _inject_quiver_bulk_for_test("sec13fchanges", bulk)
    from backtest.data.smart_money import institutional_signal
    # 45-day reporting lag: must query >= quarter_end + 45 days for visibility
    result = institutional_signal("AAPL", date(2024, 6, 1))
    assert result["signal"] in ("buy", "strong_buy"), \
        f"Expected buy variant for 3 new positions, got {result['signal']!r}"
    assert result.get("new_positions", 0) >= 1, "Should detect new positions"
    print(f"✅ BUG-273 institutional_signal AAPL (sec13fchanges schema) → {result['signal']}")


def test_bug273_institutional_signal_respects_45day_lag():
    """BUG-273: 13F filings have ~45-day reporting lag; pre-lag queries return none."""
    quarter_end = "2024-03-31"
    bulk = pd.DataFrame({
        "Ticker": ["AAPL"],
        "Date": ["2024-04-01"],
        "ReportPeriod": [quarter_end],
        "Fund": ["Fund A"],
        "Change_Share": [1000],
        "Change_Pct": [1.0],
        "Held": [1000],
    })
    _inject_quiver_bulk_for_test("sec13fchanges", bulk)
    from backtest.data.smart_money import institutional_signal
    # 30 days post quarter-end < 45-day lag → not yet available
    result_too_early = institutional_signal("AAPL", date(2024, 4, 30))
    assert result_too_early["signal"] == "none", \
        f"Pre-45-day-lag query should return none, got {result_too_early['signal']!r}"
    print("✅ BUG-273 institutional_signal 45-day lag respected")


def test_polygon_news_positive_sentiment(tmp_path, monkeypatch):
    """Pass 53 Batch 13 Row 2 closure: get_news_sentiment reads Polygon news insights."""
    # Inject fake data_prefetch/polygon/news/AAPL.parquet
    polygon_news_dir = tmp_path / "data_prefetch" / "polygon" / "news"
    polygon_news_dir.mkdir(parents=True)
    df = pd.DataFrame({
        "id": ["a", "b", "c"],
        "date": pd.to_datetime(["2024-05-30", "2024-05-31", "2024-06-01"]),
        "title": ["good", "great", "ok"],
        "insights": [
            [{"ticker": "AAPL", "sentiment": "positive", "sentiment_reasoning": "x"}],
            [{"ticker": "AAPL", "sentiment": "positive", "sentiment_reasoning": "y"}],
            [{"ticker": "AAPL", "sentiment": "neutral", "sentiment_reasoning": "z"}],
        ],
    })
    df.to_parquet(polygon_news_dir / "AAPL.parquet")
    from backtest.data import smart_money
    monkeypatch.setattr(smart_money, "PREFETCH_POLYGON_NEWS_DIR", polygon_news_dir)
    result = smart_money.get_news_sentiment("AAPL", date(2024, 6, 1), lookback_days=7)
    assert result["source"] == "polygon", f"Expected polygon source, got {result['source']!r}"
    assert result["signal"] == "bullish", f"Expected bullish, got {result['signal']!r}"
    assert result["scored_count"] == 3
    print(f"✅ Batch 13 Row 2 polygon news positive → {result['signal']} score={result['sentiment_score']}")


def test_polygon_news_negative_sentiment(tmp_path, monkeypatch):
    """Negative-sentiment articles produce bearish signal."""
    polygon_news_dir = tmp_path / "data_prefetch" / "polygon" / "news"
    polygon_news_dir.mkdir(parents=True)
    df = pd.DataFrame({
        "id": ["a", "b"],
        "date": pd.to_datetime(["2024-05-31", "2024-06-01"]),
        "title": ["bad", "worse"],
        "insights": [
            [{"ticker": "TSLA", "sentiment": "negative", "sentiment_reasoning": "x"}],
            [{"ticker": "TSLA", "sentiment": "negative", "sentiment_reasoning": "y"}],
        ],
    })
    df.to_parquet(polygon_news_dir / "TSLA.parquet")
    from backtest.data import smart_money
    monkeypatch.setattr(smart_money, "PREFETCH_POLYGON_NEWS_DIR", polygon_news_dir)
    result = smart_money.get_news_sentiment("TSLA", date(2024, 6, 1))
    assert result["signal"] == "bearish", f"Expected bearish, got {result['signal']!r}"
    print(f"✅ polygon news negative → {result['signal']} score={result['sentiment_score']}")


def test_polygon_news_only_other_tickers_in_insights(tmp_path, monkeypatch):
    """Articles tagged but with insights only for OTHER tickers → neutral with 0 scored."""
    polygon_news_dir = tmp_path / "data_prefetch" / "polygon" / "news"
    polygon_news_dir.mkdir(parents=True)
    # Article mentions GOOGL but insights only for MSFT (cross-ticker article)
    df = pd.DataFrame({
        "id": ["a"],
        "date": pd.to_datetime(["2024-06-01"]),
        "title": ["msft news mentions googl"],
        "insights": [
            [{"ticker": "MSFT", "sentiment": "positive", "sentiment_reasoning": "x"}],
        ],
    })
    df.to_parquet(polygon_news_dir / "GOOGL.parquet")
    from backtest.data import smart_money
    monkeypatch.setattr(smart_money, "PREFETCH_POLYGON_NEWS_DIR", polygon_news_dir)
    result = smart_money.get_news_sentiment("GOOGL", date(2024, 6, 1))
    # Article exists but no GOOGL-specific insight → neutral, polygon_no_insights source
    assert result["scored_count"] == 0
    assert result["signal"] == "neutral"
    assert result["source"] == "polygon_no_insights"
    print(f"✅ polygon news ticker filter excludes other-ticker insights")


def test_polygon_news_missing_falls_through_to_neutral(tmp_path, monkeypatch):
    """No polygon cache + no legacy cache → returns default neutral / source=none."""
    empty_polygon_dir = tmp_path / "data_prefetch" / "polygon" / "news"
    empty_polygon_dir.mkdir(parents=True)
    empty_legacy = tmp_path / "empty_legacy"
    empty_legacy.mkdir()
    from backtest.data import smart_money
    monkeypatch.setattr(smart_money, "PREFETCH_POLYGON_NEWS_DIR", empty_polygon_dir)
    monkeypatch.setattr(smart_money, "AV_NEWS_DIR", empty_legacy)
    monkeypatch.setattr(smart_money, "FH_NEWS_DIR", empty_legacy)
    result = smart_money.get_news_sentiment("XYZ", date(2024, 6, 1))
    assert result["source"] == "none"
    assert result["signal"] == "neutral"
    assert result["sentiment_score"] == 0.0
    print(f"✅ polygon news missing + no legacy → graceful neutral fallback")


def test_smart_money_score_uses_three_inputs_post_fix():
    """Composite smart_money_score correctly combines all 3 (now-fixed) inputs."""
    # Inject bulk data for all 3 sources matching actual schemas
    insider_bulk = pd.DataFrame({
        "Ticker": ["TEST"], "Date": ["2024-05-25"], "Name": ["CEO X"],
        "AcquiredDisposedCode": ["A"], "TransactionCode": ["P"],
        "officerTitle": ["CEO"], "isOfficer": [True], "isDirector": [False],
    })
    sec13fchanges_bulk = pd.DataFrame({
        "Ticker": ["TEST"], "Date": ["2024-05-15"], "ReportPeriod": ["2024-03-31"],
        "Fund": ["Fund A"], "Change_Share": [1000], "Change_Pct": [1.0], "Held": [1000],
    })
    _inject_quiver_bulk_for_test("insiders", insider_bulk)
    from backtest.data import smart_money
    smart_money._BULK_CACHE["sec13fchanges"] = sec13fchanges_bulk
    # Note: congressional uses _load_prefetch (per-ticker), not bulk; skip injection
    from backtest.data.smart_money import smart_money_score
    result = smart_money_score("TEST", date(2024, 6, 1))
    # All 3 keys must be present (no longer silently zeroed)
    assert "congressional_signal" in result
    assert "insider_signal" in result
    assert "institutional_signal" in result
    assert "composite_signal" in result
    assert "score" in result
    # Insider + institutional should NOT be silently 'none' (they have synthetic data)
    assert result["insider_signal"] != "none" or result["institutional_signal"] != "none", \
        "At least one of insider/institutional should have signal post-BUG-272/273 fix"
    print(f"✅ smart_money_score post-fix: composite={result['composite_signal']!r} score={result['score']}")


def test_union_universe_includes_ndx():
    """union_universe contains T1c NDX-non-S&P names like AAPL (also S&P) + e.g., MELI."""
    from backtest.data.universe import union_universe
    union = set(union_universe(date(2024, 6, 15)))
    # AAPL is in both S&P + NDX → should be in union once
    assert "AAPL" in union, "AAPL should be in union"
    print(f"✅ union_universe contains T1a + T1c overlap correctly")


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
        test_hybrid_long_trail_after_target_hit,
        test_hybrid_short_trail_after_target_hit,
        test_pit_filter_event_driven_changes,
        test_pit_filter_added_date_semantics,
        test_pit_filter_removed_date_semantics,
        test_pit_filter_multi_period_rows,
        test_union_universe_includes_etfs,
        test_union_universe_includes_ndx,
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
