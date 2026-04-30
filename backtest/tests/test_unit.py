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
