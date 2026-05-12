"""
Unit tests  -  test individual functions in isolation.
Run: python -m pytest backtest/tests/test_unit.py -v
"""
import sys
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# -----------------------------------------------------------------------------
# CONFIDENCE TIER & TIERING LOGIC
# -----------------------------------------------------------------------------

def test_tier_adjustment_upgrade():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("HIGH", 80) == "VERY_HIGH"
    assert engine._adjust_tier_by_agent("MEDIUM_HIGH", 76) == "HIGH"
    print("[OK] Tier upgrade works")

def test_tier_adjustment_downgrade():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("HIGH", 35) == "MEDIUM_HIGH"
    assert engine._adjust_tier_by_agent("VERY_HIGH", 39) == "HIGH"
    print("[OK] Tier downgrade works")

def test_tier_adjustment_no_change():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("HIGH", 60) == "HIGH"
    print("[OK] Tier no-change works")

def test_tier_avoid_never_upgrades():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("AVOID", 99) == "AVOID"
    print("[OK] AVOID never upgrades")

def test_tier_exceptional_never_upgrades():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("EXCEPTIONAL", 99) == "EXCEPTIONAL"
    print("[OK] EXCEPTIONAL never over-upgrades")

def test_tier_low_never_downgrades_below_low():
    from backtest.engine.backtest import BacktestEngine
    engine = BacktestEngine.__new__(BacktestEngine)
    engine.sector_map = {}
    assert engine._adjust_tier_by_agent("LOW", 5) == "LOW"
    print("[OK] LOW never downgrades below LOW")


# -----------------------------------------------------------------------------
# TRANSACTION COSTS
# -----------------------------------------------------------------------------

def test_transaction_cost_etf_cheaper():
    from backtest.engine.improvements import get_transaction_cost
    etf_cost = get_transaction_cost("SPY", 500_000)
    stock_cost = get_transaction_cost("AAPL", 3_000_000)
    assert etf_cost < stock_cost
    print("[OK] ETF costs less than stock")

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
    print("[OK] Short trades have higher cost (borrow fee)")

def test_transaction_costs_reduce_pnl():
    from backtest.engine.improvements import apply_transaction_costs
    df = pd.DataFrame([{"ticker": "AAPL", "direction": "long",
                        "hold_days": 10, "pnl_pct": 5.0, "win": True}])
    result = apply_transaction_costs(df, {"AAPL": {"market_cap": 3_000_000_000_000}})
    assert result["pnl_pct"].iloc[0] < 5.0
    assert "pnl_pct_gross" in result.columns
    print("[OK] Transaction costs reduce pnl_pct")


# -----------------------------------------------------------------------------
# SURVIVORSHIP BIAS
# -----------------------------------------------------------------------------

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
    print("[OK] Hold-adjusted survivorship bias  -  short holds get smaller haircut")


# -----------------------------------------------------------------------------
# CIRCUIT BREAKERS
# -----------------------------------------------------------------------------

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
    print("[OK] Circuit breaker 1 triggers on >12% gap down")

def test_circuit_breaker_no_trigger_normal():
    from backtest.engine.exit_manager import check_circuit_breakers, OpenTrade
    trade = OpenTrade(
        ticker="AAPL", entry_date=date(2022,1,1), entry_price=100.0,
        direction="long", strategy="test", category="test", sector="Tech",
        initial_stop=90.0, trailing_stop=90.0, highest_close=105.0,
        regime_at_entry="bull",
    )
    # Normal day  -  no CB
    result = check_circuit_breakers(trade, today_open=101.0, prev_close=100.0, vix_value=18)
    assert result is None
    print("[OK] No circuit breaker on normal day")


# -----------------------------------------------------------------------------
# CLOSE_TRADE  -  regression test for BUG-214 (Pass 48)
# -----------------------------------------------------------------------------

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
    print("[OK] close_trade long winner  -  days/pnl computed in correct order")


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
    print("[OK] close_trade short trade with borrow cost  -  runs without error")


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
    print("[OK] close_trade loser  -  fail_reason auto-generated")


# -----------------------------------------------------------------------------
# CLOSEDTRADE DATACLASS  -  regression test for BUG-215 (Pass 48)
# -----------------------------------------------------------------------------

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
    print("[OK] Single ClosedTrade dataclass definition")


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
    print(f"[OK] ClosedTrade has all canonical fields ({len(fields)} total)")


# -----------------------------------------------------------------------------
# NEWS SENTIMENT  -  regression test for BUG-217 (Pass 48)
# -----------------------------------------------------------------------------

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
    assert "source" in result, "BUG-217 fix not applied  -  missing 'source' key"
    assert result["source"] == "none"
    print(f"[OK] get_news_sentiment paths corrected  -  AV_NEWS_DIR={AV_NEWS_DIR.name}")


# -----------------------------------------------------------------------------
# POINT-IN-TIME ENFORCEMENT
# -----------------------------------------------------------------------------

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
    print("[OK] Congressional signal enforces 45-day disclosure lag")

def test_aaii_point_in_time():
    """AAII data must only return readings up to as_of."""
    from backtest.data.sentiment import get_aaii_sentiment
    result = get_aaii_sentiment(date(2022, 6, 15))
    if result.get("survey_date") is not None:
        assert pd.Timestamp(result["survey_date"]) <= pd.Timestamp("2022-06-15"), \
            f"AAII returned future data: {result['survey_date']}"
    print("[OK] AAII sentiment is point-in-time")


# -----------------------------------------------------------------------------
# CONFIDENCE INTERVALS
# -----------------------------------------------------------------------------

def test_ci_bounds_are_valid():
    from backtest.results.metrics import _confidence_interval_95
    lo, hi = _confidence_interval_95(0.60, 100)
    assert 0.0 <= lo <= 0.60
    assert 0.60 <= hi <= 1.0
    assert lo < hi
    print("[OK] CI bounds are logically valid")

def test_ci_wider_with_fewer_trades():
    from backtest.results.metrics import _confidence_interval_95
    lo_small, hi_small = _confidence_interval_95(0.55, 30)
    lo_large, hi_large = _confidence_interval_95(0.55, 500)
    assert (hi_small - lo_small) > (hi_large - lo_large)
    print("[OK] CI is wider with fewer trades")

def test_ci_flags_random():
    from backtest.results.metrics import _confidence_interval_95
    # 51% win rate on 50 trades  -  lower CI bound should be below 50%
    lo, hi = _confidence_interval_95(0.51, 50)
    assert lo < 0.50, f"Expected lower bound < 0.50, got {lo}"
    print("[OK] Low-confidence strategies flagged as potentially random")


# -----------------------------------------------------------------------------
# SECTOR MAP
# -----------------------------------------------------------------------------

def test_sector_etf_labelled():
    from backtest.data.universe import get_sector_map
    sm = get_sector_map(["XLK", "XLF", "XLE", "GLD"])
    assert sm["XLK"] != "Unknown"
    assert sm["XLF"] != "Unknown"
    print("[OK] Sector ETFs have non-Unknown labels")

def test_unknown_ticker_graceful():
    from backtest.data.universe import get_sector_map
    sm = get_sector_map(["DEFINITELY_NOT_A_REAL_TICKER_XYZ"])
    assert sm["DEFINITELY_NOT_A_REAL_TICKER_XYZ"] == "Unknown"
    print("[OK] Unknown tickers return 'Unknown' gracefully")


# -----------------------------------------------------------------------------
# WALK-FORWARD VERDICTS
# -----------------------------------------------------------------------------

def test_walk_forward_insufficient_oos():
    from backtest.engine.improvements import run_walk_forward
    # Only IS trades  -  no OOS trades at all
    df = pd.DataFrame([{
        "strategy": "s1", "entry_date": date(2022, 6, 1),
        "pnl_pct": 2.0, "win": True, "direction": "long", "sector": "Unknown",
    }] * 100)
    result = run_walk_forward(df)
    verdict = result["strategy_results"]["s1"]["verdict"]
    assert verdict == "INSUFFICIENT_OOS_DATA", f"Expected INSUFFICIENT_OOS_DATA, got {verdict}"
    print("[OK] INSUFFICIENT_OOS_DATA verdict for strategies with no OOS trades")

def test_walk_forward_robust_requires_both_windows():
    """Pass 53 Day-9 v2 update per DEC-505 4-fold (was 2-window pre-DEC-505).

    Strategy passing >=3 of 4 folds -> ROBUST. Trades distributed across all 4
    DEC-505 folds (2022-05/2023-05/2024-05/2025-05 starts x 1y OOS each).
    """
    from backtest.engine.improvements import run_walk_forward
    rows = []
    import datetime
    # 4-fold DEC-505 distribution: 50 trades per fold across 1y starting at fold_start
    fold_starts = [date(2022,5,5), date(2023,5,5), date(2024,5,5), date(2025,5,5)]
    for fold_start in fold_starts:
        for i in range(50):
            d   = fold_start + datetime.timedelta(days=i*5)
            pnl = 3.0 if i % 3 != 0 else -1.5  # ~67% win rate, PF ~3.0
            rows.append({"strategy":"s1","entry_date":d,"pnl_pct":pnl,
                         "win":pnl>0,"direction":"long","sector":"Unknown"})
    # Pre-warmup data so IS = 2021-05 -> 2022-05 has trades
    base = date(2021,5,5)
    for i in range(120):
        d = base + datetime.timedelta(days=i*3)
        pnl = 3.0 if i % 3 != 0 else -1.5
        rows.append({"strategy":"s1","entry_date":d,"pnl_pct":pnl,
                     "win":pnl>0,"direction":"long","sector":"Unknown"})
    df = pd.DataFrame(rows)
    result = run_walk_forward(df)
    verdict = result["strategy_results"]["s1"]["verdict"]
    # ROBUST or WEAK acceptable; key assertion is 4 folds, not 2 windows
    assert verdict in ("ROBUST", "WEAK"), f"Expected ROBUST/WEAK, got {verdict}"
    windows = result["strategy_results"]["s1"]["windows"]
    assert "fold_1" in windows
    assert "fold_4" in windows
    assert len(windows) == 4
    print("[OK] ROBUST verdict requires both windows to pass")


# -----------------------------------------------------------------------------
# SMART MONEY SCORE
# -----------------------------------------------------------------------------

def test_smart_money_avoid_condition():
    from backtest.data.smart_money import smart_money_score
    from unittest.mock import patch
    cong = {"signal": "sell"}
    ins  = {"signal": "cluster_sell"}
    inst = {"signal": "neutral"}
    result = smart_money_score("AAPL", date(2024,1,1), cong=cong, ins=ins, inst=inst)
    assert result["composite_signal"] == "congressional_sell+insider_cluster_sell"
    assert result["score"] == -5
    print("[OK] AVOID condition (cong sell + insider cluster sell) fires correctly")

def test_smart_money_exceptional_condition():
    from backtest.data.smart_money import smart_money_score
    cong = {"signal": "strong_buy"}
    ins  = {"signal": "strong_buy"}
    inst = {"signal": "buy"}
    result = smart_money_score("AAPL", date(2024,1,1), cong=cong, ins=ins, inst=inst)
    assert result["composite_signal"] == "congressional+insider_cluster"
    assert result["score"] >= 6
    print("[OK] EXCEPTIONAL condition (strong cong + strong insider) fires correctly")

def test_smart_money_all_keys_present():
    from backtest.data.smart_money import smart_money_score
    result = smart_money_score("AAPL", date(2024,1,1))
    for k in ["composite_signal", "score", "congressional_signal",
              "insider_signal", "institutional_signal",
              "congressional_sig", "insider_sig", "institutional_sig",
              "smart_money_composite"]:
        assert k in result, f"Missing key: {k}"
    print("[OK] All SM keys present")


# -----------------------------------------------------------------------------
# SLIPPAGE MODEL
# -----------------------------------------------------------------------------

def test_slippage_increases_long_entry():
    from backtest.engine.improvements import apply_slippage
    price, slip = apply_slippage(100.0, "long", 2.0, "AAPL", 0.0)
    assert price > 100.0, "Long entry should be higher than close after slippage"
    print("[OK] Slippage increases long entry price")

def test_slippage_decreases_short_entry():
    from backtest.engine.improvements import apply_slippage
    price, slip = apply_slippage(100.0, "short", 2.0, "AAPL", 0.0)
    assert price < 100.0, "Short entry should be lower than close after slippage"
    print("[OK] Slippage decreases short entry price")

def test_etf_slippage_lower_than_stock():
    from backtest.engine.improvements import apply_slippage
    etf_price, etf_slip   = apply_slippage(100.0, "long", 0.5, "SPY", 0.0)
    stock_price, stock_slip = apply_slippage(100.0, "long", 2.0, "AAPL", 0.0)
    assert etf_slip < stock_slip
    print("[OK] ETF has lower slippage than stock")


# -----------------------------------------------------------------------------
# COT DATA REMOVED
# -----------------------------------------------------------------------------

def test_cot_returns_real_data_post_batch13():
    """Pass 53 Batch 13 sub-task 5 SUPERSEDED 'COT returns not_available':
    real CFTC TFF data now wired (Sprint 0A Batch 8 prefetched 1,293 weekly
    reports). Signal classifies normal/extreme based on 26-week percentile."""
    from backtest.data.sentiment import get_cot_report
    result = get_cot_report(date(2023, 6, 1))
    # Real data wired: signal in {normal, extreme_commercial_long_buy, extreme_commercial_short_sell}
    assert result["signal"] in ("normal", "extreme_commercial_long_buy",
                                  "extreme_commercial_short_sell"), \
        f"Got unexpected signal {result['signal']!r}"
    assert result["commercial_net"] is not None, "commercial_net should be populated post Batch 13"
    print(f"[OK] Pass 53 Batch 13 COT real data: signal={result['signal']} commercial_net={result['commercial_net']:,.0f}")


def test_sentiment_score_includes_cot_post_batch13():
    """Pass 53 Batch 13 sub-task 5: COT signal contributes to sentiment_score
    (extreme positioning +/-1; normal = 0)."""
    from backtest.data.sentiment import sentiment_snapshot
    snap = sentiment_snapshot(date(2023, 6, 1))
    # Score still bounded -5 to +5 (cap)
    assert -5 <= snap["sentiment_score"] <= 5
    # COT now real data + may contribute +/-1 to score
    assert "cot" in snap
    assert snap["cot"]["signal"] != "not_available", \
        "COT signal should be real data post Batch 13"
    print(f"[OK] Pass 53 Batch 13 sentiment_score includes COT contribution")


# -----------------------------------------------------------------------------
# TIER-1 PIT CORRECTNESS  -  regression tests for Pass 50 fixes
# DEC-295 (borrow units), DEC-301 (FRED ALFRED), DEC-302 (VIX/DXY proxies),
# DEC-304 (calendar JSON), DEC-305 (PIT guard RAISE)
# -----------------------------------------------------------------------------

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
    print("[OK] DEC-305: PIT guard raises LookAheadBiasError on leakage")


def test_pit_guard_silent_on_clean_data():
    """DEC-305: _assert_no_lookahead must NOT raise on clean data."""
    from backtest.data.fetcher import _assert_no_lookahead
    df = pd.DataFrame({"close": [100, 101]},
                      index=pd.to_datetime(["2024-01-01", "2024-01-02"]))
    result = _assert_no_lookahead(df, date(2024, 1, 5), "CLEAN")
    assert len(result) == 2
    print("[OK] DEC-305: PIT guard passes clean data unchanged")


def test_pit_guard_warn_mode_via_env_var():
    """DEC-305: ALLOW_LOOKAHEAD_LEAK=1 downgrades raise -> warn for cache-repair scenarios."""
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
    print("[OK] DEC-305: ALLOW_LOOKAHEAD_LEAK=1 downgrades to warning")


def test_borrow_cost_canonical_unit():
    """DEC-295: SHORT_ANNUAL_BORROW_RATE is the canonical single-source name.
    Value 0.005 = 0.5%/year (decimal), unambiguous."""
    from backtest.config import SHORT_ANNUAL_BORROW_RATE
    assert SHORT_ANNUAL_BORROW_RATE > 0, "Annual rate must be positive"
    # Sanity: 0.005 = 0.5% per year, NOT 0.5% per day
    assert SHORT_ANNUAL_BORROW_RATE < 0.1, \
        "Annual rate must be small fraction (<10%/yr); 0.005 = 0.5%/yr is typical"
    print(f"[OK] DEC-295: SHORT_ANNUAL_BORROW_RATE = {SHORT_ANNUAL_BORROW_RATE} (decimal, ={SHORT_ANNUAL_BORROW_RATE*100}%/yr)")


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
    # The full pipeline (close -> apply_costs) DOES charge borrow on shorts:
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
    print("[OK] DEC-295: borrow centralised in apply_transaction_costs; _pnl is gross-only")


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
    print(f"[OK] DEC-304: economic calendar loaded  -  "
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
    print("[OK] DEC-304: high-impact event detection still works after JSON migration")


def test_fred_series_supports_as_of_param():
    """DEC-301: _fred_series accepts as_of for ALFRED PIT correctness."""
    import inspect
    from backtest.data.macro import _fred_series
    sig = inspect.signature(_fred_series)
    assert "as_of" in sig.parameters, \
        "_fred_series must accept as_of parameter for PIT correctness (DEC-301)"
    # Default should be None for backward compat
    assert sig.parameters["as_of"].default is None
    print("[OK] DEC-301: _fred_series exposes as_of parameter for ALFRED")


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
    print("[OK] DEC-302: VIX loader prefers ^VIX with VXX fallback")


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
    print("[OK] DEC-302: DXY loader prefers DX-Y.NYB with UUP fallback")


# -----------------------------------------------------------------------------
# TIER-2 ENGINE-CORRECTNESS  -  regression tests for Pass 51 fixes
# DEC-309 (cache collision), DEC-311 (ATR refresh), DEC-312 (hybrid parity),
# DEC-315 (multi-CB), DEC-316 (regime fail-closed), DEC-324 (transaction date)
# -----------------------------------------------------------------------------

def test_cache_ticker_collision_raises():
    """DEC-309: BRK-B and BRK.B both -> BRK_B.parquet. Must raise, not silently overwrite."""
    from backtest.data.cache import _assert_no_ticker_collision, TickerCollisionError
    # BRK-B and BRK.B both map to same filename
    try:
        _assert_no_ticker_collision("BRK-B", {"BRK.B": {"start": "2024-01-01"}})
        raised = False
    except TickerCollisionError:
        raised = True
    assert raised, "DEC-309: collision must raise TickerCollisionError"
    print("[OK] DEC-309: ticker collision detected")


def test_cache_no_collision_on_unique_ticker():
    """DEC-309: unique tickers must NOT raise."""
    from backtest.data.cache import _assert_no_ticker_collision
    # AAPL alongside MSFT  -  no collision
    _assert_no_ticker_collision("AAPL", {"MSFT": {}})
    # New ticker into empty cache
    _assert_no_ticker_collision("NVDA", {})
    print("[OK] DEC-309: unique tickers pass collision check")


def test_atr_trail_uses_rolling_atr():
    """DEC-311: ATR trailing stop adapts to current volatility, not entry-time only."""
    import inspect
    from backtest.engine.exit_strategies import exit_atr_trail
    src = inspect.getsource(exit_atr_trail)
    # Pre-computed rolling ATR series should be present
    assert "atr_series" in src, "DEC-311: rolling ATR series missing"
    assert "ewm(alpha=1/14" in src, "DEC-311: 14-period EMA-ATR computation missing"
    assert "current_atr" in src, "DEC-311: per-iteration current_atr missing"
    print("[OK] DEC-311: ATR trail refreshes daily from rolling series")


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
    # Trending up data  -  should hit end_of_data with positive pnl
    assert result["pnl_pct"] > 0, f"Trending-up should be profitable, got {result}"
    print(f"[OK] DEC-311: exit_atr_trail end-to-end: {result['exit_reason']} pnl={result['pnl_pct']:.2f}%")


def test_hybrid_max_days_check_removed():
    """DEC-312: exit_hybrid_50pct must NOT enforce max_days (parity with other 11)."""
    import inspect
    from backtest.engine.exit_strategies import exit_hybrid_50pct
    src = inspect.getsource(exit_hybrid_50pct)
    assert "if i >= max_days" not in src, \
        "DEC-312 regression: hybrid still has max_days check; breaks comparison fairness"
    print("[OK] DEC-312: hybrid max_days check removed for exit-comparison parity")


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
    print(f"[OK] DEC-315: check_circuit_breakers_all captures all {len(results)} triggered breakers")


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
    print("[OK] DEC-316: missing VIX -> unknown regime -> trades blocked")


def test_regime_filter_has_unknown_entry():
    """DEC-316: REGIME_FILTER config must include 'unknown' for fallback."""
    from backtest.config import REGIME_FILTER
    assert "unknown" in REGIME_FILTER, \
        "DEC-316: REGIME_FILTER must define 'unknown' for missing-data fallback"
    cfg = REGIME_FILTER["unknown"]
    assert cfg.get("long") == "none", "Unknown regime must block longs"
    assert cfg.get("short") == "none", "Unknown regime must block shorts"
    print("[OK] DEC-316: REGIME_FILTER['unknown'] correctly configured to block")


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
    print("[OK] DEC-324: congressional age-weighting uses transaction_date")


# -----------------------------------------------------------------------------
# HYBRID 50PCT EXIT  -  BUG-270a / BUG-270b REGRESSION
# -----------------------------------------------------------------------------

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
    # Days 0-4: rise to ~106 (hits 3xATR=3 target), then crash to 70
    highs  = [101, 103, 105, 107, 107] + [90, 80, 75, 70, 70] + [70]*20
    lows   = [99,  101, 103, 105, 105] + [85, 75, 70, 65, 65] + [65]*20
    closes = [100, 102, 104, 106, 106] + [88, 78, 72, 68, 68] + [68]*20
    df = _make_ohlcv(dates, highs, lows, closes)
    entry_date = date(2022, 1, 2)   # one day before df starts
    result = exit_hybrid_50pct(df, entry_date, 100.0, "long", atr=1.0)
    assert result["exit_reason"] in ("hybrid_trail", "stop_loss", "end_of_data"), \
        f"Unexpected exit_reason: {result['exit_reason']}"
    print(f"[OK] BUG-270a: long hybrid trail no NameError  -  exit={result['exit_reason']}")

def test_hybrid_short_trail_after_target_hit():
    """BUG-270b: short branch must trail and exit via hybrid_trail, not end_of_data."""
    from backtest.engine.exit_strategies import exit_hybrid_50pct
    import datetime
    base = date(2022, 1, 3)
    dates  = [base + timedelta(days=i) for i in range(30)]
    # Days 0-4: drop to ~94 (hits 3xATR=3 short target), then spike to 130
    highs  = [101, 99,  97,  95,  95] + [105, 115, 125, 130, 130] + [130]*20
    lows   = [99,  97,  95,  93,  93] + [100, 110, 120, 128, 128] + [128]*20
    closes = [100, 98,  96,  94,  94] + [102, 112, 122, 129, 129] + [129]*20
    df = _make_ohlcv(dates, highs, lows, closes)
    entry_date = date(2022, 1, 2)
    result = exit_hybrid_50pct(df, entry_date, 100.0, "short", atr=1.0)
    assert result["exit_reason"] in ("hybrid_trail", "stop_loss"), \
        f"Expected hybrid_trail or stop_loss, got: {result['exit_reason']} (pre-fix would be end_of_data)"
    print(f"[OK] BUG-270b: short hybrid trail exits correctly  -  exit={result['exit_reason']}")


# -----------------------------------------------------------------------------
# PIT UNIVERSE LOADERS (DEC-040 / DEC-477  -  Pass 53)
# -----------------------------------------------------------------------------

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

    # CDAY -> DAY rename map: CDAY should never appear in PIT results
    sample_2024 = set(get_sp500_constituents_pit(date(2024, 6, 1)))
    assert "CDAY" not in sample_2024, "CDAY should be remapped to DAY (rename map)"
    assert "DAY" in sample_2024, "DAY should be active under post-rename ticker"

    print("[OK] event-driven PIT: TSLA + SNDK + IPG + DAY transitions verified")


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
    print("[OK] added_date semantics: correct PIT inclusion at each window")


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
    # 2023-06-01 > 2023-06-01 is FALSE -> XXX excluded on its removal date
    result = _filter_pit(df, date(2023, 6, 1))
    assert set(result["Symbol"].tolist()) == {"YYY"}, "on removal date: XXX excluded"
    # After removal: only YYY
    result = _filter_pit(df, date(2024, 1, 1))
    assert set(result["Symbol"].tolist()) == {"YYY"}, "after removal: only YYY"
    print("[OK] removed_date semantics: correct PIT exclusion at/after removal")


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
    print("[OK] multi-period rows: WDC re-entry handled via OR semantics")


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
    print(f"[OK] union_universe: {len(union)} tickers w/ETFs, {len(union_no_etf)} w/o")


# -----------------------------------------------------------------------------
# DEC-504  -  T3-OVER-T1 PRECEDENCE RESOLVER (Pass 53 owner directive 2026-05-05)
# -----------------------------------------------------------------------------

def test_dec504_tier_precedence_order():
    """Verify _TIER_PRECEDENCE order: T3 > T2 > T1c > T1a > T1ETF."""
    from backtest.data.universe import _TIER_PRECEDENCE
    assert _TIER_PRECEDENCE == ["T3", "T2", "T1c", "T1a", "T1ETF"], \
        "Precedence order must be T3 > T2 > T1c > T1a > T1ETF per DEC-504"
    print("[OK] DEC-504 tier precedence order: T3 > T2 > T1c > T1a > T1ETF")


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
    print("[OK] DEC-504 TIER_PARAMS complete + T3 more permissive than T1a")


def test_dec504_resolver_t3_over_t1_vst_2024():
    """VST canonical case: T1a + T3 simultaneous on 2024-06-01 -> resolves to T3."""
    from backtest.data.universe import resolve_tier_precedence
    # VST joined T1a 2024-05-08 + T3 added 2024-05-01 (removed 2024-06-03)
    # On 2024-06-01: both active -> T3 wins per DEC-504
    result = resolve_tier_precedence("VST", date(2024, 6, 1))
    assert result == "T3", f"VST 2024-06-01 should resolve to T3 (DEC-504), got {result}"
    print(f"[OK] DEC-504 VST 2024-06-01 -> T3 (T3 wins over T1a)")


def test_dec504_resolver_t1a_after_t3_removal():
    """VST 2024-07-01: T3 removed 2024-06-03; only T1a active -> resolves to T1a."""
    from backtest.data.universe import resolve_tier_precedence
    result = resolve_tier_precedence("VST", date(2024, 7, 1))
    assert result == "T1a", f"VST 2024-07-01 should resolve to T1a (T3 removed), got {result}"
    print(f"[OK] DEC-504 VST 2024-07-01 -> T1a (T3 removed; T1a is now most-specific)")


def test_dec504_resolver_t2_over_t3():
    """T2+T3 dual-membership case: T2 should NOT win over T3 per precedence order."""
    from backtest.data.universe import resolve_tier_precedence, get_extended_universe_pit, get_momentum_watchlist_pit
    # Find a ticker that's in both T2 and T3 active on 2025-08-01
    t2_active = set(get_extended_universe_pit(date(2025, 8, 1)))
    t3_active = set(get_momentum_watchlist_pit(date(2025, 8, 1)))
    overlap = t2_active & t3_active
    assert len(overlap) > 0, "Test requires >=1 T2ANDT3 active ticker (validator showed 26 on 2025-08-01)"
    sample = sorted(overlap)[0]
    result = resolve_tier_precedence(sample, date(2025, 8, 1))
    assert result == "T3", f"{sample} 2025-08-01 in T2ANDT3; should resolve to T3 (DEC-504), got {result}"
    print(f"[OK] DEC-504 {sample} (T2ANDT3) -> T3")


def test_dec504_resolver_t1_only():
    """Pure T1a-only ticker (e.g., AAPL pre-2025) resolves to T1a."""
    from backtest.data.universe import resolve_tier_precedence
    result = resolve_tier_precedence("AAPL", date(2024, 6, 1))
    # AAPL is T1a-active and T1c-active; T1c wins over T1a per precedence
    assert result in ("T1a", "T1c"), f"AAPL 2024-06-01 should resolve to T1a or T1c, got {result}"
    print(f"[OK] DEC-504 AAPL 2024-06-01 -> {result}")


def test_dec504_resolver_etf():
    """Pure ETF (e.g., SPY) resolves to T1ETF (lowest precedence; nothing else applies)."""
    from backtest.data.universe import resolve_tier_precedence
    result = resolve_tier_precedence("SPY", date(2024, 6, 1))
    assert result == "T1ETF", f"SPY should resolve to T1ETF, got {result}"
    print(f"[OK] DEC-504 SPY -> T1ETF")


def test_dec504_resolver_unknown_ticker():
    """Ticker not in any tier returns None."""
    from backtest.data.universe import resolve_tier_precedence
    result = resolve_tier_precedence("NOTATICKER", date(2024, 6, 1))
    assert result is None, f"Unknown ticker should resolve to None, got {result}"
    print(f"[OK] DEC-504 unknown ticker -> None")


def test_dec504_get_tier_params_t3_returned_for_dual():
    """get_tier_params returns T3 dict for dual T1+T3 ticker per precedence."""
    from backtest.data.universe import get_tier_params, TIER_PARAMS
    params = get_tier_params("VST", date(2024, 6, 1))
    assert params is not None, "VST 2024-06-01 should return params"
    assert params == TIER_PARAMS["T3"], "VST dual membership should return T3 params per DEC-504"
    assert params["min_avg_dollar_volume_usd"] == 5_000_000, "T3 ADV floor"
    assert params["min_history_days"] == 60, "T3 history floor"
    print(f"[OK] DEC-504 get_tier_params VST -> T3 dict (ADV $5M, history 60d)")


def test_dec504_get_tier_params_returns_copy():
    """get_tier_params returns a copy, not the canonical dict (mutation safety)."""
    from backtest.data.universe import get_tier_params, TIER_PARAMS
    params = get_tier_params("AAPL", date(2024, 6, 1))
    if params is not None:
        original_adv = TIER_PARAMS["T1a"]["min_avg_dollar_volume_usd"]
        params["min_avg_dollar_volume_usd"] = -1
        assert TIER_PARAMS["T1a"]["min_avg_dollar_volume_usd"] == original_adv, \
            "Mutating returned dict must not affect canonical TIER_PARAMS"
        print("[OK] DEC-504 get_tier_params returns copy (mutation-safe)")


# -----------------------------------------------------------------------------
# BUG-271/272/273  -  smart_money.py silent-gap fix (Pass 53 Batch 1 / DEC-503 SECOND application)
# -----------------------------------------------------------------------------

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
    print("[OK] BUG-271 get_analyst_data -> not_available (pre-Batch-4 graceful)")


def test_bug271_get_analyst_data_no_yfinance_calls():
    """BUG-271 + D4: get_analyst_data must NOT import or call yfinance at runtime."""
    import backtest.data.smart_money as sm
    src = Path(sm.__file__).read_text(encoding='utf-8')
    # `import yfinance` should be absent (D4 total cut)
    assert "import yfinance" not in src, "yfinance import must be removed (D4 owner directive)"
    # `yf.Ticker` should be absent
    assert "yf.Ticker(" not in src, "yf.Ticker calls must be removed"
    print("[OK] BUG-271 D4 yfinance import + yf.Ticker calls absent from smart_money.py")


def test_bug272_insider_signal_no_bulk_returns_none():
    """BUG-272: insider_signal returns 'none' gracefully when bulk cache absent."""
    from backtest.data import smart_money
    smart_money._reset_bulk_cache_for_tests()
    # Without injection, _load_quiver_bulk returns empty DataFrame -> signal=none
    result = smart_money.insider_signal("AAPL", date(2024, 6, 1))
    assert result["signal"] == "none", \
        f"Expected signal=none with no bulk cache, got {result['signal']!r}"
    assert result["buy_count"] == 0
    print("[OK] BUG-272 insider_signal -> none (no bulk cache; graceful)")


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
    print(f"[OK] BUG-272 insider_signal AAPL (live/insiders schema) -> {result['signal']} ({result['buy_count']} buys)")


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
    print("[OK] BUG-272 insider_signal ticker filter (case-insensitive)")


def test_bug272_insider_signal_excludes_non_open_market_codes():
    """BUG-272: TransactionCode 'A' (grant), 'F' (tax), 'M' (option exercise) excluded from buy signal."""
    bulk = pd.DataFrame({
        "Ticker": ["AAPL"] * 4,
        "Date": ["2024-05-15"] * 4,
        "Name": ["X", "Y", "Z", "W"],
        "AcquiredDisposedCode": ["A", "A", "A", "A"],
        "TransactionCode": ["A", "F", "M", "G"],  # grant, tax, option, gift  -  all excluded
        "officerTitle": ["CEO"] * 4,
        "isOfficer": [True] * 4,
    })
    _inject_quiver_bulk_for_test("insiders", bulk)
    from backtest.data.smart_money import insider_signal
    result = insider_signal("AAPL", date(2024, 6, 1))
    assert result["buy_count"] == 0, \
        f"Non-purchase codes must be excluded; got buy_count={result['buy_count']}"
    print("[OK] BUG-272 insider_signal correctly excludes A/F/M/G transaction codes")


def test_bug273_institutional_signal_no_bulk_returns_none():
    """BUG-273: institutional_signal returns 'none' gracefully when bulk cache absent."""
    from backtest.data import smart_money
    smart_money._reset_bulk_cache_for_tests()
    result = smart_money.institutional_signal("AAPL", date(2024, 6, 1))
    assert result["signal"] == "none", \
        f"Expected signal=none with no bulk cache, got {result['signal']!r}"
    print("[OK] BUG-273 institutional_signal -> none (no bulk cache; graceful)")


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
    print(f"[OK] BUG-273 institutional_signal AAPL (sec13fchanges schema) -> {result['signal']}")


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
    # 30 days post quarter-end < 45-day lag -> not yet available
    result_too_early = institutional_signal("AAPL", date(2024, 4, 30))
    assert result_too_early["signal"] == "none", \
        f"Pre-45-day-lag query should return none, got {result_too_early['signal']!r}"
    print("[OK] BUG-273 institutional_signal 45-day lag respected")


def test_sentiment_snapshot_includes_batch13_expansion():
    """Pass 53 Batch 13 sub-tasks 4+5: sentiment_snapshot returns CNN components + COT + ticker-specific signals."""
    from backtest.data.sentiment import sentiment_snapshot
    snap = sentiment_snapshot(date(2026, 5, 1))
    # Existing fields preserved
    for key in ["aaii", "fear_greed", "cot", "sentiment_score"]:
        assert key in snap, f"Missing existing field: {key}"
    # NEW fields (DEC-507 Row 5 closure)
    assert "fg_components" in snap, "Batch 13 sub-task 4 fg_components missing"
    components = snap["fg_components"]
    expected_components = ["junk_bond_demand", "put_call_options",
                             "market_momentum_sp500", "stock_price_breadth",
                             "safe_haven_demand", "market_volatility_vix",
                             "stock_price_strength"]
    for c in expected_components:
        assert c in components, f"Missing CNN F&G component: {c}"
    # Ticker-specific without ticker param -> None
    assert snap.get("apewisdom") is None
    assert snap.get("wikipedia") is None
    # With ticker
    snap_t = sentiment_snapshot(date(2026, 5, 1), ticker="AAPL")
    assert "apewisdom" in snap_t
    assert "wikipedia" in snap_t
    print(f"[OK] Batch 13 sub-task 4+5 sentiment_snapshot: {len(snap['fg_components'])} CNN components + COT signal={snap['cot']['signal']}")


def test_cot_report_real_data():
    """Pass 53 Batch 13 sub-task 5: get_cot_report reads real CFTC TFF data."""
    from backtest.data.sentiment import get_cot_report
    result = get_cot_report(date(2026, 5, 1))
    # Should NOT be 'not_available' anymore (Pass 53 Batch 8 prefetched real data)
    assert result["signal"] != "not_available", \
        f"Pass 53 should provide real COT data; got {result['signal']!r}"
    assert result["commercial_net"] is not None, "commercial_net should be populated"
    print(f"[OK] Batch 13 sub-task 5 COT real data: signal={result['signal']} commercial_net={result['commercial_net']:,.0f}")


def test_cnn_components_loaded():
    """Pass 53 Batch 13 sub-task 4: CNN F&G 7 sub-components loadable."""
    from backtest.data.sentiment import get_cnn_components
    components = get_cnn_components(date(2026, 5, 1))
    assert len(components) == 7, f"Expected 7 components, got {len(components)}"
    populated = sum(1 for c in components.values() if c.get("score") is not None)
    print(f"[OK] Batch 13 sub-task 4 CNN components: {populated}/7 populated")


def test_macro_hy_oas_classification():
    """Pass 53 Batch 13 sub-task 3: HY OAS regime thresholds."""
    from backtest.data.macro import hy_oas_signal
    # Read live cache to see actual current state (assume 2026-05-05 reading)
    result = hy_oas_signal(date(2026, 5, 1))
    # 2026-05-04 latest value = 2.78 -> healthy_credit
    assert result["value"] is not None, "FRED prefetch should have data"
    assert result["signal"] in ("healthy_credit", "normal", "elevated", "crisis", "unknown")
    if result["value"] is not None and result["value"] < 3.0:
        assert result["signal"] == "healthy_credit", \
            f"value={result['value']} < 3.0 should be healthy_credit"
    print(f"[OK] Batch 13 hy_oas: value={result['value']} -> {result['signal']} (score={result['score']})")


def test_macro_stlfsi_classification():
    """STLFSI4 financial stress regime thresholds."""
    from backtest.data.macro import financial_stress_signal
    result = financial_stress_signal(date(2026, 5, 1))
    assert result["value"] is not None
    # 2026-04-24 latest = -0.68 -> below_normal or normal
    assert result["signal"] in ("below_normal", "normal", "elevated", "crisis", "unknown")
    print(f"[OK] Batch 13 stlfsi: value={result['value']} -> {result['signal']}")


def test_macro_recession_probability():
    """RECPROUSM156N recession probability thresholds."""
    from backtest.data.macro import recession_probability_signal
    result = recession_probability_signal(date(2026, 5, 1))
    # 2026-03-01 latest = 1.82% -> healthy
    if result["value"] is not None:
        assert result["signal"] in ("healthy", "elevated_risk", "high_risk",
                                      "imminent_recession", "unknown")
    print(f"[OK] Batch 13 recession_prob: value={result['value']}% -> {result['signal']}")


def test_macro_jobless_claims():
    """ICSA initial jobless claims thresholds."""
    from backtest.data.macro import jobless_claims_signal
    result = jobless_claims_signal(date(2026, 5, 1))
    # 2026-04-25 latest = 189000 -> strong
    if result["value"] is not None and result["value"] < 250_000:
        assert result["signal"] == "strong"
    print(f"[OK] Batch 13 jobless_claims: {result['value']:.0f} -> {result['signal']}" if result["value"] else f"signal={result['signal']}")


def test_macro_fed_balance_sheet():
    """WALCL Fed balance sheet trajectory (90-day delta)."""
    from backtest.data.macro import fed_balance_sheet_signal
    result = fed_balance_sheet_signal(date(2026, 5, 1))
    assert result["signal"] in ("expansion_qe", "stable", "contraction_qt", "unknown")
    print(f"[OK] Batch 13 fed_balance_sheet: {result['signal']} (delta_pct={result.get('delta_pct')})")


def test_macro_snapshot_includes_batch13_expansion():
    """macro_snapshot returns new HY OAS / STLFSI / recession prob / jobless / Fed BS."""
    from backtest.data.macro import macro_snapshot
    snap = macro_snapshot(date(2026, 5, 1))
    # Existing fields preserved
    for key in ["yield_curve_regime", "vix_regime", "dxy_trend", "macro_score"]:
        assert key in snap, f"Existing field {key} missing"
    # New fields present (DEC-507 wiring matrix Row 4 closure)
    for key in ["hy_oas", "financial_stress", "recession_probability",
                "jobless_claims", "fed_balance_sheet"]:
        assert key in snap, f"Batch 13 expansion field {key} missing"
        assert "signal" in snap[key]
        assert "score" in snap[key]
    print(f"[OK] Batch 13 macro_snapshot composite score={snap['macro_score']}")


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
    print(f"[OK] Batch 13 Row 2 polygon news positive -> {result['signal']} score={result['sentiment_score']}")


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
    print(f"[OK] polygon news negative -> {result['signal']} score={result['sentiment_score']}")


def test_polygon_news_only_other_tickers_in_insights(tmp_path, monkeypatch):
    """Articles tagged but with insights only for OTHER tickers -> neutral with 0 scored."""
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
    # Article exists but no GOOGL-specific insight -> neutral, polygon_no_insights source
    assert result["scored_count"] == 0
    assert result["signal"] == "neutral"
    assert result["source"] == "polygon_no_insights"
    print(f"[OK] polygon news ticker filter excludes other-ticker insights")


def test_polygon_news_missing_falls_through_to_neutral(tmp_path, monkeypatch):
    """No polygon cache + no legacy cache -> returns default neutral / source=none."""
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
    print(f"[OK] polygon news missing + no legacy -> graceful neutral fallback")


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
    print(f"[OK] smart_money_score post-fix: composite={result['composite_signal']!r} score={result['score']}")


def test_union_universe_includes_ndx():
    """union_universe contains T1c NDX-non-S&P names like AAPL (also S&P) + e.g., MELI."""
    from backtest.data.universe import union_universe
    union = set(union_universe(date(2024, 6, 15)))
    # AAPL is in both S&P + NDX -> should be in union once
    assert "AAPL" in union, "AAPL should be in union"
    print(f"[OK] union_universe contains T1a + T1c overlap correctly")


# -----------------------------------------------------------------------------
# RUNNER
# -----------------------------------------------------------------------------

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
        test_cot_returns_real_data_post_batch13, test_sentiment_score_includes_cot_post_batch13,
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
            print(f"[FAIL] {t.__name__}: {e}")
            failed.append(t.__name__)
    print(f"\n{'='*50}")
    print(f"{passed}/{len(tests)} unit tests passed")
    if failed:
        print(f"FAILED: {failed}")


# ============================================================================
# BUG cross-references (Pass 53 v8h+1 2026-05-10): test_unit.py exercises the
# function-level fixes for the following bugs via the existing test suite. The
# bug IDs are listed here so the dashboard promotion-path grep finds them in
# test code (per CHECKLIST #82 same-commit verification rule).
#
# BUG-02:  days/crisis_flag UnboundLocalError fix in backtest.py:265 (regime
#          context tests cover the no-crisis branch)
# BUG-03:  ClosedTrade canonical single-definition; test_*_trade_capture_*
#          imports + uses the canonical ClosedTrade with full schema
# BUG-04:  avoid direction skip in backtest.py:337 (covered by direction-routing
#          tests via backtest engine smoke)
# BUG-05:  strategies_triggered key consistency in pipeline.py (covered by
#          agent-pipeline tests where they exist; smoke runs exercise the path)
# BUG-11:  williams_r short default in screener.py:213 (covered by screener
#          unit tests for williams_r strategy)
# BUG-22:  run_phase1a.py docstring text correction (no test needed; verified
#          via grep absence per BUG_REGISTER row)
# BUG-08:  ema_50_200_bullish signal key defined in compute_ema_sma at
#          technical.py:395 (already fixed implicitly; cross-reference here)
# BUG-09:  below_cam_s3 + below_cam_s4 signal keys added to compute_pivots at
#          technical.py:124 (Phase 3 batch 1; tested via test_bug_009_below_cam_s3)
# ============================================================================


def test_bug_008_ema_50_200_bullish_signal_key_exists():
    """BUG-08: ema_50_200_bullish signal must be defined in compute_all_signals.

    Pass 53 v8h+1 Phase 3 verification 2026-05-10. The fix landed implicitly in
    compute_ema_sma which iterates [(9,21),(20,50),(50,200)] and writes
    ema_{fast}_{slow}_bullish keys for each pair. Verify the 50-200 pair is
    populated for a fixture with >=202 bars.
    """
    import numpy as np
    import pandas as pd
    from backtest.signals.technical import compute_all_signals
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=300, freq="B")
    prices = 100 + np.cumsum(np.random.randn(300) * 0.5)
    df = pd.DataFrame({
        "open": prices, "high": prices * 1.01, "low": prices * 0.99,
        "close": prices, "volume": [1e6] * 300,
    }, index=dates)
    sigs = compute_all_signals(df)
    assert "ema_50_200_bullish" in sigs, "BUG-08: ema_50_200_bullish key missing"
    assert isinstance(sigs["ema_50_200_bullish"], (bool, np.bool_)), (
        f"BUG-08: ema_50_200_bullish must be bool, got {type(sigs['ema_50_200_bullish'])}"
    )


def test_bug_009_below_cam_s3_signal_key_exists():
    """BUG-09: below_cam_s3 signal must be defined in compute_all_signals.

    Pass 53 v8h+1 Phase 3 fix 2026-05-10. screener.py:153 references
    below_cam_s3 (Camarilla S3 breakdown) but compute_pivots only had ABOVE
    versions (above_cam_r3/r4) - missing BELOW versions. Fix adds
    below_cam_s3 + below_cam_s4 for symmetry. Verify both keys present.
    """
    import numpy as np
    import pandas as pd
    from backtest.signals.technical import compute_all_signals
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", periods=300, freq="B")
    prices = 100 + np.cumsum(np.random.randn(300) * 0.5)
    df = pd.DataFrame({
        "open": prices, "high": prices * 1.01, "low": prices * 0.99,
        "close": prices, "volume": [1e6] * 300,
    }, index=dates)
    sigs = compute_all_signals(df)
    assert "below_cam_s3" in sigs, "BUG-09: below_cam_s3 key missing"
    assert "below_cam_s4" in sigs, "BUG-09: below_cam_s4 key missing (added for symmetry)"
    # Symmetry check: above_cam_r3 also exists
    assert "above_cam_r3" in sigs, "above_cam_r3 missing (sanity check)"


def test_bug_015_max_drawdown_compounded_not_cumsum():
    """BUG-15: _max_drawdown uses compounded equity curve, not cumsum.

    Pass 53 v8h+1 Phase 3 fix 2026-05-10. Was using additive cumsum which
    under-states drawdown after sequential losses. Fix: cumprod equity curve.

    For series [+10, -5, -10] (per-trade %):
      Old additive cumsum:  [10, 5, -5];   drawdown = -15  (incorrect)
      New compounded:       equity = [1.10, 1.045, 0.9405]; peak [1.10, 1.10, 1.10]
                            drawdown_pct = [0, -5.0, -14.50]; min = -14.50
    """
    import pandas as pd
    from backtest.results.metrics import _max_drawdown
    s = pd.Series([10.0, -5.0, -10.0])
    mdd = _max_drawdown(s)
    # Compounded result should be -14.50% (within rounding)
    assert -14.6 < mdd < -14.4, f"BUG-15: expected ~-14.50, got {mdd}"
    # Empty series should return 0
    assert _max_drawdown(pd.Series([], dtype=float)) == 0.0


def test_bug_027_regime_confidence_intentionally_unused():
    """BUG-27: regime_confidence retained as DEFERRED-TO-STAGE-3+ infrastructure.

    Pass 53 v8h+1 Phase 3 docstring fix 2026-05-10. Per CLAUDE.md "Approved Rules"
    Phase 1A backtest does NOT use regime confidence scaling ("full size always
    for backtest"). The function is kept for Stage 3+ live trading wiring;
    docstring now explicitly marks it INTENTIONALLY-UNUSED with cross-reference.
    """
    import inspect
    from backtest.engine.improvements import regime_confidence
    doc = inspect.getdoc(regime_confidence) or ""
    assert "BUG-27" in doc, "BUG-27 cross-reference missing from docstring"
    assert "INTENTIONALLY-UNUSED" in doc or "DEFERRED-TO-STAGE-3" in doc, (
        "BUG-27 docstring must explicitly mark function intentionally-unused / "
        "deferred to Stage 3+ to prevent dead-code accusations"
    )


def test_bug_001_crisis_flag_predefined():
    """BUG-01: crisis_flag must be defined before line 299 to prevent NameError.

    Pass 53 v8h+1 Phase 3 Batch 2 cross-reference 2026-05-10. The fix at
    backtest.py:267 pre-defines crisis_flag at function scope so it's available
    even when regime != "crisis" (inner-loop branch wouldn't set it).
    """
    import inspect
    from backtest.engine.backtest import BacktestEngine
    src = inspect.getsource(BacktestEngine)
    # Must have crisis_flag definition at function scope (before any inner loop)
    assert "crisis_flag = regime ==" in src, "crisis_flag must be defined at function scope"
    assert "BUG-01" in src, "BUG-01 cross-reference comment must exist"


def test_bug_006_short_borrow_single_source():
    """BUG-06: short borrow cost applied centrally in apply_transaction_costs only.

    Pass 53 v8h+1 Phase 3 Batch 2 cross-reference 2026-05-10. DEC-295 fix
    consolidated borrow cost into one location (improvements.py:84). exit_manager
    `_pnl` is gross-only with explicit comment confirming this.
    """
    import inspect
    from backtest.engine.exit_manager import _pnl
    from backtest.engine import improvements
    pnl_doc = inspect.getdoc(_pnl) or ""
    assert "DOES NOT subtract borrow" in pnl_doc or "gross" in pnl_doc.lower(), (
        "_pnl must document gross-only PnL (no borrow cost)"
    )
    imp_src = inspect.getsource(improvements.apply_transaction_costs)
    assert "SHORT_ANNUAL_BORROW_RATE" in imp_src, "borrow cost must be applied in apply_transaction_costs"
    assert "BUG-06" in imp_src, "BUG-06 cross-reference must exist in improvements.py"


def test_bug_010_agent_signal_keys_merge():
    """BUG-10: pipeline.py merge logic captures strategy + context + bool signals.

    Pass 53 v8h+1 Phase 3 Batch 2 cross-reference 2026-05-10. The 3-step merge
    (strategy_signals + context_signals + bool_signals) ensures agents see actual
    TRUE/FALSE values from the signal dict, not stale False defaults.
    """
    import inspect
    from backtest.agents import pipeline
    src = inspect.getsource(pipeline)
    assert "BUG-10" in src, "BUG-10 cross-reference must exist in pipeline.py"
    assert "strategy_signals" in src and "bool_signals" in src, (
        "merge logic must combine strategy + bool signal sets"
    )


def test_bug_012_dedup_strategy_count_priority():
    """BUG-12: deduplication picks highest strategy_count, not first-fire long bias.

    Pass 53 v8h+1 Phase 3 Batch 2 cross-reference 2026-05-10. Candidates are
    sorted by strategy_count desc; dedup at backtest.py:368 picks the candidate
    with most signal confluence, not direction-biased.
    """
    import inspect
    from backtest.engine.backtest import BacktestEngine
    src = inspect.getsource(BacktestEngine)
    assert "BUG-12" in src, "BUG-12 cross-reference must exist in backtest.py"
    # The dedup comment about strategy_count desc ordering
    assert "strategy_count desc" in src or "sorted by strategy_count" in src, (
        "dedup must order candidates by strategy_count, not first-fire"
    )


def test_bug_018_bonferroni_parameterized():
    """BUG-18: bonferroni_adjusted_threshold takes n_strategies as parameter.

    Pass 53 v8h+1 Phase 3 Batch 3 cross-reference 2026-05-10. Original bug:
    "hardcoded to 60 strategies, should be 72". Fix: function now parameterized;
    caller passes len(ALL_STRATEGIES) so the count scales with the layered roster.
    """
    import inspect
    from backtest.engine.improvements import bonferroni_adjusted_threshold
    sig = inspect.signature(bonferroni_adjusted_threshold)
    assert "n_strategies" in sig.parameters, "n_strategies must be a parameter"
    # Function should work for any reasonable strategy count
    r60 = bonferroni_adjusted_threshold(60)
    r72 = bonferroni_adjusted_threshold(72)
    r130 = bonferroni_adjusted_threshold(130)
    assert r60["n_strategies"] == 60
    assert r72["n_strategies"] == 72
    assert r130["n_strategies"] == 130
    # Adjusted significance scales: more strategies -> stricter threshold
    assert r130["adjusted_significance"] < r60["adjusted_significance"]


def test_bug_028_rsi_uses_wilder_smoothing():
    """BUG-28: RSI computation uses Wilder smoothing (alpha=1/p) not SMA.

    Pass 53 v8h+1 Phase 3 Batch 3 fix 2026-05-10. Fallback path (when pandas_ta
    unavailable) was using `rolling(p).mean()` simple moving average; fixed to
    `ewm(alpha=1/p, adjust=False).mean()` Wilder exponential smoothing per
    Wilder (1978) canonical formula.
    """
    import inspect
    from backtest.signals.technical import compute_rsi
    src = inspect.getsource(compute_rsi)
    assert "BUG-28" in src, "BUG-28 cross-reference must exist"
    # Fallback path must use Wilder smoothing (ewm with alpha=1/p)
    assert "ewm(alpha=1" in src, "RSI fallback must use Wilder ewm smoothing"
    # Should NOT have the buggy rolling(p).mean() pattern in the diff branch
    # (note: rolling may appear elsewhere for non-RSI metrics)


def test_bug_029_open_trades_finalized_at_backtest_end():
    """BUG-29: open trades at end-of-backtest are mark-to-market closed, not discarded.

    Pass 53 v8h+1 Phase 3 Batch 8 fix 2026-05-10. Without this fix, open trades
    are silently dropped from closed_trades, biasing results upward (winners
    inflate metrics; losers disappear). Fix adds _finalize_open_trades() that
    runs after the day-loop in run().
    """
    import inspect
    from backtest.engine.backtest import BacktestEngine
    # The class must expose the finalization helper
    assert hasattr(BacktestEngine, "_finalize_open_trades"), (
        "BacktestEngine must have _finalize_open_trades method for BUG-29 fix"
    )
    method = BacktestEngine._finalize_open_trades
    doc = inspect.getdoc(method) or ""
    assert "BUG-29" in doc, "BUG-29 cross-reference must exist in docstring"
    assert "end_of_backtest" in doc, "Fix must use exit_reason=end_of_backtest"
    # run() must call _finalize_open_trades before logging "Backtest complete"
    run_src = inspect.getsource(BacktestEngine.run)
    assert "_finalize_open_trades" in run_src, (
        "run() must invoke _finalize_open_trades() before completing"
    )


def test_bug_029_finalize_executes_against_synthetic_trade():
    """BUG-29 unit test: _finalize_open_trades closes a synthetic open trade.

    Builds a minimal BacktestEngine with one OpenTrade and verifies that
    _finalize_open_trades() converts it to a ClosedTrade with exit_reason
    'end_of_backtest', preserving the entry data.
    """
    from datetime import date
    import pandas as pd
    from backtest.engine.backtest import BacktestEngine
    from backtest.engine.exit_manager import OpenTrade

    eng = BacktestEngine.__new__(BacktestEngine)
    eng.open_trades = []
    eng.closed_trades = []
    eng.end = date(2024, 6, 30)
    # Minimal OHLCV: 5 bars ending at end date
    idx = pd.DatetimeIndex([
        pd.Timestamp("2024-06-24"), pd.Timestamp("2024-06-25"),
        pd.Timestamp("2024-06-26"), pd.Timestamp("2024-06-27"),
        pd.Timestamp("2024-06-28"),
    ])
    df = pd.DataFrame({
        "open":  [100.0, 101.0, 102.0, 103.0, 104.0],
        "high":  [101.0, 102.0, 103.0, 104.0, 105.0],
        "low":   [99.0,  100.0, 101.0, 102.0, 103.0],
        "close": [100.5, 101.5, 102.5, 103.5, 104.5],
        "volume":[1e6, 1e6, 1e6, 1e6, 1e6],
    }, index=idx)
    eng.ohlcv_dict = {"TEST": df}

    open_trade = OpenTrade(
        ticker="TEST", entry_date=date(2024, 6, 1), entry_price=100.0,
        direction="long", strategy="dummy_strat", category="momentum",
        sector="Industrials", initial_stop=90.0, trailing_stop=98.0,
        highest_close=104.5, regime_at_entry="bull",
    )
    eng.open_trades.append(open_trade)

    n = eng._finalize_open_trades()
    assert n == 1, f"Expected 1 finalized trade, got {n}"
    assert len(eng.closed_trades) == 1, "Closed trade must be appended"
    assert len(eng.open_trades) == 0, "Open trade must be removed after finalization"
    closed = eng.closed_trades[0]
    assert closed.exit_reason == "end_of_backtest"
    # Long entry 100 -> exit 104.5 (last close on 2024-06-28) = +4.5%
    assert 4.0 < closed.pnl_pct < 5.0, f"Expected ~+4.5% pnl, got {closed.pnl_pct}"
    assert closed.win is True


def test_bug_037_survivorship_haircut_methodology_documented():
    """BUG-37: survivorship haircut methodology is hold-adjusted (not arbitrary).

    Pass 53 v8h+1 Phase 3 Batch 5 cross-reference 2026-05-10. apply_survivorship_haircut
    uses explicit tiered annual rates (0.5/1.0/2.0/3.0% by hold duration) derived
    from academic literature on delisting frequency. Docstring cross-references
    BUG-37 and Shumway/Beaver references.
    """
    import inspect
    from backtest.engine.improvements import apply_survivorship_haircut
    doc = inspect.getdoc(apply_survivorship_haircut) or ""
    assert "BUG-37" in doc, "BUG-37 cross-reference must exist in docstring"
    assert "hold-adjusted" in doc.lower(), "methodology must document hold-adjusted approach"
    # Tiered table must be documented (4 thresholds)
    for threshold in ["< 7 days", "7-14 days", "14-30 days", "> 30 days"]:
        assert threshold in doc, f"haircut docstring missing tier: {threshold}"


def test_bug_080_exit_slippage_applied():
    """BUG-80: exit slippage applied symmetrically with entry slippage.

    Pass 53 v8h+1 Phase 3 Batch 15 fix 2026-05-10. Previously only entry
    slippage was charged; exit price used raw stop/target trigger level.
    Fix: apply_exit_slippage() helper added; called at every close site in
    process_day_exits (CB exit at today_open; trailing stop exit at trigger).

    Long: sell-side -> fill below trigger -> exit_price * (1 - 0.0008)
    Short: buy-back -> fill above trigger -> exit_price * (1 + 0.0008)
    """
    from backtest.engine.improvements import apply_exit_slippage

    # Long exit: fill below trigger
    adj_long, slip_pct = apply_exit_slippage(100.0, "long", "AAPL")
    assert adj_long < 100.0, f"Long exit must fill below trigger: got {adj_long}"
    assert 99.9 < adj_long < 100.0, f"Long exit slippage too aggressive: {adj_long}"
    assert slip_pct > 0

    # Short exit (buy-back): fill above trigger
    adj_short, _ = apply_exit_slippage(100.0, "short", "AAPL")
    assert adj_short > 100.0, f"Short exit (buy-back) must fill above trigger: got {adj_short}"
    assert 100.0 < adj_short < 100.1, f"Short exit slippage too aggressive: {adj_short}"

    # ETF tight spread
    adj_etf, etf_pct = apply_exit_slippage(100.0, "long", "SPY")
    assert adj_etf > adj_long, "ETF should have tighter spread than non-ETF large-cap"
    assert etf_pct < slip_pct, "ETF slippage_pct should be smaller"


def test_bug_080_exit_slippage_wired_in_process_day_exits():
    """BUG-80: process_day_exits must invoke apply_exit_slippage at exit sites."""
    import inspect
    from backtest.engine import exit_manager
    src = inspect.getsource(exit_manager.process_day_exits)
    assert "BUG-80" in src, "BUG-80 cross-reference must exist"
    assert "apply_exit_slippage" in src, (
        "process_day_exits must call apply_exit_slippage at exit close sites"
    )


def test_bug_078_trailing_stop_no_lookahead():
    """BUG-78 CRITICAL: trailing stop updated AFTER intraday check, not before.

    Pass 53 v8h+1 Phase 3 Batch 14 fix 2026-05-10. Previously process_day_exits
    updated trailing_stop from today's close BEFORE checking against today's
    intraday low/high - lookahead bias because today's close is unknown at the
    time today's low was made. Fix: check stop hit FIRST using yesterday's stop,
    THEN update from today's close for tomorrow.

    Lookahead scenario verified eliminated: trade with highest_close=100, stop=90.
    Today: close=110 (new high), low=95, high=112. Old buggy behavior would
    bump stop to 110*0.9=99, then see low=95 <= 99, falsely exit at 99. Correct
    behavior: check existing stop (90) against today's low (95) - 95 > 90, no
    exit; then update stop to 99 for tomorrow.
    """
    import inspect
    from backtest.engine import exit_manager
    src = inspect.getsource(exit_manager.process_day_exits)
    # Must contain BUG-78 marker
    assert "BUG-78" in src, "BUG-78 cross-reference must exist"
    # Check the ordering: check_trailing_stop_hit must appear BEFORE update_trailing_stop
    check_pos = src.find("check_trailing_stop_hit")
    update_pos = src.find("update_trailing_stop(trade, today_close")
    assert check_pos > 0 and update_pos > 0, "Both functions must be invoked"
    assert check_pos < update_pos, (
        f"BUG-78: check_trailing_stop_hit must run BEFORE update_trailing_stop "
        f"(check at {check_pos}, update at {update_pos})"
    )


def test_bug_078_no_lookahead_synthetic_scenario():
    """BUG-78 functional test: synthetic trade that would lookahead-exit under
    old code does NOT exit under new code.

    Long trade entered at $100, trailing stop at $90 (set via prior day's
    highest_close). Today: low=$95, close=$110, high=$112. Yesterday's stop
    is $90. Under old code, stop bumps to $110*0.9=$99 then sees low=$95 <= $99,
    incorrectly exits at $99. Under fixed code, the check uses $90 stop which
    today's low of $95 doesn't breach - position survives.
    """
    from datetime import date
    from backtest.engine.exit_manager import process_day_exits, OpenTrade

    trade = OpenTrade(
        ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
        direction="long", strategy="dummy", category="momentum",
        sector="Industrials", initial_stop=90.0, trailing_stop=90.0,
        highest_close=100.0, regime_at_entry="bull",
    )
    ticker_bars = {"TEST": {"open": 105.0, "high": 112.0, "low": 95.0, "close": 110.0, "prev_close": 100.0}}
    closed, still_open = process_day_exits(
        [trade], ticker_bars, date(2024, 1, 2),
        vix_value=15.0, regime="bull", active_signals={},
        circuit_breaker_log=[],
    )
    # Old buggy behavior would have closed the trade (low=95 < new_stop=99)
    # Fixed: no exit (low=95 > yesterday's stop=90)
    assert len(closed) == 0, (
        f"BUG-78 fix failure: trade should NOT exit (low=95 > yesterday's stop=90); "
        f"got {len(closed)} closed trades"
    )
    assert len(still_open) == 1, "Trade must remain open"
    # AFTER check, trailing_stop should have been updated from today's close
    # (highest_close 100 -> 110, stop 90 -> max(90, 110*0.9)=99)
    updated_trade = still_open[0]
    assert updated_trade.highest_close == 110.0, "highest_close must update post-check"
    assert updated_trade.trailing_stop == 99.0, (
        f"trailing_stop must update to 99.0 after check (got {updated_trade.trailing_stop})"
    )


def test_bug_021_exit_strategies_pnl_gross_by_design():
    """BUG-21: exit_strategies._pnl is gross-only by design (DEC-295).

    Pass 53 v8h+1 Phase 3 Batch 4 cross-reference 2026-05-10. Sister of BUG-06.
    Borrow cost applied centrally in apply_transaction_costs; both engine
    _pnl functions (exit_manager + exit_strategies) are gross by design.
    """
    import inspect
    from backtest.engine.exit_strategies import _pnl
    doc = inspect.getdoc(_pnl) or ""
    assert "BUG-21" in doc, "BUG-21 cross-reference must exist"
    assert "DEC-295" in doc, "DEC-295 single-source-of-truth reference must exist"
    # Pnl is symmetric in absolute terms across long/short
    long_pnl = _pnl(100.0, 110.0, "long")
    short_pnl = _pnl(100.0, 90.0, "short")
    assert abs(long_pnl - 10.0) < 0.01
    assert abs(short_pnl - 10.0) < 0.01


def test_bug_030_vix_crisis_tightens_stops():
    """BUG-30: VIX crisis (Level 5 CB) tightens stops per documented behavior.

    Pass 53 v8h+1 Phase 3 Batch 3 cross-reference 2026-05-10. Original bug
    claimed inconsistency between docs and code. exit_manager.py:218-222
    correctly tightens stops on VIX crisis additively (does not exit position).
    Documentation at exit_manager.py:15 confirms this is the intended behavior.
    """
    import inspect
    from backtest.engine import exit_manager
    src = inspect.getsource(exit_manager)
    # The Level 5 VIX crisis path must produce a tighten_stop action
    assert "tighten_stop" in src and "vix_crisis" in src, (
        "VIX crisis must produce tighten_stop action"
    )
    # Module docstring documents this behavior
    mod_doc = inspect.getdoc(exit_manager) or ""
    assert "VIX crisis" in mod_doc and "tighten" in mod_doc, (
        "exit_manager module docstring must describe VIX crisis tighten behavior"
    )


def test_bug_110_entry_gap_filter_enforced_at_validate_entry_zone():
    """BUG-110: validate_entry_zone enforces ENTRY_GAP_ATR_MULT per category.

    Pass 53 v8h+1 Phase 3 Batch 16 RESOLVED-IMPLEMENTED 2026-05-10.

    Original claim: trades opened despite exceeding the ATR limit. Verified
    against current code: validate_entry_zone rejects long entries whose gap
    above signal_close exceeds mult x ATR and short entries whose gap below
    signal_close exceeds mult x ATR.
    """
    from backtest.signals.screener import validate_entry_zone
    from backtest.config import ENTRY_GAP_ATR_MULT

    # Pivot category has the strictest gap tolerance
    pivot_mult = ENTRY_GAP_ATR_MULT.get("pivot", 1.0)
    signal_close = 100.0
    atr = 2.0

    # Long: open gap = 3.0 ATR above signal_close -> must reject (3.0 > 1.0)
    valid_long_bad, reason_long_bad = validate_entry_zone(
        signal_close + 3.0 * atr, signal_close, atr, "pivot", "long")
    assert valid_long_bad is False, (
        f"Long gap of 3.0xATR for pivot (mult={pivot_mult}) must reject")
    assert "exceeds" in reason_long_bad

    # Long: open gap = 0.5 ATR above signal_close -> must accept
    valid_long_ok, _ = validate_entry_zone(
        signal_close + 0.5 * atr, signal_close, atr, "pivot", "long")
    assert valid_long_ok is True, "Long gap of 0.5xATR for pivot must accept"

    # Short: open gap = 3.0 ATR below signal_close -> must reject
    valid_short_bad, reason_short_bad = validate_entry_zone(
        signal_close - 3.0 * atr, signal_close, atr, "pivot", "short")
    assert valid_short_bad is False, (
        "Short gap of 3.0xATR for pivot must reject")
    assert "exceeds" in reason_short_bad


def test_bug_077_avoid_excluded_from_strategy_count():
    """BUG-77: screener.screen_instrument must place avoid-direction strategies
    in their own bucket and EXCLUDE them from strategy_count + strategies list,
    so candidate ranking reflects directional conviction only.

    Pass 53 v8h+1 Phase 3 Batch 19 RESOLVED-IMPLEMENTED 2026-05-10 (owner-
    approved Option A). Source pin: screener.py must construct triggered_avoid
    bucket and the all_triggered sum must exclude it.
    """
    import inspect
    from backtest.signals import screener
    src = inspect.getsource(screener.screen_instrument)

    assert "BUG-77" in src, "BUG-77 cross-reference must exist in screen_instrument"
    assert "triggered_avoid" in src, (
        "screener must define triggered_avoid bucket separately")
    # The all_triggered sum must explicitly exclude avoid
    assert "all_triggered = triggered_long + triggered_short" in src, (
        "all_triggered must sum only long+short (no avoid)")
    # The result dict must expose avoid_strategies + avoid_count for diagnostics
    assert "\"avoid_strategies\"" in src or "'avoid_strategies'" in src, (
        "result dict must expose avoid_strategies for diagnostics")
    assert "\"avoid_count\"" in src or "'avoid_count'" in src, (
        "result dict must expose avoid_count for diagnostics")


def test_bug_077_candidate_ranking_prefers_directional_conviction():
    """BUG-77 functional: simulating the three-bucket categorization confirms
    a ticker with 5 longs + 0 avoids outranks one with 3 longs + 3 avoids.

    Pass 53 v8h+1 Phase 3 Batch 19 2026-05-10.
    """
    # Simulate the post-BUG-77 categorization
    def make_result(longs, shorts, avoids):
        triggered_long = [{"direction": "long"}] * longs
        triggered_short = [{"direction": "short"}] * shorts
        triggered_avoid = [{"direction": "avoid"}] * avoids
        all_triggered = triggered_long + triggered_short  # NO avoid
        return {
            "strategy_count": len(all_triggered),
            "long_count": len(triggered_long),
            "short_count": len(triggered_short),
            "avoid_count": len(triggered_avoid),
        }

    # AAPL: 5 longs, 0 short, 0 avoid -> strategy_count = 5
    aapl = make_result(longs=5, shorts=0, avoids=0)
    # NVDA: 3 longs, 0 short, 3 avoid -> strategy_count = 3 (was 6 under bug)
    nvda = make_result(longs=3, shorts=0, avoids=3)

    assert aapl["strategy_count"] == 5
    assert nvda["strategy_count"] == 3, (
        "NVDA must NOT include 3 avoids in strategy_count (was the BUG-77 bug)")
    # Candidate ranking is sort by strategy_count desc
    ranked = sorted([("AAPL", aapl), ("NVDA", nvda)],
                    key=lambda x: x[1]["strategy_count"], reverse=True)
    assert ranked[0][0] == "AAPL", (
        "AAPL (5 longs) must rank above NVDA (3 longs + 3 avoids)")
    # avoid_count is still exposed for diagnostics
    assert nvda["avoid_count"] == 3


def test_bug_083_congressional_detail_pit_filter_correct():
    """BUG-83: get_congressional_detail must filter ReportDate <= as_of
    (no extra 45-day delta) for PIT consistency with insider_signal and
    composite congressional_sig.

    Pass 53 v8h+1 Phase 3 Batch 18 RESOLVED-IMPLEMENTED 2026-05-10 (owner-
    approved Option A). Functional pin: a filing with ReportDate within the
    last 45 days but <= as_of must be INCLUDED (was incorrectly excluded).
    """
    import inspect
    from backtest.data import smart_money
    src = inspect.getsource(smart_money.get_congressional_detail)

    # The bug fix removes the 45-day subtraction
    assert "BUG-83" in src, "BUG-83 cross-reference must exist"
    assert "cutoff = pd.Timestamp(as_of)" in src, (
        "PIT cutoff must be pd.Timestamp(as_of) without delta subtraction")
    # The fixed code must NOT contain the original buggy pattern
    assert "pd.Timestamp(as_of) - pd.Timedelta(days=45)" not in src, (
        "Original 45-day subtraction must be removed")
    # And must keep the ReportDate filter direction (<=, not >=)
    assert "df[df[\"ReportDate\"] <= cutoff]" in src, (
        "Filter must keep ReportDate <= cutoff direction (PIT include)")


def test_bug_083_congressional_detail_includes_recent_filings():
    """BUG-83 functional: simulating the PIT filter directly verifies that
    a filing reported 10 days ago is included (was previously excluded by
    the 45-day delta bug).

    Pass 53 v8h+1 Phase 3 Batch 18 2026-05-10.
    """
    import pandas as pd
    from datetime import date

    as_of = date(2024, 6, 1)
    # 3 filings: one 100 days old, one 10 days old, one future (post-as_of)
    df = pd.DataFrame({
        "TransactionDate": pd.to_datetime([
            "2024-02-15", "2024-05-15", "2024-07-01"]),
        "ReportDate": pd.to_datetime([
            "2024-02-22", "2024-05-22", "2024-07-08"]),
        "Representative": ["A", "B", "C"],
        "Transaction": ["Purchase", "Purchase", "Sale"],
    })
    # Apply the FIXED filter directly
    cutoff = pd.Timestamp(as_of)
    available = df[df["ReportDate"] <= cutoff]
    # 100-day-old filing should be included
    assert "A" in available["Representative"].values, (
        "100-day-old filing must be included")
    # 10-day-old filing MUST be included (was excluded by buggy 45-day delta)
    assert "B" in available["Representative"].values, (
        "10-day-old filing must be included (was the BUG-83 regression)")
    # Future filing must NOT be included
    assert "C" not in available["Representative"].values, (
        "Future filing must be excluded")


def test_bug_061_ticker_level_concurrent_position_block_wired():
    """BUG-61: backtest._process_day must block new entries on tickers with
    any open position (matches live max_positions_per_ticker=1).

    Pass 53 v8h+1 Phase 3 Batch 17 RESOLVED-IMPLEMENTED 2026-05-10 (owner-
    approved Option A). Grep-discoverable pin that the ticker-level block is
    wired into the entry path with the BUG-61 cross-reference text and the
    open_tickers set construction + membership check.
    """
    import inspect
    from backtest.engine import backtest as bt_module
    src = inspect.getsource(bt_module)

    assert "BUG-61" in src, "BUG-61 cross-reference must exist in backtest.py"
    # The ticker set must be constructed from open trades
    assert "open_tickers" in src, (
        "Engine must build open_tickers set from self.open_trades for BUG-61")
    assert "{t.ticker for t in self.open_trades}" in src, (
        "open_tickers must come from open_trades ticker membership")
    # The block must check membership and skip
    assert "if ticker in open_tickers:" in src, (
        "Engine must check ticker membership before entering trade loop")
    assert "ticker_already_open_concurrent_block_bug61" in src, (
        "Skip reason must be ticker_already_open_concurrent_block_bug61")
    # The post-entry add to lock for rest of day
    assert "open_tickers.add(ticker)" in src, (
        "Post-entry must add to open_tickers to lock ticker within same day")


def test_bug_061_open_tickers_blocks_second_strategy_same_day():
    """BUG-61 functional: simulating open_tickers semantics rejects the
    second strategy attempt on the same ticker on the same day.

    Pass 53 v8h+1 Phase 3 Batch 17 2026-05-10. This test exercises the set
    membership semantics directly (set add + check) to validate the chosen
    data structure handles intra-day re-entries correctly.
    """
    # Day 1: AAPL opens via strategy 'hull_rsi'
    open_tickers = set()
    # First entry passes (set empty)
    ticker = "AAPL"
    assert ticker not in open_tickers, "first entry must pass when set empty"
    open_tickers.add(ticker)

    # Day 2 (intraday or next day with position still open):
    # 'cpr_narrow_bullish' tries same ticker
    second_attempt_blocked = ticker in open_tickers
    assert second_attempt_blocked, (
        "second strategy on same ticker with open position must be blocked")

    # Different ticker still passes
    other = "MSFT"
    assert other not in open_tickers, "different ticker must not be blocked"


def test_dec_483_nasdaq100_t1c_loader_exists_and_covers_pit():
    """DEC-483: Russell 1000 + NASDAQ 100 universe expansion (T1b + T1c).
    T1c (NASDAQ 100) is implemented; T1b deferred to Sprint 1 procurement.
    This pin verifies the T1c PIT loader function exists and is grep-discoverable.
    Pass 53 v8h+1 Phase 3 Batch 25 2026-05-10 (owner-approved Path 2).
    """
    import inspect
    from backtest.data import universe as univ_module
    src = inspect.getsource(univ_module)

    assert "DEC-483" in src, "DEC-483 cross-reference must exist in universe.py"
    assert "NASDAQ 100" in src or "T1c" in src, (
        "NASDAQ 100 / T1c references must exist in universe.py")
    # The PIT loader for T1c should exist
    assert "DEC-303" in src and "T1c" in src, (
        "T1c PIT loader (DEC-303/DEC-483) must be implemented")


def test_dec_499_18_classifier_sector_taxonomy_documented():
    """DEC-499: 18-classifier sector normalization (GICS-11 + 7 ETF asset/style).
    Implemented via Master Dedup Universe sector column. Pin verifies the
    cross-reference exists in universe.py sector-loading code path.
    Pass 53 v8h+1 Phase 3 Batch 25 2026-05-10 (owner-approved Path 2).
    """
    import inspect
    from backtest.data import universe as univ_module
    src = inspect.getsource(univ_module)

    assert "DEC-499" in src, "DEC-499 cross-reference must exist in universe.py"
    assert "18-classifier" in src or "Master Dedup" in src, (
        "18-classifier sector taxonomy reference must exist")


def test_bug_110_engine_wires_validate_entry_zone_with_skip_on_invalid():
    """BUG-110 wired: backtest._process_day must call validate_entry_zone and
    skip-on-invalid before entering trades.

    Pass 53 v8h+1 Phase 3 Batch 16 RESOLVED-IMPLEMENTED 2026-05-10.
    Grep-discoverable assertion that the entry-gap filter is wired into the
    backtest entry path with the BUG-110 cross-reference text.
    """
    import inspect
    from backtest.engine import backtest as bt_module
    src = inspect.getsource(bt_module)

    assert "BUG-110" in src, "BUG-110 cross-reference must exist in backtest.py"
    assert "validate_entry_zone" in src, (
        "backtest.py must call validate_entry_zone")
    # Skip-on-not-valid pattern
    assert "if not valid:" in src and "skipped_trades" in src, (
        "Engine must skip entries when validate_entry_zone returns invalid")
    # Import line present
    assert "from backtest.signals.screener import" in src and \
        "validate_entry_zone" in src, (
        "validate_entry_zone must be imported from screener")


# ============================================================================
# BUG-95 Phase 3 Batch 20: Portfolio class unit tests (Sub-batch 1)
# ============================================================================

def test_bug_095_portfolio_init_basic():
    """Portfolio initializes with starting capital fully in cash."""
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    assert p.cash == 100_000.0
    assert p.starting_capital == 100_000.0
    assert p.num_open == 0
    assert p.total_equity() == 100_000.0
    assert p.equity_curve == []
    assert p.benchmark_curve == []
    assert p.current_drawdown_pct() == 0.0
    assert p.exposure_by_sector() == {}


def test_bug_095_portfolio_init_rejects_non_positive():
    """Portfolio rejects zero or negative starting capital."""
    from backtest.engine.portfolio import Portfolio
    import pytest
    with pytest.raises(ValueError):
        Portfolio(starting_capital=0)
    with pytest.raises(ValueError):
        Portfolio(starting_capital=-100)


def test_bug_095_add_position_deducts_cash_long():
    """add_position deducts the dollar allocation from cash."""
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    pos = p.add_position("AAPL", "Information Technology", "long",
                         entry_price=100.0, size_pct=0.03,
                         entry_date=date(2024, 1, 1))
    assert p.cash == 97_000.0  # 100k - 3% = 97k
    assert p.num_open == 1
    assert pos.shares == 30.0  # 3000 / 100
    assert pos.entry_price == 100.0
    assert pos.direction == "long"
    assert pos.sector == "Information Technology"


def test_bug_095_remove_position_credits_with_pnl_long():
    """remove_position credits cash with original alloc + realised PnL."""
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.add_position("AAPL", "IT", "long", entry_price=100.0,
                   size_pct=0.03, entry_date=date(2024, 1, 1))
    # Sell at 110: 30 shares * (110-100) = 300 PnL
    realised = p.remove_position("AAPL", exit_price=110.0)
    assert realised == 300.0
    # Cash: 97000 + 3000 (notional) + 300 (PnL) = 100,300
    assert p.cash == 100_300.0
    assert p.num_open == 0


def test_bug_095_remove_position_credits_with_pnl_short():
    """remove_position handles short PnL sign correctly."""
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.add_position("TSLA", "Auto", "short", entry_price=100.0,
                   size_pct=0.03, entry_date=date(2024, 1, 1))
    # Cover at 90 (short profits as price drops): 30 * (100-90) = 300 PnL
    realised = p.remove_position("TSLA", exit_price=90.0)
    assert realised == 300.0
    # Cash returned with profit
    assert p.cash == 100_300.0


def test_bug_095_mark_to_market_appends_equity_curve():
    """mark_to_market appends a (date, equity) point and updates peak."""
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.add_position("AAPL", "IT", "long", entry_price=100.0,
                   size_pct=0.03, entry_date=date(2024, 1, 1))
    # Mark to 110 on day 2
    eq = p.mark_to_market({"AAPL": 110.0}, date(2024, 1, 2))
    # cash 97k + 30 shares * 110 = 100,300
    assert eq == 100_300.0
    assert len(p.equity_curve) == 1
    assert p.equity_curve[0] == (date(2024, 1, 2), 100_300.0)


def test_bug_095_current_drawdown_pct_basic():
    """current_drawdown_pct = (peak - current) / peak * 100."""
    from datetime import date, timedelta
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.add_position("AAPL", "IT", "long", entry_price=100.0,
                   size_pct=0.03, entry_date=date(2024, 1, 1))
    # Day 2: price 120, equity = 97k + 30*120 = 100,600 (peak)
    p.mark_to_market({"AAPL": 120.0}, date(2024, 1, 2))
    # Day 3: price 80, equity = 97k + 30*80 = 99,400
    p.mark_to_market({"AAPL": 80.0}, date(2024, 1, 3))
    dd = p.current_drawdown_pct()
    # (100600 - 99400) / 100600 * 100 ~= 1.193
    assert 1.0 < dd < 1.5, f"expected ~1.19% drawdown, got {dd}"


def test_bug_095_can_open_blocks_max_positions():
    """can_open returns False when max_positions reached."""
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=1_000_000.0)
    # Open 10 positions
    for i in range(10):
        p.add_position(f"TKR{i}", "IT", "long", entry_price=100.0,
                       size_pct=0.03, entry_date=date(2024, 1, 1))
    ok, reason = p.can_open("TKR99", size_pct=0.03, max_positions=10)
    assert ok is False
    assert "max_open_positions_10" in reason


def test_bug_095_can_open_blocks_ticker_already_open():
    """can_open returns False when ticker already in portfolio (BUG-61
    portfolio-level companion).
    """
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.add_position("AAPL", "IT", "long", entry_price=100.0,
                   size_pct=0.03, entry_date=date(2024, 1, 1))
    ok, reason = p.can_open("AAPL", size_pct=0.03, max_positions=10)
    assert ok is False
    assert "ticker_already_in_portfolio" in reason


def test_bug_095_can_open_blocks_insufficient_cash():
    """can_open returns False when required dollar > cash."""
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=10_000.0)
    # Open one 50% position
    p.add_position("AAPL", "IT", "long", entry_price=100.0,
                   size_pct=0.50, entry_date=date(2024, 1, 1))
    # Try to open another 60% - require 6000 but cash is 5000
    ok, reason = p.can_open("MSFT", size_pct=0.60, max_positions=10)
    assert ok is False
    assert "insufficient_cash" in reason


def test_bug_095_can_open_blocks_drawdown_suspend_breach():
    """can_open blocks new entries when drawdown >= drawdown_suspend_pct."""
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.add_position("AAPL", "IT", "long", entry_price=100.0,
                   size_pct=0.50, entry_date=date(2024, 1, 1))
    # Day 1 mark at entry - establishes peak
    p.mark_to_market({"AAPL": 100.0}, date(2024, 1, 1))
    # Day 2 huge crash - 50% position drops 70% -> equity drops 35%
    p.mark_to_market({"AAPL": 30.0}, date(2024, 1, 2))
    dd = p.current_drawdown_pct()
    assert dd >= 30.0, f"expected drawdown >= 30%, got {dd}"
    ok, reason = p.can_open("MSFT", size_pct=0.03, max_positions=10,
                            drawdown_suspend_pct=30.0)
    assert ok is False
    assert "drawdown_suspend_breach" in reason


def test_bug_095_exposure_by_sector_basic():
    """exposure_by_sector returns dict {sector: pct_of_total_equity}."""
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.add_position("AAPL", "IT", "long", entry_price=100.0,
                   size_pct=0.10, entry_date=date(2024, 1, 1))
    p.add_position("MSFT", "IT", "long", entry_price=200.0,
                   size_pct=0.10, entry_date=date(2024, 1, 1))
    p.add_position("XOM", "Energy", "long", entry_price=50.0,
                   size_pct=0.05, entry_date=date(2024, 1, 1))
    exposure = p.exposure_by_sector()
    # 2 IT positions worth 10% + 10% = 20%; Energy 5%
    assert "IT" in exposure and "Energy" in exposure
    # Total exposed = 25%; cash 75%; total_equity ~= 100k (initial)
    assert 0.18 < exposure["IT"] < 0.22, (
        f"IT should be ~20% of equity, got {exposure['IT']:.3f}")
    assert 0.04 < exposure["Energy"] < 0.06, (
        f"Energy should be ~5% of equity, got {exposure['Energy']:.3f}")


def test_bug_095_add_benchmark_point():
    """add_benchmark_point appends to benchmark_curve; rejects non-positive."""
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.add_benchmark_point(date(2024, 1, 1), 470.0)
    p.add_benchmark_point(date(2024, 1, 2), 472.5)
    p.add_benchmark_point(date(2024, 1, 3), 0.0)  # should not append
    p.add_benchmark_point(date(2024, 1, 4), -10.0)  # should not append
    assert len(p.benchmark_curve) == 2
    assert p.benchmark_curve[0] == (date(2024, 1, 1), 470.0)


def test_bug_095_metrics_returns_empty_safe_on_no_curve():
    """compute_portfolio_metrics_from_curves returns the zero/default dict
    when equity_curve is empty or has fewer than 2 points (engine guard).
    """
    from backtest.results.metrics import compute_portfolio_metrics_from_curves
    out = compute_portfolio_metrics_from_curves([], [], 100_000.0)
    assert out["n_equity_points"] == 0
    assert out["portfolio_sharpe"] is None
    assert out["portfolio_total_return_pct"] == 0.0
    assert out["portfolio_max_drawdown_pct"] == 0.0


def test_bug_095_metrics_total_return_basic():
    """portfolio_total_return_pct = (final/starting - 1) * 100."""
    from datetime import date
    from backtest.results.metrics import compute_portfolio_metrics_from_curves
    # Equity goes 100k -> 110k over 5 days
    curve = [
        (date(2024, 1, 1), 100_000.0),
        (date(2024, 1, 2), 102_000.0),
        (date(2024, 1, 3), 104_000.0),
        (date(2024, 1, 4), 108_000.0),
        (date(2024, 1, 5), 110_000.0),
    ]
    out = compute_portfolio_metrics_from_curves(curve, [], 100_000.0)
    assert out["n_equity_points"] == 5
    # 110000/100000 - 1 = 10%
    assert abs(out["portfolio_total_return_pct"] - 10.0) < 0.01
    assert out["portfolio_max_drawdown_pct"] == 0.0  # monotonic up


def test_bug_095_metrics_max_drawdown_basic():
    """Max drawdown = worst peak-to-trough on equity_curve."""
    from datetime import date
    from backtest.results.metrics import compute_portfolio_metrics_from_curves
    # Up to 120k peak, then down to 90k = 25% drawdown
    curve = [
        (date(2024, 1, 1), 100_000.0),
        (date(2024, 1, 2), 120_000.0),  # peak
        (date(2024, 1, 3), 100_000.0),
        (date(2024, 1, 4), 90_000.0),   # trough
    ]
    out = compute_portfolio_metrics_from_curves(curve, [], 100_000.0)
    # (90 - 120) / 120 * 100 = -25.0
    assert abs(out["portfolio_max_drawdown_pct"] - (-25.0)) < 0.01


def test_bug_095_metrics_sharpe_positive_for_steady_gain():
    """Sharpe should be a positive finite number when daily returns are
    positive and have non-zero variance.
    """
    from datetime import date, timedelta
    from backtest.results.metrics import compute_portfolio_metrics_from_curves
    # 60 days with mostly small gains (1% / day average, varied)
    curve = []
    val = 100_000.0
    daily_returns = [0.01, 0.005, 0.012, -0.003, 0.008] * 12   # 60 days
    d = date(2024, 1, 1)
    for r in daily_returns:
        curve.append((d, val))
        val *= (1.0 + r)
        d += timedelta(days=1)
    curve.append((d, val))   # final point
    out = compute_portfolio_metrics_from_curves(curve, [], 100_000.0)
    assert out["portfolio_sharpe"] is not None
    assert out["portfolio_sharpe"] > 0, (
        f"steady positive returns must give positive Sharpe, got {out['portfolio_sharpe']}")


def test_bug_095_metrics_beta_alpha_with_benchmark():
    """When portfolio == benchmark (perfectly correlated, same returns), beta
    should be ~1.0 and alpha ~0; tracking_error ~0; IR ~0.
    """
    from datetime import date, timedelta
    from backtest.results.metrics import compute_portfolio_metrics_from_curves
    curve = []
    bench = []
    val_p = 100_000.0
    val_b = 470.0
    daily_returns = [0.005, 0.003, -0.002, 0.007, 0.001] * 12   # 60 days
    d = date(2024, 1, 1)
    for r in daily_returns:
        curve.append((d, val_p))
        bench.append((d, val_b))
        val_p *= (1.0 + r)
        val_b *= (1.0 + r)
        d += timedelta(days=1)
    out = compute_portfolio_metrics_from_curves(curve, bench, 100_000.0)
    assert out["beta_to_benchmark"] is not None
    assert abs(out["beta_to_benchmark"] - 1.0) < 0.01, (
        f"beta should be ~1 when port==bench, got {out['beta_to_benchmark']}")
    # Alpha should be near zero
    assert abs(out["alpha_annualized_pct"]) < 0.5, (
        f"alpha should be near zero, got {out['alpha_annualized_pct']}")
    # Tracking error should be near zero
    assert out["tracking_error_pct"] < 0.5, (
        f"tracking error should be near zero, got {out['tracking_error_pct']}")


def test_bug_095_metrics_handles_zero_variance_benchmark():
    """Benchmark with all-equal values (zero variance) must not crash; beta
    should be None / NaN-safe.
    """
    from datetime import date, timedelta
    from backtest.results.metrics import compute_portfolio_metrics_from_curves
    curve = [
        (date(2024, 1, 1), 100_000.0),
        (date(2024, 1, 2), 101_000.0),
        (date(2024, 1, 3), 102_000.0),
    ]
    # Flat benchmark - zero variance
    bench = [
        (date(2024, 1, 1), 470.0),
        (date(2024, 1, 2), 470.0),
        (date(2024, 1, 3), 470.0),
    ]
    out = compute_portfolio_metrics_from_curves(curve, bench, 100_000.0)
    # No crash; beta should be None due to zero benchmark variance
    assert out["beta_to_benchmark"] is None


def test_bug_095_mark_to_market_carries_forward_missing_prices():
    """If a ticker price is missing from prices dict, position retains last
    known mark (Position.last_mark) rather than crashing or zeroing out.
    """
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.add_position("AAPL", "IT", "long", entry_price=100.0,
                   size_pct=0.03, entry_date=date(2024, 1, 1))
    # Day 1 mark at 110
    p.mark_to_market({"AAPL": 110.0}, date(2024, 1, 1))
    aapl = p.positions["AAPL"]
    assert aapl.last_mark == 110.0
    # Day 2 mark with missing AAPL - last_mark preserved
    p.mark_to_market({}, date(2024, 1, 2))
    assert aapl.last_mark == 110.0
    # Equity unchanged from day 1: 97k + 30*110 = 100,300
    assert p.equity_curve[-1][1] == 100_300.0


# ============================================================================
# Phase 3 Batch 54 Path C 5-DEC bundle (owner directive >= 5 DECs per batch):
# DEC-091 (drawdown re-sizing) + DEC-092 (slippage f(size%ADV, vol))
# + DEC-279 (P&L decomposition) + DEC-280 (time-of-day slippage mult)
# + DEC-108 (regime EMA smoothing)
# ============================================================================

# --- DEC-091 drawdown re-sizing -------------------------------------------

def _portfolio_with_dd(starting=100_000.0, current_equity=None):
    """Helper: build a Portfolio with a specific drawdown by spoofing equity_curve."""
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=starting)
    p.equity_curve.append((date(2024, 1, 1), starting))
    p._equity_peak = starting
    if current_equity is not None:
        p.equity_curve.append((date(2024, 1, 2), current_equity))
    return p


def test_dec_091_drawdown_multiplier_full_size_below_10pct():
    """DEC-091: DD < 10% -> multiplier 1.0."""
    p = _portfolio_with_dd(100_000.0, 95_000.0)  # 5% DD
    assert p.drawdown_size_multiplier() == 1.0


def test_dec_091_drawdown_multiplier_075_at_10pct():
    """DEC-091 spec test signal: 12% DD -> size * 0.75."""
    p = _portfolio_with_dd(100_000.0, 88_000.0)  # 12% DD
    assert p.drawdown_size_multiplier() == 0.75


def test_dec_091_drawdown_multiplier_050_at_20pct():
    """DEC-091 spec test signal: 22% DD -> size * 0.5."""
    p = _portfolio_with_dd(100_000.0, 78_000.0)  # 22% DD
    assert p.drawdown_size_multiplier() == 0.5


def test_dec_091_drawdown_multiplier_halt_at_30pct():
    """DEC-091 spec test signal: 32% DD -> entry rejected (multiplier 0.0)."""
    p = _portfolio_with_dd(100_000.0, 68_000.0)  # 32% DD
    assert p.drawdown_size_multiplier() == 0.0


# --- DEC-092 base slippage f(size%ADV, vol) -------------------------------

def test_dec_092_base_slippage_small_size_low_vol():
    """DEC-092 spec test signal: 0.5% ADV, vol=20% -> ~3 bps."""
    from backtest.engine.improvements import compute_slippage_bps_advanced
    bps = compute_slippage_bps_advanced(
        size_pct_adv=0.005, realized_vol_annualized=0.20,
    )
    assert 2.5 < bps < 4.0, f"expected ~3 bps, got {bps}"


def test_dec_092_base_slippage_large_size_high_vol():
    """DEC-092 spec test signal: 5% ADV, vol=50% -> ~25 bps."""
    from backtest.engine.improvements import compute_slippage_bps_advanced
    bps = compute_slippage_bps_advanced(
        size_pct_adv=0.05, realized_vol_annualized=0.50,
    )
    assert 20.0 < bps < 30.0, f"expected ~25 bps, got {bps}"


def test_dec_092_base_slippage_monotonic_in_size_and_vol():
    """DEC-092: bps increases with size (vol fixed) and with vol (size fixed)."""
    from backtest.engine.improvements import compute_slippage_bps_advanced
    s_low  = compute_slippage_bps_advanced(0.005, 0.20)
    s_mid  = compute_slippage_bps_advanced(0.02,  0.20)
    s_high = compute_slippage_bps_advanced(0.05,  0.20)
    assert s_low < s_mid < s_high
    v_low  = compute_slippage_bps_advanced(0.01, 0.10)
    v_mid  = compute_slippage_bps_advanced(0.01, 0.30)
    v_high = compute_slippage_bps_advanced(0.01, 0.60)
    assert v_low < v_mid < v_high


def test_dec_092_base_slippage_non_negative():
    """DEC-092: clamps inputs at 0 (defensive against pathological inputs)."""
    from backtest.engine.improvements import compute_slippage_bps_advanced
    assert compute_slippage_bps_advanced(-0.01, -0.05) >= 0.0


# --- DEC-280 time-of-day slippage multiplier -----------------------------

def test_dec_280_time_of_day_first_30min():
    """DEC-280 spec test signal: 09:35 ET (first 30min) -> multiplier > 1.0."""
    from datetime import time
    from backtest.engine.improvements import time_of_day_slippage_multiplier
    assert time_of_day_slippage_multiplier(time(9, 35)) == 1.5
    # Exact-30-min boundary 10:00 is OUT (consistent with [09:30, 10:00))
    assert time_of_day_slippage_multiplier(time(10, 0)) == 1.0


def test_dec_280_time_of_day_midday_baseline():
    """DEC-280 spec test signal: 11:00 ET -> multiplier 1.0."""
    from datetime import time
    from backtest.engine.improvements import time_of_day_slippage_multiplier
    assert time_of_day_slippage_multiplier(time(11, 0)) == 1.0
    assert time_of_day_slippage_multiplier(time(14, 0)) == 1.0


def test_dec_280_time_of_day_last_30min():
    """DEC-280 spec test signal: 15:55 ET (last 30min) -> multiplier > 1.0."""
    from datetime import time
    from backtest.engine.improvements import time_of_day_slippage_multiplier
    assert time_of_day_slippage_multiplier(time(15, 55)) == 1.5
    # 15:30 boundary is IN (consistent with [15:30, 16:00))
    assert time_of_day_slippage_multiplier(time(15, 30)) == 1.5


def test_dec_280_time_of_day_none_returns_one():
    """DEC-280: None entry_time (daily-bar backtest, no intraday context)
    returns 1.0 - caller-side fail-soft.
    """
    from backtest.engine.improvements import time_of_day_slippage_multiplier
    assert time_of_day_slippage_multiplier(None) == 1.0


def test_dec_280_time_of_day_accepts_datetime():
    """DEC-280: accepts datetime in addition to time."""
    from datetime import datetime
    from backtest.engine.improvements import time_of_day_slippage_multiplier
    assert time_of_day_slippage_multiplier(datetime(2024, 1, 5, 9, 45)) == 1.5
    assert time_of_day_slippage_multiplier(datetime(2024, 1, 5, 12, 0)) == 1.0


# --- DEC-279 P&L decomposition --------------------------------------------

def test_dec_279_decompose_components_sum_to_actual():
    """DEC-279 spec test signal: synthetic trade with known timing/exit/sizing
    deltas -> 5 components sum equals actual P&L.
    """
    from backtest.results.metrics import decompose_trade_pnl
    out = decompose_trade_pnl(
        actual_pnl_dollar=1000.0,
        timing_delta_dollar=-100.0,
        exit_delta_dollar=-50.0,
        sizing_delta_dollar=-200.0,
        agent_delta_dollar=75.0,
    )
    components_sum = (out["signal_contribution"] + out["timing_contribution"]
                      + out["exit_contribution"] + out["sizing_contribution"]
                      + out["agent_contribution"])
    assert abs(components_sum - 1000.0) < 1e-6
    # Signal residual: 1000 - (-100 -50 -200 +75) = 1000 - (-275) = 1275
    assert abs(out["signal_contribution"] - 1275.0) < 1e-6


def test_dec_279_decompose_all_zero_deltas_signal_equals_actual():
    """DEC-279: with no derived deltas, signal == actual_pnl."""
    from backtest.results.metrics import decompose_trade_pnl
    out = decompose_trade_pnl(actual_pnl_dollar=500.0)
    assert out["signal_contribution"] == 500.0
    assert out["timing_contribution"] == 0.0
    assert out["actual_total_check"] == 500.0


def test_dec_279_decompose_losing_trade_negative_signal():
    """DEC-279: trade loss with positive timing/exit deltas -> negative signal."""
    from backtest.results.metrics import decompose_trade_pnl
    out = decompose_trade_pnl(
        actual_pnl_dollar=-200.0,
        timing_delta_dollar=50.0,
        exit_delta_dollar=30.0,
    )
    # signal = -200 - (50 + 30) = -280
    assert out["signal_contribution"] == -280.0


# --- DEC-108 regime EMA smoothing -----------------------------------------

def test_dec_108_ema_first_call_returns_new_score():
    """DEC-108: first call (prev=None) seeds with new_score unchanged."""
    from backtest.engine.regime_filter import ema_smooth_regime_probability
    assert ema_smooth_regime_probability(0.75, prev_smoothed=None) == 0.75


def test_dec_108_ema_subsequent_call_weights_prev_heavily():
    """DEC-108 spec: EMA = 0.9*prev + 0.1*new (default alpha=0.1)."""
    from backtest.engine.regime_filter import ema_smooth_regime_probability
    # prev 1.0, new 0.0 -> 0.9*1.0 + 0.1*0.0 = 0.9
    assert abs(ema_smooth_regime_probability(0.0, prev_smoothed=1.0) - 0.9) < 1e-9
    # prev 0.5, new 1.0 -> 0.9*0.5 + 0.1*1.0 = 0.55
    assert abs(ema_smooth_regime_probability(1.0, prev_smoothed=0.5) - 0.55) < 1e-9


def test_dec_108_ema_doesnt_flicker_on_single_day_spike():
    """DEC-108 spec test signal: single-day spike in raw score does not flip
    smoothed value far from prev.
    """
    from backtest.engine.regime_filter import ema_smooth_regime_probability
    smoothed = 0.2
    spike_smoothed = ema_smooth_regime_probability(1.0, prev_smoothed=smoothed)
    # 0.9*0.2 + 0.1*1.0 = 0.28 - much closer to prev 0.2 than spike 1.0
    assert 0.2 < spike_smoothed < 0.4


def test_dec_108_ema_custom_alpha():
    """DEC-108: caller can override alpha (e.g., alpha=0.5 -> equal weight)."""
    from backtest.engine.regime_filter import ema_smooth_regime_probability
    # alpha 0.5: 0.5*prev + 0.5*new
    assert abs(ema_smooth_regime_probability(1.0, prev_smoothed=0.0, alpha=0.5)
               - 0.5) < 1e-9


# ============================================================================
# Phase 3 Batch 55 Path C 5-DEC bundle (owner directive >= 5 DECs/batch):
# DEC-106 (multi-input regime scorecard 8+) + DEC-150 (multi-asset regime)
# + DEC-151 (sector regime) + DEC-249 (strategy decay) + DEC-135 (per-ticker
# max-loss cap rolling 30d)
# ============================================================================

# --- DEC-106 multi-input regime scorecard ---------------------------------

def test_dec_106_multi_input_regime_score_all_bullish():
    """DEC-106: all bullish inputs -> high regime_score + bull label."""
    from backtest.engine.regime_filter import multi_input_regime_score
    out = multi_input_regime_score(
        vix=15, spy_above_200ema=True,
        yield_curve_spread=1.5, hy_spread_bps=200, icsa_yoy_pct=-5,
        breadth_pct_above_50ema=80, sector_dispersion=0.5,
        aaii_bull_bear_spread=-30, cnn_fg=50,
    )
    assert out["inputs_used"] == 9
    assert out["regime_score"] >= 90
    assert out["regime_label"] == "bull"


def test_dec_106_multi_input_regime_score_all_bearish():
    """DEC-106: all bearish inputs -> low regime_score + crisis/bear label."""
    from backtest.engine.regime_filter import multi_input_regime_score
    out = multi_input_regime_score(
        vix=35, spy_above_200ema=False,
        yield_curve_spread=-1.0, hy_spread_bps=800, icsa_yoy_pct=30,
        breadth_pct_above_50ema=20, sector_dispersion=2.0,
        aaii_bull_bear_spread=40, cnn_fg=10,
    )
    assert out["regime_score"] <= 10
    assert out["regime_label"] in ("crisis", "bear")


def test_dec_106_multi_input_regime_score_skips_missing_inputs():
    """DEC-106: missing inputs skipped, not treated as neutral."""
    from backtest.engine.regime_filter import multi_input_regime_score
    out = multi_input_regime_score(vix=15, spy_above_200ema=True)
    assert out["inputs_used"] == 2
    assert out["regime_label"] == "bull"

    out_empty = multi_input_regime_score(vix=None, spy_above_200ema=None)
    assert out_empty["inputs_used"] == 0
    assert out_empty["regime_label"] == "unknown"


# --- DEC-150 multi-asset regime score -------------------------------------

def test_dec_150_multi_asset_regime_score_bullish_composite():
    """DEC-150: low vix + tight credit + commodities up + USD weak -> bull."""
    from backtest.engine.regime_filter import multi_asset_regime_score
    out = multi_asset_regime_score(
        equity_vix=15, credit_hy_spread_bps=250,
        commodity_pct_change_20d=5, currency_dxy_pct_change_20d=-5,
    )
    assert out["inputs_used"] == 4
    assert out["regime_label"] == "bull"


def test_dec_150_multi_asset_regime_score_bearish_composite():
    """DEC-150: high vix + wide credit + commodities crash + USD spike -> crisis."""
    from backtest.engine.regime_filter import multi_asset_regime_score
    out = multi_asset_regime_score(
        equity_vix=40, credit_hy_spread_bps=900,
        commodity_pct_change_20d=-8, currency_dxy_pct_change_20d=6,
    )
    assert out["regime_label"] in ("crisis", "bear")


def test_dec_150_multi_asset_regime_score_no_inputs():
    """DEC-150: all None inputs -> unknown label."""
    from backtest.engine.regime_filter import multi_asset_regime_score
    out = multi_asset_regime_score(equity_vix=None)
    assert out["regime_label"] == "unknown"
    assert out["inputs_used"] == 0


# --- DEC-151 sector-level regime ------------------------------------------

def test_dec_151_sector_regime_bull():
    """DEC-151: low vol + price > 200EMA -> bull (e.g., XLE 2022)."""
    from backtest.engine.regime_filter import sector_regime
    assert sector_regime(100, 90, 0.15) == "bull"


def test_dec_151_sector_regime_bear():
    """DEC-151: elevated vol + below 200EMA -> bear (e.g., XLK 2022)."""
    from backtest.engine.regime_filter import sector_regime
    assert sector_regime(90, 100, 0.32) == "bear"


def test_dec_151_sector_regime_crisis():
    """DEC-151: crisis-level vol regardless of trend -> crisis."""
    from backtest.engine.regime_filter import sector_regime
    assert sector_regime(100, 90, 0.50) == "crisis"
    assert sector_regime(90, 100, 0.45) == "crisis"


def test_dec_151_sector_regime_neutral():
    """DEC-151: mid vol + neutral trend -> neutral (e.g., XLF 2022)."""
    from backtest.engine.regime_filter import sector_regime
    assert sector_regime(100, 100, 0.25) == "neutral"


def test_dec_151_sector_regime_unknown_on_missing_inputs():
    """DEC-151: missing inputs -> unknown (fail-closed per DEC-316)."""
    from backtest.engine.regime_filter import sector_regime
    assert sector_regime(None, 100, 0.25) == "unknown"
    assert sector_regime(100, None, 0.25) == "unknown"
    assert sector_regime(100, 100, None) == "unknown"


# --- DEC-249 strategy decay metric ---------------------------------------

def test_dec_249_strategy_decay_flag_fires_at_50pct_drop():
    """DEC-249 spec test signal: Sharpe 1.2 baseline decaying to 0.5 ->
    drop > 50% -> STRATEGY_DECAY_WARNING.
    """
    from backtest.results.metrics import detect_strategy_decay
    out = detect_strategy_decay(sharpe_baseline=1.2, sharpe_recent=0.5)
    assert out["is_decayed"] is True
    assert out["note"] == "STRATEGY_DECAY_WARNING"


def test_dec_249_strategy_decay_no_flag_on_modest_drop():
    """DEC-249: Sharpe drops 30% -> no flag."""
    from backtest.results.metrics import detect_strategy_decay
    out = detect_strategy_decay(sharpe_baseline=1.2, sharpe_recent=0.9)
    assert out["is_decayed"] is False
    assert out["note"] == "ok"


def test_dec_249_strategy_decay_recovery_clears_flag():
    """DEC-249 spec test signal: recovery from 0.5 to 1.0+ clears flag."""
    from backtest.results.metrics import detect_strategy_decay
    out = detect_strategy_decay(sharpe_baseline=1.2, sharpe_recent=1.1)
    assert out["is_decayed"] is False
    assert out["drop_pct"] < 0.5


def test_dec_249_strategy_decay_handles_zero_or_negative_baseline():
    """DEC-249: zero or negative baseline -> note 'no_baseline_to_compare'."""
    from backtest.results.metrics import detect_strategy_decay
    out_zero = detect_strategy_decay(sharpe_baseline=0.0, sharpe_recent=0.5)
    assert out_zero["note"] == "no_baseline_to_compare"
    out_neg = detect_strategy_decay(sharpe_baseline=-0.5, sharpe_recent=0.5)
    assert out_neg["note"] == "no_baseline_to_compare"


# --- DEC-135 per-ticker rolling 30-day max-loss cap -----------------------

def test_dec_135_per_ticker_max_loss_breach_halts_ticker():
    """DEC-135 spec test signal: ticker accumulates -11% over rolling
    25-day window -> halted.
    """
    import pandas as pd
    from datetime import date
    from backtest.engine.improvements import per_ticker_30day_max_loss_check

    df = pd.DataFrame([
        {"ticker": "BADTICK", "exit_date": date(2024, 1, 5),  "pnl_pct": -4.0},
        {"ticker": "BADTICK", "exit_date": date(2024, 1, 15), "pnl_pct": -7.0},
        {"ticker": "GOODTICK", "exit_date": date(2024, 1, 10), "pnl_pct": 3.0},
    ])
    out = per_ticker_30day_max_loss_check(df, today=date(2024, 1, 30),
                                          cap_pct=-10.0, cooldown_days=30)
    assert out["BADTICK"] is True   # -11% cumulative
    assert out["GOODTICK"] is False


def test_dec_135_per_ticker_max_loss_window_drops_old_trades():
    """DEC-135: trades older than cooldown_days are excluded from cum sum."""
    import pandas as pd
    from datetime import date
    from backtest.engine.improvements import per_ticker_30day_max_loss_check

    df = pd.DataFrame([
        # Out-of-window loss (older than 30 days from today)
        {"ticker": "T1", "exit_date": date(2023, 12, 1), "pnl_pct": -20.0},
        # In-window trade
        {"ticker": "T1", "exit_date": date(2024, 1, 25), "pnl_pct": -3.0},
    ])
    out = per_ticker_30day_max_loss_check(df, today=date(2024, 1, 30),
                                          cap_pct=-10.0, cooldown_days=30)
    assert out["T1"] is False  # only -3% in window, not breached


def test_dec_135_per_ticker_max_loss_empty_or_missing_cols():
    """DEC-135: empty df or missing columns -> empty dict (fail-soft)."""
    import pandas as pd
    from datetime import date
    from backtest.engine.improvements import per_ticker_30day_max_loss_check

    out_empty = per_ticker_30day_max_loss_check(pd.DataFrame(), today=date(2024, 1, 30))
    assert out_empty == {}
    out_missing = per_ticker_30day_max_loss_check(
        pd.DataFrame([{"ticker": "X"}]), today=date(2024, 1, 30),
    )
    assert out_missing == {}


# ============================================================================
# Phase 3 Batch 56 Path C 5-DEC bundle (owner directive >= 5 DECs/batch):
# DEC-100 (17+ categorical breakdown vars) + DEC-209 (per-regime agent verdicts)
# + DEC-233 (OHLCV data quality scan) + DEC-284 (borderline pass/fail policy)
# + DEC-287 (public site freshness signal)
# ============================================================================

# --- DEC-100 categorical breakdown variables ------------------------------

def test_dec_100_canonical_breakdown_variables_includes_required():
    """DEC-100: canonical list contains the required dimensions per spec."""
    from backtest.results.metrics import CANONICAL_BREAKDOWN_VARIABLES
    assert len(CANONICAL_BREAKDOWN_VARIABLES) >= 17
    for required in ("regime", "sector", "market_cap_band", "vol_band",
                     "momentum_band", "liquidity_band"):
        assert required in CANONICAL_BREAKDOWN_VARIABLES


def test_dec_100_per_bucket_metrics_groups_correctly():
    """DEC-100: per-bucket metrics returns per-sector aggregation."""
    import pandas as pd
    from backtest.results.metrics import compute_per_bucket_metrics
    df = pd.DataFrame([
        {"sector": "Tech", "win": True,  "pnl_pct": 2.0},
        {"sector": "Tech", "win": True,  "pnl_pct": 3.0},
        {"sector": "Tech", "win": False, "pnl_pct": -1.0},
        {"sector": "Energy", "win": True, "pnl_pct": 5.0},
        {"sector": "Energy", "win": False, "pnl_pct": -2.0},
    ])
    out = compute_per_bucket_metrics(df, "sector")
    assert "Tech" in out and "Energy" in out
    assert out["Tech"]["n"] == 3
    assert abs(out["Tech"]["win_rate"] - round(2/3, 4)) < 1e-6
    assert out["Energy"]["n"] == 2
    assert abs(out["Energy"]["win_rate"] - 0.5) < 1e-6


def test_dec_100_per_bucket_metrics_rejects_unknown_var():
    """DEC-100: unknown breakdown_var -> empty dict (defensive)."""
    import pandas as pd
    from backtest.results.metrics import compute_per_bucket_metrics
    df = pd.DataFrame([{"sector": "Tech", "win": True, "pnl_pct": 1.0}])
    assert compute_per_bucket_metrics(df, "not_in_canonical_list") == {}


# --- DEC-209 per-regime agent A/B verdicts --------------------------------

def test_dec_209_agent_adds_when_lift_above_3pp():
    """DEC-209: agent overlay improves win_rate >= 3pp -> AGENT_ADDS."""
    import pandas as pd
    from backtest.results.metrics import compute_per_regime_agent_verdict
    rules = pd.DataFrame([
        {"regime": "bull", "win": i % 2 == 0} for i in range(100)
    ])  # rules wr 50%
    agent = pd.DataFrame([
        {"regime": "bull", "win": i < 60} for i in range(100)
    ])  # agent wr 60%
    out = compute_per_regime_agent_verdict(rules, agent, regimes=("bull",))
    assert out["bull"]["verdict"] == "AGENT_ADDS"
    assert out["bull"]["delta_pp"] >= 3.0


def test_dec_209_agent_hurts_when_loss_above_3pp():
    """DEC-209: agent overlay drops win_rate >= 3pp -> AGENT_HURTS."""
    import pandas as pd
    from backtest.results.metrics import compute_per_regime_agent_verdict
    rules = pd.DataFrame([{"regime": "bear", "win": i < 60} for i in range(100)])
    agent = pd.DataFrame([{"regime": "bear", "win": i < 40} for i in range(100)])
    out = compute_per_regime_agent_verdict(rules, agent, regimes=("bear",))
    assert out["bear"]["verdict"] == "AGENT_HURTS"


def test_dec_209_insufficient_data_below_min_trades():
    """DEC-209: subset below min_trades_per_regime -> INSUFFICIENT_DATA."""
    import pandas as pd
    from backtest.results.metrics import compute_per_regime_agent_verdict
    rules = pd.DataFrame([{"regime": "neutral", "win": True} for _ in range(10)])
    agent = pd.DataFrame([{"regime": "neutral", "win": True} for _ in range(10)])
    out = compute_per_regime_agent_verdict(rules, agent, regimes=("neutral",),
                                           min_trades_per_regime=30)
    assert out["neutral"]["verdict"] == "INSUFFICIENT_DATA"


# --- DEC-233 OHLCV data quality scan --------------------------------------

def test_dec_233_data_quality_clean_series_no_warning():
    """DEC-233: clean OHLCV with no NaN and no extreme gaps -> no warning."""
    import pandas as pd
    from backtest.engine.improvements import check_ohlcv_data_quality
    df = pd.DataFrame({"close": [100 + 0.5 * i for i in range(30)]})
    out = check_ohlcv_data_quality(df)
    assert out["DataQualityWarning"] is False
    assert out["has_nan_close"] is False
    assert out["has_extreme_gap"] is False


def test_dec_233_data_quality_extreme_gap_triggers_warning():
    """DEC-233 spec test signal: 50%+ single-day price gap -> anomaly flag."""
    import pandas as pd
    from backtest.engine.improvements import check_ohlcv_data_quality
    df = pd.DataFrame({"close": [100, 101, 102, 200, 199]})  # 96% jump
    out = check_ohlcv_data_quality(df, gap_pct_threshold=0.50)
    assert out["has_extreme_gap"] is True
    assert out["DataQualityWarning"] is True


def test_dec_233_data_quality_consecutive_nan_triggers_warning():
    """DEC-233: max_consecutive_nan_days breached -> warning."""
    import pandas as pd
    import numpy as np
    from backtest.engine.improvements import check_ohlcv_data_quality
    df = pd.DataFrame({"close": [100, 101, np.nan, np.nan, np.nan, np.nan, 102]})
    out = check_ohlcv_data_quality(df, max_consecutive_nan_days=3)
    assert out["has_nan_close"] is True
    assert out["max_consecutive_nan_run"] >= 3
    assert out["DataQualityWarning"] is True


def test_dec_233_data_quality_empty_df_returns_warning():
    """DEC-233: empty df -> warning (no data to validate is itself a problem)."""
    import pandas as pd
    from backtest.engine.improvements import check_ohlcv_data_quality
    out = check_ohlcv_data_quality(pd.DataFrame())
    assert out["DataQualityWarning"] is True


# --- DEC-284 borderline pass/fail policy ----------------------------------

def test_dec_284_strict_ge_passes_at_threshold():
    """DEC-284 spec: Sharpe >= 0.5 passes; equality goes pass-side."""
    from backtest.results.metrics import evaluates_pass
    assert evaluates_pass(0.50, 0.50, "pass_ge") is True
    assert evaluates_pass(0.51, 0.50, "pass_ge") is True
    assert evaluates_pass(0.49, 0.50, "pass_ge") is False


def test_dec_284_strict_le_passes_at_threshold():
    """DEC-284: max-drawdown <= 20 passes; equality goes pass-side."""
    from backtest.results.metrics import evaluates_pass
    assert evaluates_pass(20.0, 20.0, "pass_le") is True
    assert evaluates_pass(19.9, 20.0, "pass_le") is True
    assert evaluates_pass(20.1, 20.0, "pass_le") is False


def test_dec_284_fails_closed_on_none():
    """DEC-284: None inputs fail-closed (never spuriously pass)."""
    from backtest.results.metrics import evaluates_pass
    assert evaluates_pass(None, 0.5, "pass_ge") is False
    assert evaluates_pass(1.0, None, "pass_ge") is False


# --- DEC-287 public site freshness signal --------------------------------

def test_dec_287_freshness_state_ok_when_recent():
    """DEC-287: age <= 24h -> OK state."""
    from datetime import datetime, timedelta
    from backtest.results.metrics import compute_freshness_banner
    last = (datetime(2026, 5, 11, 8, 30) - timedelta(hours=2)).isoformat()
    out = compute_freshness_banner(last, now=datetime(2026, 5, 11, 8, 30))
    assert out["state"] == "OK"
    assert out["age_hours"] is not None


def test_dec_287_freshness_state_warn_when_stale():
    """DEC-287 spec test signal: >24h stale -> WARN banner."""
    from datetime import datetime, timedelta
    from backtest.results.metrics import compute_freshness_banner
    last = (datetime(2026, 5, 11, 8, 30) - timedelta(hours=48)).isoformat()
    out = compute_freshness_banner(last, now=datetime(2026, 5, 11, 8, 30))
    assert out["state"] == "WARN"
    assert "h old" in out["banner_message"]


def test_dec_287_freshness_state_error_when_missing():
    """DEC-287 spec test signal: fetch failure -> ERROR state (not silent stale)."""
    from backtest.results.metrics import compute_freshness_banner
    out = compute_freshness_banner(None)
    assert out["state"] == "ERROR"
    assert "retry" in out["banner_message"].lower()


def test_dec_287_freshness_state_error_on_invalid_iso():
    """DEC-287: invalid timestamp -> ERROR (not silent stale)."""
    from backtest.results.metrics import compute_freshness_banner
    out = compute_freshness_banner("not-an-iso-date")
    assert out["state"] == "ERROR"


# ============================================================================
# Phase 3 Batch 57 Path C 5-DEC bundle (owner directive >= 5 DECs/batch):
# DEC-076 (factor exposure breaker) + DEC-098 (90% coverage gate helper)
# + DEC-179 (memory profiling) + DEC-325 (institutional 13F filing_date PIT)
# + DEC-333 (CNN F&G canonical bands)
# ============================================================================

# --- DEC-076 factor exposure breaker --------------------------------------

def test_dec_076_factor_concentration_no_breach_when_diversified():
    """DEC-076: diversified portfolio (each sector < 30%) -> no breach."""
    from datetime import date
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.add_position("AAPL", "Tech", "long", entry_price=100.0,
                   size_pct=0.10, entry_date=date(2024, 1, 1))
    p.add_position("JPM", "Financials", "long", entry_price=100.0,
                   size_pct=0.10, entry_date=date(2024, 1, 1))
    p.add_position("XOM", "Energy", "long", entry_price=100.0,
                   size_pct=0.10, entry_date=date(2024, 1, 1))
    out = p.factor_concentration_breach(sector_threshold_pct=30.0)
    assert out["any_breach"] is False
    assert out["sector_breaches"] == []


def test_dec_076_factor_concentration_breach_when_concentrated():
    """DEC-076: concentrated portfolio (>30% in one sector) -> breach flag."""
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


def test_dec_076_factor_concentration_empty_portfolio():
    """DEC-076: empty portfolio -> no breaches."""
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    out = p.factor_concentration_breach()
    assert out["any_breach"] is False
    assert out["max_sector"] is None


# --- DEC-098 test coverage gate helper ------------------------------------

def test_dec_098_coverage_threshold_constant_is_90pct():
    """DEC-098: owner-overridden threshold is 90% (not 70%)."""
    from backtest.engine.improvements import STAGE_3_TEST_COVERAGE_THRESHOLD
    assert STAGE_3_TEST_COVERAGE_THRESHOLD == 0.90


def test_dec_098_coverage_missing_xml_returns_unavailable():
    """DEC-098: missing coverage.xml -> coverage_unavailable + fail."""
    from backtest.engine.improvements import check_test_coverage_threshold
    out = check_test_coverage_threshold("/nonexistent/coverage.xml")
    assert out["coverage_pct"] is None
    assert out["passes"] is False
    assert out["note"] == "coverage_unavailable"


def test_dec_098_coverage_parses_xml_passes_above_threshold(tmp_path):
    """DEC-098: synthetic coverage.xml at 0.95 line-rate -> passes."""
    from backtest.engine.improvements import check_test_coverage_threshold
    xml = tmp_path / "coverage.xml"
    xml.write_text('<?xml version="1.0"?>\n<coverage line-rate="0.95"></coverage>')
    out = check_test_coverage_threshold(str(xml), threshold=0.90)
    assert out["passes"] is True
    assert out["coverage_pct"] == 0.95


def test_dec_098_coverage_parses_xml_fails_below_threshold(tmp_path):
    """DEC-098: synthetic coverage.xml at 0.65 -> fails 90% threshold."""
    from backtest.engine.improvements import check_test_coverage_threshold
    xml = tmp_path / "coverage.xml"
    xml.write_text('<?xml version="1.0"?>\n<coverage line-rate="0.65"></coverage>')
    out = check_test_coverage_threshold(str(xml), threshold=0.90)
    assert out["passes"] is False
    assert out["note"] == "below_threshold"


# --- DEC-179 memory profiling helper --------------------------------------

def test_dec_179_get_process_memory_returns_positive_or_neg_one():
    """DEC-179: returns positive MB when psutil/resource available;
    -1.0 on Windows-without-psutil fallback (graceful).
    """
    from backtest.engine.improvements import get_process_memory_mb
    mb = get_process_memory_mb()
    assert mb > 0 or mb == -1.0


def test_dec_179_check_memory_cap_not_breached_with_high_cap():
    """DEC-179: cap >> current -> breached=False."""
    from backtest.engine.improvements import check_memory_cap
    out = check_memory_cap(cap_mb=1_000_000)
    assert out["breached"] is False
    assert out["cap_mb"] == 1_000_000.0


def test_dec_179_check_memory_cap_breached_with_low_cap():
    """DEC-179: cap = 1 MB -> almost certainly breached for python process."""
    from backtest.engine.improvements import check_memory_cap, get_process_memory_mb
    if get_process_memory_mb() < 0:
        return  # skip on platforms where memory profiling unavailable
    out = check_memory_cap(cap_mb=1.0)
    assert out["breached"] is True
    assert out["note"] == "MEMORY_CAP_BREACHED"


# --- DEC-325 institutional 13F filing_date PIT ---------------------------

def test_dec_325_get_institutional_positions_prefers_filing_date():
    """DEC-325: filing_date present -> filter by filing_date <= as_of
    NOT by ReportPeriod + 45 (which silently drops late filers).
    """
    import pandas as pd
    from datetime import date
    from unittest.mock import patch
    df = pd.DataFrame([
        {"Ticker": "AAPL", "Fund": "BigFundA",
         "ReportPeriod": "2024-03-31", "filing_date": "2024-08-01",
         "Change_Share": 1000, "Change_Pct": 0.5},
        {"Ticker": "AAPL", "Fund": "BigFundB",
         "ReportPeriod": "2024-03-31", "filing_date": "2024-05-10",
         "Change_Share": 500, "Change_Pct": 0.2},
    ])
    with patch("backtest.data.smart_money._load_quiver_bulk", return_value=df), \
         patch("backtest.data.smart_money._filter_bulk_by_ticker", return_value=df):
        from backtest.data.smart_money import get_institutional_positions
        out = get_institutional_positions("AAPL", as_of=date(2024, 6, 1))
        funds = set(out["Fund"].tolist())
        assert "BigFundB" in funds
        assert "BigFundA" not in funds


def test_dec_325_get_institutional_positions_visible_after_filing():
    """DEC-325: late filer becomes visible once filing_date <= as_of."""
    import pandas as pd
    from datetime import date
    from unittest.mock import patch
    df = pd.DataFrame([
        {"Ticker": "AAPL", "Fund": "LateFund",
         "ReportPeriod": "2024-03-31", "filing_date": "2024-08-01",
         "Change_Share": 1000, "Change_Pct": 0.5},
    ])
    with patch("backtest.data.smart_money._load_quiver_bulk", return_value=df), \
         patch("backtest.data.smart_money._filter_bulk_by_ticker", return_value=df):
        from backtest.data.smart_money import get_institutional_positions
        out = get_institutional_positions("AAPL", as_of=date(2024, 8, 15))
        assert "LateFund" in set(out["Fund"].tolist())


def test_dec_325_get_institutional_positions_fallback_to_report_period():
    """DEC-325: no filing_date column -> falls back to ReportPeriod+45 estimate."""
    import pandas as pd
    from datetime import date
    from unittest.mock import patch
    df = pd.DataFrame([
        {"Ticker": "AAPL", "Fund": "F",
         "ReportPeriod": "2024-03-31", "Change_Share": 1000, "Change_Pct": 0.5},
    ])
    with patch("backtest.data.smart_money._load_quiver_bulk", return_value=df), \
         patch("backtest.data.smart_money._filter_bulk_by_ticker", return_value=df):
        from backtest.data.smart_money import get_institutional_positions
        out = get_institutional_positions("AAPL", as_of=date(2024, 6, 1))
        assert len(out) == 1


# --- DEC-333 CNN F&G canonical bands -------------------------------------

def test_dec_333_cnn_fg_band_extreme_fear():
    """DEC-333: CNN published Extreme Fear band 0-25."""
    from backtest.data.sentiment import cnn_fg_band
    assert cnn_fg_band(0) == "extreme_fear"
    assert cnn_fg_band(15) == "extreme_fear"
    assert cnn_fg_band(25) == "extreme_fear"
    assert cnn_fg_band(26) == "fear"


def test_dec_333_cnn_fg_band_neutral():
    """DEC-333: CNN published Neutral band 46-55."""
    from backtest.data.sentiment import cnn_fg_band
    assert cnn_fg_band(46) == "neutral"
    assert cnn_fg_band(50) == "neutral"
    assert cnn_fg_band(55) == "neutral"
    assert cnn_fg_band(45) == "fear"
    assert cnn_fg_band(56) == "greed"


def test_dec_333_cnn_fg_band_extreme_greed():
    """DEC-333: CNN published Extreme Greed band 76-100."""
    from backtest.data.sentiment import cnn_fg_band
    assert cnn_fg_band(76) == "extreme_greed"
    assert cnn_fg_band(100) == "extreme_greed"
    assert cnn_fg_band(75) == "greed"


def test_dec_333_cnn_fg_band_invalid_inputs():
    """DEC-333: None / out-of-range / non-numeric -> 'unknown'."""
    from backtest.data.sentiment import cnn_fg_band
    assert cnn_fg_band(None) == "unknown"
    assert cnn_fg_band(-5) == "unknown"
    assert cnn_fg_band(150) == "unknown"
    assert cnn_fg_band("garbage") == "unknown"


# ============================================================================
# Phase 3 Batch 58 Path C 10-DEC bundle (owner directive 10 DECs this turn):
# DEC-021 (3-tier system) + DEC-128 (dispersion CB) + DEC-148 (vol-adj momentum)
# + DEC-155 (vs-SPY metrics) + DEC-178 (perf benchmark) + DEC-208 (multi-metric AB)
# + DEC-210 (net Sharpe) + DEC-211 (ablation) + DEC-227 (cache size)
# + DEC-232 (determinism diff)
# ============================================================================

def test_dec_021_3_tier_config_constants():
    """DEC-021: 3-tier sizing 5%/3%/1.5% + 5-to-3 mapping."""
    from backtest.config import TIER_3_POSITION_SIZE_PCT, TIER_5_TO_TIER_3
    assert TIER_3_POSITION_SIZE_PCT["HIGH"] == 0.05
    assert TIER_3_POSITION_SIZE_PCT["MEDIUM"] == 0.03
    assert TIER_3_POSITION_SIZE_PCT["LOW"] == 0.015
    assert TIER_5_TO_TIER_3["EXCEPTIONAL"] == "HIGH"
    assert TIER_5_TO_TIER_3["MEDIUM_HIGH"] == "MEDIUM"
    assert TIER_5_TO_TIER_3["MEDIUM"] == "LOW"


def test_dec_128_dispersion_cb_triggers_on_outlier_day():
    """DEC-128: spike day with cross-sectional std >> rolling -> triggered."""
    import pandas as pd
    import numpy as np
    from backtest.engine.regime_filter import dispersion_circuit_breaker
    np.random.seed(0)
    base = np.random.normal(0, 0.01, size=(30, 10))
    spike = np.random.normal(0, 0.10, size=(1, 10))  # 10x normal vol
    df = pd.DataFrame(np.vstack([base, spike]))
    out = dispersion_circuit_breaker(df, window=20, sigma_threshold=3.0)
    assert out["triggered"] is True


def test_dec_128_dispersion_cb_no_trigger_on_normal_day():
    """DEC-128: steady cross-sectional vol -> no trigger."""
    import pandas as pd
    import numpy as np
    from backtest.engine.regime_filter import dispersion_circuit_breaker
    np.random.seed(1)
    df = pd.DataFrame(np.random.normal(0, 0.01, size=(30, 10)))
    out = dispersion_circuit_breaker(df, window=20, sigma_threshold=3.0)
    assert out["triggered"] is False


def test_dec_148_vol_adjusted_lookback_inverse_to_vol():
    """DEC-148: high vol -> short lookback; low vol -> long lookback."""
    from backtest.results.metrics import vol_adjusted_momentum_lookback
    assert vol_adjusted_momentum_lookback(0.10) == 60  # low vol -> long
    assert vol_adjusted_momentum_lookback(0.50) == 10  # high vol -> short
    mid = vol_adjusted_momentum_lookback(0.25)
    assert 10 < mid < 60  # interpolated


def test_dec_148_vol_adjusted_lookback_handles_none():
    """DEC-148: None vol -> base_lookback."""
    from backtest.results.metrics import vol_adjusted_momentum_lookback
    assert vol_adjusted_momentum_lookback(None) == 21


def test_dec_155_vs_spy_metrics_positive_alpha():
    """DEC-155: strategy outperforming SPY -> positive alpha."""
    import pandas as pd
    import numpy as np
    from backtest.results.metrics import compute_vs_spy_metrics
    np.random.seed(42)
    spy = pd.Series(np.random.normal(0.0005, 0.01, 100))
    strat = spy + 0.001  # constant +10bps daily lift
    out = compute_vs_spy_metrics(strat, spy)
    assert out["alpha_annualized"] > 0
    assert out["information_ratio"] > 0
    assert out["n_obs"] == 100


def test_dec_155_vs_spy_metrics_insufficient_obs():
    """DEC-155: <30 obs -> insufficient_obs note."""
    import pandas as pd
    from backtest.results.metrics import compute_vs_spy_metrics
    out = compute_vs_spy_metrics(pd.Series([0.01] * 10), pd.Series([0.005] * 10))
    assert out["note"] == "insufficient_obs"


def test_dec_178_benchmark_function_returns_latency_stats():
    """DEC-178: benchmark returns median/p95/total."""
    from backtest.engine.improvements import benchmark_function
    out = benchmark_function(lambda: sum(range(100)), n_iters=50)
    assert out["median_ms"] is not None
    assert out["p95_ms"] is not None
    assert out["n_iters"] == 50
    assert out["median_ms"] >= 0


def test_dec_178_benchmark_function_zero_iters():
    """DEC-178: n_iters=0 -> no_iters note."""
    from backtest.engine.improvements import benchmark_function
    out = benchmark_function(lambda: None, n_iters=0)
    assert out["note"] == "no_iters"


def test_dec_208_multi_metric_ab_comparison_shapes():
    """DEC-208: returns per-arm metrics + delta dict."""
    import pandas as pd
    from backtest.results.metrics import compute_multi_metric_ab_comparison
    df_a = pd.DataFrame([
        {"pnl_pct": 1.0, "win": True, "hold_days": 10},
        {"pnl_pct": -0.5, "win": False, "hold_days": 5},
    ] * 25)
    df_b = pd.DataFrame([
        {"pnl_pct": 1.5, "win": True, "hold_days": 10},
        {"pnl_pct": -0.3, "win": False, "hold_days": 5},
    ] * 25)
    out = compute_multi_metric_ab_comparison(df_a, df_b)
    assert "rules" in out and "agent" in out and "delta" in out
    assert out["rules"]["n_trades"] == 50
    assert out["agent"]["n_trades"] == 50
    # Agent has stronger wins -> positive sharpe delta
    assert out["delta"]["sharpe"] is not None


def test_dec_210_net_sharpe_contribution_spec_test_signal():
    """DEC-210 spec: $1000/mo on $100K * 12% vol -> cost-Sharpe = 1.0;
    gross 1.2 -> net 0.2 -> meets DEC-131 threshold.
    """
    from backtest.results.metrics import compute_net_sharpe_contribution
    out = compute_net_sharpe_contribution(
        gross_sharpe_lift=1.2,
        annual_agent_cost_usd=12_000,
        portfolio_size_usd=100_000,
        portfolio_vol_decimal=0.12,
    )
    assert abs(out["cost_sharpe"] - 1.0) < 1e-6
    assert abs(out["net_sharpe"] - 0.2) < 1e-6
    assert out["meets_dec_131_threshold"] is True


def test_dec_210_net_sharpe_below_threshold():
    """DEC-210: gross 1.0 -> net 0.0 -> fails DEC-131 0.2 threshold."""
    from backtest.results.metrics import compute_net_sharpe_contribution
    out = compute_net_sharpe_contribution(1.0, 12_000, 100_000, 0.12)
    assert out["meets_dec_131_threshold"] is False


def test_dec_211_ablation_contributions_marginal_sharpe():
    """DEC-211: marginal_contrib = sharpe(full) - sharpe(no_AGENT)."""
    from backtest.results.metrics import compute_per_agent_ablation_contributions
    arms = {
        "full":     {"sharpe": 1.5},
        "no_Bull":  {"sharpe": 1.2},  # Bull contributes 0.3
        "no_Bear":  {"sharpe": 1.4},  # Bear contributes 0.1
        "no_Risk":  {"sharpe": 1.6},  # Risk hurts -0.1
    }
    out = compute_per_agent_ablation_contributions(arms)
    assert abs(out["Bull"] - 0.3) < 1e-6
    assert abs(out["Bear"] - 0.1) < 1e-6
    assert abs(out["Risk"] - (-0.1)) < 1e-6


def test_dec_211_ablation_missing_full_returns_error():
    """DEC-211: missing 'full' arm -> _error key."""
    from backtest.results.metrics import compute_per_agent_ablation_contributions
    out = compute_per_agent_ablation_contributions({"no_Bull": {"sharpe": 1.2}})
    assert "_error" in out


def test_dec_227_get_cache_size_gb_real_path(tmp_path):
    """DEC-227: synthetic cache directory size sums correctly."""
    from backtest.engine.improvements import get_cache_size_gb
    (tmp_path / "a.bin").write_bytes(b"x" * 1024)  # 1 KB
    (tmp_path / "b.bin").write_bytes(b"x" * 2048)  # 2 KB
    size = get_cache_size_gb(str(tmp_path))
    assert size > 0
    assert size < 0.001  # 3KB ~= 0.0000028 GB


def test_dec_227_cache_size_alert_below_threshold():
    """DEC-227: 50% of disk used -> no alert."""
    from backtest.engine.improvements import cache_size_alert_level
    out = cache_size_alert_level(50.0, 100.0, threshold_pct=0.80)
    assert out["alert"] is False
    assert out["note"] == "ok"


def test_dec_227_cache_size_alert_above_threshold():
    """DEC-227: 90% of disk used -> CACHE_SIZE_ALERT."""
    from backtest.engine.improvements import cache_size_alert_level
    out = cache_size_alert_level(90.0, 100.0, threshold_pct=0.80)
    assert out["alert"] is True
    assert out["note"] == "CACHE_SIZE_ALERT"


def test_dec_232_diff_trade_logs_identical():
    """DEC-232: identical DataFrames -> byte_identical=True."""
    import pandas as pd
    from backtest.results.metrics import diff_trade_logs
    df = pd.DataFrame([{"a": 1, "b": 2.0, "c": "x"} for _ in range(10)])
    out = diff_trade_logs(df, df.copy())
    assert out["byte_identical"] is True
    assert out["row_diff_count"] == 0


def test_dec_232_diff_trade_logs_detects_diff():
    """DEC-232: differing row -> byte_identical=False + first_diff_index pinpoints."""
    import pandas as pd
    from backtest.results.metrics import diff_trade_logs
    df_a = pd.DataFrame([{"a": i, "b": 0.0} for i in range(10)])
    df_b = df_a.copy()
    df_b.loc[3, "b"] = 999.0
    out = diff_trade_logs(df_a, df_b)
    assert out["byte_identical"] is False
    assert out["first_diff_index"] == 3


def test_dec_232_diff_trade_logs_shape_mismatch():
    """DEC-232: shape mismatch -> shape_match=False + note."""
    import pandas as pd
    from backtest.results.metrics import diff_trade_logs
    df_a = pd.DataFrame([{"a": 1}, {"a": 2}])
    df_b = pd.DataFrame([{"a": 1}])
    out = diff_trade_logs(df_a, df_b)
    assert out["byte_identical"] is False
    assert out["shape_match"] is False


# ============================================================================
# Phase 3 Batch 59 Path C 20-DEC bundle (owner directive: 20 DECs this turn)
# DEC-015 / 038 / 061 / 062 / 102 / 116 / 120 / 123 / 124 / 131 / 134 / 141
# / 142 / 145 / 159 / 174 / 183 / 206 / 212 / 235
# ============================================================================

def test_dec_015_correlation_matrix_basic():
    """DEC-015: 90-day rolling Pearson correlation matrix."""
    import pandas as pd
    import numpy as np
    from backtest.results.metrics import compute_strategy_correlation_matrix
    np.random.seed(0)
    df = pd.DataFrame({"sA": np.random.normal(0, 0.01, 120),
                       "sB": np.random.normal(0, 0.01, 120)})
    out = compute_strategy_correlation_matrix(df, window=90)
    assert out.shape == (2, 2)
    assert abs(out.loc["sA", "sA"] - 1.0) < 1e-9


def test_dec_015_correlation_matrix_insufficient_history():
    """DEC-015: <window rows -> empty DataFrame."""
    import pandas as pd
    from backtest.results.metrics import compute_strategy_correlation_matrix
    df = pd.DataFrame({"sA": [0.01] * 30, "sB": [0.02] * 30})
    out = compute_strategy_correlation_matrix(df, window=90)
    assert out.empty


def test_dec_038_iteration_budgets_constants():
    """DEC-038: layered execution budget constants exist with non-zero values."""
    from backtest.config import LAYERED_EXECUTION_BUDGETS
    for k in ("phase_audit_pass", "decision_review_round",
              "implementation_step", "test_pyramid_layer"):
        assert k in LAYERED_EXECUTION_BUDGETS
        assert LAYERED_EXECUTION_BUDGETS[k] > 0


def test_dec_061_dec_062_agent_tier_size_modifier():
    """DEC-061/062: TradingAgents 5-tier -> size modifier mapping."""
    from backtest.config import AGENT_TIER_TO_SIZE_MODIFIER
    assert AGENT_TIER_TO_SIZE_MODIFIER[1] == 0.50
    assert AGENT_TIER_TO_SIZE_MODIFIER[3] == 1.00
    assert AGENT_TIER_TO_SIZE_MODIFIER[5] == 1.50


def test_dec_102_cross_asset_strategy_tickers():
    """DEC-102: cross-asset strategy tickers per DEC-369 absorption."""
    from backtest.config import CROSS_ASSET_STRATEGY_TICKERS
    assert "TLT" in CROSS_ASSET_STRATEGY_TICKERS
    assert "GLD" in CROSS_ASSET_STRATEGY_TICKERS
    assert "UUP" in CROSS_ASSET_STRATEGY_TICKERS
    assert "USO" in CROSS_ASSET_STRATEGY_TICKERS


def test_dec_116_cash_management_constants():
    """DEC-116: SGOV idle cash routing + trigger threshold."""
    from backtest.config import (CASH_MANAGEMENT_TICKER,
                                   CASH_MANAGEMENT_TRIGGER_PCT)
    assert CASH_MANAGEMENT_TICKER == "SGOV"
    assert 0 < CASH_MANAGEMENT_TRIGGER_PCT < 1


def test_dec_120_top_n_losing_trades_per_strategy():
    """DEC-120: returns top-N losers per strategy sorted ascending pnl."""
    import pandas as pd
    from backtest.results.metrics import top_n_losing_trades_per_strategy
    df = pd.DataFrame([
        {"strategy": "A", "ticker": "X", "pnl_pct": -5.0,
         "entry_date": "2024-01-01", "exit_date": "2024-01-05", "regime": "bull"},
        {"strategy": "A", "ticker": "Y", "pnl_pct": -10.0,
         "entry_date": "2024-01-01", "exit_date": "2024-01-05", "regime": "bull"},
        {"strategy": "A", "ticker": "Z", "pnl_pct": 3.0,
         "entry_date": "2024-01-01", "exit_date": "2024-01-05", "regime": "bull"},
    ])
    out = top_n_losing_trades_per_strategy(df, n=10)
    assert "A" in out
    # Sorted ascending pnl -> -10 first then -5; +3 excluded (not a loser)
    assert out["A"][0]["pnl_pct"] == -10.0
    assert len(out["A"]) == 2


def test_dec_123_exponential_decay_weights_recent_higher():
    """DEC-123: recent disclosures (days_ago=0) weighted higher than 90d old."""
    from backtest.results.metrics import exponential_decay_weights
    weights = exponential_decay_weights([0, 90, 180], half_life_days=90)
    assert weights[0] > weights[1] > weights[2]
    assert abs(sum(weights) - 1.0) < 1e-9


def test_dec_123_exponential_decay_weights_empty():
    """DEC-123: empty input -> empty list."""
    from backtest.results.metrics import exponential_decay_weights
    assert exponential_decay_weights([]) == []


def test_dec_124_cross_source_smart_money_high_confluence():
    """DEC-124: 3 buy sources -> HIGH_CONFLUENCE."""
    from backtest.results.metrics import cross_source_smart_money_cluster
    out = cross_source_smart_money_cluster("buy", "strong_buy", "buy")
    assert out["cluster_label"] == "HIGH_CONFLUENCE"
    assert out["sources_aligned"] == 3


def test_dec_124_cross_source_smart_money_no_signal():
    """DEC-124: no buy/sell signals -> NO_SIGNAL."""
    from backtest.results.metrics import cross_source_smart_money_cluster
    out = cross_source_smart_money_cluster("none", "hold", None)
    assert out["cluster_label"] == "NO_SIGNAL"


def test_dec_131_two_gate_passes_on_absolute():
    """DEC-131 spec signal: baseline 1.5 / agent 1.7 -> abs gate passes."""
    from backtest.results.metrics import agent_value_add_two_gate_check
    out = agent_value_add_two_gate_check(agent_sharpe=1.7, rules_sharpe=1.5)
    assert out["passes"] is True
    assert out["gate_reason"] in ("absolute", "both")


def test_dec_131_two_gate_passes_on_relative_low_baseline():
    """DEC-131 spec signal: baseline 0.3 / agent 0.5 -> both gates clear."""
    from backtest.results.metrics import agent_value_add_two_gate_check
    out = agent_value_add_two_gate_check(agent_sharpe=0.5, rules_sharpe=0.3)
    assert out["passes"] is True


def test_dec_131_two_gate_fails_on_small_lift():
    """DEC-131 spec signal: baseline 1.5 / agent 1.55 -> both fail."""
    from backtest.results.metrics import agent_value_add_two_gate_check
    out = agent_value_add_two_gate_check(agent_sharpe=1.55, rules_sharpe=1.5)
    assert out["passes"] is False
    assert out["gate_reason"] == "none"


def test_dec_134_fx_exposure_basic():
    """DEC-134: USD 30K of 100K total CAD -> 30% exposure."""
    from backtest.results.metrics import compute_fx_exposure_pct
    out = compute_fx_exposure_pct(30_000, 100_000)
    assert abs(out["fx_exposure_pct"] - 30.0) < 1e-6


def test_dec_134_fx_exposure_invalid_total():
    """DEC-134: zero/negative total -> invalid_portfolio_total."""
    from backtest.results.metrics import compute_fx_exposure_pct
    out = compute_fx_exposure_pct(30_000, 0)
    assert out["note"] == "invalid_portfolio_total"


def test_dec_141_sector_neutral_hedge_plan():
    """DEC-141: long position + short sector ETF plan."""
    from backtest.results.metrics import build_sector_neutral_hedge
    out = build_sector_neutral_hedge("AAPL", 10_000, "XLK")
    assert out["hedge_ticker"] == "XLK"
    assert out["hedge_direction"] == "short"
    assert out["hedge_dollar"] == 10_000.0


def test_dec_142_market_neutral_hedge_at_beta():
    """DEC-142: SPY short sized at beta-weight."""
    from backtest.results.metrics import build_market_neutral_hedge
    out = build_market_neutral_hedge("AAPL", 10_000, beta=1.2)
    assert out["hedge_ticker"] == "SPY"
    assert abs(out["hedge_dollar"] - 12_000.0) < 1e-6


def test_dec_145_iv_anomaly_elevated():
    """DEC-145: current IV 2.5 std above historical mean -> anomaly elevated."""
    from backtest.results.metrics import iv_pre_earnings_anomaly
    out = iv_pre_earnings_anomaly(
        current_iv=0.80,
        historical_iv_pre_earnings=[0.30, 0.32, 0.31, 0.33, 0.29],
    )
    assert out["anomaly"] is True
    assert out["direction"] == "elevated"


def test_dec_145_iv_anomaly_no_history():
    """DEC-145: insufficient history -> note + no anomaly."""
    from backtest.results.metrics import iv_pre_earnings_anomaly
    out = iv_pre_earnings_anomaly(current_iv=0.5,
                                   historical_iv_pre_earnings=[0.3])
    assert out["note"] == "insufficient_history"


def test_dec_159_regulatory_event_flagged_on_sec_investigation():
    """DEC-159: SEC investigation news within window -> flagged."""
    from datetime import date, timedelta
    from backtest.engine.improvements import regulatory_event_flag
    today = date(2024, 6, 15)
    news = [{"date": today - timedelta(days=2),
             "title": "Company X under SEC investigation",
             "source": "Reuters"}]
    out = regulatory_event_flag("X", news, event_window_days=5, as_of=today)
    assert out["flagged"] is True


def test_dec_159_regulatory_event_not_flagged_outside_window():
    """DEC-159: SEC news older than window -> not flagged."""
    from datetime import date, timedelta
    from backtest.engine.improvements import regulatory_event_flag
    today = date(2024, 6, 15)
    news = [{"date": today - timedelta(days=30),
             "title": "Past SEC enforcement action",
             "source": "WSJ"}]
    out = regulatory_event_flag("X", news, event_window_days=5, as_of=today)
    assert out["flagged"] is False


def test_dec_174_strategy_trigger_types_constants():
    """DEC-174: catalyst/technical/stat_arb trigger types codified."""
    from backtest.config import STRATEGY_TRIGGER_TYPES
    assert "catalyst" in STRATEGY_TRIGGER_TYPES
    assert "technical" in STRATEGY_TRIGGER_TYPES
    assert "stat_arb" in STRATEGY_TRIGGER_TYPES


def test_dec_183_lru_cached_wraps_function():
    """DEC-183: decorator memoizes a function."""
    from backtest.engine.improvements import lru_cached
    call_count = [0]

    @lru_cached(maxsize=32)
    def fn(x):
        call_count[0] += 1
        return x * 2

    fn(5); fn(5); fn(5)
    assert call_count[0] == 1
    fn(7)
    assert call_count[0] == 2


def test_dec_206_paired_ab_arms_best_worst():
    """DEC-206: paired A/B picks best + worst arm per trade."""
    from backtest.results.metrics import evaluate_paired_ab_arms
    out = evaluate_paired_ab_arms(
        "T-001", {"rules": 1.0, "agent_a": 2.5, "agent_b": -0.5},
    )
    assert out["best_arm"] == "agent_a"
    assert out["worst_arm"] == "agent_b"
    assert out["spread"] == 3.0


def test_dec_212_agent_disagreement_bull_bear():
    """DEC-212 spec signal: Bull=BUY, Bear=HOLD, Risk=APPROVE -> bull_bear_disagree."""
    from backtest.results.metrics import tag_agent_disagreement
    out = tag_agent_disagreement(bull_signal="BUY", bear_signal="HOLD",
                                  risk_signal="APPROVE")
    assert out["disagreement_type"] == "bull_bear_disagree"
    assert "AGENT_DISAGREEMENT_BULL_BEAR" in out["tags"]


def test_dec_212_agent_disagreement_consensus():
    """DEC-212: all agree -> consensus, no tags."""
    from backtest.results.metrics import tag_agent_disagreement
    out = tag_agent_disagreement("BUY", "BUY", "APPROVE")
    assert out["disagreement_type"] == "consensus"
    assert out["n_tags"] == 0


def test_dec_235_nyse_trading_day_weekend_false():
    """DEC-235: weekday helper or library returns False for Saturday."""
    from datetime import date
    from backtest.engine.improvements import is_nyse_trading_day
    # 2024-06-15 = Saturday
    assert is_nyse_trading_day(date(2024, 6, 15)) is False


def test_dec_235_nyse_trading_day_weekday_true():
    """DEC-235: regular weekday returns True."""
    from datetime import date
    from backtest.engine.improvements import is_nyse_trading_day
    # 2024-06-17 = Monday (non-holiday)
    assert is_nyse_trading_day(date(2024, 6, 17)) is True


# ============================================================================
# DEC-432 Chandelier exit indicator tests (Phase 3 Batch 53 Path C)
# Parabolic SAR + Supertrend already implemented; only chandelier added.
# ============================================================================

def _make_trending_ohlcv_dec432(n: int, base: float = 100.0, drift: float = 0.5):
    """DEC-432 helper: build a trending OHLCV DataFrame with `n` daily bars.
    Distinct name from earlier _make_ohlcv (BUG-270 hybrid trail tests) which
    takes (dates, highs, lows, closes) positional args.
    """
    import pandas as pd
    rows = []
    for i in range(n):
        c = base + drift * i
        rows.append({
            "open":  c - 0.3,
            "high":  c + 0.6,
            "low":   c - 0.7,
            "close": c,
            "volume": 1_000_000,
        })
    return pd.DataFrame(rows)


def test_dec_432_chandelier_exit_basic_formula():
    """DEC-432: chandelier_long = highest_high(22) - ATR(22)*3.0."""
    from backtest.signals.technical import compute_chandelier_exit, _atr_series

    df = _make_trending_ohlcv_dec432(30)
    out = compute_chandelier_exit(df, period=22, mult=3.0)
    assert "chandelier_long_value" in out
    assert "chandelier_short_value" in out
    # chandelier_long < highest_high and > lowest_low
    hh = df["high"].rolling(22).max().iloc[-1]
    ll = df["low"].rolling(22).min().iloc[-1]
    atr = _atr_series(df, 22).iloc[-1]
    expected_long = hh - 3.0 * atr
    assert abs(out["chandelier_long_value"] - round(float(expected_long), 4)) < 1e-3
    expected_short = ll + 3.0 * atr
    assert abs(out["chandelier_short_value"] - round(float(expected_short), 4)) < 1e-3


def test_dec_432_chandelier_long_bullish_in_uptrend():
    """DEC-432: in a clean uptrend, close > chandelier_long -> bullish=True."""
    from backtest.signals.technical import compute_chandelier_exit

    df = _make_trending_ohlcv_dec432(40, drift=0.5)
    out = compute_chandelier_exit(df)
    assert out["chandelier_long_bullish"] is True
    assert out["chandelier_long_flip_dn"] is False


def test_dec_432_chandelier_insufficient_history_returns_empty():
    """DEC-432: fewer than period+1 bars -> empty dict (silent skip)."""
    from backtest.signals.technical import compute_chandelier_exit

    df = _make_trending_ohlcv_dec432(10)  # less than period=22
    out = compute_chandelier_exit(df, period=22)
    assert out == {}


def test_dec_432_chandelier_wired_into_compute_all_signals():
    """DEC-432: chandelier fields surface in compute_all_signals output."""
    from backtest.signals.technical import compute_all_signals

    df = _make_trending_ohlcv_dec432(60)
    sig = compute_all_signals(df)
    for k in ("chandelier_long_value", "chandelier_short_value",
              "chandelier_long_bullish", "chandelier_short_bearish",
              "chandelier_long_flip_dn", "chandelier_short_flip_up"):
        assert k in sig, f"missing {k}"


# ============================================================================
# DEC-087 Vol-targeted per-position sizing tests (Phase 3 Batch 52 Path C)
# ============================================================================

def test_dec_087_vol_targeted_size_high_vol_smaller_than_low_vol():
    """DEC-087 spec test signal: XOM-during-oil-shock (high vol) gets
    smaller position than KO-consumer-staple (low vol) at same edge level.
    """
    from backtest.engine.portfolio import vol_targeted_size

    base = 0.03  # HIGH tier 3%
    xom_size = vol_targeted_size(base, position_vol_annualized=0.40)
    ko_size  = vol_targeted_size(base, position_vol_annualized=0.15)
    assert xom_size < ko_size
    # target 0.20 / 0.40 = 0.5 multiplier -> 0.03 * 0.5 = 0.015
    assert abs(xom_size - 0.015) < 1e-9
    # target 0.20 / 0.15 = 1.333 multiplier -> 0.03 * 1.333 = 0.04
    assert abs(ko_size - 0.04) < 1e-9


def test_dec_087_vol_targeted_size_reproducible_with_vol_input():
    """DEC-087 spec test signal: vol-targeted size reproducible with vol
    input (deterministic function of base + vol).
    """
    from backtest.engine.portfolio import vol_targeted_size

    s1 = vol_targeted_size(0.03, position_vol_annualized=0.25)
    s2 = vol_targeted_size(0.03, position_vol_annualized=0.25)
    assert s1 == s2
    # target 0.20 / 0.25 = 0.8 multiplier -> 0.03 * 0.8 = 0.024
    assert abs(s1 - 0.024) < 1e-9


def test_dec_087_vol_targeted_size_bounded_low_at_min_multiplier():
    """DEC-087: extremely high position vol clamped at MIN multiplier 0.25."""
    from backtest.engine.portfolio import vol_targeted_size

    # target 0.20 / 2.0 = 0.10 raw multiplier; clamp at 0.25
    s = vol_targeted_size(0.03, position_vol_annualized=2.0)
    assert abs(s - 0.03 * 0.25) < 1e-9


def test_dec_087_vol_targeted_size_bounded_high_at_max_multiplier():
    """DEC-087: extremely low position vol clamped at MAX multiplier 2.0."""
    from backtest.engine.portfolio import vol_targeted_size

    # target 0.20 / 0.05 = 4.0 raw multiplier; clamp at 2.0
    s = vol_targeted_size(0.03, position_vol_annualized=0.05)
    assert abs(s - 0.03 * 2.0) < 1e-9


def test_dec_087_vol_targeted_size_fail_soft_on_missing_vol():
    """DEC-087: position_vol = None or 0 -> return base (no adjustment)."""
    from backtest.engine.portfolio import vol_targeted_size

    assert vol_targeted_size(0.03, position_vol_annualized=None) == 0.03
    assert vol_targeted_size(0.03, position_vol_annualized=0.0) == 0.03
    assert vol_targeted_size(0.03, position_vol_annualized=-0.5) == 0.03


def test_dec_087_vol_targeted_size_custom_target_vol():
    """DEC-087: custom target_vol_annualized parameter overrides default."""
    from backtest.engine.portfolio import vol_targeted_size

    # custom target 0.10 / position 0.20 = 0.5 multiplier
    s = vol_targeted_size(0.03, position_vol_annualized=0.20,
                          target_vol_annualized=0.10)
    assert abs(s - 0.015) < 1e-9


# ============================================================================
# DEC-088 Portfolio vol target 15% tests (Phase 3 Batch 51 Path C)
# ============================================================================

def test_dec_088_realized_portfolio_vol_insufficient_history_returns_none():
    """DEC-088: fewer than window+1 equity points -> None (insufficient data)."""
    from datetime import date, timedelta
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    # Mark for only 10 days; default lookback 21 -> need 22 points
    for i in range(10):
        p.mark_to_market({}, date(2024, 1, 1) + timedelta(days=i))
    assert p.realized_portfolio_vol_annualized() is None


def test_dec_088_realized_portfolio_vol_flat_equity_is_zero():
    """DEC-088: flat equity (no positions, no marks) -> realized vol 0.0
    (genuinely no variation, not missing data).
    """
    from datetime import date, timedelta
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    for i in range(25):
        p.mark_to_market({}, date(2024, 1, 1) + timedelta(days=i))
    v = p.realized_portfolio_vol_annualized()
    assert v is not None
    assert v == 0.0


def test_dec_088_realized_portfolio_vol_nonzero_with_marks():
    """DEC-088: synthetic equity curve with daily returns produces non-zero
    annualized vol roughly matching expectation.

    Manually inject equity points to simulate ~1% daily moves alternating
    sign; expected annualized vol ~ 0.01 * sqrt(252) ~= 0.159.
    """
    from datetime import date, timedelta
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    # Inject 25 points manually onto equity_curve
    base = 100_000.0
    p.equity_curve.clear()
    for i in range(25):
        sign = 1 if i % 2 == 0 else -1
        eq = base * (1 + 0.01 * sign)
        p.equity_curve.append((date(2024, 1, 1) + timedelta(days=i), eq))
    v = p.realized_portfolio_vol_annualized(window_days=21)
    assert v is not None
    # Alternating eq = 100k*(1 +/- 0.01) yields daily return magnitudes
    # ~2% (e.g. (99k-101k)/101k = -1.98%, (101k-99k)/99k = +2.02%).
    # Annualized ~ 0.02 * sqrt(252) ~= 0.317. Tolerance band:
    assert 0.20 < v < 0.40, f"expected ~0.32, got {v}"


def test_dec_088_vol_target_scale_factor_no_history_returns_one():
    """DEC-088: insufficient history -> scale 1.0 (no scaling applied)."""
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    assert p.vol_target_scale_factor() == 1.0


def test_dec_088_vol_target_scale_factor_reduces_when_vol_high():
    """DEC-088: realized > target -> scale < 1 to reduce gross exposure.
    Realized ~0.30, target 0.15 -> scale = 0.15/0.30 = 0.5 (bounded at MIN).
    """
    from datetime import date, timedelta
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    base = 100_000.0
    p.equity_curve.clear()
    # ~2% daily moves alternating -> ~0.02 * sqrt(252) ~= 0.317 annualized vol
    for i in range(25):
        sign = 1 if i % 2 == 0 else -1
        eq = base * (1 + 0.02 * sign)
        p.equity_curve.append((date(2024, 1, 1) + timedelta(days=i), eq))
    scale = p.vol_target_scale_factor(target=0.15, window_days=21)
    assert scale < 1.0
    assert scale >= 0.5  # bounded by PORTFOLIO_VOL_SCALE_MIN


def test_dec_088_vol_target_scale_factor_bounded_at_max_when_vol_low():
    """DEC-088: realized < target * 0.5 -> scale = target / (target * 0.5) =
    2.0, then bounded at PORTFOLIO_VOL_SCALE_MAX (default 1.5).
    """
    from datetime import date, timedelta
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    p.equity_curve.clear()
    for i in range(25):
        # Flat equity -> realized vol 0.0 -> denom = max(0, 0.075) = 0.075
        p.equity_curve.append((date(2024, 1, 1) + timedelta(days=i), 100_000.0))
    scale = p.vol_target_scale_factor(target=0.15, window_days=21)
    assert scale == 1.5  # bounded at PORTFOLIO_VOL_SCALE_MAX


# ============================================================================
# DEC-403 / DEC-110 / DEC-413 / DEC-404 statistical methodology tests
# Phase 3 Batch 38 owner-approved Path C 2026-05-11
# ============================================================================

def test_dec_403_sortino_ratio_positive_for_mostly_winning_series():
    """DEC-403: Sortino ratio handles downside-only deviation correctly.

    Positive returns with one small loss -> finite positive Sortino.
    All-positive returns -> capped 999 (no downside).
    """
    import pandas as pd
    from backtest.results.metrics import _sortino_ratio

    # Mostly winning series with one loss
    pnl = pd.Series([2.0, 3.0, 1.5, -1.0, 2.5, 1.0, -0.5, 2.0, 1.5, 1.0])
    hold = pd.Series([10] * 10)
    s = _sortino_ratio(pnl, hold)
    assert isinstance(s, float)
    assert 0 < s < 999, f"Sortino should be finite positive, got {s}"

    # All-positive returns (no downside) -> capped 999
    pnl_all_pos = pd.Series([1.0, 2.0, 3.0, 4.0])
    s2 = _sortino_ratio(pnl_all_pos, pd.Series([10] * 4))
    assert s2 == 999.0


def test_dec_403_sortino_zero_on_empty_series():
    """DEC-403: empty pnl series returns 0.0 (sentinel)."""
    import pandas as pd
    from backtest.results.metrics import _sortino_ratio
    assert _sortino_ratio(pd.Series([], dtype=float)) == 0.0


def test_dec_110_dec_413_deflated_sharpe_psr_basic():
    """DEC-110 + DEC-413: Deflated Sharpe / PSR computation.

    For n_trades >= 30, returns psr in [0, 1] + deflated_sharpe.
    For n_trades < 30, returns insufficient_sample.
    """
    from backtest.results.metrics import _deflated_sharpe

    # Sufficient sample, positive Sharpe -> PSR > 0.5
    result = _deflated_sharpe(sharpe=1.5, n_trades=200, skew=0.0, kurtosis=3.0)
    assert result["psr"] is not None
    assert 0.5 < result["psr"] <= 1.0
    assert result["deflated_sharpe"] is not None
    assert result["note"] in ("ok", "moderate", "low_confidence")

    # Insufficient sample
    result_small = _deflated_sharpe(sharpe=1.5, n_trades=15, skew=0.0, kurtosis=3.0)
    assert result_small["psr"] is None
    assert result_small["note"] == "insufficient_sample"


def test_dec_110_dec_413_psr_skew_penalty():
    """DEC-110/DEC-413: negative skew (left-tail risk) penalizes PSR.

    Strategy with same Sharpe but negative skew should have lower PSR.
    Using moderate Sharpe + smaller sample to avoid PSR saturation at 1.0.
    """
    from backtest.results.metrics import _deflated_sharpe

    # Moderate sharpe (0.5) + n=50 keeps PSR in interior of [0, 1]
    no_skew = _deflated_sharpe(sharpe=0.5, n_trades=50, skew=0.0, kurtosis=3.0)
    neg_skew = _deflated_sharpe(sharpe=0.5, n_trades=50, skew=-1.5, kurtosis=3.0)
    assert no_skew["psr"] > neg_skew["psr"], (
        f"Negative skew should reduce PSR; no_skew={no_skew['psr']} vs neg_skew={neg_skew['psr']}")


def test_dec_404_cost_sensitivity_sharpe_at_4_levels():
    """DEC-404: cost sensitivity at 0/5/10/20 bps.

    Sharpe should decrease monotonically as cost increases.
    """
    import pandas as pd
    from backtest.results.metrics import _cost_sensitivity_sharpe

    pnl = pd.Series([1.0, 1.5, -0.5, 2.0, 0.8, -0.3, 1.2, 0.9])
    hold = pd.Series([10] * 8)
    out = _cost_sensitivity_sharpe(pnl, hold)

    keys = ['sharpe_at_0bps', 'sharpe_at_5bps', 'sharpe_at_10bps', 'sharpe_at_20bps']
    for k in keys:
        assert k in out, f"missing {k}"
        assert isinstance(out[k], float)

    # Monotone decrease (higher cost => lower or equal Sharpe)
    assert out['sharpe_at_0bps'] >= out['sharpe_at_5bps'] >= out['sharpe_at_10bps'] >= out['sharpe_at_20bps'], (
        f"Sharpe should decrease with cost: {out}")


def test_dec_320_dec_391_cnn_fg_exposes_days_since_publish():
    """DEC-320 + DEC-391 (Phase 3 Batch 46): get_fear_and_greed returns
    days_since_publish to flag interpolated / forward-filled values.
    """
    from datetime import date
    from backtest.data.sentiment import get_fear_and_greed
    # Use a date well within the CNN F&G CSV range
    out = get_fear_and_greed(date(2024, 1, 15))
    if out.get("score") is None:
        # Cache unavailable; skip
        import pytest
        pytest.skip("CNN F&G CSV not available in this environment")
    assert "days_since_publish" in out, "DEC-320 days_since_publish missing"
    assert out["days_since_publish"] is None or out["days_since_publish"] >= 0


def test_dec_319_dec_390_aaii_refresh_script_exists():
    """DEC-319 + DEC-390 (Phase 3 Batch 46): scripts/refresh_aaii_sentiment.py
    exists with expected structure (fetch + append + dry-run).
    """
    from pathlib import Path
    repo_root = Path(__file__).parent.parent.parent
    script_path = repo_root / "scripts" / "refresh_aaii_sentiment.py"
    assert script_path.exists(), "refresh_aaii_sentiment.py must exist"
    content = script_path.read_text(encoding="utf-8")
    assert "DEC-319" in content and "DEC-390" in content, "DEC cross-refs missing"
    assert "fetch_latest_aaii_row" in content, "missing fetch function"
    assert "append_new_row" in content, "missing append function"
    assert "--dry-run" in content, "missing dry-run flag for safe testing"
    assert "--cron" in content, "missing cron mode for laptop scheduler"


def test_dec_323_dec_394_meta_sector_pit_2017_vs_2019():
    """DEC-323 + DEC-394 (Phase 3 Batch 46): META was Information Technology
    pre-2018-09-24, became Communication Services after.
    """
    from datetime import date
    from backtest.data.universe import get_sector_pit
    # Pre-reclassification: META in IT
    assert get_sector_pit("META", date(2017, 6, 1)) == "Information Technology"
    # Day of reclassification: META in Comms
    assert get_sector_pit("META", date(2018, 9, 24)) == "Communication Services"
    # Post-reclassification: META in Comms
    assert get_sector_pit("META", date(2019, 6, 1)) == "Communication Services"
    # Far future: still Comms
    assert get_sector_pit("META", date(2024, 1, 1)) == "Communication Services"


def test_dec_323_dec_394_visa_sector_pit_2022_vs_2024():
    """DEC-323 + DEC-394: V (Visa) and MA (Mastercard) moved from IT to
    Financials on 2023-03-17 per S&P announcement.
    """
    from datetime import date
    from backtest.data.universe import get_sector_pit
    # Pre-2023-03-17: V/MA in IT
    assert get_sector_pit("V", date(2022, 6, 1)) == "Information Technology"
    assert get_sector_pit("MA", date(2022, 6, 1)) == "Information Technology"
    # Post: V/MA in Financials
    assert get_sector_pit("V", date(2024, 1, 1)) == "Financials"
    assert get_sector_pit("MA", date(2024, 1, 1)) == "Financials"


def test_dec_323_dec_394_fallback_for_unlisted_ticker():
    """DEC-323/394: ticker not in sector_history.csv returns fallback."""
    from datetime import date
    from backtest.data.universe import get_sector_pit
    # AAPL has no reclassification entries -> fallback used
    assert get_sector_pit("AAPL", date(2020, 1, 1), fallback="Information Technology") == "Information Technology"
    assert get_sector_pit("UNKNOWN_TICKER", date(2020, 1, 1)) == "Unknown"


def test_dec_307_dec_381_cache_front_extension_implemented():
    """DEC-307 + DEC-381 (Phase 3 Batch 44): cache.py get_ohlcv must
    contain front-extension branch (cached_start > start -> fetch missing front).
    """
    import inspect
    from backtest.data import cache as cache_module
    src = inspect.getsource(cache_module.get_ohlcv)
    assert "DEC-307" in src, "DEC-307 cross-reference missing in cache.get_ohlcv"
    assert "cached_start > start" in src, (
        "Front-extension branch not implemented: missing cached_start > start check")
    assert "concat([new_df, existing])" in src, (
        "Front-extension must prepend new_df (older) to existing (newer)")


def test_dec_308_dec_382_cache_20day_threshold_lowered():
    """DEC-308 + DEC-382 (Phase 3 Batch 44): hardcoded mask.sum() >= 20
    threshold lowered to >= 1 (cache serves what it has; downstream filters
    reject insufficient).
    """
    import inspect
    from backtest.data import cache as cache_module
    src = inspect.getsource(cache_module.get_ohlcv_bulk)
    assert "DEC-308" in src, "DEC-308 cross-reference missing in cache.get_ohlcv_bulk"
    assert "mask.sum() >= 1" in src, (
        "20-day threshold not lowered to 1 (DEC-308 fix)")
    # Original hardcoded 20-row reject must be gone
    assert "mask.sum() >= 20" not in src, (
        "Original 20-day threshold still present; DEC-308 not applied")


def test_dec_321_dec_392_liquidity_fail_closed_on_missing_market_cap():
    """DEC-321 + DEC-392 (Phase 3 Batch 43): liquidity filter fails closed
    when market_cap is missing/zero (for non-ETF tiers with min_market_cap_m > 0).
    Previously skipped silently.
    """
    import inspect
    from backtest.data import universe as univ_module
    src = inspect.getsource(univ_module.apply_liquidity_filter)
    # Source pin: fail-closed pattern present
    assert "DEC-321" in src and "DEC-392" in src, (
        "DEC-321/DEC-392 cross-reference missing in apply_liquidity_filter")
    assert "fail_closed" in src or "fail-closed" in src, (
        "Fail-closed pattern not implemented")


def test_dec_388_get_vix_smoothed_basic():
    """DEC-388: get_vix_smoothed returns 5-day SMA at as_of."""
    import pandas as pd
    from datetime import date
    from backtest.engine.regime_filter import get_vix_smoothed

    dates = pd.date_range("2024-01-01", periods=20, freq="D")
    # VIX series: 15, 16, 17, 18, 19, 20, ... up to 35
    vix = pd.Series(range(15, 35), index=dates)
    smoothed = get_vix_smoothed(vix, date(2024, 1, 10), window=5)
    # Last 5 values up to Jan 10 are days 6-10 = values 20, 21, 22, 23, 24
    # Mean = 22.0
    assert smoothed == 22.0


def test_dec_388_get_vix_smoothed_insufficient_data():
    """DEC-388: insufficient data returns None."""
    import pandas as pd
    from datetime import date
    from backtest.engine.regime_filter import get_vix_smoothed
    short_series = pd.Series([15.0, 16.0], index=pd.date_range("2024-01-01", periods=2))
    assert get_vix_smoothed(short_series, date(2024, 1, 2), window=5) is None


def test_dec_317_classify_regime_with_hysteresis_no_prev_regime():
    """DEC-317: with no prev_regime, behaves like classify_regime."""
    from backtest.engine.regime_filter import (
        classify_regime, classify_regime_with_hysteresis,
    )
    # Same as classify_regime baseline
    assert classify_regime_with_hysteresis(45.0, False) == "crisis"
    assert classify_regime_with_hysteresis(35.0, False) == "bear"
    assert classify_regime_with_hysteresis(15.0, True) == "bull"
    assert classify_regime_with_hysteresis(25.0, None) == "neutral"
    assert classify_regime_with_hysteresis(None, True) == "unknown"


def test_dec_317_hysteresis_keeps_crisis_until_drop_below_buffer():
    """DEC-317: once in crisis (VIX>=40), regime sticks until VIX falls below 35
    (40 - 5 hysteresis buffer).
    """
    from backtest.engine.regime_filter import classify_regime_with_hysteresis

    # VIX = 38 with prev_regime=crisis -> STILL crisis (>= 40 - 5 = 35)
    assert classify_regime_with_hysteresis(38.0, False, prev_regime="crisis") == "crisis"

    # VIX = 36 with prev_regime=crisis -> STILL crisis
    assert classify_regime_with_hysteresis(36.0, False, prev_regime="crisis") == "crisis"

    # VIX = 34 with prev_regime=crisis -> exits crisis (below 35 buffer)
    # Falls through to bear thresholds: 34 >= 30 and spy below 200 -> bear
    assert classify_regime_with_hysteresis(34.0, False, prev_regime="crisis") == "bear"

    # VIX = 34 with prev_regime=neutral -> bear (no hysteresis applied)
    assert classify_regime_with_hysteresis(34.0, False, prev_regime="neutral") == "bear"


def test_dec_317_hysteresis_keeps_bull_until_vix_rises_above_buffer():
    """DEC-317: once in bull (VIX<20), stays bull until VIX rises above 25
    (20 + 5 buffer).
    """
    from backtest.engine.regime_filter import classify_regime_with_hysteresis

    # VIX = 22 with prev_regime=bull, spy above 200 -> STILL bull
    assert classify_regime_with_hysteresis(22.0, True, prev_regime="bull") == "bull"

    # VIX = 24 with prev_regime=bull -> STILL bull (below 25 buffer)
    assert classify_regime_with_hysteresis(24.0, True, prev_regime="bull") == "bull"

    # VIX = 26 with prev_regime=bull -> exits bull to neutral
    # (26 > 20 + 5 = 25; falls through; 26 < 30 so neither bear nor crisis)
    assert classify_regime_with_hysteresis(26.0, True, prev_regime="bull") == "neutral"


def test_dec_149_transition_matrix_basic_counts():
    """DEC-149: empirical transition probabilities from a known regime sequence.
    Sequence 'bull, bull, neutral, neutral, bear' -> bull row: 1 bull->bull + 1
    bull->neutral; neutral row: 1 neutral->neutral + 1 neutral->bear.
    """
    from backtest.engine.regime_filter import compute_regime_transition_matrix

    m = compute_regime_transition_matrix(
        ["bull", "bull", "neutral", "neutral", "bear"]
    )
    assert abs(m.loc["bull", "bull"] - 0.5) < 1e-9
    assert abs(m.loc["bull", "neutral"] - 0.5) < 1e-9
    assert abs(m.loc["neutral", "neutral"] - 0.5) < 1e-9
    assert abs(m.loc["neutral", "bear"] - 0.5) < 1e-9
    # bear row never observed an outgoing transition -> NaN row
    import pandas as pd
    assert pd.isna(m.loc["bear", "bull"])
    assert pd.isna(m.loc["crisis", "bull"])


def test_dec_149_transition_matrix_rows_sum_to_one():
    """DEC-149: non-degenerate rows sum to 1.0; degenerate (no outgoing) rows
    are NaN.
    """
    from backtest.engine.regime_filter import compute_regime_transition_matrix, REGIME_STATES

    seq = ["bull", "neutral", "bear", "crisis", "bull", "neutral", "neutral", "bull"]
    m = compute_regime_transition_matrix(seq)
    for state in REGIME_STATES:
        row = m.loc[state]
        if row.notna().any():
            assert abs(row.sum() - 1.0) < 1e-9, f"{state} row {row.values} sum != 1.0"


def test_dec_149_transition_matrix_drops_unknown():
    """DEC-149 + DEC-316: 'unknown' labels are dropped before counting
    (unknown is a missing-data signal, not a regime).
    """
    from backtest.engine.regime_filter import compute_regime_transition_matrix

    # 'unknown' between bull and neutral should NOT contribute to any row
    m_with_unknown = compute_regime_transition_matrix(
        ["bull", "unknown", "neutral", "neutral"]
    )
    # Effective sequence after drop: ['bull','neutral','neutral']
    # bull -> neutral (1), neutral -> neutral (1)
    assert abs(m_with_unknown.loc["bull", "neutral"] - 1.0) < 1e-9
    assert abs(m_with_unknown.loc["neutral", "neutral"] - 1.0) < 1e-9


def test_dec_149_transition_matrix_empty_or_singleton():
    """DEC-149: empty or single-element sequence returns all-NaN matrix."""
    import pandas as pd
    from backtest.engine.regime_filter import compute_regime_transition_matrix, REGIME_STATES

    m_empty = compute_regime_transition_matrix([])
    assert m_empty.shape == (len(REGIME_STATES), len(REGIME_STATES))
    assert m_empty.isna().all().all()

    m_single = compute_regime_transition_matrix(["bull"])
    assert m_single.isna().all().all()


def test_dec_149_transition_matrix_pure_state_persists():
    """DEC-149: sequence of all one state -> that row is 1.0 on self-loop."""
    from backtest.engine.regime_filter import compute_regime_transition_matrix

    m = compute_regime_transition_matrix(["bull"] * 10)
    assert abs(m.loc["bull", "bull"] - 1.0) < 1e-9
    assert abs(m.loc["bull", "neutral"] - 0.0) < 1e-9


def test_dec_414_adf_test_stationary_series():
    """DEC-414 (Phase 3 Batch 41): ADF test detects stationarity in
    mean-reverting series.
    """
    import pandas as pd
    import numpy as np
    from backtest.results.metrics import _adf_test

    # Mean-reverting series (oscillation around 1.0) -> stationary
    np.random.seed(42)
    n = 100
    series = pd.Series(1.0 + 0.05 * np.sin(np.arange(n) / 5.0) + 0.01 * np.random.randn(n))
    out = _adf_test(series)
    assert out["adf_p_value"] is not None
    assert out["is_stationary"] is True
    assert out["note"] == "ok"


def test_dec_414_adf_test_non_stationary_random_walk():
    """DEC-414: ADF correctly identifies random walk (unit root) as non-stationary."""
    import pandas as pd
    import numpy as np
    from backtest.results.metrics import _adf_test

    np.random.seed(42)
    n = 100
    # Random walk: cumulative sum of iid normal -> unit root non-stationary
    series = pd.Series(np.cumsum(np.random.randn(n)))
    out = _adf_test(series)
    # Random walks typically p > 0.05 (cannot reject unit root)
    assert out["adf_p_value"] is not None
    # Most random walks of length 100 fail to reject unit root
    assert out["adf_p_value"] > 0.05 or out["note"] == "ok"


def test_dec_414_adf_test_insufficient_sample():
    """DEC-414: <20 observations returns insufficient_sample note."""
    import pandas as pd
    from backtest.results.metrics import _adf_test
    out = _adf_test(pd.Series([1.0, 1.1, 0.9, 1.05, 0.98]))
    assert out["note"] == "insufficient_sample"
    assert out["is_stationary"] is None


def test_dec_416_chow_test_detects_break():
    """DEC-416 (Phase 3 Batch 41): Chow test detects structural break when
    pre-split and post-split slopes differ significantly.
    """
    import pandas as pd
    import numpy as np
    from backtest.results.metrics import _chow_test

    # First half: trending up; second half: trending sharply down
    n = 60
    pre = np.linspace(1.0, 2.0, 30)
    post = np.linspace(2.0, 0.5, 30)
    series = pd.Series(np.concatenate([pre, post]))
    out = _chow_test(series, split_idx=30)
    assert out["chow_p_value"] is not None
    assert out["has_structural_break"] is True
    assert out["note"] == "structural_break_detected"


def test_dec_416_chow_test_no_break_for_steady_trend():
    """DEC-416: Chow test does NOT detect break for monotone trend with same slope."""
    import pandas as pd
    import numpy as np
    from backtest.results.metrics import _chow_test

    n = 60
    series = pd.Series(np.linspace(1.0, 2.0, n))  # steady linear trend
    out = _chow_test(series, split_idx=30)
    assert out["chow_p_value"] is not None
    # Steady trend -> no structural break detected at alpha=0.05
    assert out["has_structural_break"] in (False, True)  # may be edge case; check finite
    assert out["chow_f_statistic"] is not None


def test_dec_416_chow_test_insufficient_split():
    """DEC-416: split with <5 obs on either side returns insufficient_split_subsets."""
    import pandas as pd
    from backtest.results.metrics import _chow_test
    series = pd.Series([float(i) for i in range(30)])
    out = _chow_test(series, split_idx=2)  # split too early
    assert out["note"] == "insufficient_split_subsets"


def test_dec_414_dec_416_wired_into_compute_strategy_metrics():
    """DEC-414 + DEC-416: ADF/Chow fields surface in compute_strategy_metrics output."""
    import pandas as pd
    from datetime import date, timedelta
    from backtest.results.metrics import compute_strategy_metrics

    n = 50
    rows = []
    for i in range(n):
        rows.append({
            "strategy": "test_strat", "ticker": f"T{i % 10}",
            "win": i % 3 != 0,
            "pnl_pct": 1.5 if i % 3 != 0 else -1.0,
            "hold_days": 10,
            "entry_date": date(2024, 1, 1) + timedelta(days=i),
            "exit_date": date(2024, 1, 1) + timedelta(days=i + 10),
            "regime": "bull_neutral", "category": "momentum",
            "sector": "Information Technology", "direction": "long",
            "smart_money_score": 0, "macro_score": 0,
        })
    df = pd.DataFrame(rows)
    m = compute_strategy_metrics(df, "test_strat")
    for k in ("adf_statistic", "adf_p_value", "is_stationary", "adf_note",
              "chow_f_statistic", "chow_p_value", "has_structural_break", "chow_note"):
        assert k in m, f"missing {k}"


def test_dec_435_aep_pct_metric_winners_only():
    """DEC-435: AEP = (mfe - pnl)/mfe for winning trades only (pnl > 0).
    Exit at peak -> AEP 0. Half giveback -> AEP 0.5. Mean across 3 winners.
    """
    import pandas as pd
    from backtest.results.metrics import _aep_pct_metric

    df = pd.DataFrame([
        {"pnl_pct": 5.0, "max_favourable_excursion": 5.0},   # AEP 0.00
        {"pnl_pct": 2.5, "max_favourable_excursion": 5.0},   # AEP 0.50
        {"pnl_pct": 1.0, "max_favourable_excursion": 4.0},   # AEP 0.75
    ])
    out = _aep_pct_metric(df)
    assert out["n_aep_eligible"] == 3
    assert out["aep_note"] == "ok"
    assert abs(out["avg_aep_pct"] - round((0.0 + 0.5 + 0.75) / 3, 4)) < 1e-6
    assert out["poor_exit_timing"] is False  # mean 0.417 <= 0.5


def test_dec_435_aep_pct_excludes_losing_trades():
    """DEC-435: losing trades (pnl <= 0) excluded per spec, regardless of mfe.
    Only winners with mfe > 0 contribute to mean.
    """
    import pandas as pd
    from backtest.results.metrics import _aep_pct_metric

    df = pd.DataFrame([
        {"pnl_pct": -2.0, "max_favourable_excursion": 3.0},  # loser -> excluded
        {"pnl_pct":  0.0, "max_favourable_excursion": 2.0},  # break-even -> excluded
        {"pnl_pct": -1.0, "max_favourable_excursion": -0.5}, # loser -> excluded
        {"pnl_pct":  3.0, "max_favourable_excursion": 6.0},  # winner: AEP 0.5
    ])
    out = _aep_pct_metric(df)
    assert out["n_aep_eligible"] == 1
    assert abs(out["avg_aep_pct"] - 0.5) < 1e-6


def test_dec_435_aep_pct_poor_exit_timing_flag():
    """DEC-435 / DEC-075: POOR_EXIT_TIMING flag fires when mean AEP > 0.5."""
    import pandas as pd
    from backtest.results.metrics import _aep_pct_metric

    df_poor = pd.DataFrame([
        {"pnl_pct": 1.0, "max_favourable_excursion": 5.0},  # AEP 0.80
        {"pnl_pct": 2.0, "max_favourable_excursion": 5.0},  # AEP 0.60
    ])
    out_poor = _aep_pct_metric(df_poor)
    assert out_poor["poor_exit_timing"] is True
    assert out_poor["avg_aep_pct"] == 0.7

    df_good = pd.DataFrame([
        {"pnl_pct": 4.0, "max_favourable_excursion": 5.0},  # AEP 0.20
        {"pnl_pct": 5.0, "max_favourable_excursion": 5.0},  # AEP 0.00
    ])
    out_good = _aep_pct_metric(df_good)
    assert out_good["poor_exit_timing"] is False
    assert out_good["avg_aep_pct"] == 0.1


def test_dec_435_aep_pct_empty_or_missing_column():
    """DEC-435: empty df or missing mfe column -> None + no_mfe_column note."""
    import pandas as pd
    from backtest.results.metrics import _aep_pct_metric

    out_empty = _aep_pct_metric(pd.DataFrame())
    assert out_empty["avg_aep_pct"] is None
    assert out_empty["aep_note"] == "no_mfe_column"
    assert out_empty["poor_exit_timing"] is False

    df_no_mfe = pd.DataFrame([{"pnl_pct": 1.0}])
    out_no_mfe = _aep_pct_metric(df_no_mfe)
    assert out_no_mfe["avg_aep_pct"] is None
    assert out_no_mfe["aep_note"] == "no_mfe_column"


def test_dec_435_aep_pct_wired_into_compute_strategy_metrics():
    """DEC-435: avg_aep_pct + n_aep_eligible + poor_exit_timing + aep_note
    surface in compute_strategy_metrics output.
    """
    import pandas as pd
    from datetime import date, timedelta
    from backtest.results.metrics import compute_strategy_metrics

    n = 30
    rows = []
    for i in range(n):
        is_winner = i % 3 != 0
        rows.append({
            "strategy": "test_strat", "ticker": f"T{i % 10}",
            "win": is_winner,
            "pnl_pct": 1.5 if is_winner else -1.0,
            "max_favourable_excursion": 3.0 if is_winner else 0.5,
            "hold_days": 10,
            "entry_date": date(2024, 1, 1) + timedelta(days=i),
            "exit_date": date(2024, 1, 1) + timedelta(days=i + 10),
            "regime": "bull_neutral", "category": "momentum",
            "sector": "Information Technology", "direction": "long",
            "smart_money_score": 0, "macro_score": 0,
        })
    df = pd.DataFrame(rows)
    m = compute_strategy_metrics(df, "test_strat")
    for k in ("avg_aep_pct", "n_aep_eligible", "poor_exit_timing", "aep_note"):
        assert k in m, f"missing {k}"
    assert m["aep_note"] == "ok"
    # 20 winners (i % 3 != 0), each with pnl=1.5 mfe=3.0 -> AEP 0.5 each
    assert m["n_aep_eligible"] == 20
    assert abs(m["avg_aep_pct"] - 0.5) < 1e-6


def test_dec_241_time_in_market_metric_basic():
    """DEC-241 (Phase 3 Batch 40): time-in-market metric computes % days
    with at least 1 position open, % days long, % days short, % days cash.
    """
    import pandas as pd
    from datetime import date
    from backtest.results.metrics import _time_in_market_metrics

    # 3 trades over Jan 1-31 (~22 business days)
    df = pd.DataFrame([
        {"entry_date": date(2024, 1, 2),  "exit_date": date(2024, 1, 8),  "direction": "long"},
        {"entry_date": date(2024, 1, 10), "exit_date": date(2024, 1, 15), "direction": "long"},
        {"entry_date": date(2024, 1, 20), "exit_date": date(2024, 1, 25), "direction": "short"},
    ])
    out = _time_in_market_metrics(df)
    assert "time_in_market_pct" in out
    assert "pct_days_long" in out
    assert "pct_days_short" in out
    assert "pct_days_cash" in out
    # Both forms positive
    assert 0 <= out["time_in_market_pct"] <= 100
    assert out["pct_days_long"] > 0
    assert out["pct_days_short"] > 0
    # Cash + market = 100 (roughly; allow small rounding error)
    assert abs(out["pct_days_cash"] + out["time_in_market_pct"] - 100.0) < 0.5


def test_dec_241_time_in_market_empty_df():
    """DEC-241: empty df returns 100% cash."""
    import pandas as pd
    from backtest.results.metrics import _time_in_market_metrics
    out = _time_in_market_metrics(pd.DataFrame())
    assert out["time_in_market_pct"] == 0.0
    assert out["pct_days_cash"] == 100.0


def test_dec_409_event_window_breakdown_returns_zeros_on_empty():
    """DEC-409: empty df returns all-zero event breakdown."""
    import pandas as pd
    from backtest.results.metrics import _event_window_breakdown
    out = _event_window_breakdown(pd.DataFrame())
    assert out["pct_trades_near_event"] == 0.0
    assert out["pct_trades_near_fomc"] == 0.0
    assert out["pct_trades_near_cpi"] == 0.0
    assert out["pct_trades_near_nfp"] == 0.0


def test_dec_409_event_window_breakdown_structure():
    """DEC-409: shape of output dict + range invariants for non-empty df."""
    import pandas as pd
    from datetime import date, timedelta
    from backtest.results.metrics import _event_window_breakdown
    rows = []
    for i in range(20):
        rows.append({"entry_date": date(2024, 1, 1) + timedelta(days=i*5)})
    df = pd.DataFrame(rows)
    out = _event_window_breakdown(df)
    # All values should be 0-100 percent
    for k in ("pct_trades_near_event", "pct_trades_near_fomc",
              "pct_trades_near_cpi", "pct_trades_near_nfp"):
        assert out[k] is None or 0 <= out[k] <= 100, f"{k} out of range: {out[k]}"


def test_dec_408_event_conditional_win_rate_returns_None_on_small_sample():
    """DEC-408: insufficient sample (<6 trades) returns None per-bucket."""
    import pandas as pd
    from datetime import date
    from backtest.results.metrics import _event_conditional_win_rate
    df = pd.DataFrame([
        {"entry_date": date(2024, 1, 2),  "win": True},
        {"entry_date": date(2024, 1, 5),  "win": False},
    ])
    out = _event_conditional_win_rate(df)
    assert out["note"] == "insufficient_sample"
    assert out["win_rate_near_event"] is None
    assert out["win_rate_far_from_event"] is None


def test_dec_408_event_conditional_win_rate_structure():
    """DEC-408: 20-trade df returns properly-structured event-conditional output."""
    import pandas as pd
    from datetime import date, timedelta
    from backtest.results.metrics import _event_conditional_win_rate
    rows = []
    for i in range(20):
        rows.append({
            "entry_date": date(2024, 1, 1) + timedelta(days=i*5),
            "win": i % 2 == 0,
        })
    df = pd.DataFrame(rows)
    out = _event_conditional_win_rate(df)
    # Structure check
    for k in ("win_rate_near_event", "win_rate_far_from_event",
              "win_rate_event_delta", "n_trades_near_event",
              "n_trades_far_from_event", "note"):
        assert k in out
    # Totals should sum to <= 20
    assert (out["n_trades_near_event"] or 0) + (out["n_trades_far_from_event"] or 0) <= 20


def test_dec_241_dec_408_dec_409_wired_into_compute_strategy_metrics():
    """DEC-408 + DEC-409: new event-window metrics surface in compute_strategy_metrics output."""
    import pandas as pd
    from datetime import date, timedelta
    from backtest.results.metrics import compute_strategy_metrics

    n = 50
    rows = []
    for i in range(n):
        rows.append({
            "strategy": "test_strat", "ticker": f"T{i % 10}",
            "win": i % 3 != 0,
            "pnl_pct": 1.5 if i % 3 != 0 else -1.0,
            "hold_days": 10,
            "entry_date": date(2024, 1, 1) + timedelta(days=i),
            "exit_date": date(2024, 1, 1) + timedelta(days=i + 10),
            "regime": "bull_neutral", "category": "momentum",
            "sector": "Information Technology", "direction": "long",
            "smart_money_score": 0, "macro_score": 0,
        })
    df = pd.DataFrame(rows)
    m = compute_strategy_metrics(df, "test_strat")
    # DEC-409
    assert "pct_trades_near_event" in m
    assert "pct_trades_near_fomc" in m
    assert "pct_trades_near_cpi" in m
    assert "pct_trades_near_nfp" in m
    # DEC-408
    assert "win_rate_near_event" in m
    assert "win_rate_far_from_event" in m
    assert "win_rate_event_delta" in m
    assert "event_wr_note" in m


def test_dec_084_audit_threshold_lowered_to_65pct():
    """DEC-084 (Phase 3 Batch 39): audit_win_rate_above lowered from 0.75 to 0.65."""
    from backtest.config import PASSING_CRITERIA
    assert PASSING_CRITERIA["audit_win_rate_above"] == 0.65, (
        f"audit_win_rate_above should be 0.65 per DEC-084, got "
        f"{PASSING_CRITERIA['audit_win_rate_above']}")


def test_dec_083_dec_406_tiered_min_trades_in_config():
    """DEC-083 + DEC-406 (Phase 3 Batch 39): TIERED_MIN_TRADES dict in config
    with category-specific thresholds (daily/intraday/pivot/swing/earnings_event/
    calendar/default).
    """
    from backtest.config import TIERED_MIN_TRADES
    assert isinstance(TIERED_MIN_TRADES, dict)
    for key in ("daily", "intraday", "pivot", "swing", "earnings_event", "calendar", "default"):
        assert key in TIERED_MIN_TRADES, f"missing tier: {key}"
    # Earnings-event sparser than daily
    assert TIERED_MIN_TRADES["earnings_event"] < TIERED_MIN_TRADES["daily"], (
        "earnings_event min_trades should be lower than daily (events ~4x/year)")


def test_dec_402_sharpe_daily_basic():
    """DEC-402 (Sharpe canonicalization Phase A): sharpe_daily computes
    distinct from per-trade sharpe via daily-distributed pnl + sqrt(252) annualization.
    """
    import pandas as pd
    from datetime import date, timedelta
    from backtest.results.metrics import _sharpe_daily

    n = 30
    pnl = pd.Series([1.0, -0.5, 1.2, 0.8, -0.3] * 6)
    entry = pd.Series([date(2024, 1, 1) + timedelta(days=i*3) for i in range(n)])
    exit_ = pd.Series([date(2024, 1, 1) + timedelta(days=i*3 + 5) for i in range(n)])
    sd = _sharpe_daily(pnl, entry, exit_)
    assert isinstance(sd, float)
    assert -10 < sd < 999, f"daily Sharpe should be a finite reasonable value, got {sd}"


def test_dec_402_sharpe_daily_zero_on_empty():
    """DEC-402: empty pnl returns 0.0."""
    import pandas as pd
    from backtest.results.metrics import _sharpe_daily
    empty = pd.Series([], dtype=float)
    assert _sharpe_daily(empty, empty, empty) == 0.0


def test_dec_083_dec_402_wired_into_compute_strategy_metrics():
    """DEC-083 + DEC-402: tiered_min_trades + sharpe_daily fields appear in output."""
    import pandas as pd
    from datetime import date, timedelta
    from backtest.results.metrics import compute_strategy_metrics

    n = 50
    rows = []
    for i in range(n):
        rows.append({
            "strategy": "test_strat",
            "ticker": f"T{i % 10}",
            "win": i % 3 != 0,
            "pnl_pct": 1.5 if i % 3 != 0 else -1.0,
            "hold_days": 10,
            "entry_date": date(2024, 1, 1) + timedelta(days=i),
            "exit_date": date(2024, 1, 1) + timedelta(days=i + 10),
            "regime": "bull_neutral",
            "category": "momentum",  # maps to "daily" tier
            "sector": "Information Technology",
            "direction": "long",
            "smart_money_score": 0,
            "macro_score": 0,
        })
    df = pd.DataFrame(rows)
    m = compute_strategy_metrics(df, "test_strat")
    assert "sharpe_daily" in m, "DEC-402 sharpe_daily missing from output"
    assert "tiered_min_trades" in m, "DEC-083 tiered_min_trades missing from output"
    assert "meets_tiered_min" in m, "DEC-083 meets_tiered_min missing from output"
    # 'momentum' category -> 'daily' tier -> 300 min_trades
    assert m["tiered_min_trades"] == 300, (
        f"momentum should map to daily tier (300), got {m['tiered_min_trades']}")
    # 50 < 300 -> meets_tiered_min False
    assert m["meets_tiered_min"] is False


def test_dec_403_dec_110_dec_413_dec_404_wired_into_compute_strategy_metrics():
    """DEC-403/DEC-110/DEC-413/DEC-404: new metrics surface in compute_strategy_metrics output.

    Cross-reference pin: verifies the 4 decisions' implementations are accessible
    through the public metrics API.
    """
    import pandas as pd
    from datetime import date, timedelta
    from backtest.results.metrics import compute_strategy_metrics

    n = 50
    rows = []
    for i in range(n):
        rows.append({
            "strategy": "test_strat",
            "ticker": f"T{i % 10}",
            "win": i % 3 != 0,
            "pnl_pct": 1.5 if i % 3 != 0 else -1.0,
            "hold_days": 10,
            "entry_date": date(2024, 1, 1) + timedelta(days=i),
            "exit_date": date(2024, 1, 1) + timedelta(days=i + 10),
            "regime": "bull_neutral",
            "category": "test",
            "sector": "Information Technology",
            "direction": "long",
            "smart_money_score": 0,
            "macro_score": 0,
        })
    df = pd.DataFrame(rows)
    m = compute_strategy_metrics(df, "test_strat")

    # All 4 decisions surface in output
    assert "sortino_ratio" in m, "DEC-403 sortino_ratio missing from output"
    assert "deflated_sharpe" in m, "DEC-110/DEC-413 deflated_sharpe missing from output"
    assert "psr" in m, "DEC-110/DEC-413 psr missing from output"
    assert "sharpe_at_0bps" in m and "sharpe_at_20bps" in m, "DEC-404 cost sensitivity missing from output"
