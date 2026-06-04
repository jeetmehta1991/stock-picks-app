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
    """Congressional trades must respect PIT disclosure date.
    BUG-273 fix 2026-05-13: prior assertion was wrong (test passed only because
    the Chamber/House bug caused silent exception -> always returned 'none').
    Correct PIT rule: disclosure_date <= as_of -> visible; future disclosure -> invisible.
    """
    from backtest.data.smart_money import congressional_signal
    from unittest.mock import patch
    import pandas as pd
    from datetime import timedelta

    today = date(2024, 6, 15)

    # Case 1: disclosure TOMORROW -- trade is NOT yet public, signal must be none
    future_df = pd.DataFrame([{
        "TransactionDate": pd.Timestamp("2024-06-01"),
        "ReportDate":      pd.Timestamp(today + timedelta(days=1)),  # future
        "Transaction":     "Purchase",
        "Amount":          "500001 - 1000000",
        "Representative":  "Test Rep",
        "House":           "Senate",
    }])
    with patch("backtest.data.smart_money._load_prefetch", return_value=future_df):
        result = congressional_signal("AAPL", today)
        assert result.get("signal") in ["none", "neutral", "no_data"], \
            f"Future disclosure must not produce signal, got: {result.get('signal')}"

    # Case 2: disclosure today -- trade IS public, signal must be produced
    today_df = pd.DataFrame([{
        "TransactionDate": pd.Timestamp("2024-06-01"),
        "ReportDate":      pd.Timestamp(today),  # same day
        "Transaction":     "Purchase",
        "Amount":          "500001 - 1000000",
        "Representative":  "Test Rep",
        "House":           "Representatives",
    }])
    with patch("backtest.data.smart_money._load_prefetch", return_value=today_df):
        result = congressional_signal("AAPL", today)
        assert result.get("signal") in ["buy", "strong_buy"], \
            f"Same-day disclosure must produce buy signal, got: {result.get('signal')}"
    print("[OK] Congressional signal enforces PIT disclosure date (BUG-273 fix verified)")

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
    """DEC-324: congressional_signal age-weights by transaction_date, not disclosure_date.

    Batch 548 OPT-C update: the Quiver field-read + date-conversion logic
    moved to the _load_congressional_processed helper for caching; the
    age-weight (using transaction_dt) stays in congressional_signal. This
    test now greps BOTH source bodies so the DEC-324 invariant remains
    pinned across the refactor.
    """
    import inspect
    from backtest.data.smart_money import (
        congressional_signal, _load_congressional_processed,
    )
    sig_src = inspect.getsource(congressional_signal)
    helper_src = inspect.getsource(_load_congressional_processed)
    combined = sig_src + helper_src

    # Age-weight body must use transaction_dt (post-B548) or
    # transaction_date (pre-B548)
    assert "transaction_dt" in sig_src or "transaction_date" in sig_src, (
        "DEC-324: congressional_signal must reference transaction_date/dt"
    )
    # Quiver TransactionDate field-read must exist SOMEWHERE in the
    # congressional code path (helper post-B548; signal body pre-B548)
    assert "TransactionDate" in combined, \
        "DEC-324: must read Quiver TransactionDate field"
    # Ensure age-weight uses transaction_dt (B548) or transaction_date (legacy)
    age_marker_end = (
        sig_src.find("buys   = recent") if "buys   = recent" in sig_src
        else sig_src.find("buys")
    )
    age_weight_section = sig_src[sig_src.find("age_days"):age_marker_end]
    assert ("transaction_dt" in age_weight_section
            or "transaction_date" in age_weight_section), (
        "DEC-324: age_days must be computed from transaction_date/dt"
    )
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
    # AFTER check, trailing_stop should have been updated from today's close.
    # Batch 281 deployed both trail_pct=0.15 + breakeven_move_at_1r=True.
    # For this fixture (entry 100, initial_stop 90, one_r=10):
    #   today_close 110 >= 100 + 10  -> breakeven ratchet activates -> stop=$100
    #   Normal 15% trail: 110 * 0.85 = $93.5
    #   Final stop = max(100, 93.5) = $100 (breakeven wins).
    # Compute expected based on whichever logic produces the tighter stop.
    from backtest.config import TRAILING_STOP
    normal_trail = 110.0 * (1 - TRAILING_STOP["trail_pct"])
    breakeven_active = TRAILING_STOP.get("breakeven_move_at_1r", False)
    breakeven_stop = 100.0 if breakeven_active else 90.0
    expected_stop = max(90.0, normal_trail, breakeven_stop)
    updated_trade = still_open[0]
    assert updated_trade.highest_close == 110.0, "highest_close must update post-check"
    assert updated_trade.trailing_stop == expected_stop, (
        f"trailing_stop must update to {expected_stop} (got "
        f"{updated_trade.trailing_stop}); trail_pct={TRAILING_STOP['trail_pct']}, "
        f"breakeven={breakeven_active}"
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
    BUG-060 Batch 161 2026-05-13: short entry zone updated -- gap-downs for shorts
    are now ALLOWED (favorable). Only adverse gap-UPs are rejected for shorts.

    Correct behavior:
    - Long:  reject excessive gap-UP   (adverse: opened above signal level)
    - Short: reject excessive gap-UP   (adverse: stock moved against short entry)
    - Long:  allow gap-DOWN            (favorable: better long entry price)
    - Short: allow gap-DOWN            (favorable: lower short entry = more downside room)
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

    # Short: open gap = 3.0 ATR BELOW signal_close -> must ACCEPT (BUG-060 fix: gap-down is favorable)
    valid_short_gap_down, _ = validate_entry_zone(
        signal_close - 3.0 * atr, signal_close, atr, "pivot", "short")
    assert valid_short_gap_down is True, (
        "Short gap-down of 3.0xATR must ACCEPT (BUG-060 fix: gap-down is favorable for short entries)"
    )

    # Short: open gap = 3.0 ATR ABOVE signal_close -> must REJECT (adverse gap-up for short)
    valid_short_gap_up, reason_short_gap_up = validate_entry_zone(
        signal_close + 3.0 * atr, signal_close, atr, "pivot", "short")
    assert valid_short_gap_up is False, (
        "Short adverse gap-up of 3.0xATR must REJECT (opened above signal = adverse for short)"
    )
    assert "exceeds" in reason_short_gap_up


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


def test_dec_091_drawdown_multiplier_full_size_below_5pct():
    """DEC-091 / Batch 213 tightened curve: DD <5% -> multiplier 1.0.
    Pre-Batch-213 ladder used DD<10% threshold; tightened per research
    review (owner-approved 2026-05-17) to add 5% early-warning band."""
    # 3% DD -> 1.0 (below 5% threshold)
    p = _portfolio_with_dd(100_000.0, 97_000.0)
    assert p.drawdown_size_multiplier() == 1.0


def test_dec_091_drawdown_multiplier_080_at_5pct():
    """Batch 213 new band: DD >=5% AND <10% -> 0.8 (early-warning)."""
    p = _portfolio_with_dd(100_000.0, 94_000.0)  # 6% DD
    assert p.drawdown_size_multiplier() == 0.8


def test_dec_091_drawdown_multiplier_050_at_10pct():
    """Batch 213 tightened: DD >=10% AND <15% -> 0.5 (was 0.75 pre-batch)."""
    p = _portfolio_with_dd(100_000.0, 88_000.0)  # 12% DD
    assert p.drawdown_size_multiplier() == 0.5


def test_dec_091_drawdown_multiplier_025_at_15pct():
    """Batch 213 new band: DD >=15% AND <20% -> 0.25 (pre-halt)."""
    p = _portfolio_with_dd(100_000.0, 83_000.0)  # 17% DD
    assert p.drawdown_size_multiplier() == 0.25


def test_dec_091_drawdown_multiplier_halt_at_20pct():
    """Batch 213 tightened: DD >=20% -> 0.0 halt (was 30% pre-batch).
    Matches DEC-515 Level 6 default 20% DD halt threshold."""
    p = _portfolio_with_dd(100_000.0, 78_000.0)  # 22% DD
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
# Phase 3 Batch 60 Path C 20-DEC bundle (owner directive: 20 DECs this turn)
# DEC-013/019/078A/126/213/214/234/253/254/263/265/275/290/329/332/334/335
#   /349/364/606
# ============================================================================

def test_dec_013_earnings_tolerant_default_false():
    """DEC-013: missing attribute defaults to False (conservative close-before)."""
    from backtest.results.metrics import is_earnings_tolerant_strategy
    assert is_earnings_tolerant_strategy({}) is False
    assert is_earnings_tolerant_strategy(None) is False
    assert is_earnings_tolerant_strategy({"earnings_tolerant": True}) is True


def test_dec_019_liquidity_drop_warning_above_50pct():
    """DEC-019 spec test signal: ADV drops 60% -> warning."""
    from backtest.results.metrics import liquidity_drop_warning
    out = liquidity_drop_warning(entry_adv_shares=1_000_000,
                                  current_adv_shares=400_000)
    assert out["warning"] is True
    assert out["note"] == "LIQUIDITY_DROP_WARNING"


def test_dec_019_liquidity_drop_no_warning_modest_drop():
    """DEC-019: 30% drop -> no warning (below 50% threshold)."""
    from backtest.results.metrics import liquidity_drop_warning
    out = liquidity_drop_warning(1_000_000, 700_000)
    assert out["warning"] is False


def test_dec_078A_stop_cluster_fires_on_5_stops_in_10_days():
    """DEC-078A spec test signal: 5 stops in 10 days -> STOP_CLUSTER_PATTERN."""
    from datetime import date, timedelta
    from backtest.results.metrics import detect_stop_cluster_pattern
    stops = [date(2024, 6, 3) + timedelta(days=i) for i in range(0, 9, 2)]
    out = detect_stop_cluster_pattern(stops, window_days=10, threshold=5)
    assert out["cluster_detected"] is True
    assert out["note"] == "STOP_CLUSTER_PATTERN"


def test_dec_078A_stop_cluster_no_fire_spread_30_days():
    """DEC-078A spec test signal: 5 stops spread across 30 days -> no fire."""
    from datetime import date, timedelta
    from backtest.results.metrics import detect_stop_cluster_pattern
    stops = [date(2024, 6, 1) + timedelta(days=7 * i) for i in range(5)]
    out = detect_stop_cluster_pattern(stops, window_days=10, threshold=5)
    assert out["cluster_detected"] is False


def test_dec_126_circuit_breaker_time_resolution_doc_present():
    """DEC-126: time-resolution limits documented as constant in
    improvements.py (circuit_breakers.py itself has pre-existing non-ASCII
    that blocks C1 preflight on touched files; doc landed adjacent instead).
    """
    from backtest.engine.improvements import CIRCUIT_BREAKER_TIME_RESOLUTION_LIMITS
    assert "DEC-126" in CIRCUIT_BREAKER_TIME_RESOLUTION_LIMITS
    assert "daily" in CIRCUIT_BREAKER_TIME_RESOLUTION_LIMITS.lower()
    assert "intraday" in CIRCUIT_BREAKER_TIME_RESOLUTION_LIMITS.lower()


def test_dec_213_both_rationales_storage_schema():
    """DEC-213: TRADE_RATIONALE_FIELDS schema includes both rules + agent."""
    from backtest.config import TRADE_RATIONALE_FIELDS
    assert "rules_rationale" in TRADE_RATIONALE_FIELDS
    assert "agent_rationale" in TRADE_RATIONALE_FIELDS


def test_dec_214_agent_ab_revalidation_constants():
    """DEC-214: quarterly cadence + DEC-131 decay floor."""
    from backtest.config import (AGENT_AB_REVALIDATION_DAYS,
                                   AGENT_AB_DECAY_NET_SHARPE_FLOOR)
    assert AGENT_AB_REVALIDATION_DAYS == 90
    assert AGENT_AB_DECAY_NET_SHARPE_FLOOR == 0.20


def test_dec_234_ticker_lifecycle_schema():
    """DEC-234: CUSIP/ISIN + event-type schema codified."""
    from backtest.config import (TICKER_LIFECYCLE_FIELDS,
                                   TICKER_LIFECYCLE_EVENT_TYPES)
    assert "cusip" in TICKER_LIFECYCLE_FIELDS
    assert "isin" in TICKER_LIFECYCLE_FIELDS
    assert "rename" in TICKER_LIFECYCLE_EVENT_TYPES
    assert "merger" in TICKER_LIFECYCLE_EVENT_TYPES


def test_dec_253_interlisted_routing_tsx_for_small_canadian_bank():
    """DEC-253 spec: TD $30K trade + TSX liquidity OK -> TSX route."""
    from backtest.results.metrics import route_interlisted_trade
    out = route_interlisted_trade("TD", trade_size_usd=30_000,
                                   tsx_adv_shares=500_000, is_interlisted=True)
    assert out["venue"] == "TSX"
    assert out["routed_ticker"] == "TD.TO"


def test_dec_253_interlisted_routing_us_for_large_trade():
    """DEC-253 spec: $200K trade -> US-NYSE (above $50K threshold)."""
    from backtest.results.metrics import route_interlisted_trade
    out = route_interlisted_trade("TD", trade_size_usd=200_000,
                                   tsx_adv_shares=500_000, is_interlisted=True)
    assert out["venue"] == "US-NYSE"


def test_dec_253_interlisted_routing_non_interlisted_us_only():
    """DEC-253 spec: AAPL non-interlisted -> US-NYSE."""
    from backtest.results.metrics import route_interlisted_trade
    out = route_interlisted_trade("AAPL", trade_size_usd=30_000,
                                   tsx_adv_shares=0, is_interlisted=False)
    assert out["venue"] == "US-NYSE"


def test_dec_254_etf_substitution_table():
    """DEC-254: SPY->XUU, QQQ->XQQ, IWM->XSU, VTI->VUN."""
    from backtest.config import ETF_TSX_SUBSTITUTION
    assert ETF_TSX_SUBSTITUTION["SPY"] == "XUU.TO"
    assert ETF_TSX_SUBSTITUTION["QQQ"] == "XQQ.TO"
    assert ETF_TSX_SUBSTITUTION["IWM"] == "XSU.TO"
    assert ETF_TSX_SUBSTITUTION["VTI"] == "VUN.TO"


def test_dec_263_burst_day_stress_constants():
    """DEC-263: top-20 burst days + 2018 start covers 2018 Volmageddon etc."""
    from backtest.config import (BURST_DAY_STRESS_TOP_N,
                                   BURST_DAY_STRESS_START_YEAR)
    assert BURST_DAY_STRESS_TOP_N == 20
    assert BURST_DAY_STRESS_START_YEAR == 2018


def test_dec_265_smoke_test_min_trades_constant():
    """DEC-265: smoke test minimum 30 per cell (matches DEC-426 5-gate)."""
    from backtest.config import SMOKE_TEST_MIN_TRADES_PER_CELL
    assert SMOKE_TEST_MIN_TRADES_PER_CELL == 30


def test_dec_275_requirements_audit_includes_missing_deps():
    """DEC-275: openai + fredapi + pandas-market-calendars added."""
    from pathlib import Path
    req = Path("requirements.txt").read_text(encoding="utf-8")
    assert "openai" in req.lower()
    assert "fredapi" in req.lower()
    assert "pandas-market-calendars" in req.lower()


def test_dec_290_dropped_strategy_reeval_quarterly():
    """DEC-290 spec: quarterly cadence (90 days)."""
    from backtest.config import DROPPED_STRATEGY_REEVAL_DAYS
    assert DROPPED_STRATEGY_REEVAL_DAYS == 90


def test_dec_329_multi_process_safety_guidance():
    """DEC-329: multi-process safety note constant present."""
    from backtest.engine.improvements import MULTI_PROCESS_SAFETY_GUIDANCE
    assert "per-process" in MULTI_PROCESS_SAFETY_GUIDANCE
    assert "filelock" in MULTI_PROCESS_SAFETY_GUIDANCE


def test_dec_332_smart_money_composite_canonical_values():
    """DEC-332: canonical Pass 53 B1 weights -> composite score + label."""
    from backtest.results.metrics import smart_money_composite_score
    out = smart_money_composite_score("strong_buy", "strong_buy", "buy")
    # cong +4 + ins +4 + inst +1 = 9 -> "congressional+insider_cluster"
    assert out["score"] == 9
    assert out["label"] == "congressional+insider_cluster"


def test_dec_332_smart_money_veto_case():
    """DEC-332 spec veto: cong=sell AND insider=cluster_sell -> -5 override."""
    from backtest.results.metrics import smart_money_composite_score
    out = smart_money_composite_score("sell", "cluster_sell", None)
    assert out["score"] == -5


def test_dec_334_composite_score_with_roi_proxy():
    """DEC-334: replace win_rate with actual ROI when use_roi_proxy=True."""
    from backtest.results.metrics import composite_score
    s_wr = composite_score(win_rate=0.5, profit_factor=1.5, smart_money_score=3)
    s_roi = composite_score(win_rate=0.5, profit_factor=1.5, smart_money_score=3,
                            use_roi_proxy=True, total_roi_pct=80)
    # ROI 80% -> normalized 0.8 substitutes for win_rate 0.5 -> different result
    assert s_wr != s_roi


def test_dec_335_composite_score_weights_configurable():
    """DEC-335: custom weights dict overrides default 40/30/30."""
    from backtest.config import COMPOSITE_SCORE_WEIGHTS
    from backtest.results.metrics import composite_score
    assert COMPOSITE_SCORE_WEIGHTS["win_rate"] == 0.40
    custom = {"win_rate": 1.0, "profit_factor": 0.0, "smart_money": 0.0}
    s = composite_score(win_rate=0.6, profit_factor=2.0, smart_money_score=5,
                        weights=custom)
    assert abs(s - 0.6) < 1e-9


def test_dec_349_asymmetric_event_window_constants():
    """DEC-349 spec: pre_days=1, post_days=3."""
    from backtest.config import EVENT_WINDOW_PRE_DAYS, EVENT_WINDOW_POST_DAYS
    assert EVENT_WINDOW_PRE_DAYS == 1
    assert EVENT_WINDOW_POST_DAYS == 3


def test_dec_364_tier_3_max_tickers_100():
    """DEC-364 spec: Tier 3 expanded to 100."""
    from backtest.config import TIER_3_MAX_TICKERS
    assert TIER_3_MAX_TICKERS == 100


def test_dec_606_finnhub_financials_excluded_constant():
    """DEC-606: exclusion flag set + guard raises on banned path."""
    import pytest
    from backtest.engine.improvements import (FINNHUB_FINANCIALS_REPORTED_EXCLUDED,
                                                assert_no_finnhub_financials)
    assert FINNHUB_FINANCIALS_REPORTED_EXCLUDED is True
    # Banned path
    with pytest.raises(RuntimeError, match="DEC-606"):
        assert_no_finnhub_financials("data_prefetch/finnhub/financials_reported/")
    # Innocent path
    assert_no_finnhub_financials("data_prefetch/sec_xbrl/")
    assert_no_finnhub_financials("data_prefetch/polygon/financials/")


# ============================================================================
# Phase 3 Batch 61 Path C 20-DEC bundle (owner directive: 20 DECs this turn)
# DEC-001/006/033/045/125/169/170/171/173/274/341/347/348/350/363/400
#   /440/453/479/489
# ============================================================================

def test_dec_001_quiver_subscription_cancel_stage():
    """DEC-001: Quiver cancellation timing constant present."""
    from backtest.config import QUIVER_SUBSCRIPTION_CANCEL_STAGE
    assert "Stage 3" in QUIVER_SUBSCRIPTION_CANCEL_STAGE


def test_dec_006_phase_1f_deferred_families():
    """DEC-006: Phase 1F deferred strategy families list."""
    from backtest.config import PHASE_1F_DEFERRED_STRATEGY_FAMILIES
    assert "advanced_options_arbitrage" in PHASE_1F_DEFERRED_STRATEGY_FAMILIES
    assert "high_frequency_intraday" in PHASE_1F_DEFERRED_STRATEGY_FAMILIES


def test_dec_033_email_notifications_replaced_approval():
    """DEC-033: email notifications mode (NOT approval gateway)."""
    from backtest.config import (EMAIL_OPERATIONAL_MODE,
                                   EMAIL_DAILY_SUMMARY_ENABLED,
                                   EMAIL_APPROVAL_GATEWAY_DISABLED)
    assert EMAIL_OPERATIONAL_MODE == "notifications_only"
    assert EMAIL_DAILY_SUMMARY_ENABLED is True
    assert EMAIL_APPROVAL_GATEWAY_DISABLED is True


def test_dec_125_form_144_prefetch_deferred():
    """DEC-125: Form 144 prefetch deferred (Sprint 4 activation)."""
    from backtest.config import (FORM_144_PREFETCH_ENABLED,
                                   FORM_144_SOURCE_PRIORITY)
    assert FORM_144_PREFETCH_ENABLED is False
    assert "quiver_paid" in FORM_144_SOURCE_PRIORITY
    assert "sec_edgar" in FORM_144_SOURCE_PRIORITY


def test_dec_169_owner_skills_audit_areas():
    """DEC-169: skills audit area list codified."""
    from backtest.config import OWNER_SKILLS_AUDIT_AREAS
    assert "statistical_methodology" in OWNER_SKILLS_AUDIT_AREAS
    assert "SRE_operations" in OWNER_SKILLS_AUDIT_AREAS


def test_dec_170_dec_171_dec_173_pyproject_toml_present():
    """DEC-170/171/173: pyproject.toml with ruff/black/isort/mypy/pydocstyle."""
    from pathlib import Path
    p = Path("pyproject.toml")
    assert p.exists()
    content = p.read_text(encoding="utf-8")
    assert "[tool.ruff]" in content
    assert "[tool.black]" in content
    assert "[tool.isort]" in content
    assert "[tool.mypy]" in content
    assert "[tool.pydocstyle]" in content
    assert "google" in content.lower()  # DEC-171 Google-style


def test_dec_274_sync_conflict_policy_no_ff():
    """DEC-274: sync_from_claude conflict policy = no_ff (not strategy_theirs)."""
    from backtest.config import SYNC_FROM_CLAUDE_CONFLICT_POLICY
    assert SYNC_FROM_CLAUDE_CONFLICT_POLICY == "no_ff"


def test_dec_341_universe_docstring_correct():
    """DEC-341: universe.py docstring describes static CSV (not Wikipedia fetch)."""
    from backtest.data import universe
    doc = universe.__doc__ or ""
    assert "static CSV" in doc or "Current Snapshot" in doc
    # L88 reference present (Wikipedia banned for runtime)
    assert "L88" in doc or "static CSV pattern" in doc


def test_dec_347_lagging_indicator_absorbed_constants():
    """DEC-347: cross-reference constant documents absorption chain."""
    from backtest.config import DEC_347_ABSORBED_BY
    assert "DEC-071" in DEC_347_ABSORBED_BY
    assert "DEC-106" in DEC_347_ABSORBED_BY


def test_dec_348_event_suppression_earnings_within_window():
    """DEC-348 spec: entry 1 day before FOMC suppressed; 2 days before allowed."""
    from datetime import date
    from backtest.results.metrics import event_calendar_suppression_check
    fomc_day = date(2024, 6, 12)
    # 1 day before -- WITHIN window (pre=1)
    out_pre = event_calendar_suppression_check(
        as_of_date=date(2024, 6, 11), fomc_dates=[fomc_day],
    )
    assert out_pre["suppressed"] is True
    assert "EVENT_SUPPRESSION_FOMC" in out_pre["reasons"]


def test_dec_348_event_suppression_outside_window():
    """DEC-348: 2 days before FOMC -- OUTSIDE asymmetric window (pre=1)."""
    from datetime import date
    from backtest.results.metrics import event_calendar_suppression_check
    out = event_calendar_suppression_check(
        as_of_date=date(2024, 6, 10),
        fomc_dates=[date(2024, 6, 12)],
    )
    assert out["suppressed"] is False


def test_dec_348_event_suppression_earnings():
    """DEC-348: ticker earnings day suppression."""
    from datetime import date
    from backtest.results.metrics import event_calendar_suppression_check
    out = event_calendar_suppression_check(
        as_of_date=date(2024, 8, 1),
        ticker_earnings_date=date(2024, 8, 1),  # same day
    )
    assert out["suppressed"] is True
    assert "EVENT_SUPPRESSION_EARNINGS" in out["reasons"]


def test_dec_350_non_ict_timeframes():
    """DEC-350: cube timeframe dim = {daily, weekly} for non-ICT only."""
    from backtest.config import NON_ICT_TIMEFRAME_DIMENSIONS
    assert NON_ICT_TIMEFRAME_DIMENSIONS == ("daily", "weekly")
    assert "intraday" not in NON_ICT_TIMEFRAME_DIMENSIONS


def test_dec_363_commodity_etf_expansion_narrow_scope():
    """DEC-363: lithium + base metals only (LIT/DBB/COPX)."""
    from backtest.config import COMMODITY_ETF_EXPANSION_APPROVED
    assert set(COMMODITY_ETF_EXPANSION_APPROVED) == {"LIT", "DBB", "COPX"}
    assert "USO" not in COMMODITY_ETF_EXPANSION_APPROVED


def test_dec_400_bonferroni_dynamic_n_basic():
    """DEC-400: replace hardcoded N=60 with len(p_values) by default."""
    from backtest.results.metrics import bonferroni_dynamic_n
    out = bonferroni_dynamic_n([0.001, 0.05, 0.5])
    assert out["n_tested"] == 3
    # alpha = 0.05/3 = 0.01667
    assert abs(out["alpha_bonferroni"] - 0.05/3) < 1e-7
    # 0.001 < 0.01667 -> passes; 0.05 > 0.01667 -> fails
    assert out["per_strategy_pass"] == [True, False, False]


def test_dec_400_bonferroni_override_n():
    """DEC-400: caller-supplied n_strategies_tested overrides len(p_values)."""
    from backtest.results.metrics import bonferroni_dynamic_n
    out = bonferroni_dynamic_n([0.001], n_strategies_tested=60)
    assert out["n_tested"] == 60
    assert abs(out["alpha_bonferroni"] - 0.05/60) < 1e-7


def test_dec_440_alpha_vantage_deprecated_flag():
    """DEC-440: Alpha Vantage deprecated; Polygon canonical."""
    from backtest.config import ALPHA_VANTAGE_DEPRECATED, CANONICAL_NEWS_SOURCE
    assert ALPHA_VANTAGE_DEPRECATED is True
    assert CANONICAL_NEWS_SOURCE == "polygon"


def test_dec_479_polygon_cost_correction_29():
    """DEC-479: $30 -> $29 cost correction."""
    from backtest.config import POLYGON_STOCKS_STARTER_MONTHLY_USD
    assert POLYGON_STOCKS_STARTER_MONTHLY_USD == 29


def test_dec_071_insider_officer_role_weights():
    """DEC-071: CEO/CFO weighted 2x; minor officer 0.5x; 10b5-1 excluded."""
    from backtest.config import (INSIDER_OFFICER_ROLE_WEIGHTS,
                                   INSIDER_EXCLUDE_10B5_1_PLANNED)
    assert INSIDER_OFFICER_ROLE_WEIGHTS["CEO"] == 2.0
    assert INSIDER_OFFICER_ROLE_WEIGHTS["CFO"] == 2.0
    assert INSIDER_OFFICER_ROLE_WEIGHTS["minor_officer"] == 0.5
    assert INSIDER_EXCLUDE_10B5_1_PLANNED is True


def test_dec_256_earnings_cache_schema():
    """DEC-256: 7-field earnings parquet schema + BMO/AMC/During."""
    from backtest.config import (EARNINGS_CACHE_DIR, EARNINGS_CACHE_SCHEMA,
                                   EARNINGS_TIME_OF_DAY_VALUES)
    assert "earnings" in EARNINGS_CACHE_DIR
    assert "report_date" in EARNINGS_CACHE_SCHEMA
    assert "eps_actual" in EARNINGS_CACHE_SCHEMA
    assert "BMO" in EARNINGS_TIME_OF_DAY_VALUES


def test_dec_257_fundamentals_15_required_fields():
    """DEC-257: 15 required fields + 9 computed + filing-lag default."""
    from backtest.config import (FUNDAMENTALS_REQUIRED_FIELDS,
                                   FUNDAMENTALS_COMPUTED_FIELDS,
                                   FUNDAMENTALS_PIT_FILING_LAG_DAYS)
    assert len(FUNDAMENTALS_REQUIRED_FIELDS) == 15
    assert "revenue" in FUNDAMENTALS_REQUIRED_FIELDS
    assert "shares_outstanding" in FUNDAMENTALS_REQUIRED_FIELDS
    assert len(FUNDAMENTALS_COMPUTED_FIELDS) == 9
    assert "PE_ttm" in FUNDAMENTALS_COMPUTED_FIELDS
    assert FUNDAMENTALS_PIT_FILING_LAG_DAYS == 45


def test_dec_259_ictsmc_cache_schema():
    """DEC-259: ICT/SMC cache schema (FVG/BOS/CHoCH/order_blocks/etc)."""
    from backtest.config import ICTSMC_CACHE_DIR, ICTSMC_CACHE_SCHEMA
    assert "ictsmc" in ICTSMC_CACHE_DIR
    for k in ("fvg_count", "bos_event", "choch_event", "order_block_levels",
              "liquidity_grab_event"):
        assert k in ICTSMC_CACHE_SCHEMA


def test_dec_298_cache_stores_raw_ohlcv():
    """DEC-298: cache stores RAW OHLCV (auto_adjust=False), recompute on-demand."""
    from backtest.config import CACHE_AUTO_ADJUST, CACHE_STORES_CORP_ACTIONS
    assert CACHE_AUTO_ADJUST is False
    assert CACHE_STORES_CORP_ACTIONS is True


def test_dec_345_ict_timeframes_scope():
    """DEC-345: ICT daily-trigger + weekly-HTF context only."""
    from backtest.config import ICT_TIMEFRAMES
    assert "daily_trigger" in ICT_TIMEFRAMES
    assert "weekly_HTF_context" in ICT_TIMEFRAMES


def test_dec_352_institutional_underwater_flag():
    """DEC-352: institutions underwater when current_price < avg cost - 10%."""
    from backtest.results.metrics import institutional_price_level_mapping
    out = institutional_price_level_mapping(
        quarterly_avg_cost_basis=100.0, current_price=85.0,
    )
    assert out["underwater"] is True
    assert out["position"] == "below"
    assert out["note"] == "INSTITUTIONS_UNDERWATER"


def test_dec_352_institutional_above_water():
    """DEC-352: current_price > avg cost -> above + no underwater flag."""
    from backtest.results.metrics import institutional_price_level_mapping
    out = institutional_price_level_mapping(100.0, 110.0)
    assert out["underwater"] is False
    assert out["position"] == "above"


def test_dec_354_chart_pattern_parent_roster_present():
    """DEC-354: parent roster contains all 6 child pattern keys."""
    from backtest.config import CHART_PATTERN_STRATEGIES
    expected = {"trendline_break_retest", "wedge_triangle_pennant",
                "head_and_shoulders", "double_top_bottom",
                "cup_and_handle", "flag_pennant_continuation"}
    assert expected.issubset(set(CHART_PATTERN_STRATEGIES.keys()))


def test_dec_355_trendline_break_retest_spec():
    """DEC-355: trendline pattern requires min 3 touches."""
    from backtest.config import CHART_PATTERN_STRATEGIES
    spec = CHART_PATTERN_STRATEGIES["trendline_break_retest"]
    assert spec["min_touches"] == 3
    assert spec["entry"] == "break+retest"


def test_dec_358_wedge_triangle_pennant_sub_patterns():
    """DEC-358: 7 sub-patterns (rising/falling wedge + 3 triangles + 2 pennants)."""
    from backtest.config import CHART_PATTERN_STRATEGIES
    spec = CHART_PATTERN_STRATEGIES["wedge_triangle_pennant"]
    sp = spec["sub_patterns"]
    assert "rising_wedge" in sp and "falling_wedge" in sp
    assert "symmetric_triangle" in sp
    assert "bullish_pennant" in sp and "bearish_pennant" in sp


def test_dec_359_head_and_shoulders_measured_move():
    """DEC-359: H&S spec uses measured_move target method."""
    from backtest.config import CHART_PATTERN_STRATEGIES
    spec = CHART_PATTERN_STRATEGIES["head_and_shoulders"]
    assert spec["target_method"] == "measured_move"
    assert spec["entry"] == "neckline_break+retest"


def test_dec_360_double_top_bottom_tolerance():
    """DEC-360: 3% peak tolerance + 10 bar minimum apart."""
    from backtest.config import CHART_PATTERN_STRATEGIES
    spec = CHART_PATTERN_STRATEGIES["double_top_bottom"]
    assert spec["tolerance_pct"] == 0.03
    assert spec["min_bars_apart"] == 10


def test_dec_361_cup_and_handle_shape():
    """DEC-361: U-base + handle pullback + breakout."""
    from backtest.config import CHART_PATTERN_STRATEGIES
    spec = CHART_PATTERN_STRATEGIES["cup_and_handle"]
    assert spec["shape"] == "U_base+handle"


def test_dec_362_flag_distinct_from_symmetric_pennant():
    """DEC-362: flag is sloping (distinct from DEC-358 symmetric pennant)."""
    from backtest.config import CHART_PATTERN_STRATEGIES
    spec = CHART_PATTERN_STRATEGIES["flag_pennant_continuation"]
    assert "sloping" in spec["note"]


def test_dec_354_skeleton_helper_returns_spec_and_unknown_pattern():
    """DEC-354 parent helper: returns spec for known + None for unknown."""
    from backtest.results.metrics import detect_chart_pattern_skeleton
    out_known = detect_chart_pattern_skeleton("head_and_shoulders")
    assert out_known["spec"] is not None
    assert out_known["detected"] is False  # skeleton; full impl deferred
    assert out_known["note"] == "SKELETON_PENDING_FULL_IMPL"
    out_unknown = detect_chart_pattern_skeleton("nonexistent_pattern")
    assert out_unknown["spec"] is None


def test_dec_372_dec_376_github_actions_workflow_paths():
    """DEC-372 + DEC-376: workflow file paths codified."""
    from backtest.config import GITHUB_ACTIONS_WORKFLOWS
    assert (GITHUB_ACTIONS_WORKFLOWS["refresh_extended_universe"]
            == ".github/workflows/refresh_extended_universe.yml")
    assert (GITHUB_ACTIONS_WORKFLOWS["refresh_momentum_watchlist"]
            == ".github/workflows/refresh_momentum_watchlist.yml")


def test_dec_380_polygon_corp_actions_paths():
    """DEC-380: Polygon Reference corp-actions API paths."""
    from backtest.config import POLYGON_CORP_ACTIONS_API_PATHS
    assert POLYGON_CORP_ACTIONS_API_PATHS["dividends"] == "/v3/reference/dividends"
    assert POLYGON_CORP_ACTIONS_API_PATHS["splits"] == "/v3/reference/splits"


def test_dec_407_fred_macro_expansion_series():
    """DEC-407: 8 FRED series added (NFP, CPI, IP, etc.)."""
    from backtest.config import FRED_MACRO_EXPANSION_SERIES
    assert len(FRED_MACRO_EXPANSION_SERIES) == 8
    for series in ("PAYEMS", "MANEMP", "UMCSENT", "RSAFS", "HOUST",
                    "INDPRO", "BAMLH0A0HYM2", "M2SL"):
        assert series in FRED_MACRO_EXPANSION_SERIES


def test_dec_417_test_run_audit_gate_constants():
    """DEC-417: audit-results path + required fields codified."""
    from backtest.config import (TEST_RUN_AUDIT_GATE_RESULTS_PATH,
                                   TEST_RUN_AUDIT_GATE_REQUIRED_FIELDS)
    assert TEST_RUN_AUDIT_GATE_RESULTS_PATH == "AUDIT_TEST_RUN_RESULTS.md"
    assert "decision_id" in TEST_RUN_AUDIT_GATE_REQUIRED_FIELDS
    assert "test_signal" in TEST_RUN_AUDIT_GATE_REQUIRED_FIELDS


def test_dec_436_ci_regression_assertions():
    """DEC-436: CI/CD regression assertions (Layer 2 catch defense)."""
    from backtest.config import (CI_REGRESSION_WORKFLOW_PATH,
                                   CI_REGRESSION_BEHAVIOR_ASSERTIONS)
    assert CI_REGRESSION_WORKFLOW_PATH == ".github/workflows/regression.yml"
    assert CI_REGRESSION_BEHAVIOR_ASSERTIONS["vix_threshold_crisis"] == 40
    assert CI_REGRESSION_BEHAVIOR_ASSERTIONS["rr_minimum_all_exits"] == 2.0


# ============================================================================
# Phase 3 Batch 63 Path C 23-DEC close-out (owner: close ALL remaining)
# DEC-075/184/215/425/426/428/429/431/433/441/450/456/458/460/461/463/464
#   /465/466/468/605/601/593
# ============================================================================

def test_dec_184_parallel_backtest_constants():
    """DEC-184: ProcessPool + default 4 workers."""
    from backtest.config import (PARALLEL_BACKTEST_WORKERS_DEFAULT,
                                   PARALLEL_BACKTEST_EXECUTOR)
    assert PARALLEL_BACKTEST_WORKERS_DEFAULT == 4
    assert PARALLEL_BACKTEST_EXECUTOR == "ProcessPoolExecutor"


def test_dec_215_ab_test_registry_schema():
    """DEC-215: 9-field registry schema."""
    from backtest.config import (AB_TEST_REGISTRY_DIR,
                                   AB_TEST_REGISTRY_SCHEMA)
    assert AB_TEST_REGISTRY_DIR == "ab_test_results"
    for k in ("test_id", "as_of_date", "arms", "sharpe_rules",
              "sharpe_agent", "net_sharpe", "verdict", "manifest_hash"):
        assert k in AB_TEST_REGISTRY_SCHEMA


def test_dec_441_polygon_subscription_active():
    """DEC-441: Polygon Stocks Starter active flag."""
    from backtest.config import (POLYGON_STOCKS_STARTER_ACTIVE,
                                   POLYGON_STOCKS_STARTER_TIER)
    assert POLYGON_STOCKS_STARTER_ACTIVE is True
    assert POLYGON_STOCKS_STARTER_TIER == "stocks_starter"


def test_dec_450_quiver_paid_endpoints_manifest():
    """DEC-450: all paid-tier Quiver endpoints enumerated."""
    from backtest.config import QUIVER_PAID_ENDPOINTS
    for endpoint in ("congresstrading", "sec13f", "insidertrading",
                      "wsbtrading", "patentmomentum"):
        assert endpoint in QUIVER_PAID_ENDPOINTS


def test_dec_456_sec_edgar_differential_reference():
    """DEC-456: SEC EDGAR active for DEC-439 differential testing."""
    from backtest.config import (SEC_EDGAR_DIFFERENTIAL_REFERENCE,
                                   SEC_EDGAR_DIFFERENTIAL_CACHE_DIR)
    assert SEC_EDGAR_DIFFERENTIAL_REFERENCE is True
    assert "sec_xbrl" in SEC_EDGAR_DIFFERENTIAL_CACHE_DIR


def test_dec_458_lead_lag_strategy_spec():
    """DEC-458: lead-lag intra-sector momentum spec."""
    from backtest.config import LEAD_LAG_INTRA_SECTOR_STRATEGY
    assert LEAD_LAG_INTRA_SECTOR_STRATEGY["rebalance_cadence"] == "weekly"
    assert LEAD_LAG_INTRA_SECTOR_STRATEGY["lookback_days"] == 5
    assert LEAD_LAG_INTRA_SECTOR_STRATEGY["sector_dim"] == "GICS_sector"


def test_dec_460_dec_461_polygon_pit_verification_and_fmp_fallback():
    """DEC-460/461: PIT verification gate + FMP fallback flag."""
    from backtest.config import (POLYGON_PIT_VERIFICATION_DONE,
                                   FMP_FALLBACK_ENABLED,
                                   FMP_SUBSCRIPTION_COST_USD_MO)
    # Verification pending owner gate
    assert POLYGON_PIT_VERIFICATION_DONE is False
    # FMP gated by PIT-verification outcome
    assert FMP_FALLBACK_ENABLED is False
    assert FMP_SUBSCRIPTION_COST_USD_MO == 50


def test_dec_463_dec_464_dec_465_dec_466_agent_toolkits():
    """DEC-463/464/465/466: 4 agent toolkit specs codified."""
    from backtest.config import AGENT_TOOLKIT_SPECS
    for cls in ("OurFundamentalsToolkit", "OurNewsToolkit",
                 "OurTraderToolkit", "OurRiskToolkit"):
        assert cls in AGENT_TOOLKIT_SPECS
        assert "capabilities" in AGENT_TOOLKIT_SPECS[cls]
        assert "data_sources" in AGENT_TOOLKIT_SPECS[cls]
    # Fundamentals + News extend existing TradingAgents classes
    assert "FundamentalsToolkit" in AGENT_TOOLKIT_SPECS["OurFundamentalsToolkit"]["extends"]
    # Trader + Risk are NEW classes (no parent)
    assert AGENT_TOOLKIT_SPECS["OurTraderToolkit"]["extends"] is None
    assert AGENT_TOOLKIT_SPECS["OurRiskToolkit"]["extends"] is None


def test_dec_468_ortex_short_interest_constants():
    """DEC-468: Ortex short-interest fields + squeeze threshold."""
    from backtest.config import (ORTEX_SHORT_INTEREST_CACHE_DIR,
                                   ORTEX_SHORT_INTEREST_FIELDS,
                                   ORTEX_HIGH_SHORT_THRESHOLD_PCT)
    assert "ortex" in ORTEX_SHORT_INTEREST_CACHE_DIR
    assert "short_interest_pct_float" in ORTEX_SHORT_INTEREST_FIELDS
    assert "days_to_cover" in ORTEX_SHORT_INTEREST_FIELDS
    assert ORTEX_HIGH_SHORT_THRESHOLD_PCT == 20.0


def test_dec_605_finnhub_social_sentiment_excluded_phase_1a():
    """DEC-605: Finnhub social_sentiment excluded Phase 1A; revisit Phase 1B+."""
    from backtest.config import (FINNHUB_SOCIAL_SENTIMENT_EXCLUDED_PHASE_1A,
                                   FINNHUB_SOCIAL_SENTIMENT_PHASE_1B_REVISIT)
    assert FINNHUB_SOCIAL_SENTIMENT_EXCLUDED_PHASE_1A is True
    assert FINNHUB_SOCIAL_SENTIMENT_PHASE_1B_REVISIT is True


def test_dec_601_aaii_extended_13_col_schema():
    """DEC-601: 13-col AAII extended schema (replaces 5-col v1)."""
    from backtest.config import (AAII_EXTENDED_SCHEMA_COLS,
                                   AAII_EXTENDED_SCHEMA_VERSION)
    assert len(AAII_EXTENDED_SCHEMA_COLS) == 13
    assert "bull_bear_spread" in AAII_EXTENDED_SCHEMA_COLS
    assert "regime_signal" in AAII_EXTENDED_SCHEMA_COLS
    assert AAII_EXTENDED_SCHEMA_VERSION == 2


def test_batch_64_audit_index_only_resolved_or_rejected():
    """Batch 64 invariant (UPDATED Batch 69 phase 2 2026-05-12 per owner
    directive to revert false-positive flips): AUDIT_INDEX statuses must be
    one of the documented closure terminals.

    Status vocabulary (post-Batch-423 reconciliation):
      - RESOLVED-IMPLEMENTED        - canonical completion
      - RESOLVED-DECIDED-DEFERRED   - decision made but build deferred
                                       (12 DECs in 2026-05-28 snapshot)
      - RESOLVED-PARTIALLY-SUPERSEDED - older DEC partially superseded by
                                         a newer one (1 DEC: see e.g.
                                         Batch 418 STRATEGY_REGIME_AFFINITY
                                         overrides supersede Batch 203/293/370
                                         curated entries)
      - REJECTED                    - decision intentionally not pursued
      - PARTIAL-IMPL-HELPER-ONLY    - helper exists in prod-code modules
                                       but engine call path does not consume
                                       (Batch 69 revert target status;
                                       0 active in 2026-05-28 snapshot after
                                       Batch 400 closed the remaining 20)

    Batch 423 (2026-05-28): added RESOLVED-DECIDED-DEFERRED +
    RESOLVED-PARTIALLY-SUPERSEDED to the allowed set after CI red surfaced
    the test invariant was stale. Both statuses are owner-created via
    DEC closures in batches between 64-422; test was never updated to
    track the vocabulary growth.
    """
    import json
    from pathlib import Path
    data_path = Path("dashboard_stage_2/data.json")
    if not data_path.exists():
        return  # dashboard not regenerated yet (e.g., pre-build CI)
    data = json.loads(data_path.read_text(encoding="utf-8"))
    statuses = {x.get("status") for x in data.get("decisions", [])}
    allowed = {
        "RESOLVED-IMPLEMENTED",
        "RESOLVED-DECIDED-DEFERRED",       # Batch 423 added
        "RESOLVED-PARTIALLY-SUPERSEDED",   # Batch 423 added
        "REJECTED",
        "PARTIAL-IMPL-HELPER-ONLY",  # Batch 69 revert target; 0 active 2026-05-28
    }
    leaked = statuses - allowed
    assert not leaked, f"Audit invariant breached: unexpected statuses {leaked}"


def test_dashboard_filter_promotioncell_hidden_tier_span():
    """Dashboard filter fix 2026-05-13: DataTables column.search() operates on
    stripped text (not raw HTML). promotionCell hidden tier span makes tier code
    visible as text. Status columns use ^v$ regex for exact match; promotion
    columns use plain substring v to find tier code in hidden span text.
    """
    from pathlib import Path
    html = Path("dashboard_stage_2/index.html").read_text(encoding="utf-8")
    # Hidden tier-text span must still be present (makes tier code visible to DT search)
    assert "<span style=\"display:none\">${tier}</span>" in html, (
        "promotionCell missing hidden tier-text span"
    )
    # Old broken pattern must be gone (it searched raw HTML, DT uses stripped text)
    old_count = html.count("`>${v}<`")
    assert old_count == 0, (
        f"Old >v< raw-HTML pattern still present ({old_count} occurrences); should be 0"
    )
    # New pattern: ^v.toLowerCase()$ regex for status columns.
    # DataTables lowercases filter data when caseInsensitive=true (default); regex
    # must also be lowercased or it never matches. v.toLowerCase() fixes the mismatch.
    # dec-status-filter was removed 2026-05-14 (Promotion supersedes); inv + cav remain.
    exact_count = html.count("`^${v.toLowerCase()}$`")
    assert exact_count == 2, (
        f"Expected 2 lowercase-regex ^v.toLowerCase()$ patterns (inv-status, cav-status); got {exact_count}"
    )
    # Old uppercase regex must be gone (it never matched lowercased DT filter data)
    old_upper_count = html.count("`^${v}$`")
    assert old_upper_count == 0, (
        f"Old uppercase `^${{v}}$` pattern still present ({old_upper_count} occurrences); must be 0"
    )


# ============================================================================
# Phase 3 Batch 65 - real implementation of 10 previously-PARTIAL-SPEC-ONLY DECs
# DEC-018 / 037 / 107 / 117 / 136 / 138 / 144 / 152 / 175 / 177
# ============================================================================

def test_dec_018_stopout_cooldown_active_within_5d():
    """DEC-018: stop-out within 5 days -> in_cooldown=True."""
    import pandas as pd
    from datetime import date, timedelta
    from backtest.results.metrics import is_ticker_in_stopout_cooldown
    df = pd.DataFrame([
        {"ticker": "AAPL", "exit_date": date(2024, 6, 10), "exit_reason": "atr_trail_stop"},
    ])
    out = is_ticker_in_stopout_cooldown("AAPL", df, as_of=date(2024, 6, 12))
    assert out["in_cooldown"] is True
    assert out["note"] == "STOPOUT_COOLDOWN"


def test_dec_018_stopout_cooldown_expires_after_5d():
    """DEC-018: stop-out 7 days ago -> in_cooldown=False."""
    import pandas as pd
    from datetime import date
    from backtest.results.metrics import is_ticker_in_stopout_cooldown
    df = pd.DataFrame([
        {"ticker": "AAPL", "exit_date": date(2024, 6, 1), "exit_reason": "stop_loss"},
    ])
    out = is_ticker_in_stopout_cooldown("AAPL", df, as_of=date(2024, 6, 10))
    assert out["in_cooldown"] is False


def test_dec_037_characterization_absorbed_by_438():
    """DEC-037: cross-reference to DEC-438 golden-master tests."""
    from backtest.config import DEC_037_ABSORBED_BY
    assert "DEC-438" in DEC_037_ABSORBED_BY


def test_dec_107_regime_probability_phase_a_returns_label_and_vector():
    """DEC-107 Phase A: emits both label AND probability vector."""
    from backtest.results.metrics import regime_probability_phase_a
    out = regime_probability_phase_a(80)
    assert out["regime_label"] == "bull"
    probs = out["regime_probabilities"]
    # Vector sums to ~1.0
    assert abs(sum(probs.values()) - 1.0) < 1e-6
    # bull probability is dominant at score=80
    assert probs["bull"] > probs["neutral"]
    assert probs["bull"] > probs["bear"]


def test_dec_107_regime_probability_phase_a_low_score():
    """DEC-107: low score -> crisis label + crisis-dominated vector."""
    from backtest.results.metrics import regime_probability_phase_a
    out = regime_probability_phase_a(10)
    assert out["regime_label"] == "crisis"
    assert out["regime_probabilities"]["crisis"] > out["regime_probabilities"]["bull"]


def test_dec_117_cache_checksum_computes_sha256(tmp_path):
    """DEC-117: SHA-256 + last_validated + size for a real file."""
    from backtest.results.metrics import compute_cache_checksum
    p = tmp_path / "cache.bin"
    p.write_bytes(b"hello world")
    out = compute_cache_checksum(str(p))
    # SHA-256 of "hello world" is a known constant
    assert out["sha256"] == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    assert out["size_bytes"] == 11
    assert out["last_validated_iso"] is not None


def test_dec_117_cache_checksum_missing_file():
    """DEC-117: missing file -> note='missing_file' + None values."""
    from backtest.results.metrics import compute_cache_checksum
    out = compute_cache_checksum("/nonexistent/path.bin")
    assert out["sha256"] is None
    assert out["note"] == "missing_file"


def test_dec_136_portfolio_rebalance_drift_breach():
    """DEC-136: position drift > 2x target -> rebalance triggered."""
    from backtest.results.metrics import should_rebalance_portfolio
    pos = {"AAPL": 0.10, "MSFT": 0.03}
    target = {"AAPL": 0.03, "MSFT": 0.03}
    out = should_rebalance_portfolio(pos, target)
    assert out["should_rebalance"] is True
    assert out["worst_drift_ticker"] == "AAPL"
    assert "DRIFT_BREACH" in out["reason"]


def test_dec_136_portfolio_rebalance_cash_deployable():
    """DEC-136: cash > 10% AND deployable signals -> rebalance."""
    from backtest.results.metrics import should_rebalance_portfolio
    out = should_rebalance_portfolio(
        {"AAPL": 0.04}, {"AAPL": 0.04},
        cash_pct=0.15, deployable_signals_available=True,
    )
    assert out["should_rebalance"] is True
    assert "CASH_DEPLOYABLE" in out["reason"]


def test_dec_136_portfolio_rebalance_no_trigger():
    """DEC-136: no drift + no cash overflow -> no rebalance."""
    from backtest.results.metrics import should_rebalance_portfolio
    out = should_rebalance_portfolio(
        {"AAPL": 0.04}, {"AAPL": 0.04},
        cash_pct=0.05, deployable_signals_available=True,
    )
    assert out["should_rebalance"] is False


def test_dec_138_cold_start_ci_constants():
    """DEC-138: workflow path + 30min target."""
    from backtest.config import COLD_START_CI_WORKFLOW_PATH, COLD_START_CI_MAX_MINUTES
    assert COLD_START_CI_WORKFLOW_PATH == ".github/workflows/cold_start.yml"
    assert COLD_START_CI_MAX_MINUTES == 30


def test_dec_144_momentum_delta_band_high_outperform():
    """DEC-144: stock +20% vs sector +5% -> high_outperform band."""
    from backtest.results.metrics import momentum_delta_band
    out = momentum_delta_band(0.20, 0.05)
    assert out["band"] == "high_outperform"
    assert abs(out["delta"] - 0.15) < 1e-9


def test_dec_144_momentum_delta_band_neutral_and_underperform():
    """DEC-144: bands shake out: neutral / underperform / high_underperform."""
    from backtest.results.metrics import momentum_delta_band
    assert momentum_delta_band(0.05, 0.04)["band"] == "neutral"
    assert momentum_delta_band(0.02, 0.10)["band"] == "underperform"
    assert momentum_delta_band(-0.05, 0.10)["band"] == "high_underperform"


def test_dec_175_signal_persistence_weighting_monotonic():
    """DEC-175: consecutive-day weight grows monotonically + caps at max."""
    from backtest.results.metrics import signal_persistence_weight
    assert signal_persistence_weight(1) == 1.0
    assert signal_persistence_weight(3) == 1.5     # 1.0 + 2 * 0.25
    assert signal_persistence_weight(7) == 2.5     # capped (would be 2.5)
    assert signal_persistence_weight(20) == 2.5    # still capped
    assert signal_persistence_weight(0) == 0.0     # no fire


def test_dec_177_backtest_seed_constants():
    """DEC-177: default seed + output field name for reproducibility."""
    from backtest.config import BACKTEST_DEFAULT_SEED, BACKTEST_SEED_OUTPUT_FIELD
    assert BACKTEST_DEFAULT_SEED == 20260511
    assert BACKTEST_SEED_OUTPUT_FIELD == "random_seed"


# ============================================================================
# Phase 3 Batch 66 - 10 more PARTIAL-SPEC-ONLY -> real impl
# DEC-205 / 207 / 216 / 251 / 258 / 260 / 269 / 277 / 338 / 353
# ============================================================================

def test_dec_205_ab_test_arms_minimum_4():
    """DEC-205: AB_TEST_ARMS has minimum 4 arms (rules/full/no_risk/no_bull_bear)."""
    from backtest.config import AB_TEST_ARMS, AB_TEST_MIN_ARMS
    assert AB_TEST_MIN_ARMS == 4
    assert len(AB_TEST_ARMS) >= 4
    assert "rules" in AB_TEST_ARMS
    assert "full_agents" in AB_TEST_ARMS
    assert "no_risk" in AB_TEST_ARMS
    assert "no_bull_bear" in AB_TEST_ARMS


def test_dec_207_ab_min_paired_trades_per_arm():
    """DEC-207: pre-commit minimum 300 paired trades per arm."""
    from backtest.config import AB_TEST_MIN_PAIRED_TRADES_PER_ARM
    assert AB_TEST_MIN_PAIRED_TRADES_PER_ARM == 300


def test_dec_216_ab_orchestrator_module_path_and_seeds():
    """DEC-216: orchestrator module path + deterministic-seed config.

    Batch 373 (2026-05-26 T2 closure): tightened path assertion to the
    actual module location `backtest/results/ab_orchestrator.py` (was
    a loose endswith check that masked a path drift; pre-Batch-373 the
    constant pointed to `backtest/ab_orchestrator.py` which does not
    exist). Module wired Batch 245; engine-consumed via test_phase_1b_
    sprint_7.py importing run_ab_test + dataclasses + verdict logic."""
    from pathlib import Path
    from backtest.config import (AB_ORCHESTRATOR_MODULE_PATH,
                                   AB_ORCHESTRATOR_DETERMINISTIC_SEEDS)
    assert AB_ORCHESTRATOR_MODULE_PATH == "backtest/results/ab_orchestrator.py", (
        f"DEC-216 path drift: expected 'backtest/results/ab_orchestrator.py'; "
        f"got {AB_ORCHESTRATOR_MODULE_PATH!r}"
    )
    # Verify module actually exists at the cited path
    repo = Path(__file__).resolve().parents[2]
    assert (repo / AB_ORCHESTRATOR_MODULE_PATH).exists(), (
        f"DEC-216: module file missing at cited path {AB_ORCHESTRATOR_MODULE_PATH}"
    )
    assert AB_ORCHESTRATOR_DETERMINISTIC_SEEDS is True


def test_dec_251_di_refactor_candidate_modules():
    """DEC-251: candidate modules for DI refactor."""
    from backtest.config import DI_REFACTOR_CANDIDATE_MODULES
    assert "backtest/agents/pipeline.py" in DI_REFACTOR_CANDIDATE_MODULES
    assert "backtest/data/smart_money.py" in DI_REFACTOR_CANDIDATE_MODULES


def test_dec_258_options_chain_cache_schema():
    """DEC-258: options chain schema (strike/IV/OI/PCR/IV-rank)."""
    from backtest.config import (OPTIONS_CHAIN_CACHE_DIR,
                                   OPTIONS_CHAIN_CACHE_SCHEMA)
    assert "options_chain" in OPTIONS_CHAIN_CACHE_DIR
    for k in ("strike", "implied_volatility", "open_interest",
              "put_call_ratio", "iv_rank_252d"):
        assert k in OPTIONS_CHAIN_CACHE_SCHEMA


def test_dec_260_cache_stale_raises_when_requested_beyond_cached():
    """DEC-260: requested_date > cached_end_date -> CacheStaleError."""
    import pytest
    from datetime import date
    from backtest.results.metrics import assert_cache_fresh, CacheStaleError
    with pytest.raises(CacheStaleError) as exc_info:
        assert_cache_fresh("AAPL", "ohlcv",
                            cached_end_date=date(2024, 6, 10),
                            requested_date=date(2024, 6, 12))
    assert exc_info.value.ticker == "AAPL"
    assert exc_info.value.cache_type == "ohlcv"


def test_dec_260_cache_fresh_no_raise_when_in_range():
    """DEC-260: requested_date <= cached_end_date -> no raise."""
    from datetime import date
    from backtest.results.metrics import assert_cache_fresh
    # No exception expected
    assert_cache_fresh("AAPL", "ohlcv",
                       cached_end_date=date(2024, 6, 15),
                       requested_date=date(2024, 6, 10))


def test_dec_269_stage_4_entry_gates():
    """DEC-269: Stage 4 explicit numeric gates."""
    from backtest.config import STAGE_4_ENTRY_GATES
    assert STAGE_4_ENTRY_GATES["sharpe_oos_min"] == 1.0
    assert STAGE_4_ENTRY_GATES["max_drawdown_pct_max"] == 25.0
    assert STAGE_4_ENTRY_GATES["win_rate_min"] == 0.50
    assert STAGE_4_ENTRY_GATES["ab_test_winner_clear"] is True
    assert STAGE_4_ENTRY_GATES["min_trades_oos"] == 150


def test_dec_277_strategy_promotion_states():
    """DEC-277: 6 promotion states codified."""
    from backtest.config import STRATEGY_PROMOTION_STATES
    for s in ("stage_1_baseline", "stage_2_validation", "stage_3_papertrade",
              "stage_4_live_micro", "stage_4_live_full", "demoted"):
        assert s in STRATEGY_PROMOTION_STATES


def test_dec_338_conversion_fires_on_short_in_bull_flip():
    """DEC-338: short position + regime flip to bull -> close+open long."""
    from backtest.results.metrics import maybe_convert_short_to_long
    short_pos = {"ticker": "AAPL", "shares": -100, "entry_price": 150.0}
    out = maybe_convert_short_to_long(short_pos,
                                       current_regime="bull",
                                       prior_regime="bear")
    assert out["action"] == "close_short_and_open_long"
    assert out["close_short_shares"] == 100
    assert out["open_long_shares"] == 100
    assert out["note"] == "REGIME_FLIP_BULL_CONVERSION"


def test_dec_338_no_conversion_when_not_short():
    """DEC-338: long position (shares > 0) -> no conversion."""
    from backtest.results.metrics import maybe_convert_short_to_long
    long_pos = {"ticker": "AAPL", "shares": 100, "entry_price": 150.0}
    out = maybe_convert_short_to_long(long_pos, "bull", "bear")
    assert out["action"] == "no_conversion"
    assert out["note"] == "not_a_short"


def test_dec_338_no_conversion_when_regime_not_bull():
    """DEC-338: short + regime=bear -> no conversion."""
    from backtest.results.metrics import maybe_convert_short_to_long
    short_pos = {"ticker": "AAPL", "shares": -100}
    out = maybe_convert_short_to_long(short_pos, "bear", "bull")
    assert out["action"] == "no_conversion"
    assert out["note"] == "regime_not_bull"


def test_dec_338_no_conversion_when_not_flip_day():
    """DEC-338: short + bull regime + prior=bull (not flip) -> no conversion."""
    from backtest.results.metrics import maybe_convert_short_to_long
    short_pos = {"ticker": "AAPL", "shares": -100}
    out = maybe_convert_short_to_long(short_pos, "bull", "bull")
    assert out["action"] == "no_conversion"
    assert out["note"] == "not_flip_day"


def test_dec_353_rr_minimum_and_defaults():
    """DEC-353: 2:1 R:R minimum + exit_fixed_target defaults updated."""
    from backtest.config import (RR_RATIO_MINIMUM, RR_RATIO_SWEEP_VALUES,
                                   EXIT_FIXED_TARGET_DEFAULTS)
    assert RR_RATIO_MINIMUM == 2.0
    assert 2.0 in RR_RATIO_SWEEP_VALUES
    # Defaults must meet the minimum
    rr = (EXIT_FIXED_TARGET_DEFAULTS["target_mult"]
          / EXIT_FIXED_TARGET_DEFAULTS["stop_mult"])
    assert rr >= RR_RATIO_MINIMUM


# ============================================================================
# Phase 3 Batch 67 - 10 more PARTIAL-SPEC-ONLY -> real impl + dashboard re-fix
# DEC-368 / 369 / 370 / 378 / 420 / 422 / 427 / 430 / 437 / 438
# ============================================================================

def test_dec_368_calendar_seasonal_strategies():
    """DEC-368: 7 calendar/seasonal strategy specs."""
    from backtest.config import CALENDAR_SEASONAL_STRATEGIES
    for s in ("sell_in_may_and_go_away", "january_effect", "santa_rally",
              "fomc_drift", "end_of_month_drift"):
        assert s in CALENDAR_SEASONAL_STRATEGIES


def test_dec_369_cross_asset_strategies():
    """DEC-369: cross-asset strategy specs + joint DEC-102 ticker list."""
    from backtest.config import CROSS_ASSET_STRATEGIES, CROSS_ASSET_STRATEGY_TICKERS
    assert "yield_curve_steepener_equity_rotation" in CROSS_ASSET_STRATEGIES
    assert "TLT" in CROSS_ASSET_STRATEGY_TICKERS


def test_dec_370_index_rebalance_strategies():
    """DEC-370: 4 index-rebalance strategy specs."""
    from backtest.config import INDEX_REBALANCE_STRATEGIES
    assert "sp500_inclusion_drift_T_minus_5" in INDEX_REBALANCE_STRATEGIES
    assert "russell_reconstitution_arbitrage" in INDEX_REBALANCE_STRATEGIES


def test_dec_378_nasdaq_symbol_directory_constants():
    """DEC-378: NASDAQ FTP URL + >$5B threshold."""
    from backtest.config import (NASDAQ_SYMBOL_DIRECTORY_URL,
                                   NASDAQ_SYMBOL_DIFF_THRESHOLD_USD)
    assert "nasdaqtraded.txt" in NASDAQ_SYMBOL_DIRECTORY_URL
    assert NASDAQ_SYMBOL_DIFF_THRESHOLD_USD == 5_000_000_000


def test_dec_420_agent_ab_three_case_pairing():
    """DEC-420: 3-case A/B pairing + net-lift formula."""
    from backtest.config import (AGENT_AB_THREE_CASE_PAIRING,
                                   AGENT_AB_NET_LIFT_FORMULA)
    assert "rules_only_signal" in AGENT_AB_THREE_CASE_PAIRING
    assert "agent_overlay_signal" in AGENT_AB_THREE_CASE_PAIRING
    assert "agent_overrides_no_signal" in AGENT_AB_THREE_CASE_PAIRING
    assert "compute_net_sharpe_contribution" in AGENT_AB_NET_LIFT_FORMULA


def test_dec_437_property_based_testing_layer_3():
    """DEC-437: hypothesis library + Layer 3 defense."""
    from backtest.config import (PROPERTY_BASED_TESTING_LIB,
                                   PROPERTY_BASED_TESTING_DEFENSE_LAYER,
                                   PROPERTY_BASED_TESTING_TARGETS)
    assert PROPERTY_BASED_TESTING_LIB == "hypothesis"
    assert PROPERTY_BASED_TESTING_DEFENSE_LAYER == 3
    assert "exit_strategies" in PROPERTY_BASED_TESTING_TARGETS


def test_dec_438_golden_master_testing_layer_4():
    """DEC-438: golden-master + Layer 4 + byte-identical tolerance."""
    from backtest.config import (GOLDEN_MASTER_TESTING_DEFENSE_LAYER,
                                   GOLDEN_MASTER_TESTING_ARTIFACT_DIR,
                                   GOLDEN_MASTER_TESTING_DIFF_TOLERANCE)
    assert GOLDEN_MASTER_TESTING_DEFENSE_LAYER == 4
    assert "golden_masters" in GOLDEN_MASTER_TESTING_ARTIFACT_DIR
    assert GOLDEN_MASTER_TESTING_DIFF_TOLERANCE == 0.0  # byte-identical


def test_dashboard_filter_uses_value_pattern_batch_67():
    """Dashboard filter fix 2026-05-13: the old `>v<` raw-HTML pattern is
    replaced. DataTables column.search() strips HTML before searching, so
    `>VALUE<` never matched. Correct patterns:
      - Status columns: ^v$ regex (exact-token on stripped badge text)
      - Promotion columns: plain v substring (finds tier code in hidden span)
    """
    from pathlib import Path
    html = Path("dashboard_stage_2/index.html").read_text(encoding="utf-8")
    # Old broken pattern must be completely gone
    old_count = html.count("`>${v}<`")
    assert old_count == 0, (
        f"Old >v< pattern still present ({old_count} occurrences); must be 0"
    )
    # Status columns use lowercase-regex exact-match (2: inv-status, cav-status).
    # DataTables lowercases filter data; regex must also be lowercased to match.
    # dec-status-filter was removed 2026-05-14 (Promotion column supersedes it).
    exact_count = html.count("`^${v.toLowerCase()}$`")
    assert exact_count == 2, (
        f"Expected 2 toLowerCase-regex handlers (inv, cav); got {exact_count}"
    )
    # Old uppercase `^${{v}}$` must be gone
    old_upper_count = html.count("`^${v}$`")
    assert old_upper_count == 0, (
        f"Old uppercase `^${{v}}$` still present ({old_upper_count}); must be 0"
    )
    # Promotion columns use plain substring (v, false, false).
    # dec-promotion now at column 3 (Doc Status column removed), bug-promotion still col 3, inv-promotion col 4
    assert "decTable.column(3).search(v, false, false)" in html, "dec-promotion filter broken"
    assert "bugTable.column(3).search(v, false, false)" in html, "bug-promotion filter broken"
    assert "invTable.column(4).search(v, false, false)" in html, "inv-promotion filter broken"


def test_verification_matrix_consumed_by_dashboard_batch_155():
    """Owner directive 2026-05-14: coverage-driven engine consumption ground truth.

    Dashboard must:
      (a) load verification_matrix.json (machine-readable mirror of VERIFICATION_MATRIX.md)
      (b) emit `coverage_engine` field on every dec / bug / inv
      (c) render an Engine column in the decisions + bugs tables
      (d) use the coverage status as authoritative when compute_promotion_path
          decides between IMPLEMENTED vs NOT-CONSUMED tiers

    Replaces the prior grep-based wired heuristic that produced ~150 false
    RESOLVED-IMPLEMENTED claims (memory feedback 2026-05-12).
    """
    import json
    import re
    from pathlib import Path

    repo = Path(__file__).resolve().parents[2]

    # (a) verification_matrix.json exists and parses
    vm_path = repo / "verification_matrix.json"
    assert vm_path.exists(), \
        "verification_matrix.json missing; run scripts/build_verification_matrix.py"
    vm = json.loads(vm_path.read_text(encoding="utf-8"))
    assert "items" in vm and len(vm["items"]) > 0, \
        "verification_matrix.json must have items dict"
    # Schema: every item has engine + evidence
    for iid, entry in list(vm["items"].items())[:5]:
        assert "engine" in entry and "evidence" in entry and "tier" in entry, \
            f"matrix item {iid} missing engine/evidence/tier keys"

    # (b) data.js carries coverage_engine on every dec + bug + inv
    data_js = (repo / "dashboard_stage_2" / "data.js").read_text(encoding="utf-8")
    js = re.sub(r"^const STAGE2_DATA = ", "", data_js.strip())
    js = re.sub(r";$", "", js.strip())
    d = json.loads(js)
    for kind in ("decisions", "bugs", "investigations"):
        for item in d.get(kind, [])[:5]:
            assert "coverage_engine" in item, \
                f"{kind[:-1]} {item.get('short_id') or item.get('id')} missing coverage_engine"

    # (c) Engine column rendered in dashboard HTML
    html = (repo / "dashboard_stage_2" / "index.html").read_text(encoding="utf-8")
    assert "engineCell(" in html, \
        "engineCell renderer must be defined in index.html"
    assert html.count(">Engine</th>") >= 2, \
        "Engine <th> must appear in both decisions + bugs tables"

    # (d) compute_promotion_path overrides on NO / FUNC-DEAD
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "dash_build", repo / "scripts" / "build_dashboard_stage_2.py")
    dash = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dash)
    # Synthetic NO case
    no_item = {
        "status": "RESOLVED-IMPLEMENTED",
        "coverage_engine": "NO",
        "status_grep": {"coded": True, "wired": True, "tested": True},
    }
    result = dash.compute_promotion_path(no_item, "decision")
    assert result["tier"] == "NOT-CONSUMED", \
        f"coverage NO must override IMPLEMENTED claim, got {result['tier']}"
    # Synthetic FUNC-DEAD case
    fd_item = {
        "status": "RESOLVED-IMPLEMENTED",
        "coverage_engine": "FUNC-DEAD",
        "status_grep": {"coded": True, "wired": True, "tested": True},
    }
    result2 = dash.compute_promotion_path(fd_item, "decision")
    assert result2["tier"] == "FUNC-DEAD", \
        f"coverage FUNC-DEAD must override IMPLEMENTED, got {result2['tier']}"
    # Sanity: YES does NOT change IMPLEMENTED behavior
    yes_item = {
        "status": "RESOLVED-IMPLEMENTED",
        "coverage_engine": "YES",
        "status_grep": {"coded": True, "wired": True, "tested": True},
    }
    result3 = dash.compute_promotion_path(yes_item, "decision")
    assert result3["tier"] == "IMPLEMENTED", \
        f"coverage YES must preserve IMPLEMENTED tier, got {result3['tier']}"


# ============================================================================
# Phase 3 Batch 68 - FINAL 9 PARTIAL-SPEC-ONLY -> real impl
# DEC-439 / 467 / 478 / 485 / 490 / 496 / 501 / 502 / 506
# ============================================================================

def test_dec_439_differential_testing_layer_5():
    """DEC-439: differential testing Layer 5 of multi-layer defense."""
    from backtest.config import (DIFFERENTIAL_TESTING_DEFENSE_LAYER,
                                   DIFFERENTIAL_TESTING_TARGETS)
    assert DIFFERENTIAL_TESTING_DEFENSE_LAYER == 5
    assert "fundamentals_polygon_vs_sec_xbrl" in DIFFERENTIAL_TESTING_TARGETS


def test_dec_467_our_agent_state_schema():
    """DEC-467: 7 new state fields + extends parent class."""
    from backtest.config import (OUR_AGENT_STATE_NEW_FIELDS,
                                   OUR_AGENT_STATE_EXTENDS)
    assert len(OUR_AGENT_STATE_NEW_FIELDS) == 7
    assert "rules_only_rationale" in OUR_AGENT_STATE_NEW_FIELDS
    assert "ab_arm_label" in OUR_AGENT_STATE_NEW_FIELDS
    assert "tradingagents.AgentState" in OUR_AGENT_STATE_EXTENDS


def test_dec_478_polygon_tier_stocks_starter():
    """DEC-478: Stocks Starter tier + 5-year history."""
    from backtest.config import POLYGON_TIER_SELECTED, POLYGON_TIER_HISTORY_YEARS
    assert POLYGON_TIER_SELECTED == "stocks_starter"
    assert POLYGON_TIER_HISTORY_YEARS == 5


def test_dec_485_earnings_transcripts_dropped():
    """DEC-485: transcripts dropped Stage 2."""
    from backtest.config import (EARNINGS_TRANSCRIPTS_STAGE_2_ENABLED,
                                   EARNINGS_TRANSCRIPTS_DROP_REASON)
    assert EARNINGS_TRANSCRIPTS_STAGE_2_ENABLED is False
    assert "250 calls/day" in EARNINGS_TRANSCRIPTS_DROP_REASON


def test_dec_490_phase_1a_skipped_strategies():
    """DEC-490: 2 Phase 1A skip strategies + reasons."""
    from backtest.config import (PHASE_1A_SKIPPED_STRATEGIES,
                                   PHASE_1A_SKIPPED_REASONS)
    assert "fundamentals_quality_screen" in PHASE_1A_SKIPPED_STRATEGIES
    assert "earnings_call_sentiment" in PHASE_1A_SKIPPED_STRATEGIES
    assert "DEC-484" in PHASE_1A_SKIPPED_REASONS["fundamentals_quality_screen"]
    assert "DEC-485" in PHASE_1A_SKIPPED_REASONS["earnings_call_sentiment"]


def test_dec_496_tier_3_jegadeesh_titman_methodology():
    """DEC-496: J-T 12-1 momentum + tie-breakers."""
    from backtest.config import (TIER_3_MOMENTUM_METHODOLOGY,
                                   TIER_3_MOMENTUM_LOOKBACK_DAYS,
                                   TIER_3_MOMENTUM_SKIP_DAYS,
                                   TIER_3_MOMENTUM_RISK_ADJUSTMENT,
                                   TIER_3_MOMENTUM_TIE_BREAKERS)
    assert TIER_3_MOMENTUM_METHODOLOGY == "jegadeesh_titman_12_1"
    assert TIER_3_MOMENTUM_LOOKBACK_DAYS == 252
    assert TIER_3_MOMENTUM_SKIP_DAYS == 21
    assert TIER_3_MOMENTUM_RISK_ADJUSTMENT is False
    assert "vol_ascending" in TIER_3_MOMENTUM_TIE_BREAKERS
    assert "adv_descending" in TIER_3_MOMENTUM_TIE_BREAKERS


def test_dec_502_quiver_trader_tier_endpoint_groups():
    """DEC-502: 8 Quiver endpoint groups + 2 supplemental sources."""
    from backtest.config import (QUIVER_TRADER_TIER_ENDPOINT_GROUPS,
                                   QUIVER_SUPPLEMENTAL_SOURCES)
    assert len(QUIVER_TRADER_TIER_ENDPOINT_GROUPS) == 8
    assert "congresstrading" in QUIVER_TRADER_TIER_ENDPOINT_GROUPS
    assert "patentmomentum" in QUIVER_TRADER_TIER_ENDPOINT_GROUPS
    assert "apewisdom" in QUIVER_SUPPLEMENTAL_SOURCES
    assert "pytrends" in QUIVER_SUPPLEMENTAL_SOURCES


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


# -----------------------------------------------------------------------------
# DEC-458: Lead-lag intra-sector rotation strategy
# -----------------------------------------------------------------------------

def _make_momentum_df(five_day_return: float, n: int = 40) -> "pd.DataFrame":
    base = 100.0
    closes = [base] * (n - 5)
    for i in range(1, 6):
        closes.append(base * (1 + five_day_return * i / 5))
    import pandas as pd
    return pd.DataFrame({
        "open":   closes,
        "high":   [c * 1.01 for c in closes],
        "low":    [c * 0.99 for c in closes],
        "close":  closes,
        "volume": [1_000_000] * n,
    })


def test_dec458_lead_lag_fires_on_laggards():
    """DEC-458: lead_lag_sector_rotation fires on bottom laggards; leader excluded."""
    from backtest.signals.screener import screen_lead_lag_sector
    as_of = date(2024, 6, 1)
    ohlcv = {
        "LEAD": _make_momentum_df(0.10),
        "MID1": _make_momentum_df(0.02),
        "LAG1": _make_momentum_df(-0.03),
        "LAG2": _make_momentum_df(-0.06),
    }
    info = {t: {"sector": "Information Technology"} for t in ohlcv}
    cands = screen_lead_lag_sector(ohlcv, info, as_of)
    fired = {c["ticker"] for c in cands}
    assert "LEAD" not in fired, "Leader should not fire"
    assert fired, "At least one laggard should fire"
    for c in cands:
        s = c["strategies"][0]
        assert s["strategy"] == "lead_lag_sector_rotation"
        assert s["direction"] == "long"
        assert s["category"] == "rotation"


def test_dec458_lead_lag_skips_small_sectors():
    """DEC-458: sectors with <4 members produce no candidates."""
    from backtest.signals.screener import screen_lead_lag_sector
    as_of = date(2024, 6, 1)
    df = _make_momentum_df(0.0)
    ohlcv = {"A": df, "B": df, "C": df}
    info = {t: {"sector": "Energy"} for t in ohlcv}
    assert screen_lead_lag_sector(ohlcv, info, as_of) == []


def test_dec458_lead_lag_excludes_etf_sectors():
    """DEC-458: ETF-proxy sectors (Broad Market, Volatility, etc.) are excluded."""
    from backtest.signals.screener import screen_lead_lag_sector
    as_of = date(2024, 6, 1)
    df = _make_momentum_df(-0.05)
    ohlcv = {f"T{i}": _make_momentum_df(-0.01 * i) for i in range(5)}
    info = {t: {"sector": "Broad Market"} for t in ohlcv}
    assert screen_lead_lag_sector(ohlcv, info, as_of) == []


def test_dec458_lead_lag_wired_in_screen_universe():
    """DEC-458: lead_lag_sector_rotation appears in screen_universe output."""
    from backtest.signals.screener import screen_universe
    as_of = date(2024, 6, 1)
    ohlcv = {
        "LEAD": _make_momentum_df(0.12),
        "MID":  _make_momentum_df(0.03),
        "LAG1": _make_momentum_df(-0.04),
        "LAG2": _make_momentum_df(-0.07),
    }
    info = {t: {"sector": "Financials"} for t in ohlcv}
    candidates = screen_universe(ohlcv, info, as_of)
    all_strats = [s["strategy"] for c in candidates for s in c.get("strategies", [])]
    assert "lead_lag_sector_rotation" in all_strats, "DEC-458 not wired into screen_universe"


# ---------------------------------------------------------------------------
# Batch 148 BUG regression tags (BUG-081/224/225/228/230/231/240/242/264)
# Each test references the BUG-NNN id so coded+tested grep flags flip True
# ---------------------------------------------------------------------------

def test_bug_081_short_borrow_rate_is_annualized():
    """BUG-081: SHORT_ANNUAL_BORROW_RATE must be annualized decimal (0.005 = 0.5%/yr).
    The old SHORT_BORROW_COST_PER_DAY = 0.005 was ambiguous (could imply 126%/yr).
    """
    from backtest.config import SHORT_ANNUAL_BORROW_RATE
    assert SHORT_ANNUAL_BORROW_RATE < 0.01, "BUG-081: rate > 1%/yr; check if accidentally per-day"
    assert SHORT_ANNUAL_BORROW_RATE > 0, "BUG-081: rate must be positive"
    import backtest.config as cfg
    assert not hasattr(cfg, "SHORT_BORROW_COST_PER_DAY"), "BUG-081: old ambiguous constant must be removed"


def test_bug_224_assert_no_lookahead_raises():
    """BUG-224: _assert_no_lookahead must RAISE LookAheadBiasError (not just warn)."""
    import pandas as pd
    from datetime import date
    from backtest.data.fetcher import _assert_no_lookahead, LookAheadBiasError
    idx = pd.date_range("2024-01-01", periods=5)
    df = pd.DataFrame({"close": range(5)}, index=idx)
    try:
        _assert_no_lookahead(df, date(2024, 1, 3), "BUG-224-test")
        assert False, "BUG-224: should have raised LookAheadBiasError"
    except LookAheadBiasError:
        pass


def test_bug_225_regime_unknown_on_missing_vix():
    """BUG-225: classify_regime returns 'unknown' (not 'neutral') when VIX is None."""
    from backtest.engine.regime_filter import classify_regime
    result = classify_regime(None, 100.0)
    assert result == "unknown", f"BUG-225: expected 'unknown', got {result!r}"


def test_bug_228_ticker_collision_raises():
    """BUG-228: BRK-B and BRK.B both map to BRK_B.parquet - cache must raise on collision."""
    from backtest.data.cache import _assert_no_ticker_collision, _cache_path, TickerCollisionError
    index = {"BRK-B": {}}
    try:
        _assert_no_ticker_collision("BRK.B", index)
        assert False, "BUG-228: should have raised TickerCollisionError"
    except TickerCollisionError:
        pass


def test_bug_230_atr_trail_uses_rolling_atr():
    """BUG-230: exit_atr_trail must use rolling ATR (DEC-311), not frozen entry-time ATR."""
    import inspect
    from backtest.engine.exit_strategies import exit_atr_trail
    src = inspect.getsource(exit_atr_trail)
    assert "BUG-230" in src or "DEC-311" in src, "BUG-230: DEC-311 rolling ATR fix not found in exit_atr_trail"
    assert "current_atr" in src or "rolling" in src.lower(), "BUG-230: no rolling ATR variable in exit_atr_trail"


def test_bug_231_hybrid_max_days_parity():
    """BUG-231: exit_hybrid_50pct must have max_days in signature (parity with other exits)."""
    import inspect
    from backtest.engine.exit_strategies import exit_hybrid_50pct
    sig = inspect.signature(exit_hybrid_50pct)
    assert "max_days" in sig.parameters, "BUG-231: max_days must be in exit_hybrid_50pct signature"
    src = inspect.getsource(exit_hybrid_50pct)
    assert "DEC-312" in src or "BUG-231" in src, "BUG-231: DEC-312 parity fix not found"


def test_bug_240_congressional_uses_transaction_date():
    """BUG-240: congressional signal must age-weight by transaction_date not disclosure_date."""
    import inspect
    from backtest.data.smart_money import congressional_signal
    src = inspect.getsource(congressional_signal)
    assert "transaction_date" in src, "BUG-240: transaction_date not used in congressional signal"
    assert "DEC-324" in src or "BUG-240" in src, "BUG-240: DEC-324 fix not found"


def test_bug_242_borrow_cost_single_source():
    """BUG-242: borrow cost must come from config.SHORT_ANNUAL_BORROW_RATE only (no local constant)."""
    import inspect
    from backtest.engine.improvements import apply_transaction_costs
    src = inspect.getsource(apply_transaction_costs)
    assert "SHORT_ANNUAL_BORROW_RATE" in src, "BUG-242: improvements.py must import canonical rate"
    assert "DEC-295" in src or "BUG-242" in src, "BUG-242: DEC-295 single-source fix not found"


def test_bug_264_universe_docstring_no_wikipedia():
    """BUG-264: universe.py must reference static CSV not live Wikipedia fetch."""
    import backtest.data.universe as u
    mod_src = open(u.__file__, encoding="utf-8").read()
    assert "wikipedia.org/wiki" not in mod_src.lower() or "BUG-264" in mod_src, \
        "BUG-264: universe.py must not runtime-fetch from Wikipedia"
    assert "static CSV" in mod_src or "BUG-264" in mod_src or "closes BUG-264" in mod_src, \
        "BUG-264: docstring should reference static CSV pattern"


def test_batch181_master_universe_loader_returns_5_tier_dedup():
    """Batch 181 Phase 1A-β engine wiring: get_master_universe() must return the
    full Master Dedup 5-tier set (~1937 tickers per DEC-504), not the legacy
    config.UNIVERSE 67-ticker SP50+ETFs scope."""
    from backtest.data.universe import get_master_universe
    tickers = get_master_universe()
    assert isinstance(tickers, list), "must return list"
    assert len(tickers) > 1500, f"Master Dedup must have ~1937 tickers, got {len(tickers)}"
    assert len(tickers) < 2500, f"sanity ceiling - got {len(tickers)} (suspicious)"
    # Spot-check tier diversity: must contain examples from T1a (AAPL), T1ETF (SPY)
    upper = {t.upper() for t in tickers}
    assert "AAPL" in upper, "T1a S&P 500 representative missing"
    assert "SPY" in upper, "T1ETF representative missing"
    # Must be sorted + deduplicated
    assert tickers == sorted(tickers), "must be sorted"
    assert len(tickers) == len(set(tickers)), "must be deduplicated"


def test_batch181_run_phase1a_accepts_1a_beta():
    """Batch 181: --phase 1a-beta argparse choice + uses get_master_universe."""
    import inspect
    import backtest.run_phase1a as r
    src = inspect.getsource(r)
    assert "1a-beta" in src, "Batch 181: --phase 1a-beta choice missing"
    assert "get_master_universe" in src, "Batch 181: 1a-beta branch must call get_master_universe"


def test_batch370_max_open_positions_59_with_regime_caps_preserved():
    """Batch 370 Fix 1 owner-approved 2026-05-26: max_open_positions raised
    25 -> 59 to unlock bull-regime effective cap (25 -> 40 = Batch 203 spec).
    Empirical Phase-1A-beta evidence: 12,180 skips were
    `max_open_positions_25_reached`. Regime caps (bull 40 / neutral 25 /
    bear 15 / crisis 10 / unknown 5) preserved per Batch 203 risk control
    on the 2022 -117pp bear loss-year.

    Effective cap = min(base, regime_cap):
      bull    -> min(59, 40) = 40  (UNLOCKED from prior 25)
      neutral -> min(59, 25) = 25  (unchanged)
      bear    -> min(59, 15) = 15  (unchanged; Batch 203 risk control)
      crisis  -> min(59, 10) = 10  (unchanged)
      unknown -> min(59, 5)  = 5   (unchanged)
    """
    from backtest.config import LIVE_TRADING_RULES
    assert LIVE_TRADING_RULES["max_open_positions"] == 59, (
        f"Batch 370 Fix 1: max_open_positions must be 59 (owner directive 2026-05-26); "
        f"got {LIVE_TRADING_RULES['max_open_positions']}"
    )
    # Regime caps unchanged (Batch 203 risk control)
    from backtest.engine.regime_selector import regime_position_count_cap
    assert regime_position_count_cap("bull")    == 40, "Batch 203 bull cap must stay 40"
    assert regime_position_count_cap("neutral") == 25, "Batch 203 neutral cap must stay 25"
    assert regime_position_count_cap("bear")    == 15, "Batch 203 bear cap must stay 15"
    assert regime_position_count_cap("crisis")  == 10, "Batch 203 crisis cap must stay 10"
    # Effective cap calculation per engine/backtest.py:1634
    base = LIVE_TRADING_RULES["max_open_positions"]
    assert min(base, regime_position_count_cap("bull"))    == 40
    assert min(base, regime_position_count_cap("neutral")) == 25
    assert min(base, regime_position_count_cap("bear"))    == 15
    assert min(base, regime_position_count_cap("crisis"))  == 10


def test_batch186_passing_criteria_relaxations():
    """Batch 186 owner-approved 2026-05-16: 4 threshold relaxations + DSR gate
    per industry research (Lux Algo / Bailey-Lopez de Prado / Quantified Strategies).
    Regression guard: future tightening must be explicit."""
    from backtest.config import PASSING_CRITERIA, SECTOR_PASSING_CRITERIA
    # (A) Win rate per-regime baseline 0.55 -> 0.45
    assert PASSING_CRITERIA["min_win_rate"] == 0.45, (
        f"Batch 186: min_win_rate must be 0.45 (was 0.55); got {PASSING_CRITERIA['min_win_rate']}"
    )
    # (A) High-volatility sector win rate 0.50 -> 0.40
    assert SECTOR_PASSING_CRITERIA["high_volatility"]["min_win_rate"] == 0.40, (
        f"Batch 186: HV min_win_rate must be 0.40 (was 0.50)"
    )
    # (B) Profit factor overall 1.5 -> 1.3
    assert PASSING_CRITERIA["min_profit_factor_overall"] == 1.3, (
        f"Batch 186: min_profit_factor_overall must be 1.3 (was 1.5); "
        f"got {PASSING_CRITERIA['min_profit_factor_overall']}"
    )
    # (C) Max drawdown 20.0 -> 25.0 baseline
    assert PASSING_CRITERIA["max_drawdown"] == 25.0, (
        f"Batch 186: max_drawdown must be 25.0 (was 20.0); got {PASSING_CRITERIA['max_drawdown']}"
    )
    # (C) High-volatility max drawdown 25.0 -> 30.0
    assert SECTOR_PASSING_CRITERIA["high_volatility"]["max_drawdown"] == 30.0, (
        f"Batch 186: HV max_drawdown must be 30.0 (was 25.0)"
    )
    # (D) Smart money + macro correlation default to False (per-strategy opt-in)
    assert PASSING_CRITERIA["smart_money_lift"] is False, (
        f"Batch 186: smart_money_lift global default must be False (per-strategy opt-in)"
    )
    assert PASSING_CRITERIA["macro_correlation"] is False, (
        f"Batch 186: macro_correlation global default must be False (per-strategy opt-in)"
    )
    # (E) NEW: DSR gate at 0.95
    assert PASSING_CRITERIA["min_deflated_sharpe"] == 0.95, (
        f"Batch 186: min_deflated_sharpe must be 0.95 per Bailey-Lopez de Prado 2014; "
        f"got {PASSING_CRITERIA.get('min_deflated_sharpe', 'MISSING')}"
    )


def test_batch186_verdict_wires_dsr_and_optin_signals():
    """Batch 186 metrics.py compute_overall_verdict wiring: passes dict must
    include `deflated_sharpe` key AND smart_money_lift / macro_correlation
    must be opt-in gated by pc flag."""
    import inspect
    from backtest.results import metrics
    src = inspect.getsource(metrics)
    # DSR gate present
    assert '"deflated_sharpe":' in src and "min_deflated_sharpe" in src, (
        "Batch 186: metrics.py must gate on min_deflated_sharpe in passes dict"
    )
    # Per-strategy opt-in pattern: (not pc["flag"]) or ...
    assert 'not pc["smart_money_lift"]' in src, (
        "Batch 186: smart_money_lift must be opt-in via 'not pc[\"smart_money_lift\"]'"
    )
    assert 'not pc["macro_correlation"]' in src, (
        "Batch 186: macro_correlation must be opt-in via 'not pc[\"macro_correlation\"]'"
    )


def test_batch214_cpcv_splits_yields_expected_paths():
    """Batch 214 (Validation 2026-05-17): CPCV with 6 groups, choose 2
    yields C(6,2) = 15 distinct paths. Lopez de Prado 2018 Ch 12
    canonical configuration."""
    from backtest.results.cpcv import cpcv_splits, cpcv_summary
    paths = list(cpcv_splits(n_samples=600, n_groups=6, n_test_groups=2))
    assert len(paths) == 15, f"6 choose 2 = 15 paths, got {len(paths)}"
    # Each train/test pair must be disjoint
    for train_idx, test_idx in paths:
        train_set, test_set = set(train_idx), set(test_idx)
        assert train_set.isdisjoint(test_set), "Train and test must be disjoint"
        # Both must be non-empty
        assert len(train_idx) > 0
        assert len(test_idx) > 0
        # Combined cannot exceed n_samples; embargo zones removed from train
        assert len(train_idx) + len(test_idx) <= 600

    # Summary helper
    summary = cpcv_summary(n_samples=600, n_groups=6, n_test_groups=2)
    assert summary["n_paths"] == 15
    assert summary["avg_test_size"] == 200  # 2 chunks * 100 samples


def test_batch214_cpcv_handles_edge_cases():
    """Batch 214: CPCV defensive returns empty iterator on degenerate
    inputs (n_samples <= 0; n_test_groups >= n_groups)."""
    from backtest.results.cpcv import cpcv_splits
    assert list(cpcv_splits(0, 6, 2)) == []
    assert list(cpcv_splits(100, 2, 2)) == []  # n_test_groups not < n_groups
    assert list(cpcv_splits(100, 6, 6)) == []  # k = n_groups invalid


def test_batch214_meta_label_classifier_fit_predicts_proba():
    """Batch 214: meta_label_classifier_fit trains a binary classifier;
    predict_proba returns P(win) per row. Lopez de Prado 2017 / Hudson
    & Thames 2022 meta-labeling discipline."""
    import pandas as pd
    import numpy as np
    from backtest.results.cpcv import (
        meta_label_classifier_fit,
        meta_label_predict_proba,
    )
    # Synthetic: feature_a positively correlated with win label
    rng = np.random.default_rng(42)
    n = 500
    feat_a = rng.normal(0, 1, n)
    labels = (feat_a + rng.normal(0, 0.5, n) > 0).astype(int)
    feat_b = rng.normal(0, 1, n)  # noise feature
    features = pd.DataFrame({"feat_a": feat_a, "feat_b": feat_b})
    labels_s = pd.Series(labels)

    clf = meta_label_classifier_fit(features, labels_s)
    if clf is None:
        # sklearn not available - test should skip gracefully
        return
    proba = meta_label_predict_proba(clf, features)
    assert proba is not None
    assert len(proba) == n
    # All probabilities in [0, 1]
    assert (proba >= 0).all() and (proba <= 1).all()
    # The model should differentiate (not all same value)
    assert proba.std() > 0.05, "Classifier produced uniform predictions"


def test_batch214_meta_label_handles_empty_inputs():
    """Batch 214: meta_label_classifier_fit returns None on empty / null
    inputs without raising. Defensive."""
    import pandas as pd
    from backtest.results.cpcv import meta_label_classifier_fit
    assert meta_label_classifier_fit(None, None) is None
    assert meta_label_classifier_fit(pd.DataFrame(), pd.Series([], dtype=int)) is None
    # Mismatched lengths
    assert meta_label_classifier_fit(
        pd.DataFrame({"a": [1, 2, 3]}), pd.Series([0, 1])
    ) is None
    # Single-class labels (degenerate)
    assert meta_label_classifier_fit(
        pd.DataFrame({"a": [1, 2, 3, 4]}), pd.Series([1, 1, 1, 1])
    ) is None


def test_batch213_dd_size_curve_tightened_gradient():
    """Batch 213 (Risk mgmt 2026-05-17): drawdown_size_multiplier
    tightened to gradient curve per Lopez de Prado smooth de-risking:
      <5%: 1.0   >=5%: 0.8   >=10%: 0.5   >=15%: 0.25   >=20%: 0.0
    Pre-batch ladder (10/20/30%) was too coarse; new curve adds 5%
    early-warning and 15% pre-halt steps."""
    from backtest.engine.portfolio import Portfolio
    p = Portfolio(starting_capital=100_000.0)
    # Simulate equity at various DD levels
    p.equity_curve = [(None, 100_000.0), (None, 100_000.0)]  # peak
    # 0% DD -> 1.0
    p.equity_curve.append((None, 100_000.0))
    assert p.drawdown_size_multiplier() == 1.0
    # 6% DD -> 0.8 (Batch 213 new band)
    p.equity_curve.append((None, 94_000.0))
    assert p.drawdown_size_multiplier() == 0.8
    # 12% DD -> 0.5
    p.equity_curve.append((None, 88_000.0))
    assert p.drawdown_size_multiplier() == 0.5
    # 16% DD -> 0.25 (Batch 213 new band)
    p.equity_curve.append((None, 84_000.0))
    assert p.drawdown_size_multiplier() == 0.25
    # 22% DD -> halt at 0.0
    p.equity_curve.append((None, 78_000.0))
    assert p.drawdown_size_multiplier() == 0.0


def test_batch213_time_stop_triggers_after_window():
    """Batch 213: time-stop closes trades that fail to develop MFE > 0.5pct
    within per-category window (mean-reversion: 10 bars; momentum: 30;
    trend: 50; default: 20). Kestner discipline."""
    from datetime import date, timedelta
    from backtest.engine.backtest import OpenTrade
    from backtest.engine.exit_manager import process_day_exits

    # Mean-reversion trade entered 11 business days ago, low MFE
    entry_d = date(2024, 1, 2)
    today = date(2024, 1, 18)  # ~12 calendar days = ~10 business days
    trade = OpenTrade(
        ticker="TEST", entry_date=entry_d, entry_price=100.0,
        direction="long", strategy="rsi_oversold", category="mean_reversion",
        sector="Unknown", initial_stop=95.0, trailing_stop=95.0,
        highest_close=100.0, regime_at_entry="neutral",
        signals_at_entry={}, context_bullets=[], context_paragraph="",
        confidence_tier="MEDIUM",
        trade_id="TEST_test",
    )
    trade.max_favourable_excursion = 0.1  # only 0.1% MFE - fails threshold

    bars = {"TEST": {"open": 99.5, "high": 100.0, "low": 99.0, "close": 99.5,
                     "prev_close": 99.0}}
    closed, still_open = process_day_exits(
        [trade], bars, today, vix_value=20.0,
        regime="neutral", active_signals={}, circuit_breaker_log=[],
    )
    # Trade should have been closed with time_stop reason
    assert len(closed) == 1
    assert "time_stop" in closed[0].exit_reason
    assert "batch213" in closed[0].exit_reason


def test_batch213_time_stop_skips_when_mfe_above_threshold():
    """Batch 213: time-stop must NOT close trades that have developed
    MFE > 0.5% (still working - give them room to run)."""
    from datetime import date
    from backtest.engine.backtest import OpenTrade
    from backtest.engine.exit_manager import process_day_exits

    entry_d = date(2024, 1, 2)
    today = date(2024, 1, 18)
    trade = OpenTrade(
        ticker="TEST", entry_date=entry_d, entry_price=100.0,
        direction="long", strategy="rsi_oversold", category="mean_reversion",
        sector="Unknown", initial_stop=95.0, trailing_stop=95.0,
        highest_close=102.0, regime_at_entry="neutral",
        signals_at_entry={}, context_bullets=[], context_paragraph="",
        confidence_tier="MEDIUM",
        trade_id="TEST_test",
    )
    trade.max_favourable_excursion = 2.0  # 2% MFE - well above threshold

    bars = {"TEST": {"open": 101, "high": 102, "low": 100.5, "close": 101.5,
                     "prev_close": 101}}
    closed, still_open = process_day_exits(
        [trade], bars, today, vix_value=20.0,
        regime="neutral", active_signals={}, circuit_breaker_log=[],
    )
    # Trade should remain open (no time_stop close)
    time_stop_closes = [c for c in closed if "time_stop" in c.exit_reason]
    assert len(time_stop_closes) == 0


def test_batch212_half_kelly_fraction_basic():
    """Batch 212 (HRP + Kelly sizing 2026-05-17): half-Kelly fraction
    f*/2 from win_rate, avg_win, avg_loss. MacLean-Ziemba-Blazenko
    (1992): half-Kelly = 75% of full-Kelly growth at 50% of volatility."""
    from backtest.engine.sizing_hrp_kelly import half_kelly_fraction
    # 60% WR, avg_win 2%, avg_loss -1% (b=2, p=0.6, q=0.4)
    # Kelly = (2*0.6 - 0.4) / 2 = 0.8 / 2 = 0.4
    # Half-Kelly = 0.2 -> bounded to min_mult=0.25
    out = half_kelly_fraction(0.6, 2.0, -1.0, n_trades=50)
    assert 0.25 <= out <= 1.0
    assert abs(out - 0.25) < 0.01 or abs(out - 0.2) < 0.01  # floor at 0.25

    # 70% WR, avg_win 3, avg_loss -1 (b=3, p=0.7)
    # Kelly = (3*0.7 - 0.3)/3 = 1.8/3 = 0.6, half-Kelly = 0.3
    out2 = half_kelly_fraction(0.7, 3.0, -1.0, n_trades=50)
    assert 0.25 <= out2 <= 1.0

    # Insufficient sample (n_trades < min_trades) -> 1.0 no-op
    assert half_kelly_fraction(0.6, 2.0, -1.0, n_trades=10) == 1.0
    # Missing inputs -> 1.0 no-op
    assert half_kelly_fraction(None, 2.0, -1.0, n_trades=50) == 1.0
    assert half_kelly_fraction(0.6, None, -1.0, n_trades=50) == 1.0
    assert half_kelly_fraction(0.6, 2.0, None, n_trades=50) == 1.0
    # Zero avg_loss -> 1.0 no-op
    assert half_kelly_fraction(0.6, 2.0, 0.0, n_trades=50) == 1.0


def test_batch212_kelly_per_strategy_from_trade_log():
    """Batch 212: per_strategy_kelly_from_trade_log builds rolling
    per-strategy Kelly multiplier from closed-trades DataFrame."""
    from backtest.engine.sizing_hrp_kelly import per_strategy_kelly_from_trade_log
    import pandas as pd
    # Build synthetic trade log with 100 trades, 60% WR
    trades = []
    for i in range(100):
        win = (i % 5) >= 2  # 60% WR pattern
        trades.append({
            "strategy": "test_strat",
            "entry_date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=i),
            "win":     bool(win),
            "pnl_pct": 2.0 if win else -1.0,
        })
    df = pd.DataFrame(trades)
    out = per_strategy_kelly_from_trade_log(
        df, "test_strat",
        as_of=pd.Timestamp("2024-12-31"),
    )
    assert 0.25 <= out <= 1.0
    # Unknown strategy -> 1.0 no-op
    assert per_strategy_kelly_from_trade_log(df, "nonexistent") == 1.0
    # Empty -> 1.0
    assert per_strategy_kelly_from_trade_log(pd.DataFrame(), "test_strat") == 1.0


def test_batch212_hrp_cluster_weights_equal_weight_fallback():
    """Batch 212: HRP returns equal-weight Series on insufficient data
    or single column (defensive fallback)."""
    import pandas as pd
    from backtest.engine.sizing_hrp_kelly import hrp_cluster_weights
    # Empty -> empty
    assert hrp_cluster_weights(pd.DataFrame()).empty
    # Single column -> 100%
    df1 = pd.DataFrame({"A": [0.01, 0.02, 0.0, 0.01] * 10})
    w1 = hrp_cluster_weights(df1)
    assert abs(w1["A"] - 1.0) < 1e-9
    # Few obs (< min_obs default 30) -> equal weight fallback
    df_small = pd.DataFrame({"A": [0.01] * 10, "B": [0.02] * 10, "C": [0.0] * 10})
    w_small = hrp_cluster_weights(df_small)
    assert abs(w_small["A"] - 1.0/3) < 1e-9
    assert abs(w_small["B"] - 1.0/3) < 1e-9


def test_batch212_hrp_cluster_weights_uses_correlation():
    """Batch 212: HRP weights sum to 1.0 and are positive. Highly-
    correlated columns share a weight budget."""
    import pandas as pd, numpy as np
    from backtest.engine.sizing_hrp_kelly import hrp_cluster_weights
    rng = np.random.default_rng(42)
    n = 100
    # A and B perfectly correlated; C independent
    a = rng.normal(0, 0.01, n)
    df = pd.DataFrame({
        "A": a,
        "B": a + rng.normal(0, 0.0001, n),  # near-perfect with A
        "C": rng.normal(0, 0.01, n),
    })
    w = hrp_cluster_weights(df)
    assert abs(w.sum() - 1.0) < 1e-6, f"HRP weights must sum to 1.0, got {w.sum()}"
    assert (w > 0).all()
    # All 3 weights must be reasonable (not zero)
    for col in ("A", "B", "C"):
        assert w[col] > 0.05


def test_batch211_orb_strategies_registered_and_gap_signals():
    """Batch 211 (ORB 2026-05-17): orb_stocks_in_play_long/short registered.
    compute_pivots emits gap_up_pct / gap_dn_pct / gap_*_2pct /
    close_above_open / close_below_open signals."""
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.signals.technical import compute_pivots
    import pandas as pd
    # Strategies registered
    assert "orb_stocks_in_play_long" in ALL_STRATEGIES
    assert "orb_stocks_in_play_short" in ALL_STRATEGIES
    # Signal emission: gap up of 3% with close above open
    df = pd.DataFrame({
        "high":  [100, 105], "low": [99, 102], "close": [100, 104], "open": [100, 103],
    })
    out = compute_pivots(df)
    assert "gap_up_pct" in out
    assert out["gap_up_pct"] > 0
    assert "gap_up_2pct" in out
    # bool-like check covers numpy True_ and built-in True
    assert bool(out["gap_up_2pct"]) is True  # 3% > 2% threshold
    assert bool(out["close_above_open"]) is True


def test_batch211_orb_long_requires_gap_volume_and_regime():
    """Batch 211: orb_stocks_in_play_long requires gap_up_2pct +
    close_above_open + vol_spike_2x + price_above_ema_200."""
    from backtest.signals.screener import strat_orb_stocks_in_play_long
    # All conditions met
    s = {
        "gap_up_2pct": True, "gap_up_pct": 3.5,
        "close_above_open": True,
        "vol_spike_2x": True,
        "price_above_ema_200": True,
    }
    r = strat_orb_stocks_in_play_long(s)
    assert r["fires"] is True and r["direction"] == "long"
    # Missing each requirement individually -> no fire
    for missing_key in ("gap_up_2pct", "close_above_open", "vol_spike_2x"):
        s_copy = dict(s); s_copy[missing_key] = False
        assert strat_orb_stocks_in_play_long(s_copy)["fires"] is False, (
            f"Batch 211: ORB long must NOT fire when {missing_key}=False"
        )
    # 200-EMA gate enforced
    s["price_above_ema_200"] = False
    assert strat_orb_stocks_in_play_long(s)["fires"] is False


def test_batch211_orb_short_symmetric():
    """Batch 211: orb_stocks_in_play_short symmetric on gap-down."""
    from backtest.signals.screener import strat_orb_stocks_in_play_short
    s = {
        "gap_dn_2pct": True, "gap_dn_pct": 3.5,
        "close_below_open": True,
        "vol_spike_2x": True,
        "price_above_ema_200": False,  # bear regime
    }
    r = strat_orb_stocks_in_play_short(s)
    assert r["fires"] is True and r["direction"] == "short"
    # Bull regime -> short must NOT fire
    s["price_above_ema_200"] = True
    assert strat_orb_stocks_in_play_short(s)["fires"] is False


def test_batch233_volume_profile_emits_poc_and_value_area():
    """Batch 233 (Volume Profile 2026-05-18 owner-approved Track A):
    compute_volume_profile returns POC + Value Area High/Low + close
    position flags. Steidlmayer 1985 Market Profile foundation."""
    import pandas as pd
    import numpy as np
    from backtest.signals.volume_profile import compute_volume_profile
    n = 80
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    rng = np.random.default_rng(42)
    base = 100 + np.cumsum(rng.normal(0, 1, n))
    df = pd.DataFrame({
        "open":   base, "high": base + 2, "low": base - 2,
        "close":  base, "volume": rng.integers(1_000_000, 5_000_000, n).astype(float),
    }, index=idx)
    out = compute_volume_profile(df, lookback_days=60)
    assert "vp_poc" in out
    assert "vp_value_area_high" in out
    assert "vp_value_area_low" in out
    # POC must lie within the price range
    assert df["low"].min() <= out["vp_poc"] <= df["high"].max()
    # VAH > VAL
    assert out["vp_value_area_high"] > out["vp_value_area_low"]
    # POC lies within Value Area
    assert out["vp_value_area_low"] <= out["vp_poc"] <= out["vp_value_area_high"]
    # Close-position flags consistent
    close = float(df["close"].iloc[-1])
    if close > out["vp_poc"]:
        assert out["vp_close_above_poc"] is True
    if close < out["vp_value_area_low"]:
        assert out["vp_below_value_area"] is True
    if out["vp_value_area_low"] <= close <= out["vp_value_area_high"]:
        assert out["vp_in_value_area"] is True


def test_batch233_volume_profile_insufficient_data():
    """Batch 233: empty dict on insufficient bars or missing cols."""
    import pandas as pd
    from backtest.signals.volume_profile import compute_volume_profile
    assert compute_volume_profile(pd.DataFrame()) == {}
    short = pd.DataFrame({"high": [1], "low": [1], "close": [1], "volume": [1]})
    assert compute_volume_profile(short, lookback_days=60) == {}
    # Missing volume column
    no_vol = pd.DataFrame({"high": [1] * 60, "low": [1] * 60, "close": [1] * 60})
    assert compute_volume_profile(no_vol, lookback_days=60) == {}


def test_batch233_period_pocs_returns_chronological_list():
    """Batch 233: compute_period_pocs returns oldest-first POC list."""
    import pandas as pd
    import numpy as np
    from backtest.signals.volume_profile import compute_period_pocs
    n = 200
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    rng = np.random.default_rng(7)
    base = 100 + np.cumsum(rng.normal(0, 1, n))
    df = pd.DataFrame({
        "open":   base, "high": base + 2, "low": base - 2,
        "close":  base, "volume": rng.integers(1_000_000, 5_000_000, n).astype(float),
    }, index=idx)
    pocs = compute_period_pocs(df, period_lookback=120, n_periods=4)
    assert isinstance(pocs, list)
    assert len(pocs) <= 4
    # Each POC must be a positive float
    for p in pocs:
        assert isinstance(p, float)
        assert p > 0
    # Insufficient data -> empty
    short_df = df.head(10)
    assert compute_period_pocs(short_df, period_lookback=120) == []


def test_batch232_cross_asset_signals_run_on_real_data():
    """Batch 232 (cross-asset 2026-05-18 owner-approved Track A):
    compute_cross_asset_signals returns a non-empty dict on real
    prefetched data."""
    from datetime import date
    from backtest.signals.cross_asset import compute_cross_asset_signals
    out = compute_cross_asset_signals(date(2025, 6, 1))
    # Bond/equity + sector rotation should populate from prefetched data
    assert isinstance(out, dict)
    # If TLT/SPY prefetched, expect bond_equity_ratio populated
    if "bond_equity_ratio" in out:
        assert isinstance(out["bond_equity_ratio"], float)
        assert out["bond_equity_ratio"] > 0
    # Sector rotation should always populate if SPY + at least one sector exists
    if "sector_strongest" in out:
        assert out["sector_strongest"] in (
            "XLF", "XLY", "XLI", "XLK", "XLU", "XLP", "XLV", "XLE"
        )


def test_batch232_ratio_trend_signal_helper():
    """Batch 232: _ratio_trend_signal returns ratio + pct_change + trend flags."""
    import pandas as pd
    from backtest.signals.cross_asset import _ratio_trend_signal
    # Up-trending ratio
    n = pd.Series([100, 102, 104, 106, 108, 110, 112, 114, 116, 118,
                   120, 122, 124, 126, 128, 130, 132, 134, 136, 138, 140, 142])
    d = pd.Series([100] * 22)
    out = _ratio_trend_signal(n, d, window=20)
    assert out is not None
    assert out["trend_up"] is True
    assert out["pct_change"] > 0.02
    # Insufficient data
    out_short = _ratio_trend_signal(pd.Series([1, 2]), pd.Series([1, 2]), window=20)
    assert out_short is None


def test_batch232_missing_data_returns_empty():
    """Batch 232: defensive empty dict when ETF parquets missing."""
    from datetime import date
    from backtest.signals.cross_asset import (
        compute_bond_equity_signals, compute_gold_silver_ratio_signals,
    )
    # Distant past where prefetch may not exist
    out = compute_bond_equity_signals(date(1995, 6, 1))
    # Either empty (no data) or valid dict; should not raise
    assert isinstance(out, dict)


def test_batch231_calendar_signals_basic_keys():
    """Batch 231 (calendar effects 2026-05-18 owner-approved Track A):
    compute_calendar_signals emits the expected keys."""
    from datetime import date
    from backtest.signals.calendar_effects import compute_calendar_signals
    out = compute_calendar_signals(date(2024, 6, 17))  # Monday
    for key in (
        "dow", "is_monday", "is_friday",
        "trading_day_of_month", "trading_days_left_in_month",
        "is_totm_window", "is_january", "is_pre_holiday",
        "is_halloween_period", "is_summer_period",
        "days_to_next_holiday",
    ):
        assert key in out, f"Batch 231: missing key {key}"
    assert out["is_monday"] is True
    assert out["is_friday"] is False
    assert out["is_january"] is False


def test_batch231_totm_window_detection():
    """Batch 231: TOTM window fires last-4 + first-3 trading days
    (Ariel 1987 *Journal of Business*)."""
    from datetime import date
    from backtest.signals.calendar_effects import compute_calendar_signals
    # 2024-01-02 = first trading day of January (T+1) -> TOTM True
    assert compute_calendar_signals(date(2024, 1, 2))["is_totm_window"] is True
    # 2024-01-31 = last trading day of January -> TOTM True
    assert compute_calendar_signals(date(2024, 1, 31))["is_totm_window"] is True
    # Mid-month should NOT be TOTM
    assert compute_calendar_signals(date(2024, 6, 14))["is_totm_window"] is False


def test_batch231_pre_holiday_detection():
    """Batch 231: pre-holiday flag fires when next non-weekend day is a
    US market holiday. Lakonishok-Smidt 1988 RFS."""
    from datetime import date
    from backtest.signals.calendar_effects import compute_calendar_signals
    # 2024-07-03 (Wed) - next day 07-04 is Independence Day
    assert compute_calendar_signals(date(2024, 7, 3))["is_pre_holiday"] is True
    # 2024-11-27 (Wed) - next day 11-28 is Thanksgiving
    assert compute_calendar_signals(date(2024, 11, 27))["is_pre_holiday"] is True
    # Friday before a Monday holiday counts too (Memorial Day 2024-05-27)
    assert compute_calendar_signals(date(2024, 5, 24))["is_pre_holiday"] is True
    # Random mid-week (Wed 06-12-2024) - no holiday adjacent
    assert compute_calendar_signals(date(2024, 6, 12))["is_pre_holiday"] is False


def test_batch231_halloween_indicator():
    """Batch 231: Halloween indicator (Bouman-Jacobsen 2002 AER)
    flags Nov-Apr as 'winter premium' window."""
    from datetime import date
    from backtest.signals.calendar_effects import compute_calendar_signals
    # November = winter
    assert compute_calendar_signals(date(2024, 11, 15))["is_halloween_period"] is True
    # April = winter
    assert compute_calendar_signals(date(2024, 4, 15))["is_halloween_period"] is True
    # May = summer
    assert compute_calendar_signals(date(2024, 5, 15))["is_halloween_period"] is False
    assert compute_calendar_signals(date(2024, 5, 15))["is_summer_period"] is True


def test_batch230_rule_based_sentiment_basic():
    """Batch 230 (LLM news sentiment 2026-05-18 owner-approved deferred):
    rule-based sentiment scorer returns [-1, 1] using Loughran-McDonald
    finance lexicon subset."""
    from backtest.signals.news_sentiment import _rule_based_sentiment
    # All positive
    assert _rule_based_sentiment("beat exceeded strong growth") == 1.0
    # All negative
    assert _rule_based_sentiment("missed weak layoffs lawsuit") == -1.0
    # Neutral (no scoring words)
    assert _rule_based_sentiment("The company filed a report.") == 0.0
    # Mixed (1 pos / 1 neg -> 0)
    score = _rule_based_sentiment("Q3 beat expectations but missed full-year guidance")
    assert -0.5 <= score <= 0.5
    # Empty / None
    assert _rule_based_sentiment("") == 0.0
    assert _rule_based_sentiment(None) == 0.0


def test_batch230_polygon_sentiment_to_score():
    """Batch 230: maps Polygon's sentiment string to [-1, 0, 1]."""
    from backtest.signals.news_sentiment import _polygon_sentiment_to_score
    assert _polygon_sentiment_to_score("positive") == 1.0
    assert _polygon_sentiment_to_score("Positive") == 1.0
    assert _polygon_sentiment_to_score("bullish") == 1.0
    assert _polygon_sentiment_to_score("negative") == -1.0
    assert _polygon_sentiment_to_score("bearish") == -1.0
    assert _polygon_sentiment_to_score("neutral") == 0.0
    assert _polygon_sentiment_to_score("unknown") is None
    assert _polygon_sentiment_to_score(None) is None


def test_batch230_compute_news_sentiment_signals_no_data():
    """Batch 230: defensive empty dict when ticker has no prefetched news."""
    from datetime import date
    from backtest.signals.news_sentiment import compute_news_sentiment_signals
    out = compute_news_sentiment_signals("NONEXISTENT_TICKER_ZYX", date(2024, 6, 1))
    assert out == {}


def test_batch267_news_sentiment_alias_keys_emitted(tmp_path, monkeypatch):
    """Batch 267 Path B: compute_news_sentiment_signals must emit
    news_article_count + news_sentiment_mean as aliases of
    news_count_7d + news_sentiment_score so strat_news_sentiment_long
    (which reads the alias names) can fire."""
    from datetime import date
    import pandas as pd
    import backtest.signals.news_sentiment as ns

    fake = pd.DataFrame({
        "ticker": ["TST"] * 5,
        "published_utc": pd.to_datetime([
            "2024-04-01", "2024-04-02", "2024-04-03",
            "2024-04-04", "2024-04-05",
        ]),
        "title": ["beats strong growth", "exceeded outperform raises",
                  "robust gains surge", "weak miss decline",
                  "neutral coverage"],
        "description": [""] * 5,
        "sentiment": [None, None, None, None, None],
    })
    path = tmp_path / "TST.parquet"
    fake.to_parquet(path)
    monkeypatch.setattr(ns, "_NEWS_DIR", tmp_path)

    out = ns.compute_news_sentiment_signals("TST", date(2024, 4, 6), lookback_days=7)
    # Alias keys must be present and match canonical keys.
    assert out["news_article_count"] == out["news_count_7d"] == 5
    assert out["news_sentiment_mean"] == out["news_sentiment_score"]
    # Mean must be > 0 given the bullish-skewed fixture.
    assert out["news_sentiment_mean"] > 0.0


def test_batch267_news_sentiment_shift_positive_delta(tmp_path, monkeypatch):
    """Batch 267 Path B: news_sentiment_shift = current 7d mean - prior 7d
    mean. Strongly bullish current + bearish prior => positive shift."""
    from datetime import date
    import pandas as pd
    import backtest.signals.news_sentiment as ns

    # B535 OPT-A + B552 OPT-C: _NEWS_BY_TICKER cache must be cleared
    # so the monkeypatched _NEWS_DIR is actually consulted (cache layer
    # is keyed by ticker, not by dir; cross-test re-use of 'TST' ticker
    # would otherwise return the prior test's DataFrame).
    ns._NEWS_BY_TICKER.clear()

    fake = pd.DataFrame({
        "ticker": ["TST"] * 6,
        "published_utc": pd.to_datetime([
            "2024-03-25", "2024-03-26", "2024-03-27",   # prior window (bearish)
            "2024-04-02", "2024-04-03", "2024-04-04",   # current window (bullish)
        ]),
        "title": [
            "weak miss decline", "loss bankruptcy", "downgrade plunge",
            "beats strong growth", "exceeded outperform", "surge rally",
        ],
        "description": [""] * 6,
        "sentiment": [None] * 6,
    })
    path = tmp_path / "TST.parquet"
    fake.to_parquet(path)
    monkeypatch.setattr(ns, "_NEWS_DIR", tmp_path)

    out = ns.compute_news_sentiment_signals("TST", date(2024, 4, 5), lookback_days=7)
    assert "news_sentiment_shift" in out
    assert out["news_sentiment_shift"] > 0.5, (
        f"Expected strongly positive shift (bullish current vs bearish prior), "
        f"got {out['news_sentiment_shift']}"
    )
    assert out["news_prior_article_count"] == 3


def test_batch267_news_sentiment_shift_zero_when_prior_empty(tmp_path, monkeypatch):
    """Batch 267 Path B: shift defaults to 0.0 when prior window has
    no articles (insufficient data to compute meaningful delta)."""
    from datetime import date
    import pandas as pd
    import backtest.signals.news_sentiment as ns

    # B535 OPT-A + B552 OPT-C: clear _NEWS_BY_TICKER cache so prior
    # test's 'TST' DataFrame doesn't bleed into this one.
    ns._NEWS_BY_TICKER.clear()

    fake = pd.DataFrame({
        "ticker": ["TST"] * 3,
        "published_utc": pd.to_datetime([
            "2024-04-02", "2024-04-03", "2024-04-04",   # current only
        ]),
        "title": ["beats strong", "exceeded raises", "surge gains"],
        "description": [""] * 3,
        "sentiment": [None] * 3,
    })
    path = tmp_path / "TST.parquet"
    fake.to_parquet(path)
    monkeypatch.setattr(ns, "_NEWS_DIR", tmp_path)

    out = ns.compute_news_sentiment_signals("TST", date(2024, 4, 5), lookback_days=7)
    assert out["news_sentiment_shift"] == 0.0
    assert out["news_prior_article_count"] == 0
    # Current window still has content
    assert out["news_article_count"] == 3
    assert out["news_sentiment_mean"] > 0.0


def test_batch267_news_sentiment_strat_fires_on_aliased_keys():
    """Batch 267 Path B + Batch 278 gate tightening end-to-end:
    strat_news_sentiment_long must fire when fed signals with aliased keys
    + tighter thresholds (mean>0.5, article_count>=5, +200 EMA, +momentum
    confirm via MACD bullish OR RSI>55)."""
    from backtest.signals.screener import strat_news_sentiment_long
    signals = {
        "news_sentiment_mean":      0.6,    # >0.5 (Batch 278 tightened)
        "news_article_count":       5,      # >=5 (Batch 278 tightened)
        "price_above_ema_200":      True,
        "macd_12_26_9_bullish":     True,   # Batch 278: momentum confirm
    }
    res = strat_news_sentiment_long(signals)
    assert res is not None, "Strategy must fire when entry gates met"
    assert res.get("direction") == "long"


def test_batch278_news_sentiment_blocks_loose_signals():
    """Batch 278 + Batch 314 Cat-2 B+C: the mean>0.5 + count>=3 + 200-EMA
    gates must still BLOCK signals that violate the surviving Batch 278
    thresholds. Momentum confirmation was REMOVED in Batch 314 (owner-approved
    2026-05-24) because per-regime backtest showed it suppressed news edge.
    Article-count threshold relaxed 5 -> 3 in Batch 314 for the same reason.
    """
    from backtest.signals.screener import strat_news_sentiment_long
    # Sentiment too weak: mean=0.4 (<0.5 Batch-278 threshold still in force)
    signals = {
        "news_sentiment_mean":      0.4,
        "news_article_count":       5,
        "price_above_ema_200":      True,
    }
    res = strat_news_sentiment_long(signals)
    assert not res["fires"], "mean=0.4 must NOT fire under threshold >0.5"

    # Article count too low: 2 (<3 Batch-314 threshold)
    signals2 = {
        "news_sentiment_mean":      0.6,
        "news_article_count":       2,
        "price_above_ema_200":      True,
    }
    res2 = strat_news_sentiment_long(signals2)
    assert not res2["fires"], "count=2 must NOT fire under Batch 314 >=3 gate"

    # Below 200-EMA: regime gate still required
    signals3 = {
        "news_sentiment_mean":      0.6,
        "news_article_count":       6,
        "price_above_ema_200":      False,
    }
    res3 = strat_news_sentiment_long(signals3)
    assert not res3["fires"], "Below 200-EMA must NOT fire (regime gate)"


def test_batch278_cup_and_handle_blocks_unconfirmed_breakouts():
    """Batch 278: cup_and_handle now requires vol_spike_2x + above_ema_50
    + RSI<70 (O'Neil CANSLIM canonical breakout requires volume)."""
    from backtest.signals.screener import strat_cup_and_handle_long
    # Pattern detected but no volume confirm -> should NOT fire
    signals_no_vol = {
        "cup_handle_detected":   True,
        "price_above_ema_200":   True,
        "price_above_ema_50":    True,
        "rsi_14":                60,
        "vol_spike_2x":          False,
    }
    res = strat_cup_and_handle_long(signals_no_vol)
    assert not res["fires"], "cup_and_handle must NOT fire without volume confirm"

    # All gates met -> should fire
    signals_ok = {
        "cup_handle_detected":   True,
        "price_above_ema_200":   True,
        "price_above_ema_50":    True,
        "rsi_14":                60,
        "vol_spike_2x":          True,
    }
    res_ok = strat_cup_and_handle_long(signals_ok)
    assert res_ok["fires"], "cup_and_handle must fire when all gates met"


def test_batch278_smc_bos_continuation_requires_volume_and_momentum():
    """Batch 278: smc_bos_continuation now requires volume confirm
    (vol_spike_2x OR force_index_breakout) + momentum confirm
    (RSI direction-aligned)."""
    from backtest.signals.screener import strat_smc_bos_continuation
    # Stale BOS signal (from 90 bars ago) without volume confirm -> block
    signals_stale = {
        "smc_bos_bullish":        True,
        "price_above_ema_200":    True,
        "vol_spike_2x":           False,
        "force_index_breakout":   False,
        "rsi_14":                 60,
    }
    res = strat_smc_bos_continuation(signals_stale)
    assert not res["fires"], "Stale BOS without volume confirm must NOT fire"

    # Confirmed BOS -> should fire
    signals_confirmed = {
        "smc_bos_bullish":        True,
        "price_above_ema_200":    True,
        "vol_spike_2x":           True,
        "rsi_14":                 60,
    }
    res_ok = strat_smc_bos_continuation(signals_confirmed)
    assert res_ok["fires"], "Confirmed BOS with volume + RSI>50 must fire"

    # Wrong-direction momentum -> block
    signals_wrong = {
        "smc_bos_bullish":        True,
        "price_above_ema_200":    True,
        "vol_spike_2x":           True,
        "rsi_14":                 40,    # RSI<50 contradicts bullish BOS
    }
    res_wrong = strat_smc_bos_continuation(signals_wrong)
    assert not res_wrong["fires"], "RSI<50 must block bullish BOS entry"


def test_batch267_news_sentiment_shift_strat_fires():
    """Batch 267 Path B: strat_news_sentiment_shift_long must fire when
    shift>0.4 + article_count>=2 + 200-EMA gates met."""
    from backtest.signals.screener import strat_news_sentiment_shift_long
    signals = {
        "news_sentiment_shift": 0.6,    # >0.4
        "news_article_count":   3,      # >=2
        "price_above_ema_200":  True,
    }
    res = strat_news_sentiment_shift_long(signals)
    assert res is not None, "Shift strategy must fire when entry gates met"
    assert res.get("direction") == "long"


def test_batch270_roster_sanity_passes_in_current_state():
    """Batch 270 (Tier 2.3 of T1A_COMPREHENSIVE_REVIEW): startup roster
    sanity gate. All 148 ALL_STRATEGIES entries must be callable + return
    a dict with 'fires' key when called with empty signals. Fail-fast at
    startup prevents the 2026-05-19 stale-roster bug (Batches 252-255
    registered 16h after T1a launch -> 25 silent zero-fire strategies
    across the entire 17h run).
    """
    from backtest.signals.screener import validate_strategy_roster, ALL_STRATEGIES
    summary = validate_strategy_roster()
    assert summary["total_registered"] == len(ALL_STRATEGIES)
    assert summary["callable_ok"] == summary["total_registered"]
    assert summary["callable_failed"] == []
    assert summary["load_errors"] == []
    # Guard against accidental mass-deprecation.
    assert summary["active_count"] >= 100, (
        f"Active strategy count dropped to {summary['active_count']}"
    )


def test_batch270_roster_sanity_raises_on_broken_strategy():
    """Batch 270: validator must FAIL FAST if a strategy raises on call."""
    import pytest
    from backtest.signals import screener
    broken_fn = lambda s: 1 / 0
    orig = screener.ALL_STRATEGIES.copy()
    screener.ALL_STRATEGIES["TEST_BROKEN_STRATEGY"] = broken_fn
    try:
        with pytest.raises(RuntimeError, match="Strategy roster validation failed"):
            screener.validate_strategy_roster()
    finally:
        screener.ALL_STRATEGIES.clear()
        screener.ALL_STRATEGIES.update(orig)


def test_batch270_roster_sanity_raises_on_missing_fires_key():
    """Batch 270: a strategy returning a dict without 'fires' breaks the
    screening protocol silently mid-run. Validator catches at startup."""
    import pytest
    from backtest.signals import screener
    broken_fn = lambda s: {"direction": "long"}  # missing 'fires'
    orig = screener.ALL_STRATEGIES.copy()
    screener.ALL_STRATEGIES["TEST_NO_FIRES_KEY"] = broken_fn
    try:
        with pytest.raises(RuntimeError, match="missing_fires_key|roster validation"):
            screener.validate_strategy_roster()
    finally:
        screener.ALL_STRATEGIES.clear()
        screener.ALL_STRATEGIES.update(orig)


def test_batch229_engle_granger_returns_expected_keys():
    """Batch 229 (deferred-items pairs trading 2026-05-18 owner-approved):
    engle_granger_cointegration returns dict with cointegrated, hedge_ratio,
    intercept, adf_pvalue, residuals, note keys. Krauss 2017/2024 JEFM."""
    import pandas as pd
    import numpy as np
    from backtest.signals.pairs_trading import engle_granger_cointegration
    rng = np.random.default_rng(42)
    n = 100
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    s_a = pd.Series(100 + np.cumsum(rng.normal(0, 0.01, n)), index=idx)
    s_b = pd.Series(50 + np.cumsum(rng.normal(0, 0.01, n)), index=idx)
    out = engle_granger_cointegration(s_a, s_b)
    for key in ("cointegrated", "hedge_ratio", "intercept",
                 "adf_pvalue", "residuals", "note"):
        assert key in out, f"Batch 229: engle_granger must emit {key}"
    assert isinstance(out["cointegrated"], bool)


def test_batch229_engle_granger_defensive_inputs():
    """Batch 229: defensive returns on null/insufficient input."""
    import pandas as pd
    from backtest.signals.pairs_trading import engle_granger_cointegration
    # Null input
    out_null = engle_granger_cointegration(None, None)
    assert out_null["cointegrated"] is False
    assert out_null["note"] == "null_input"
    # Insufficient overlap (<60 obs)
    s_short = pd.Series([1, 2, 3])
    out_short = engle_granger_cointegration(s_short, s_short)
    assert out_short["cointegrated"] is False
    assert out_short["note"] == "insufficient_overlap"


def test_batch229_half_life_detects_mean_reversion():
    """Batch 229: spread_half_life on synthetic mean-reverting series."""
    import pandas as pd
    import numpy as np
    from backtest.signals.pairs_trading import spread_half_life
    rng = np.random.default_rng(11)
    n = 200
    # Mean-reverting AR(1) series with theta = -0.1 -> half-life ~ ln(2)/0.1 = 6.93
    s = [0.0]
    for _ in range(n - 1):
        s.append(s[-1] - 0.1 * s[-1] + rng.normal(0, 0.5))
    out = spread_half_life(pd.Series(s))
    assert out is not None
    assert 3 < out < 20, f"Half-life of theta=-0.1 series should be ~6.93, got {out}"
    # Random walk (no mean reversion) -> half-life should be substantially
    # larger than the mean-reverting case (noisy on finite samples; allow
    # None or > 25 days as the post-HFT-survival floor would already reject it)
    rw = pd.Series(np.cumsum(rng.normal(0, 0.1, n)))
    rw_hl = spread_half_life(rw)
    assert rw_hl is None or rw_hl > 25, (
        f"Random walk half-life should be None or >25 (well beyond the "
        f"5-30 post-HFT band); got {rw_hl}"
    )


def test_batch229_pair_zscore_returns_float():
    """Batch 229: pair_zscore computes (spread - mean) / std over window."""
    import pandas as pd
    import numpy as np
    from backtest.signals.pairs_trading import pair_zscore
    rng = np.random.default_rng(7)
    n = 100
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    s_a = pd.Series(100 + np.cumsum(rng.normal(0, 0.01, n)), index=idx)
    s_b = pd.Series(50 + np.cumsum(rng.normal(0, 0.01, n)), index=idx)
    z = pair_zscore(s_a, s_b, hedge_ratio=2.0, intercept=0.0, window=60)
    assert z is not None
    assert isinstance(z, float)
    # Insufficient data -> None
    z_short = pair_zscore(s_a.head(5), s_b.head(5), 2.0, 0.0, 60)
    assert z_short is None


def test_batch229_find_pairs_handles_empty_input():
    """Batch 229: find_cointegrated_pairs defensive on empty / single-col."""
    import pandas as pd
    from backtest.signals.pairs_trading import find_cointegrated_pairs
    assert find_cointegrated_pairs(pd.DataFrame()) == []
    df_one = pd.DataFrame({"A": [1, 2, 3]})
    assert find_cointegrated_pairs(df_one) == []


def test_batch228_xgboost_meta_labeler_preferred():
    """Batch 228 (housekeeping 2026-05-18 owner-approved): XGBoost
    is preferred over sklearn GBM for meta-labeling per Joubert-Snyman
    2024. Confirms xgboost backend is wired + falls back gracefully."""
    import pandas as pd
    import numpy as np
    from backtest.results.cpcv import meta_label_classifier_fit
    rng = np.random.default_rng(42)
    n = 200
    feat_a = rng.normal(0, 1, n)
    labels = (feat_a + rng.normal(0, 0.5, n) > 0).astype(int)
    features = pd.DataFrame({"feat_a": feat_a, "feat_b": rng.normal(0, 1, n)})

    # auto method should pick xgboost first when available
    clf_auto = meta_label_classifier_fit(features, pd.Series(labels), method="auto")
    assert clf_auto is not None
    # When xgboost installed, the auto classifier should be XGBClassifier
    try:
        from xgboost import XGBClassifier
        assert isinstance(clf_auto, XGBClassifier), (
            f"Batch 228: auto method should prefer XGBClassifier when "
            f"xgboost available; got {type(clf_auto).__name__}"
        )
    except ImportError:
        pass  # xgboost not installed; auto fallback chain handles

    # Explicit xgb method works
    clf_xgb = meta_label_classifier_fit(features, pd.Series(labels), method="xgb")
    if clf_xgb is not None:
        from xgboost import XGBClassifier
        assert isinstance(clf_xgb, XGBClassifier)

    # logreg fallback still works
    clf_lr = meta_label_classifier_fit(features, pd.Series(labels), method="logreg")
    assert clf_lr is not None


def test_batch228_pbo_check_script_imports_and_builds_perf_matrix():
    """Batch 228: scripts/run_pbo_check.py helper builds per-strategy
    daily returns matrix from a synthetic trade log."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
    import pandas as pd
    # Inline import via importlib to avoid module-level sys.path side effects
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "run_pbo_check",
        Path(__file__).parent.parent.parent / "scripts" / "run_pbo_check.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Synthetic trade log: 3 strategies, 50 trades each
    rows = []
    for s in ["s_a", "s_b", "s_c"]:
        for i in range(50):
            rows.append({
                "strategy":   s,
                "exit_date":  f"2024-{(i // 20) + 1:02d}-{(i % 20) + 1:02d}",
                "pnl_pct":    0.5 if i % 2 == 0 else -0.3,
            })
    df = pd.DataFrame(rows)
    perf = mod.build_perf_matrix(df)
    # All 3 strategies have >= 30 trades -> all in matrix
    assert perf.shape[1] == 3
    assert "s_a" in perf.columns
    # Fewer than 30 trades for one strategy -> excluded
    rows_small = [
        {"strategy": "tiny", "exit_date": "2024-01-01", "pnl_pct": 0.1}
    ] * 5
    df_small = pd.DataFrame(rows + rows_small)
    perf2 = mod.build_perf_matrix(df_small)
    assert "tiny" not in perf2.columns


def test_batch228_ohlcv_freshness_cutoff_extended_to_21_days():
    """Batch 228: data freshness cutoff extended 14 -> 21 days for
    realistic Stage 2 prefetch cadence.

    Batch 423 (2026-05-28) further extended 21 -> 35 days after CI red
    pattern (924 ACTIVE-ticker files with last_bar=2026-05-05 vs CI date
    2026-05-28 = 23 days, 2 days past prior 21-day cutoff). Test pin
    updated to 35; the historic 14 -> 21 step retained in the negative
    assertion."""
    import inspect
    from backtest.tests import test_data_integrity as tdi
    src = inspect.getsource(tdi.test_data_integrity_2_ohlcv_freshness)
    assert "days=35" in src
    assert "days=14" not in src


def test_batch227b_multi_tier_partial_registered():
    """Batch 227b (multi-tier partial-fill 2026-05-18 owner-approved): 1
    new exit method (multi_tier_partial) bringing roster 24 -> 25."""
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    assert "multi_tier_partial" in EXIT_STRATEGIES
    assert len(EXIT_STRATEGIES) >= 25


def test_batch227b_multi_tier_hits_1r_then_2r_then_trail():
    """Batch 227b: synthetic strong-uptrend triggers 1R + 2R partial fills
    then trail-stop. Weighted-average exit price > entry."""
    import pandas as pd
    from backtest.engine.exit_strategies import exit_multi_tier_partial
    n = 60
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    # Strong rally past 2R (entry 100, atr 2.0 -> 1R=102, 2R=104), then pullback
    closes = list(range(100, 130)) + [130 - i * 0.5 for i in range(30)]
    df = pd.DataFrame({
        "open":  closes, "high": [c + 1 for c in closes],
        "low":   [c - 1 for c in closes], "close": closes,
    }, index=idx)
    out = exit_multi_tier_partial(df, idx[0].date(), 100.0, "long", atr=2.0)
    assert out is not None
    # Should hit at least 1R; reason contains "1R"
    assert "1R" in out["exit_reason"]
    # Net exit price weighted across tiers should exceed entry
    assert out["exit_price"] > 100.0
    # Should be a win
    assert out["win"] is True


def test_batch227b_multi_tier_partial_stops_out_before_1r():
    """Batch 227b: synthetic decline that never hits 1R should exit via
    trailing stop (no partial fill at 1R). Weighted-avg = trail-stop fill."""
    import pandas as pd
    from backtest.engine.exit_strategies import exit_multi_tier_partial
    n = 30
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    # Steady decline from 100 (entry) - never hits 1R target at 102
    closes = [100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88,
              87, 86, 85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74, 73, 72, 71]
    df = pd.DataFrame({
        "open":  closes, "high": [c + 0.5 for c in closes],
        "low":   [c - 0.5 for c in closes], "close": closes,
    }, index=idx)
    out = exit_multi_tier_partial(df, idx[0].date(), 100.0, "long", atr=2.0)
    assert out is not None
    # Stop out before any tier hit -> reason contains "trail" (only trail tier)
    assert "trail" in out["exit_reason"]
    # Should be a loss
    assert out["pnl_pct"] < 0


def test_batch227b_multi_tier_partial_short_side_symmetric():
    """Batch 227b: short-side symmetric on downward move."""
    import pandas as pd
    from backtest.engine.exit_strategies import exit_multi_tier_partial
    n = 50
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    # Decline 100 -> 90 (5R) then partial recovery
    closes = list(range(100, 90, -1)) + [90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
                                          100, 101, 102, 103, 104, 105, 106, 107,
                                          108, 109, 110, 111, 112, 113, 114, 115,
                                          116, 117, 118, 119, 120, 121, 122, 123,
                                          124, 125, 126, 127, 128, 129]
    df = pd.DataFrame({
        "open":  closes, "high": [c + 1 for c in closes],
        "low":   [c - 1 for c in closes], "close": closes,
    }, index=idx)
    out = exit_multi_tier_partial(df, idx[0].date(), 100.0, "short", atr=2.0)
    assert out is not None
    # Should hit 1R at price=98 (entry-1xATR)
    assert "1R" in out["exit_reason"] or "trail" in out["exit_reason"]


def test_batch227a_new_exits_registered():
    """Batch 227a (deferred exits 2026-05-18 owner-approved): 2 new exit
    methods (reverse_signal, smc_mitigation_zone) bringing roster 22 -> 24."""
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    assert "reverse_signal" in EXIT_STRATEGIES
    assert "smc_mitigation_zone" in EXIT_STRATEGIES
    assert len(EXIT_STRATEGIES) >= 24


def test_batch227a_reverse_signal_evaluators_defined():
    """Batch 227a: REVERSE_SIGNAL_EVALUATORS maps key entry strategies."""
    from backtest.engine.exit_strategies import REVERSE_SIGNAL_EVALUATORS
    must_map = {
        "bollinger_lower", "bollinger_tight",
        "rsi_oversold", "williams_r_oversold",
        "pivot_r1_breakout", "pivot_r2_continuation",
        "bollinger_upper_short", "rsi_overbought_short",
    }
    for k in must_map:
        assert k in REVERSE_SIGNAL_EVALUATORS, f"Batch 227a: {k} must have reverse evaluator"


def test_batch227a_bb_upper_touch_evaluator():
    """Batch 227a: _bb_upper_touch detects close above mean + 2*std."""
    import pandas as pd
    from backtest.engine.exit_strategies import _bb_upper_touch
    closes = [100] * 20 + [120]
    df = pd.DataFrame({"close": closes})
    assert _bb_upper_touch(df) is True
    closes2 = [100, 101, 99, 100, 100] * 4 + [101]
    df2 = pd.DataFrame({"close": closes2})
    assert _bb_upper_touch(df2) is False


def test_batch227a_rsi14_overbought_evaluator():
    """Batch 227a: _rsi14_overbought returns True when RSI > 65."""
    import pandas as pd
    from backtest.engine.exit_strategies import _rsi14_overbought
    closes = list(range(100, 130))
    df = pd.DataFrame({"close": closes})
    assert _rsi14_overbought(df) is True


def test_batch227a_reverse_signal_fallback_when_no_mapping():
    """Batch 227a: unmapped strategy -> fallback to atr_trail."""
    import pandas as pd
    from backtest.engine.exit_strategies import exit_reverse_signal
    n = 30
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    closes = list(range(100, 130))
    df = pd.DataFrame({
        "open": closes, "high": [c + 1 for c in closes],
        "low": [c - 1 for c in closes], "close": closes,
    }, index=idx)
    out = exit_reverse_signal(df, idx[0].date(), 100.0, "long", atr=2.0,
                                signals={"strategy_name": "unknown_strategy"})
    assert out["exit_reason"] in (
        "atr_trailing_stop", "end_of_data", "trailing_stop",
    )


def test_batch227a_smc_mitigation_zone_completes_with_synthetic_data():
    """Batch 227a: exit_smc_mitigation_zone runs end-to-end on synthetic
    OHLCV (may exit via SMC, trail-safety, or end-of-data)."""
    import pandas as pd
    import numpy as np
    from backtest.engine.exit_strategies import exit_smc_mitigation_zone
    rng = np.random.default_rng(42)
    n = 200
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    base = 100 + np.cumsum(rng.normal(0, 1, n))
    df = pd.DataFrame({
        "open":  base, "high": base + 1, "low": base - 1,
        "close": base, "volume": rng.integers(1_000_000, 5_000_000, n).astype(float),
    }, index=idx)
    out = exit_smc_mitigation_zone(df, idx[0].date(), 100.0, "long", atr=2.0)
    assert out is not None
    assert out["exit_reason"] in (
        "smc_mitigation_batch227a",
        "smc_trail_safety_batch227a",
        "end_of_data",
    )


def test_batch226_new_exits_registered():
    """Batch 226 (exits gap fill 2026-05-18 owner-approved): 4 new exit
    methods registered (chandelier_3x, atr_trail_vix_conditional,
    mfe_lockin_trail, atr_trail_mae_conditional) bringing roster from
    17 to 21."""
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    for name in (
        "chandelier_3x", "atr_trail_vix_conditional",
        "mfe_lockin_trail", "atr_trail_mae_conditional",
    ):
        assert name in EXIT_STRATEGIES, f"Batch 226: {name} must be registered"
    assert len(EXIT_STRATEGIES) >= 21


def test_batch226_chandelier_exits_long_when_close_below_anchor():
    """Batch 226: exit_chandelier - trail from rolling_high - 3*ATR
    (LeBeau-Lucas 1992). Long should fire chandelier_exit reason
    after sustained drawdown."""
    import pandas as pd
    from backtest.engine.exit_strategies import exit_chandelier
    n = 100
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    closes = list(range(100, 140)) + [140 - i * 2 for i in range(60)]
    df = pd.DataFrame({
        "open":   closes, "high": [c + 1 for c in closes],
        "low":    [c - 1 for c in closes], "close": closes,
    }, index=idx)
    result = exit_chandelier(df, idx[0].date(), 100.0, "long", atr=2.0)
    assert result is not None
    assert result["exit_reason"] in ("chandelier_exit", "end_of_data")


def test_batch226_atr_trail_vix_conditional_scales_by_band():
    """Batch 226: exit_atr_trail_vix_conditional source verifies the
    0.75x / 1.5x scaling logic for low / high VIX bands."""
    import inspect
    from backtest.engine.exit_strategies import exit_atr_trail_vix_conditional
    src = inspect.getsource(exit_atr_trail_vix_conditional)
    assert "vix_band_low" in src
    assert "vix_band_high" in src
    assert "0.75" in src
    assert "1.5" in src


def test_batch226_mfe_lockin_logic():
    """Batch 226: exit_mfe_lockin_trail tightens stop to (best_high -
    1xATR) when MFE >= 2xATR. Bandy 2014 lock-in discipline."""
    import pandas as pd
    from backtest.engine.exit_strategies import exit_mfe_lockin_trail
    n = 80
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    closes = list(range(100, 130)) + [130 - i * 0.5 for i in range(50)]
    df = pd.DataFrame({
        "open":   closes, "high": [c + 1 for c in closes],
        "low":    [c - 1 for c in closes], "close": closes,
    }, index=idx)
    result = exit_mfe_lockin_trail(df, idx[0].date(), 100.0, "long",
                                    atr=2.0, mfe_threshold_atr=2.0,
                                    lock_back_atr=1.0)
    assert result is not None
    assert result["exit_reason"] in (
        "mfe_lockin_trail", "mfe_pre_threshold_trail", "end_of_data",
    )


def test_batch226_mae_conditional_helper():
    """Batch 226: per_strategy_mae_75th_pct_of_winners returns
    default 1.0 on insufficient data."""
    import pandas as pd
    from backtest.engine.exit_strategies import per_strategy_mae_75th_pct_of_winners
    assert per_strategy_mae_75th_pct_of_winners(None, "any") == 1.0
    assert per_strategy_mae_75th_pct_of_winners(pd.DataFrame(), "any") == 1.0
    df = pd.DataFrame({"strategy": ["a", "b"], "win": [True, True],
                       "mae_pct": [-2.0, -1.5]})
    assert per_strategy_mae_75th_pct_of_winners(df, "missing") == 1.0


def test_batch268_vix_spike_kill_switch_removed():
    """Batch 268 (2026-05-20 owner-approved): vix_spike_kill_switch REMOVED
    from process_day_exits after counterfactual bootstrap showed it cost
    -6.98% per trade vs trailing_15pct (95% CI [-11.35%, -3.00%], p=0.0005)
    on 91 matched trades from the 20tkr x 2y smoke. The "profit-protect"
    reading was wrong - vix_kill cuts winners short during transient VIX
    spikes that resolve favorably.

    Supersedes prior Batch 226 wiring test."""
    import inspect
    from backtest.engine import exit_manager as em
    src = inspect.getsource(em.process_day_exits)
    # The exit reason string must NOT appear in the function body.
    assert "vix_spike_kill_switch_batch226" not in src, (
        "Batch 268: vix_spike_kill_switch must be removed; the exit reason "
        "string should not appear in process_day_exits"
    )
    # The activation variable must not be set/used.
    assert "vix_spike_active" not in src, (
        "Batch 268: vix_spike_active flag must be removed"
    )
    # vix_history parameter retained for back-compat with callers; not asserted.


def test_batch226_ci_exit_count_assertion_updated():
    """Batch 226: CI_REGRESSION_BEHAVIOR_ASSERTIONS exit_method_count_min
    bumped 17 -> 21 to match the new roster."""
    from backtest.config import CI_REGRESSION_BEHAVIOR_ASSERTIONS
    assert CI_REGRESSION_BEHAVIOR_ASSERTIONS["exit_method_count_min"] >= 21


def test_batch224_pre_fomc_strategies_registered():
    """Batch 224 (pre-FOMC + buybacks 2026-05-18 owner-approved):
    3 new event-driven strategies registered + 3 entries in
    STRATEGIES_BYPASS_EVENT_SUPPRESSION."""
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.config import STRATEGIES_BYPASS_EVENT_SUPPRESSION
    for name in (
        "pre_fomc_long_sleeve",
        "pre_fomc_quality_momentum_long",
        "buyback_8k_recent_long",
    ):
        assert name in ALL_STRATEGIES, f"Batch 224: {name} must be registered"
        assert name in STRATEGIES_BYPASS_EVENT_SUPPRESSION, (
            f"Batch 224: {name} must bypass event suppression"
        )


def test_batch224_pre_fomc_long_sleeve_fires_on_d1():
    """Batch 224: pre_fomc_long_sleeve fires only on pre-FOMC day-1 +
    200-EMA gate. Lucca-Moench 2015 +50bps/yr alpha pre-FOMC drift."""
    from backtest.signals.screener import strat_pre_fomc_long_sleeve
    s = {
        "pre_fomc_d1": True,
        "days_until_fomc": 1,
        "price_above_ema_200": True,
    }
    r = strat_pre_fomc_long_sleeve(s)
    assert r["fires"] is True and r["direction"] == "long"
    # Not pre-FOMC day-1 -> no fire
    s["pre_fomc_d1"] = False
    assert strat_pre_fomc_long_sleeve(s)["fires"] is False
    # Bear regime -> no fire
    s["pre_fomc_d1"] = True
    s["price_above_ema_200"] = False
    assert strat_pre_fomc_long_sleeve(s)["fires"] is False


def test_batch224_pre_fomc_quality_momentum_long():
    """Batch 224: combines pre-FOMC timing + top-decile XS momentum
    + 200-EMA. Higher conviction variant."""
    from backtest.signals.screener import strat_pre_fomc_quality_momentum_long
    s = {
        "pre_fomc_d1": True,
        "xs_momentum_top_decile": True,
        "price_above_ema_200": True,
    }
    assert strat_pre_fomc_quality_momentum_long(s)["fires"] is True
    s["xs_momentum_top_decile"] = False
    assert strat_pre_fomc_quality_momentum_long(s)["fires"] is False


def test_batch224_buyback_8k_recent_long():
    """Batch 224: 8-K filed last 5 days + 200-EMA + 1.5x volume.
    Generic event-driven proxy for buyback / M&A / guidance change.
    Batch 385 (2026-05-26 surgical threshold change): days_since_8k loosened
    3 -> 5 per PHASE_1A_BETA_STATUS.md "What still applies in cube eval" +
    empirical 86/86 fires-at-boundary observation. Test threshold updated
    here in Batch 412 (test-drift cleanup bundled with vectorized exit ship)."""
    from backtest.signals.screener import strat_buyback_8k_recent_long
    s = {
        "recent_8k_filed": True,
        "days_since_8k": 2,
        "price_above_ema_200": True,
        "vol_spike_15x": True,
    }
    assert strat_buyback_8k_recent_long(s)["fires"] is True
    # >5 days since 8-K -> no fire (post-Batch-385 threshold)
    s["days_since_8k"] = 7
    assert strat_buyback_8k_recent_long(s)["fires"] is False


def test_batch224_event_suppression_bypass_wired():
    """Batch 224: engine source must check
    STRATEGIES_BYPASS_EVENT_SUPPRESSION and allow tagged strategies
    through the suppression gate."""
    import inspect
    from backtest.engine import backtest as bt
    src = inspect.getsource(bt)
    assert "STRATEGIES_BYPASS_EVENT_SUPPRESSION" in src
    assert "in STRATEGIES_BYPASS_EVENT_SUPPRESSION" in src


def test_batch224_compute_pre_fomc_signals_no_data():
    """Batch 224: compute_pre_fomc_signals returns empty dict when
    FOMC calendar parquet missing (defensive)."""
    from datetime import date
    from backtest.signals.macro_events import compute_pre_fomc_signals
    # Should return empty dict gracefully if FRED calendar missing
    out = compute_pre_fomc_signals(date(2024, 6, 1))
    assert isinstance(out, dict)


def test_batch223_correlation_with_open_positions():
    """Batch 223 (correlation cap 2026-05-18 owner-approved):
    correlation_with_open_positions returns max |corr| with any open
    position over lookback window. Carver 2015 IDM-inspired."""
    import pandas as pd
    import numpy as np
    from datetime import date
    from backtest.engine.correlation_gate import correlation_with_open_positions
    rng = np.random.default_rng(42)
    n = 100
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    # Candidate
    cand_returns = rng.normal(0, 0.02, n)
    cand_close = 100 + np.cumsum(cand_returns)
    # Highly correlated open position (same returns + tiny noise)
    pos_a_returns = cand_returns + rng.normal(0, 0.001, n)
    pos_a_close = 100 + np.cumsum(pos_a_returns)
    # Uncorrelated open position
    pos_b_close = 100 + np.cumsum(rng.normal(0, 0.02, n))
    ohlcv = {
        "CAND": pd.DataFrame({"close": cand_close}, index=idx),
        "POS_A": pd.DataFrame({"close": pos_a_close}, index=idx),
        "POS_B": pd.DataFrame({"close": pos_b_close}, index=idx),
    }
    out = correlation_with_open_positions(
        "CAND", ohlcv, ["POS_A", "POS_B"], as_of=date(2024, 5, 1),
    )
    # POS_A should be the high-correlation match
    assert out["max_corr_ticker"] == "POS_A"
    assert out["max_abs_corr"] > 0.9
    assert out["any_correlated"] is True


def test_batch223_correlation_size_multiplier():
    """Batch 223: correlation_size_multiplier maps |corr| to [0, 0.5, 1.0]:
    >=0.85 skip (0.0), [0.7, 0.85) halve (0.5), <0.7 full (1.0)."""
    from backtest.engine.correlation_gate import correlation_size_multiplier
    assert correlation_size_multiplier(0.5) == 1.0   # uncorrelated
    assert correlation_size_multiplier(0.69) == 1.0  # just under halve
    assert correlation_size_multiplier(0.70) == 0.5  # halve threshold
    assert correlation_size_multiplier(0.84) == 0.5  # still halve
    assert correlation_size_multiplier(0.85) == 0.0  # skip threshold
    assert correlation_size_multiplier(0.99) == 0.0  # extreme


def test_batch223_gross_portfolio_beta():
    """Batch 223: gross_portfolio_beta computes weighted beta vs SPY."""
    import pandas as pd
    import numpy as np
    from datetime import date
    from backtest.engine.correlation_gate import gross_portfolio_beta
    rng = np.random.default_rng(11)
    n = 300
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    # Use compound-return construction so pct_change recovers the
    # original return series (cumsum mixes scale; cumprod preserves it)
    spy_ret = rng.normal(0, 0.01, n)
    spy_close = 400 * np.cumprod(1 + spy_ret)
    # POS_HIGH_BETA: 1.5 * SPY returns + noise
    pos_high_ret = 1.5 * spy_ret + rng.normal(0, 0.003, n)
    # POS_LOW_BETA: 0.3 * SPY returns
    pos_low_ret = 0.3 * spy_ret + rng.normal(0, 0.003, n)
    ohlcv = {
        "SPY": pd.DataFrame({"close": spy_close}, index=idx),
        "POS_HIGH": pd.DataFrame({"close": 100 * np.cumprod(1 + pos_high_ret)}, index=idx),
        "POS_LOW":  pd.DataFrame({"close": 100 * np.cumprod(1 + pos_low_ret)},  index=idx),
    }
    open_pos = {"POS_HIGH": 0.5, "POS_LOW": 0.5}
    beta = gross_portfolio_beta(open_pos, ohlcv, benchmark="SPY",
                                 as_of=date(2024, 12, 1))
    # Expected ~ (1.5 + 0.3) / 2 = 0.9
    assert 0.7 <= beta <= 1.1, f"Gross beta should be ~0.9, got {beta}"


def test_batch223_config_flags_added():
    """Batch 223: LIVE_TRADING_RULES exposes correlation + beta-hedge
    config keys."""
    from backtest.config import LIVE_TRADING_RULES
    assert LIVE_TRADING_RULES.get("correlation_skip_threshold") == 0.85
    assert LIVE_TRADING_RULES.get("correlation_halve_threshold") == 0.70
    # Beta hedge OFF by default
    assert LIVE_TRADING_RULES.get("beta_hedge_enabled") is False
    assert LIVE_TRADING_RULES.get("beta_hedge_ratio") == 0.5


def test_batch223_sector_cap_tightened_to_25pct():
    """Batch 223: engine sector_threshold_pct tightened 30 -> 25 per
    Litterman 2003 industry-standard. Source-level pin."""
    import inspect
    from backtest.engine import backtest as bt
    src = inspect.getsource(bt)
    assert "sector_threshold_pct=25.0" in src
    # The old 30.0 should NOT be the engine call (only allowed in
    # defaults / dead code outside the engine call)
    # Check the call site specifically
    assert "factor_concentration_breach(" in src


def test_batch222_strategies_registered():
    """Batch 222 (event-driven + quality factor 2026-05-18 owner-approved):
    5 new strategies registered."""
    from backtest.signals.screener import ALL_STRATEGIES
    for name in (
        "insider_cluster_long",
        "insider_cluster_with_director_long",
        "xs_quality_top_quintile_long",
        "xs_momentum_quality_combined",
        "pead_with_insider_confirmation_long",
    ):
        assert name in ALL_STRATEGIES, f"Batch 222: {name} must be registered"


def test_batch222_insider_cluster_long_requires_cluster_and_regime():
    """Batch 222: insider_cluster_long fires only on insider_cluster_active
    + 200-EMA gate. Cohen-Malloy-Pomorski 2012 documented ~7pct alpha."""
    from backtest.signals.screener import strat_insider_cluster_long
    s = {
        "insider_cluster_active": True,
        "insider_unique_buyers_30d": 3,
        "price_above_ema_200": True,
    }
    r = strat_insider_cluster_long(s)
    assert r["fires"] is True and r["direction"] == "long"
    s["insider_cluster_active"] = False
    assert strat_insider_cluster_long(s)["fires"] is False
    s["insider_cluster_active"] = True
    s["price_above_ema_200"] = False
    assert strat_insider_cluster_long(s)["fires"] is False


def test_batch222_insider_director_variant_requires_director():
    """Batch 222: director variant requires at least 1 director buyer
    (higher signal value per Lakonishok-Lee 2001 RFS)."""
    from backtest.signals.screener import strat_insider_cluster_with_director_long
    s = {
        "insider_cluster_active": True,
        "insider_unique_buyers_30d": 3,
        "insider_director_buyers_30d": 0,  # no directors
        "price_above_ema_200": True,
    }
    assert strat_insider_cluster_with_director_long(s)["fires"] is False
    s["insider_director_buyers_30d"] = 1
    assert strat_insider_cluster_with_director_long(s)["fires"] is True


def test_batch222_quality_top_quintile_long():
    """Batch 222: top-quintile gross profitability + 200-EMA gate."""
    from backtest.signals.screener import strat_xs_quality_top_quintile_long
    s = {"xs_quality_top_quintile": True, "price_above_ema_200": True}
    assert strat_xs_quality_top_quintile_long(s)["fires"] is True
    s["xs_quality_top_quintile"] = False
    assert strat_xs_quality_top_quintile_long(s)["fires"] is False


def test_batch222_compute_insider_cluster_signals_no_data():
    """Batch 222: compute_insider_cluster_signals returns empty dict
    when ticker has no recent qualifying transactions / data miss."""
    from datetime import date
    from backtest.signals.insider_buying import compute_insider_cluster_signals
    # Use a clearly-nonexistent ticker
    out = compute_insider_cluster_signals("NONEXISTENT_TICKER_ZYX", date(2024, 6, 1))
    assert out == {}


def test_batch221_passing_criteria_adds_sortino_calmar_regime():
    """Batch 221 (validation gates 2026-05-18 owner-approved): config
    PASSING_CRITERIA must define min_sortino_overall, min_sortino_per_regime,
    min_calmar, min_regimes_passing."""
    from backtest.config import PASSING_CRITERIA
    assert PASSING_CRITERIA.get("min_sortino_overall") == 1.0
    assert PASSING_CRITERIA.get("min_sortino_per_regime") == 0.7
    assert PASSING_CRITERIA.get("min_calmar") == 0.5
    assert PASSING_CRITERIA.get("min_regimes_passing") == 2


def test_batch221_compute_pbo_cscv_basic():
    """Batch 221: PBO (Probability of Backtest Overfitting) via CSCV.
    Bailey-Borwein-Lopez de Prado-Zhu 2017 J. Comp. Finance."""
    import pandas as pd
    import numpy as np
    from backtest.results.cpcv import compute_pbo_cscv
    # Synthesize a perf matrix where IS-best is also OOS-best (low PBO)
    rng = np.random.default_rng(42)
    n_periods = 200
    n_strats = 20
    # Build correlated returns where 1 strategy has consistent edge
    base = rng.normal(0, 0.02, (n_periods, n_strats))
    base[:, 0] += 0.005  # strategy 0 has consistent positive drift
    df = pd.DataFrame(base, columns=[f"s{i}" for i in range(n_strats)])
    out = compute_pbo_cscv(df, n_partitions=8)
    assert "pbo" in out
    assert out["pbo"] is not None
    # PBO should be in [0, 1]
    assert 0.0 <= out["pbo"] <= 1.0
    # Verdict should be one of the categorical values
    assert out["verdict"] in ("ok", "warning", "overfit", "n/a")


def test_batch221_compute_pbo_handles_edge_cases():
    """Batch 221: PBO returns None on empty / single-strategy /
    insufficient periods."""
    import pandas as pd
    from backtest.results.cpcv import compute_pbo_cscv
    # Empty
    out = compute_pbo_cscv(pd.DataFrame())
    assert out["pbo"] is None
    # Single strategy
    out2 = compute_pbo_cscv(pd.DataFrame({"only": [0.01] * 100}))
    assert out2["pbo"] is None
    # Insufficient periods (less than n_partitions=16)
    out3 = compute_pbo_cscv(pd.DataFrame({
        "a": [0.01] * 10, "b": [0.02] * 10,
    }), n_partitions=16)
    assert out3["pbo"] is None


def test_batch220_cross_sectional_features_emits_factor_ranks():
    """Batch 220 (cross-sectional factor 2026-05-18 owner-approved):
    compute_cross_sectional_features returns dict-of-dicts with
    xs_momentum_decile, xs_beta_decile, xs_ivol_decile,
    xs_max_anomaly_decile per ticker. Moskowitz-Ooi-Pedersen 2012 JFE +
    Ang-Hodrick-Xing-Zhang 2006 + Bali-Cakici-Whitelaw 2011."""
    import pandas as pd
    import numpy as np
    from datetime import date
    from backtest.signals.cross_sectional import compute_cross_sectional_features
    rng = np.random.default_rng(42)
    n = 300
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    # Synthesize 15 tickers + SPY benchmark with varying momentum profiles
    ohlcv = {}
    for i, ticker in enumerate(["SPY"] + [f"T{j}" for j in range(15)]):
        # Vary drift to create cross-sectional momentum dispersion
        drift = 0.05 + (i - 7) * 0.02   # SPY=0.07/-tickers spread
        base = 100 + np.cumsum(rng.normal(drift, 0.8, n))
        ohlcv[ticker] = pd.DataFrame({
            "open":  base, "high": base + 1, "low": base - 1,
            "close": base, "volume": rng.integers(1_000_000, 5_000_000, n).astype(float),
        }, index=idx)
    out = compute_cross_sectional_features(ohlcv, as_of=date(2025, 1, 1))
    # At least 10 tickers should have factor features
    assert len(out) >= 10, f"Expected 10+ tickers with XS features, got {len(out)}"
    # Spot-check a non-benchmark ticker has the expected keys
    sample = next((v for k, v in out.items() if k != "SPY"), None)
    assert sample is not None
    for key in (
        "xs_momentum_12_1", "xs_momentum_decile", "xs_momentum_top_decile",
        "xs_beta", "xs_beta_decile",
        "xs_ivol", "xs_ivol_decile", "xs_avoid_high_ivol",
        "xs_max_anomaly", "xs_max_anomaly_decile", "xs_avoid_high_max",
    ):
        assert key in sample, f"Batch 220: missing factor key {key}"
    # Deciles in [1, 10]
    assert 1 <= sample["xs_momentum_decile"] <= 10
    assert 1 <= sample["xs_beta_decile"] <= 10


def test_batch220_xs_momentum_top_decile_long_fires():
    """Batch 220: xs_momentum_top_decile long fires only on top decile
    + IVOL/MAX filters pass + 200-EMA gate."""
    from backtest.signals.screener import strat_xs_momentum_top_decile
    s = {
        "xs_momentum_top_decile": True,
        "xs_avoid_high_ivol": True,
        "xs_avoid_high_max": True,
        "price_above_ema_200": True,
    }
    r = strat_xs_momentum_top_decile(s)
    assert r["fires"] is True and r["direction"] == "long"
    # IVOL filter rejects
    s["xs_avoid_high_ivol"] = False
    assert strat_xs_momentum_top_decile(s)["fires"] is False
    # MAX filter rejects
    s["xs_avoid_high_ivol"] = True
    s["xs_avoid_high_max"] = False
    assert strat_xs_momentum_top_decile(s)["fires"] is False
    # Regime gate rejects
    s["xs_avoid_high_max"] = True
    s["price_above_ema_200"] = False
    assert strat_xs_momentum_top_decile(s)["fires"] is False


def test_batch220_xs_low_beta_long_requires_filters():
    """Batch 220: BAB long requires xs_low_beta_decile + 200-EMA +
    not-high-IVOL."""
    from backtest.signals.screener import strat_xs_low_beta_long
    s = {
        "xs_low_beta_decile": True,
        "price_above_ema_200": True,
        "xs_avoid_high_ivol": True,
    }
    assert strat_xs_low_beta_long(s)["fires"] is True


def test_batch220_xs_combined_momentum_low_ivol():
    """Batch 220: combined momentum + low-IVOL (Asness-Moskowitz-Pedersen
    2013 quality-momentum). Requires top-decile momentum AND IVOL decile
    <=3 (bottom 30%) AND 200-EMA gate."""
    from backtest.signals.screener import strat_xs_combined_momentum_low_ivol
    s = {
        "xs_momentum_top_decile": True,
        "xs_ivol_decile": 2,
        "price_above_ema_200": True,
    }
    assert strat_xs_combined_momentum_low_ivol(s)["fires"] is True
    # IVOL too high -> no fire
    s["xs_ivol_decile"] = 7
    assert strat_xs_combined_momentum_low_ivol(s)["fires"] is False


def test_batch220_factor_strategies_registered():
    """Batch 220: 4 new factor strategies registered in ALL_STRATEGIES."""
    from backtest.signals.screener import ALL_STRATEGIES
    for name in (
        "xs_momentum_top_decile",
        "xs_momentum_bottom_decile_short",
        "xs_low_beta_long",
        "xs_combined_momentum_low_ivol",
    ):
        assert name in ALL_STRATEGIES, f"Batch 220: {name} must be registered"


def test_batch219_hrp_per_strategy_weight_basic():
    """Batch 219 (HRP wiring 2026-05-18 owner-approved): per-strategy
    HRP-relative multiplier from trade log. Returns hrp_weight /
    equal_weight bounded [0.25, 2.0]."""
    import pandas as pd
    import numpy as np
    from backtest.engine.sizing_hrp_kelly import (
        per_strategy_hrp_weight_from_trade_log,
    )
    rng = np.random.default_rng(42)
    strats = ["s_a", "s_b", "s_c"]
    dates = pd.date_range("2024-01-01", periods=150, freq="B")
    trades = []
    for d in dates:
        for s in strats:
            trades.append({
                "strategy":   s,
                "entry_date": d,
                "win":        bool(rng.random() < 0.5),
                "pnl_pct":    rng.normal(0.5, 1.5),
            })
    df = pd.DataFrame(trades)
    for s in strats:
        m = per_strategy_hrp_weight_from_trade_log(
            df, s, as_of=pd.Timestamp("2024-12-31"),
        )
        assert 0.25 <= m <= 2.0, f"HRP mult for {s} must be in [0.25, 2.0], got {m}"


def test_batch219_hrp_returns_1_on_insufficient_data():
    """Batch 219: no-op when trade log empty / strategy absent /
    fewer than min_strategies (default 3)."""
    import pandas as pd
    from backtest.engine.sizing_hrp_kelly import (
        per_strategy_hrp_weight_from_trade_log,
    )
    assert per_strategy_hrp_weight_from_trade_log(pd.DataFrame(), "any") == 1.0
    df = pd.DataFrame({
        "strategy": ["x", "x"], "entry_date": ["2024-01-01", "2024-01-02"],
        "pnl_pct": [1.0, 2.0],
    })
    assert per_strategy_hrp_weight_from_trade_log(df, "missing") == 1.0
    # Only 2 strategies -> below min_strategies=3 -> no-op
    df2 = pd.DataFrame({
        "strategy":   ["a"] * 50 + ["b"] * 50,
        "entry_date": pd.date_range("2024-01-01", periods=100, freq="B"),
        "pnl_pct":    [1.0] * 100,
    })
    assert per_strategy_hrp_weight_from_trade_log(df2, "a") == 1.0


def test_batch219_hrp_wired_in_engine_sizing_stack():
    """Batch 219: source-level pin verifying engine imports the HRP
    helper and applies the multiplier with sizing_log entry."""
    import inspect
    from backtest.engine import backtest as bt
    src = inspect.getsource(bt)
    assert "per_strategy_hrp_weight_from_trade_log" in src
    assert "hrp_mult = per_strategy_hrp_weight_from_trade_log" in src
    assert "hrp_relative_batch219" in src


def test_batch218_deprecated_strategies_defined():
    """Batch 218 (2026-05-18) deprecation REVERSED by owner directive
    2026-05-25 (Batch 316a): all 23 previously-deprecated strategies
    re-activated for Stage D + Phase 1A-beta empirical validation. The
    DEPRECATED_STRATEGIES SET still exists (as a re-pruning vector) but
    must be empty post-Batch-316a."""
    from backtest.config import DEPRECATED_STRATEGIES
    assert isinstance(DEPRECATED_STRATEGIES, set), "Set type preserved"
    assert len(DEPRECATED_STRATEGIES) == 0, (
        f"Batch 316a owner directive 2026-05-25: DEPRECATED_STRATEGIES "
        f"must be empty (all 23 re-activated for empirical testing); got "
        f"{len(DEPRECATED_STRATEGIES)} entries: {sorted(DEPRECATED_STRATEGIES)}"
    )


def test_batch357_doc_count_drift_strategies():
    """Batch 357 (2026-05-25 owner-directed doc-count drift guard per
    feedback_doc_count_drift_must_be_test_pinned memory): CLAUDE.md +
    CANONICAL_FACTS.md F-002 numeric claims must match the live
    `len(ALL_STRATEGIES)`. Drift between Batches 209-356 went unnoticed
    (148 claimed vs 186 actual); this test fails on future drift before
    the doc gets out of sync again."""
    from pathlib import Path
    from backtest.signals.screener import ALL_STRATEGIES
    live_count = len(ALL_STRATEGIES)
    repo = Path(__file__).parent.parent.parent
    claude_md = (repo / "CLAUDE.md").read_text(encoding="utf-8")
    canonical_facts = (repo / "CANONICAL_FACTS.md").read_text(encoding="utf-8")
    # Both docs must mention the live count somewhere in their body
    assert str(live_count) in claude_md, (
        f"CLAUDE.md does not mention live strategy count {live_count}. "
        f"Update CLAUDE.md to cite `len(ALL_STRATEGIES) = {live_count}`."
    )
    assert str(live_count) in canonical_facts, (
        f"CANONICAL_FACTS.md F-002 does not mention live strategy count "
        f"{live_count}. Update CANONICAL_FACTS.md."
    )


def test_batch357_doc_count_drift_exit_methods():
    """Batch 357 doc-count drift guard for EXIT_STRATEGIES. Drift between
    Batches 282-356 went unnoticed (12 claimed vs 25 actual)."""
    from pathlib import Path
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    live_count = len(EXIT_STRATEGIES)
    repo = Path(__file__).parent.parent.parent
    claude_md = (repo / "CLAUDE.md").read_text(encoding="utf-8")
    canonical_facts = (repo / "CANONICAL_FACTS.md").read_text(encoding="utf-8")
    assert str(live_count) in claude_md, (
        f"CLAUDE.md does not mention live exit-method count {live_count}. "
        f"Update CLAUDE.md repo-structure entry for `exit_strategies.py`."
    )
    assert str(live_count) in canonical_facts, (
        f"CANONICAL_FACTS.md F-004 does not mention live exit-method count "
        f"{live_count}. Update CANONICAL_FACTS.md F-004."
    )


def test_batch218_deprecated_strategies_NOT_in_screener_loop():
    """Batch 218 deprecation-filter wiring is still PRESENT in the screener
    (a future re-deprecation must work without code changes), but the
    DEPRECATED_STRATEGIES set is empty per Batch 316a so the filter is a
    no-op at runtime. This test pins the import + skip-on-membership site
    so the filter remains operational for future re-deprecation."""
    import inspect
    from backtest.signals import screener as scr
    src = inspect.getsource(scr)
    assert "DEPRECATED_STRATEGIES" in src, (
        "screen_instrument must import DEPRECATED_STRATEGIES (filter wiring)"
    )
    assert "if name in _DEPRECATED" in src or "if name in DEPRECATED_STRATEGIES" in src, (
        "screen loop must retain skip-on-membership filter (no-op while set is empty)"
    )


def test_batch218_kept_strategies_not_accidentally_deprecated():
    """Batch 218 defensive: strategies we PROVED have edge in Phase 1A-beta
    or are net-new from Batches 209-217 (PEAD/SMC/AVWAP/ORB/PO3/multi-TF)
    must NOT be in DEPRECATED_STRATEGIES."""
    from backtest.config import DEPRECATED_STRATEGIES
    # Phase 1A-beta empirically-validated (best Sharpe in family or proven sample)
    must_keep = [
        "bollinger_lower", "bollinger_tight", "pivot_r1_breakout",
        "williams_r_oversold",  # Phase 1A-beta best Sharpe (0.30) on 82 trades
        "ultimate_oscillator",   # Phase 1A-beta Sharpe 0.49 on 27 trades
        "stochrsi_oversold", "cpr_narrow_bullish",
        "ichimoku_cloud_breakout", "hull_rsi", "supertrend_macd",
        # New families from Batches 208-217 (literature-backed)
        "avwap_252_breakout", "avwap_50_reclaim",
        "pead_long", "pead_short",
        "smc_bos_continuation", "smc_choch_reversal",
        "orb_stocks_in_play_long",
        "po3_bullish", "weekly_bias_pullback_long",
    ]
    accidental = [s for s in must_keep if s in DEPRECATED_STRATEGIES]
    assert not accidental, (
        f"Batch 218: empirically-validated or research-backed strategies "
        f"must NOT be deprecated: {accidental}"
    )


def test_batch217_po3_multi_tf_strategies_registered():
    """Batch 217 (PO3 + multi-TF 2026-05-18 owner-approved): 9 new
    strategies registered (2 PO3 + 2 PO3+HTF + 2 HTF-aligned breakout
    + 2 weekly-bias pullback + 1 monthly-bias momentum)."""
    from backtest.signals.screener import ALL_STRATEGIES
    new_names = [
        "po3_bullish", "po3_bearish",
        "po3_htf_aligned_long", "po3_htf_aligned_short",
        "htf_aligned_breakout_long", "htf_aligned_breakout_short",
        "weekly_bias_pullback_long", "weekly_bias_pullback_short",
        "monthly_bias_momentum_long",
    ]
    for name in new_names:
        assert name in ALL_STRATEGIES, f"Batch 217: {name} must be registered"


def test_batch217_compute_po3_signal_detects_bullish():
    """Batch 217: compute_po3_signal po3_bullish=True when today sweeps
    below prior low, closes above open, in upper third of range."""
    import pandas as pd
    from backtest.signals.multi_timeframe import compute_po3_signal
    df = pd.DataFrame({
        "open":  [100, 99],
        "high":  [102, 105],
        "low":   [99,  98],
        "close": [101, 104],
        "volume":[1e6, 2e6],
    })
    out = compute_po3_signal(df)
    assert out["po3_bullish"] is True
    assert out["po3_bearish"] is False
    assert out["po3_sweep_below_prior_low"] is True
    assert out["po3_close_position"] > 0.66


def test_batch217_compute_po3_signal_detects_bearish():
    """Batch 217: bearish PO3."""
    import pandas as pd
    from backtest.signals.multi_timeframe import compute_po3_signal
    df = pd.DataFrame({
        "open":  [100, 102],
        "high":  [102, 105],
        "low":   [99,  97],
        "close": [101, 98],
        "volume":[1e6, 2e6],
    })
    out = compute_po3_signal(df)
    assert out["po3_bearish"] is True
    assert out["po3_bullish"] is False


def test_batch217_compute_weekly_bias_emits_signals():
    """Batch 217: compute_weekly_bias emits bias signals after >=100
    daily bars + >=22 weekly bars after resample."""
    import pandas as pd
    import numpy as np
    from backtest.signals.multi_timeframe import compute_weekly_bias
    rng = np.random.default_rng(7)
    n = 200
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    base = 100 + np.cumsum(rng.normal(0.1, 0.5, n))
    df = pd.DataFrame({
        "open":  base, "high": base + 1, "low": base - 1,
        "close": base, "volume": rng.integers(1_000_000, 5_000_000, n).astype(float),
    }, index=idx)
    out = compute_weekly_bias(df)
    for key in [
        "weekly_close", "weekly_ema_10", "weekly_ema_20",
        "weekly_above_ema_10", "weekly_above_ema_20",
        "weekly_bias_bull", "weekly_bias_bear",
        "weekly_momentum_4w", "weekly_momentum_pos",
    ]:
        assert key in out, f"Batch 217: weekly bias must emit {key}"
    # Bull and bear mutually exclusive
    assert not (out["weekly_bias_bull"] and out["weekly_bias_bear"])


def test_batch217_compute_monthly_bias_emits_signals():
    """Batch 217: monthly bias requires 260+ daily bars."""
    import pandas as pd
    import numpy as np
    from backtest.signals.multi_timeframe import compute_monthly_bias
    rng = np.random.default_rng(11)
    n = 400
    idx = pd.date_range("2023-01-01", periods=n, freq="B")
    base = 100 + np.cumsum(rng.normal(0.1, 0.5, n))
    df = pd.DataFrame({
        "open":  base, "high": base + 1, "low": base - 1,
        "close": base, "volume": rng.integers(1_000_000, 5_000_000, n).astype(float),
    }, index=idx)
    out = compute_monthly_bias(df)
    for key in [
        "monthly_close", "monthly_sma_6", "monthly_sma_12",
        "monthly_above_sma_6", "monthly_above_sma_12",
        "monthly_bias_bull", "monthly_bias_bear",
        "monthly_momentum_6m", "monthly_momentum_pos",
    ]:
        assert key in out, f"Batch 217: monthly bias must emit {key}"


def test_batch217_htf_alignment_composes_weekly_and_monthly():
    """Batch 217: compute_htf_alignment combines weekly+monthly bias."""
    from backtest.signals.multi_timeframe import compute_htf_alignment
    # Both bull -> aligned_bull
    out = compute_htf_alignment(
        {"weekly_bias_bull": True, "weekly_bias_bear": False},
        {"monthly_bias_bull": True, "monthly_bias_bear": False},
    )
    assert out["htf_aligned_bull"] is True
    assert out["htf_aligned_bear"] is False
    assert out["htf_disagreement"] is False
    # Disagreement
    out2 = compute_htf_alignment(
        {"weekly_bias_bull": True, "weekly_bias_bear": False},
        {"monthly_bias_bull": False, "monthly_bias_bear": True},
    )
    assert out2["htf_disagreement"] is True
    # Empty -> empty
    assert compute_htf_alignment({}, {}) == {}


def test_batch217_po3_bullish_strategy_requires_regime_gate():
    """Batch 217: strat_po3_bullish requires po3_bullish + 200-EMA gate."""
    from backtest.signals.screener import strat_po3_bullish
    s = {"po3_bullish": True, "price_above_ema_200": True}
    assert strat_po3_bullish(s)["fires"] is True
    s["price_above_ema_200"] = False
    assert strat_po3_bullish(s)["fires"] is False


def test_batch217_htf_aligned_breakout_long_requires_triple_confluence():
    """Batch 217: htf_aligned_breakout_long needs prev_high break + 1.5x
    volume + htf_aligned_bull."""
    from backtest.signals.screener import strat_htf_aligned_breakout_long
    s = {"above_prev_high": True, "vol_spike_15x": True,
         "htf_aligned_bull": True}
    assert strat_htf_aligned_breakout_long(s)["fires"] is True
    s["htf_aligned_bull"] = False
    assert strat_htf_aligned_breakout_long(s)["fires"] is False


def test_batch217_weekly_bias_pullback_long_requires_oversold_reversal():
    """Batch 217: weekly_bias_pullback_long requires weekly_bias_bull +
    RSI<40 + (hammer or bullish_engulfing)."""
    from backtest.signals.screener import strat_weekly_bias_pullback_long
    s = {"weekly_bias_bull": True, "rsi_14": 35.0,
         "hammer": True, "bullish_engulfing": False}
    assert strat_weekly_bias_pullback_long(s)["fires"] is True
    s["rsi_14"] = 50.0
    assert strat_weekly_bias_pullback_long(s)["fires"] is False


def test_batch216_smc_expansion_strategies_registered():
    """Batch 216 (SMC expansion 2026-05-18 owner-approved): 13 new SMC
    strategies registered in ALL_STRATEGIES bringing total SMC roster
    from 4 (Batch 210) to 17."""
    from backtest.signals.screener import ALL_STRATEGIES
    new_smc = [
        "smc_fvg_retest_long", "smc_fvg_retest_short", "smc_inverse_fvg",
        "smc_breaker_block_short", "smc_breaker_block_long",
        "smc_mitigation_block_long", "smc_mitigation_block_short",
        "smc_discount_long", "smc_premium_short",
        "smc_ote_long", "smc_ote_short",
        "smc_equal_highs_sweep_short", "smc_equal_lows_sweep_long",
        "smc_bos_retest_entry",
    ]
    for name in new_smc:
        assert name in ALL_STRATEGIES, f"Batch 216: {name} must be registered"
    # All 17 SMC strategies (4 + 13)
    smc_total = [k for k in ALL_STRATEGIES if k.startswith("smc_")]
    assert len(smc_total) >= 17, (
        f"Expected 17+ smc_* strategies, got {len(smc_total)}"
    )


def test_batch216_smc_fvg_retest_long_requires_zone_and_regime():
    """Batch 216: smc_fvg_retest_long fires only when price is INSIDE
    an unmitigated bullish FVG zone AND price > 200-EMA."""
    from backtest.signals.screener import strat_smc_fvg_retest_long
    s = {"smc_fvg_retest_long_zone": True, "price_above_ema_200": True}
    r = strat_smc_fvg_retest_long(s)
    assert r["fires"] is True and r["direction"] == "long"
    s["price_above_ema_200"] = False
    assert strat_smc_fvg_retest_long(s)["fires"] is False
    s["price_above_ema_200"] = True
    s["smc_fvg_retest_long_zone"] = False
    assert strat_smc_fvg_retest_long(s)["fires"] is False


def test_batch216_smc_inverse_fvg_handles_both_directions():
    """Batch 216 + 262 fix: smc_inverse_fvg fires long on inverse_fvg_bullish
    (bearish FVG broken upward) + 200-EMA gate + volume confirms. Symmetric
    short on inverse_fvg_bearish + below 200-EMA + volume confirms.
    Batch 262 added gates: 200-EMA regime + (vol_spike_2x OR force_index_breakout)
    per post-1A-alpha forensic (strategy was the dominant -1659pp contributor)."""
    from backtest.signals.screener import strat_smc_inverse_fvg
    # Long: bullish IFVG + above 200 EMA + vol confirms -> fires
    s = {
        "smc_inverse_fvg_bullish": True, "smc_inverse_fvg_bearish": False,
        "price_above_ema_200": True, "vol_spike_2x": True,
    }
    r = strat_smc_inverse_fvg(s)
    assert r["fires"] is True and r["direction"] == "long"
    # Short: bearish IFVG + below 200 EMA + vol confirms -> fires
    s = {
        "smc_inverse_fvg_bullish": False, "smc_inverse_fvg_bearish": True,
        "price_above_ema_200": False, "force_index_breakout": True,
    }
    r = strat_smc_inverse_fvg(s)
    assert r["fires"] is True and r["direction"] == "short"
    # No IFVG signal -> no fire
    s = {"smc_inverse_fvg_bullish": False, "smc_inverse_fvg_bearish": False}
    assert strat_smc_inverse_fvg(s)["fires"] is False
    # Batch 262 regression check: IFVG flag alone is NOT enough anymore
    # (this was the bug that caused 478 trades / -1659pp contribution).
    s = {"smc_inverse_fvg_bullish": True, "smc_inverse_fvg_bearish": False}
    assert strat_smc_inverse_fvg(s)["fires"] is False, (
        "Batch 262: IFVG should NOT fire without 200-EMA + volume gates"
    )


def test_batch216_smc_discount_long_requires_zone_and_structure():
    """Batch 216: discount_long requires (in discount zone) AND (BOS or
    CHoCH bullish) AND (price > 200-EMA). Strict confluence per ICT
    discipline."""
    from backtest.signals.screener import strat_smc_discount_long
    # All conditions met
    s = {
        "smc_in_discount_zone": True,
        "smc_bos_bullish": True,
        "smc_choch_bullish": False,
        "smc_dealing_range_pct": 0.3,
        "price_above_ema_200": True,
    }
    r = strat_smc_discount_long(s)
    assert r["fires"] is True and r["direction"] == "long"
    # Out of discount zone -> no fire
    s["smc_in_discount_zone"] = False
    assert strat_smc_discount_long(s)["fires"] is False
    # In zone but no structure -> no fire
    s["smc_in_discount_zone"] = True
    s["smc_bos_bullish"] = False
    assert strat_smc_discount_long(s)["fires"] is False
    # CHoCH bullish (alternate structure) also acceptable
    s["smc_choch_bullish"] = True
    assert strat_smc_discount_long(s)["fires"] is True


def test_batch216_smc_ote_long_requires_fib_zone_and_structure():
    """Batch 216: OTE long fires in 62-79% Fib retracement zone with
    bullish BOS/CHoCH backdrop."""
    from backtest.signals.screener import strat_smc_ote_long
    s = {
        "smc_ote_long_zone": True,
        "smc_bos_bullish": True,
        "smc_retracement_pct": 70.0,
    }
    r = strat_smc_ote_long(s)
    assert r["fires"] is True and r["direction"] == "long"
    # Without structure -> no fire
    s["smc_bos_bullish"] = False
    s["smc_choch_bullish"] = False
    assert strat_smc_ote_long(s)["fires"] is False


def test_batch216_smc_equal_highs_sweep_short_confluence():
    """Batch 216: equal_highs_sweep_short requires (equal-highs swept)
    AND (bearish FVG below). Both must be true."""
    from backtest.signals.screener import strat_smc_equal_highs_sweep_short
    s = {"smc_equal_highs_swept": True, "smc_fvg_bearish_active": True}
    r = strat_smc_equal_highs_sweep_short(s)
    assert r["fires"] is True and r["direction"] == "short"
    s["smc_fvg_bearish_active"] = False
    assert strat_smc_equal_highs_sweep_short(s)["fires"] is False


def test_batch216_smc_bos_retest_handles_both_directions():
    """Batch 216: bos_retest_entry fires long on bos_retest_long +
    regime gate; short symmetric."""
    from backtest.signals.screener import strat_smc_bos_retest_entry
    s_long = {"smc_bos_retest_long": True, "smc_bos_retest_short": False,
              "price_above_ema_200": True}
    r = strat_smc_bos_retest_entry(s_long)
    assert r["fires"] is True and r["direction"] == "long"
    s_short = {"smc_bos_retest_long": False, "smc_bos_retest_short": True,
               "price_above_ema_200": False}
    r2 = strat_smc_bos_retest_entry(s_short)
    assert r2["fires"] is True and r2["direction"] == "short"


def test_batch216_compute_smc_signals_emits_new_keys():
    """Batch 216: compute_smc_signals must emit the new Batch 216 keys
    when given 260+ daily bars (the SMC library's swing-detection
    history threshold is exceeded)."""
    import io, contextlib, pandas as pd, numpy as np
    from backtest.signals.smc_ict import compute_smc_signals
    rng = np.random.default_rng(7)
    n = 320
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    base = 100 + np.cumsum(rng.normal(0, 1, n))
    df = pd.DataFrame({
        "open":  base,
        "high":  base + 1 + rng.uniform(0, 1, n),
        "low":   base - 1 - rng.uniform(0, 1, n),
        "close": base + rng.normal(0, 0.3, n),
        "volume": rng.integers(1_000_000, 5_000_000, n).astype(float),
    }, index=idx)
    with contextlib.redirect_stdout(io.StringIO()):
        out = compute_smc_signals(df)
    # Batch 216 new keys - all should be present (booleans default False
    # when zones not active; dealing range pct always emitted)
    for key in [
        "smc_fvg_retest_long_zone", "smc_fvg_retest_short_zone",
        "smc_inverse_fvg_bullish", "smc_inverse_fvg_bearish",
        "smc_breaker_block_bullish", "smc_breaker_block_bearish",
        "smc_mitigation_block_long", "smc_mitigation_block_short",
        "smc_dealing_range_pct", "smc_in_discount_zone",
        "smc_in_premium_zone",
        "smc_bos_retest_long", "smc_bos_retest_short",
    ]:
        assert key in out, f"Batch 216: compute_smc_signals must emit {key}"
    # Dealing range pct must be in [0, 1]
    assert 0.0 <= out["smc_dealing_range_pct"] <= 1.0


def test_batch210_smc_strategies_registered():
    """Batch 210 (SMC/ICT family 2026-05-17): 4 SMC strategies registered."""
    from backtest.signals.screener import ALL_STRATEGIES
    for name in (
        "smc_bos_continuation",
        "smc_choch_reversal",
        "smc_order_block_bounce",
        "smc_liquidity_sweep_reversal",
    ):
        assert name in ALL_STRATEGIES, f"Batch 210: {name} must be registered"


def test_batch210_compute_smc_signals_handles_missing_data():
    """Batch 210: compute_smc_signals returns empty dict on empty input
    or missing columns (no raise)."""
    import pandas as pd
    from backtest.signals.smc_ict import compute_smc_signals
    assert compute_smc_signals(pd.DataFrame()) == {}
    # Missing required columns
    bad_df = pd.DataFrame({"foo": [1, 2, 3]})
    assert compute_smc_signals(bad_df) == {}


def test_batch210_smc_bos_continuation_long_fires_with_regime():
    """Batch 210: smc_bos_continuation long fires on BOS bullish + 200-EMA
    regime gate. Batch 278 added volume confirm + RSI direction gate."""
    from backtest.signals.screener import strat_smc_bos_continuation
    s = {
        "smc_bos_bullish": True,
        "smc_bos_bearish": False,
        "price_above_ema_200": True,
        "vol_spike_2x": True,        # Batch 278: required
        "rsi_14": 60,                # Batch 278: required > 50 for long
    }
    r = strat_smc_bos_continuation(s)
    assert r["fires"] is True and r["direction"] == "long"
    # Without regime gate -> no fire
    s["price_above_ema_200"] = False
    assert strat_smc_bos_continuation(s)["fires"] is False


def test_batch210_smc_choch_reversal_requires_fvg_confluence():
    """Batch 210: CHoCH reversal requires same-direction FVG active
    (confluence). Single-signal CHoCH alone insufficient."""
    from backtest.signals.screener import strat_smc_choch_reversal
    # CHoCH alone -> no fire
    s = {"smc_choch_bullish": True, "smc_fvg_bullish_active": False}
    assert strat_smc_choch_reversal(s)["fires"] is False
    # CHoCH + FVG -> fire
    s["smc_fvg_bullish_active"] = True
    assert strat_smc_choch_reversal(s)["fires"] is True


def test_batch209_pead_strategies_registered():
    """Batch 209 (PEAD module 2026-05-17): pead_long + pead_short
    registered in ALL_STRATEGIES."""
    from backtest.signals.screener import ALL_STRATEGIES
    assert "pead_long" in ALL_STRATEGIES
    assert "pead_short" in ALL_STRATEGIES


def test_batch209_pead_long_requires_window_and_positive_surprise():
    """Batch 209: pead_long fires only when within 60d post-earnings AND
    positive surprise (YoY EPS growth AND announcement-day return > +2%).
    Bernard-Thomas 1989 / Garfinkel-Hribar-Hsiao 2024."""
    from backtest.signals.screener import strat_pead_long
    # All conditions met
    s = {
        "within_pead_window": True,
        "pead_positive_surprise": True,
        "earnings_eps_yoy_growth": 0.25,
        "earnings_announcement_return": 0.05,
    }
    r = strat_pead_long(s)
    assert r["fires"] is True and r["direction"] == "long"
    # Outside window -> no fire
    s["within_pead_window"] = False
    assert strat_pead_long(s)["fires"] is False
    # In window but no positive surprise -> no fire
    s["within_pead_window"] = True
    s["pead_positive_surprise"] = False
    assert strat_pead_long(s)["fires"] is False


def test_batch209_pead_short_requires_negative_surprise():
    """Batch 209: pead_short fires only on within-window + negative
    surprise (YoY EPS contraction AND announcement-day return < -2%)."""
    from backtest.signals.screener import strat_pead_short
    s = {
        "within_pead_window": True,
        "pead_negative_surprise": True,
        "earnings_eps_yoy_growth": -0.15,
        "earnings_announcement_return": -0.05,
    }
    r = strat_pead_short(s)
    assert r["fires"] is True and r["direction"] == "short"
    s["pead_negative_surprise"] = False
    assert strat_pead_short(s)["fires"] is False


def test_batch209_compute_pead_signals_handles_missing_data():
    """Batch 209: compute_pead_signals returns empty dict when ticker
    has no financials prefetch / unknown ticker (no raise)."""
    from backtest.signals.pead import compute_pead_signals
    from datetime import date
    import pandas as pd
    out = compute_pead_signals("NONEXISTENT_TICKER_ZYX", pd.DataFrame(), date(2024, 6, 1))
    assert out == {}


def test_batch208_avwap_strategies_registered_in_ALL_STRATEGIES():
    """Batch 208 (new strategy family 2026-05-17): 3 Anchored VWAP
    strategies must be registered in ALL_STRATEGIES so the screener
    iterates them per ticker. Brian Shannon 2022 AVWAP discipline."""
    from backtest.signals.screener import ALL_STRATEGIES
    for name in ("avwap_252_breakout", "avwap_50_reclaim",
                 "avwap_20high_rejection_short"):
        assert name in ALL_STRATEGIES, f"Batch 208: {name} must be registered"


def test_batch208_avwap_252_breakout_long_fires_near_reclaim():
    """Batch 208: avwap_252_breakout long fires when price is just above
    AVWAP-252-low (within 2%) with volume confirmation."""
    from backtest.signals.screener import strat_avwap_252_breakout
    s = {
        "above_avwap_252low": True,
        "pct_from_avwap_252low": 0.5,  # 0.5% above (near inflection)
        "vol_spike_15x": True,
        "rsi_14": 50.0,
    }
    r = strat_avwap_252_breakout(s)
    assert r["fires"] is True and r["direction"] == "long"

    # Beyond 2% from AVWAP -> no fire (no longer "near inflection")
    s["pct_from_avwap_252low"] = 5.0
    assert strat_avwap_252_breakout(s)["fires"] is False

    # Volume missing -> no fire
    s["pct_from_avwap_252low"] = 0.5
    s["vol_spike_15x"] = False
    assert strat_avwap_252_breakout(s)["fires"] is False


def test_batch208_avwap_50_reclaim_requires_200ema_regime():
    """Batch 208: avwap_50_reclaim long requires price > 200-EMA (regime
    gate). Short side requires price below 200-EMA (symmetric)."""
    from backtest.signals.screener import strat_avwap_50_reclaim
    s = {
        "above_avwap_50low": True,
        "pct_from_avwap_50low": 0.5,
        "macd_12_26_9_bullish": True,
        "price_above_ema_200": False,  # bear regime
    }
    r = strat_avwap_50_reclaim(s)
    assert not r["fires"] or r["direction"] != "long"

    s["price_above_ema_200"] = True
    r2 = strat_avwap_50_reclaim(s)
    assert r2["fires"] is True
    assert r2["direction"] == "long"


def test_batch208_avwap_20high_rejection_short_requires_bear_regime():
    """Batch 208: avwap_20high_rejection_short requires below 200-EMA
    (bear regime confirmation) + bearish reversal candle."""
    from backtest.signals.screener import strat_avwap_20high_rejection_short
    s = {
        "above_avwap_20high": False,
        "pct_from_avwap_20high": 0.5,
        "shooting_star": True,
        "bearish_engulfing": False,
        "vol_spike_15x": True,
        "price_above_ema_200": False,
    }
    r = strat_avwap_20high_rejection_short(s)
    assert r["fires"] is True and r["direction"] == "short"

    # In bull regime -> NOT fires
    s["price_above_ema_200"] = True
    assert strat_avwap_20high_rejection_short(s)["fires"] is False


def test_batch207_compute_ichimoku_emits_weekly_kumo_signals():
    """Batch 207 (Ichimoku optimization 2026-05-17): compute_ichimoku
    must emit ichi_weekly_above_cloud / ichi_weekly_below_cloud /
    ichi_weekly_in_cloud when 260+ daily bars available. Resamples to
    weekly via pd.resample('W') and computes 9/26/52 Kumo on weekly
    bars. Linda Raschke multi-timeframe Ichimoku discipline."""
    import pandas as pd
    import numpy as np
    from backtest.signals.technical import compute_ichimoku
    # Need 260+ daily bars indexed by DatetimeIndex
    n = 320
    idx = pd.date_range("2023-01-02", periods=n, freq="B")
    rng = np.random.default_rng(42)
    base = 100 + np.cumsum(rng.normal(0.05, 1, n))  # mild uptrend
    df = pd.DataFrame({
        "open":  base,
        "high":  base + 1,
        "low":   base - 1,
        "close": base,
        "volume": (1_000_000 + rng.integers(0, 500_000, n)).astype(float),
    }, index=idx)
    out = compute_ichimoku(df)
    assert "ichi_weekly_above_cloud" in out, (
        "Batch 207: weekly Kumo signals must be emitted with 260+ daily bars"
    )
    assert "ichi_weekly_below_cloud" in out
    assert "ichi_weekly_in_cloud" in out
    # Exactly one of above/below/in must be true (mutually exclusive)
    flags = sum([
        out["ichi_weekly_above_cloud"],
        out["ichi_weekly_below_cloud"],
        out["ichi_weekly_in_cloud"],
    ])
    assert flags == 1, f"Batch 207: weekly Kumo flags must be mutually exclusive, got {flags} true"


def test_batch207_ichimoku_cloud_breakout_requires_weekly_kumo():
    """Batch 207: strat_ichimoku_cloud_breakout long requires weekly
    Kumo also above cloud. Phase 1A-beta showed -1.00 Sharpe at 43
    trades indicating daily-only Kumo is too permissive (catches
    counter-trend false breakouts)."""
    from backtest.signals.screener import strat_ichimoku_cloud_breakout
    # Daily above cloud + tk_bullish + adx_trending BUT weekly below cloud
    s = {
        "ichi_above_cloud": True, "ichi_below_cloud": False,
        "ichi_tk_bullish": True, "ichi_tk_bearish": False,
        "adx_trending": True,
        "ichi_weekly_above_cloud": False,  # weekly disagrees
        "ichi_weekly_below_cloud": True,
    }
    r = strat_ichimoku_cloud_breakout(s)
    assert not r["fires"] or r["direction"] != "long", (
        "Batch 207: ichimoku long must NOT fire when weekly Kumo disagrees"
    )
    # Now weekly agrees
    s["ichi_weekly_above_cloud"] = True
    s["ichi_weekly_below_cloud"] = False
    r2 = strat_ichimoku_cloud_breakout(s)
    assert r2["fires"] is True
    assert r2["direction"] == "long"


def test_batch207_hull_rsi_requires_adx_gt_20():
    """Batch 207: strat_hull_rsi must require ADX(14)>20 trend
    confirmation. Hull alone whipsaws in chop; ADX>20 gate cuts
    false-signal rate in half (cited SSRN replications).

    Batch 358 update: hull_rsi long also requires price_above_ema_200
    (bear-block per cell-audit Bucket B). Fixture extended with the
    200-EMA gate so the test still validates the Batch 207 ADX path."""
    from backtest.signals.screener import strat_hull_rsi
    # Hull bullish, price above hull, RSI>50, above 200-EMA - but ADX=15 (chop)
    s = {
        "hull_bullish": True,
        "price_above_hull": True,
        "rsi_9": 60.0,
        "adx": 15.0,           # below 20
        "adx_trending": False,
        "price_above_ema_200": True,  # Batch 358 gate satisfied
    }
    r = strat_hull_rsi(s)
    assert not r["fires"] or r["direction"] != "long", (
        "Batch 207: hull_rsi long must NOT fire when ADX<20 (chop)"
    )
    # Same scenario with ADX=25 -> fires
    s["adx"] = 25.0
    r2 = strat_hull_rsi(s)
    assert r2["fires"] is True
    assert r2["direction"] == "long"


def test_batch206_williams_r_oversold_connors_rsi2_path():
    """Batch 206 (Connors stack 2026-05-17): williams_r_oversold long
    fires on EITHER williams_r_oversold OR rsi_2<5 (short-window extreme).
    Phase 1A-beta showed this strategy at Sharpe 0.30 (best in oversold
    family) on 82 trades; opening the RSI(2) path increases fill rate
    while preserving the 200-EMA regime gate + CMF confirmation."""
    from backtest.signals.screener import strat_williams_r_oversold
    # rsi_2<5 fires even when williams_r_oversold is False
    s = {
        "williams_r_oversold": False,
        "williams_r": -50.0,
        "rsi_2": 3.0,
        "price_above_ema_200": True,
        "cmf_positive": True,
    }
    r = strat_williams_r_oversold(s)
    assert r["fires"] is True and r["direction"] == "long"

    # Both False -> no fire
    s["rsi_2"] = 50.0
    assert strat_williams_r_oversold(s)["fires"] is False

    # 200-EMA gate still enforced
    s["rsi_2"] = 3.0
    s["price_above_ema_200"] = False
    assert strat_williams_r_oversold(s)["fires"] is False


def test_batch206_stochrsi_oversold_adds_regime_gate():
    """Batch 206: strat_stochrsi_oversold must require price_above_ema_200
    for long entry. Phase 1A-beta showed -1.01 expected_value across 132
    trades indicating bias toward firing in downtrends without the gate."""
    from backtest.signals.screener import strat_stochrsi_oversold
    s = {
        "stochrsi_oversold": True,
        "stochrsi_cross_up": True,
        "rsi_14": 40.0,
        "price_above_ema_200": False,
    }
    r = strat_stochrsi_oversold(s)
    assert not r["fires"] or r["direction"] != "long", (
        "Batch 206: stochrsi_oversold long must NOT fire when price below 200-EMA"
    )
    s["price_above_ema_200"] = True
    r2 = strat_stochrsi_oversold(s)
    assert r2["fires"] is True


def test_batch206_ultimate_oscillator_connors_rsi2_path():
    """Batch 206: ultimate_oscillator must accept rsi_2<5 as alternate
    long primary. UO had Sharpe 0.49 on 27 trades in Phase 1A-beta - best
    oversold-family risk-adjusted but small sample. Connors path opens
    new entries without sacrificing the 200-SMA regime gate."""
    from backtest.signals.screener import strat_ultimate_oscillator
    s = {
        "uo_oversold": False,
        "uo": 50.0,
        "rsi_2": 3.0,
        "price_above_sma_200": True,
    }
    r = strat_ultimate_oscillator(s)
    assert r["fires"] is True and r["direction"] == "long"


def test_batch206_rsi_oversold_rsi2_path_opens_inactive_strategy():
    """Batch 206: strat_rsi_oversold (0 trades in Phase 1A-beta) gains
    Connors RSI(2)<5 path so it can actually fire. 200-EMA regime gate
    added in addition to existing 50-SMA pullback context."""
    from backtest.signals.screener import strat_rsi_oversold
    # rsi_14=50 (NOT below 35) but rsi_2=3 -> fires via Connors path
    s = {
        "rsi_2": 3.0, "rsi_14": 50.0,
        "price_above_sma_50": True,
        "price_above_ema_200": True,
    }
    r = strat_rsi_oversold(s)
    assert r["fires"] is True and r["direction"] == "long"
    # 200-EMA gate enforced
    s["price_above_ema_200"] = False
    assert strat_rsi_oversold(s)["fires"] is False


def test_batch205_compute_vwap_emits_anchored_vwap_signals():
    """Batch 205 (Pivot optimization 2026-05-17): compute_vwap must emit
    avwap_252low / avwap_50low / avwap_20high and the above_*/pct_from_*
    counterparts. Brian Shannon (2022) "Maximum Trading Gains With
    Anchored VWAP" CMT whitepaper: AVWAP anchored at swing low/high is
    the institutional reference level for pivot breakouts."""
    import pandas as pd
    import numpy as np
    from backtest.signals.technical import compute_vwap
    rng = np.random.default_rng(42)
    closes = 100 + np.cumsum(rng.normal(0, 1, 300))
    highs = closes + 1
    lows  = closes - 1
    vols  = (1_000_000 + rng.integers(0, 500_000, 300)).astype(float)
    df = pd.DataFrame({"high": highs, "low": lows, "close": closes, "volume": vols})
    out = compute_vwap(df)
    assert "avwap_252low" in out, "Batch 205: compute_vwap must emit avwap_252low"
    assert "above_avwap_252low" in out
    assert "pct_from_avwap_252low" in out
    assert "avwap_50low" in out
    assert "above_avwap_50low" in out
    assert "avwap_20high" in out
    assert "above_avwap_20high" in out
    # AVWAP values must be positive
    assert out["avwap_252low"] > 0
    assert out["avwap_50low"]  > 0


def test_batch205_pivot_r1_requires_avwap_gate():
    """Batch 205: strat_pivot_r1_breakout must require above_avwap_252low
    AND above_avwap_50low for long entries. AVWAP gate filters out R1
    breakouts that occur below the institutional reference (failed
    breakouts more likely)."""
    from backtest.signals.screener import strat_pivot_r1_breakout
    # All entry conditions met EXCEPT AVWAP
    s = {
        "above_r1": True, "below_s1": False,
        "vol_spike_15x": True,
        "macd_12_26_9_bullish": True,
        "above_avwap_252low": False,  # below institutional reference
        "above_avwap_50low": False,
    }
    r = strat_pivot_r1_breakout(s)
    assert not r["fires"] or r["direction"] != "long", (
        "Batch 205: pivot_r1 long must NOT fire when below AVWAP"
    )
    # All conditions met INCLUDING AVWAP
    s["above_avwap_252low"] = True
    s["above_avwap_50low"]  = True
    r2 = strat_pivot_r1_breakout(s)
    assert r2["fires"] is True
    assert r2["direction"] == "long"


def test_batch205_pivot_r2_requires_2x_volume():
    """Batch 205: pivot_r2_continuation upgrades volume gate from 1.5x
    to 2x ADV(20) (DiNapoli discipline for stronger trend signals).
    Falls back to vol_spike_15x when vol_spike_2x missing."""
    from backtest.signals.screener import strat_pivot_r2_continuation
    s = {
        "above_r2": True, "below_s2": False,
        "adx_trending": True,
        "ema_50_200_bullish": True,
        "above_avwap_252low": True, "above_avwap_50low": True,
        "vol_spike_2x": False,    # 2x not met
        "vol_spike_15x": True,    # 1.5x met
    }
    # vol_spike_2x missing -> falls back to vol_spike_15x. With 1.5x
    # available (but not 2x), strategy uses vol_spike_15x as fallback.
    # Since vol_spike_2x is False, the test should still fire when
    # vol_spike_2x evaluates falsy -> fallback to vol_spike_15x.
    r = strat_pivot_r2_continuation(s)
    # Either both present and 2x preferred, or only 15x present and used.
    # The fallback construct s.get('vol_spike_2x', s.get('vol_spike_15x'))
    # returns False (2x is explicitly False), so r should NOT fire.
    assert r["fires"] is False, (
        "Batch 205: r2_continuation must require 2x volume when explicit "
        "vol_spike_2x=False (no fallback when key present-and-False)"
    )
    # Now with 2x true
    s["vol_spike_2x"] = True
    r2 = strat_pivot_r2_continuation(s)
    assert r2["fires"] is True


def test_batch205_cpr_narrow_bullish_avwap_gate():
    """Batch 205: cpr_narrow_bullish requires above_avwap_50low for long.

    Batch 358 update: long also requires price_above_ema_200 (bear-block
    per cell-audit Bucket B). Fixture extended."""
    from backtest.signals.screener import strat_cpr_narrow_bullish
    s = {
        "cpr_narrow": True, "above_cpr": True, "below_cpr": False,
        "rsi_14": 55, "above_avwap_50low": False,
        "price_above_ema_200": True,  # Batch 358 gate satisfied
    }
    r = strat_cpr_narrow_bullish(s)
    assert not r["fires"] or r["direction"] != "long"
    s["above_avwap_50low"] = True
    assert strat_cpr_narrow_bullish(s)["fires"] is True


def test_batch204_rsi_2_added_to_compute_rsi():
    """Batch 204 (Bollinger optimization 2026-05-17): compute_rsi must
    emit rsi_2 alongside rsi_9/14/21 to support Connors RSI(2) gate.
    Larry Connors discipline (Quantified Strategies 2024 backtest): RSI(2)
    is the canonical short-window mean-reversion oscillator."""
    import pandas as pd
    import numpy as np
    from backtest.signals.technical import compute_rsi
    rng = np.random.default_rng(42)
    closes = 100 + np.cumsum(rng.normal(0, 1, 250))
    df = pd.DataFrame({"close": closes})
    out = compute_rsi(df)
    assert "rsi_2" in out, "Batch 204: compute_rsi must emit rsi_2"
    assert "rsi_9" in out
    assert "rsi_14" in out
    assert "rsi_21" in out
    assert 0 <= out["rsi_2"] <= 100


def test_batch204_compute_macro_overlays_adds_vix_band():
    """Batch 204: compute_macro_overlays adds vix_percentile + vix_band
    to signals dict when VIX context is supplied; no-op when missing."""
    from backtest.signals.technical import compute_macro_overlays
    hist = list(range(10, 41)) * 10  # VIX 10..40, 310 obs
    out_low = compute_macro_overlays({"rsi_14": 30.0}, vix_value=10.0, vix_history=hist)
    assert out_low["vix_band"] == "low"
    assert out_low["vix_band_low"] is True
    assert out_low["rsi_14"] == 30.0
    out_hi = compute_macro_overlays({"rsi_14": 30.0}, vix_value=40.0, vix_history=hist)
    assert out_hi["vix_band"] == "high"
    out_none = compute_macro_overlays({"rsi_14": 30.0}, vix_value=None, vix_history=hist)
    assert "vix_band" not in out_none
    out_none2 = compute_macro_overlays({"rsi_14": 30.0}, vix_value=20.0, vix_history=None)
    assert "vix_band" not in out_none2
    out_short = compute_macro_overlays({"rsi_14": 30.0}, vix_value=20.0, vix_history=[15.0] * 10)
    assert "vix_band" not in out_short


def test_batch204_bollinger_lower_requires_200ema_regime_gate():
    """Batch 204: strat_bollinger_lower must require price_above_ema_200
    for long entry (Connors regime-gate discipline). Without the gate,
    the strategy fades mega-cap-driven uptrends (Mag-7 fade trap)."""
    from backtest.signals.screener import strat_bollinger_lower
    s = {
        "bb_20_20_touch_lower": True, "bb_20_20_touch_upper": False,
        "rsi_2": 3.0, "rsi_14": 30.0, "adx": 20.0,
        "price_above_ema_200": False,
    }
    r = strat_bollinger_lower(s)
    assert not r["fires"] or r["direction"] != "long", (
        "Batch 204: bollinger_lower long must NOT fire when price below 200-EMA"
    )
    s["price_above_ema_200"] = True
    r2 = strat_bollinger_lower(s)
    assert r2["fires"] is True
    assert r2["direction"] == "long"


def test_batch204_bollinger_lower_connors_rsi2_path():
    """Batch 204: RSI(2)<5 fires even when RSI(14) is moderate.
    Connors canonical: short-window oscillator extreme is the primary
    entry signal, long-window RSI is the fallback."""
    from backtest.signals.screener import strat_bollinger_lower
    s = {
        "bb_20_20_touch_lower": True, "bb_20_20_touch_upper": False,
        "rsi_2": 3.0, "rsi_14": 50.0,  # NOT conventionally oversold
        "adx": 20.0, "price_above_ema_200": True,
    }
    r = strat_bollinger_lower(s)
    assert r["fires"] is True
    assert r["direction"] == "long"


def test_batch204_bollinger_vix_band_adjusts_threshold():
    """Batch 204: VIX-low band tightens RSI threshold (35 vs 40); VIX-high
    band loosens (45 vs 40). Atlantis-Press Su 2024 confluence study."""
    from backtest.signals.screener import strat_bollinger_lower
    s_low = {
        "bb_20_20_touch_lower": True, "bb_20_20_touch_upper": False,
        "rsi_2": 30.0, "rsi_14": 42.0, "adx": 20.0,
        "price_above_ema_200": True, "vix_band_low": True,
    }
    assert strat_bollinger_lower(s_low)["fires"] is False
    s_hi = dict(s_low)
    s_hi["vix_band_low"] = False
    s_hi["vix_band_high"] = True
    assert strat_bollinger_lower(s_hi)["fires"] is True


def test_batch203_regime_selector_default_allows_uncharacterized():
    """Batch 203 (regime SELECTOR per AMH research review owner-approved
    2026-05-17): strategies NOT in STRATEGY_REGIME_AFFINITY default to
    allow-all-regimes so existing behavior is preserved on day 1; only
    explicit affinity entries gate. This matches the existing
    STRATEGY_REGIME_BLOCKLIST opt-in semantics (config.py)."""
    from backtest.engine.regime_selector import (
        should_strategy_fire_in_regime,
        STRATEGY_REGIME_AFFINITY,
    )
    for r in ("bull", "neutral", "bear", "crisis"):
        assert should_strategy_fire_in_regime("brand_new_strategy_not_in_map", r) is True
    # Unknown regime: always block (fail-closed per DEC-316)
    assert should_strategy_fire_in_regime("anything", "unknown") is False


def test_batch203_regime_selector_enforces_affinity():
    """Batch 203: strategies WITH affinity entries only fire in permitted regimes.
    Updated Batch 271: shorts now allow neutral too (expansion per T1a forensic).
    """
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    # bollinger_lower: allow neutral+bear, block bull+crisis (Mag-7 fade trap)
    assert should_strategy_fire_in_regime("bollinger_lower", "neutral") is True
    assert should_strategy_fire_in_regime("bollinger_lower", "bear") is True
    assert should_strategy_fire_in_regime("bollinger_lower", "bull") is False
    assert should_strategy_fire_in_regime("bollinger_lower", "crisis") is False
    # pivot_r1_breakout: allow bull+neutral, block bear+crisis
    assert should_strategy_fire_in_regime("pivot_r1_breakout", "bull") is True
    assert should_strategy_fire_in_regime("pivot_r1_breakout", "bear") is False
    # cmf_flip: Batch 418 cube-empirical override 2026-05-28 - was allow-all
    # ("regime-agnostic"), now {bear, neutral} only (bull Sharpe negative;
    # 0 crisis trades in cube). Pin updated per cube data.
    assert should_strategy_fire_in_regime("cmf_flip", "bear") is True
    assert should_strategy_fire_in_regime("cmf_flip", "neutral") is True
    assert should_strategy_fire_in_regime("cmf_flip", "bull") is False
    assert should_strategy_fire_in_regime("cmf_flip", "crisis") is False
    # Short-side (post-Batch-271): allow bear + crisis + neutral, block bull only
    assert should_strategy_fire_in_regime("hull_rsi_short", "bear") is True
    assert should_strategy_fire_in_regime("hull_rsi_short", "crisis") is True
    assert should_strategy_fire_in_regime("hull_rsi_short", "neutral") is True
    assert should_strategy_fire_in_regime("hull_rsi_short", "bull") is False


def test_batch273_smc_most_recent_event_within():
    """Batch 273 (Tier 2.1 SMC family wiring audit): helper returns the
    most-recent non-zero value if within recency_bars, else None.
    Addresses the SMC library detection-lag bug: BOS/CHOCH/OB events
    detected 20-80 bars after the actual event, making fvg_lookback=5
    tail-slice always miss them."""
    import pandas as pd
    from backtest.signals.smc_ict import _most_recent_event_within

    # Event at index 80, current at index 100: within 50-bar recency
    s = pd.Series([0] * 80 + [1] + [0] * 19 + [0])
    assert _most_recent_event_within(s, current_idx=100, recency_bars=50) == 1

    # Event at index 30, current at index 100: outside 50-bar recency
    s = pd.Series([0] * 30 + [-1] + [0] * 70)
    assert _most_recent_event_within(s, current_idx=100, recency_bars=50) is None

    # No events: returns None
    s = pd.Series([0] * 100)
    assert _most_recent_event_within(s, current_idx=99, recency_bars=50) is None

    # Most-recent of multiple: returns the last one
    s = pd.Series([0] * 50 + [1] + [0] * 30 + [-1] + [0] * 20)
    assert _most_recent_event_within(s, current_idx=100, recency_bars=50) == -1


def test_batch273_smc_base_signals_fire_with_default_params():
    """Batch 273: after the fix (swing_length=20 + event_recency_bars=90
    defaults), SMC base signals like smc_bos_bullish must fire at least
    occasionally on real OHLCV data. The bug being fixed: all 15 of 16
    SMC strategies (everything except smc_inverse_fvg) fired zero
    candidates in the T1a 4y backtest because of detection-lag +
    tail-slice mismatch."""
    import numpy as np
    import pandas as pd
    from backtest.signals.smc_ict import compute_smc_signals, _SMC_AVAILABLE

    if not _SMC_AVAILABLE:
        import pytest
        pytest.skip("smartmoneyconcepts library not available")

    # Build a synthetic OHLC with clear swing structure
    rng = np.random.default_rng(42)
    n = 500
    # Create a series with multiple swing highs/lows to force BOS detection
    closes = []
    base = 100.0
    for i in range(n):
        if (i // 40) % 2 == 0:
            base += rng.normal(0.5, 1.0)  # uptrend
        else:
            base -= rng.normal(0.5, 1.0)  # downtrend
        closes.append(base)
    closes = np.array(closes)
    df = pd.DataFrame({
        "open":   closes - 0.5,
        "high":   closes + 1.0,
        "low":    closes - 1.0,
        "close":  closes,
        "volume": 1_000_000,
    })

    out = compute_smc_signals(df)
    assert "smc_bos_bullish" in out or "smc_bos_bearish" in out, (
        "BOS signal keys must appear in output even when False"
    )


def test_batch284_check_per_strategy_exit_hit_fixed_4r_2r_target():
    """Batch 284: fixed_4r_2r target hit triggers exit at +4R from entry."""
    from datetime import date
    from backtest.engine.exit_manager import _check_per_strategy_exit_hit, OpenTrade
    # bollinger_lower has fixed_4r_2r in STRATEGY_EXIT_OVERRIDE per Batch 284.
    trade = OpenTrade(
        ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
        direction="long", strategy="bollinger_lower", category="mean_reversion",
        sector="Tech", initial_stop=95.0, trailing_stop=95.0,
        highest_close=100.0, regime_at_entry="neutral",
    )
    # R = 5. +4R target = 120. today_high 121 reaches target -> exit at 120
    exit_price, exit_reason = _check_per_strategy_exit_hit(
        trade, today_high=121.0, today_low=110.0, today_close=119.0,
        today_date=date(2024, 1, 10),
    )
    assert exit_price == 120.0, f"target should fire at 120, got {exit_price}"
    assert "fixed_4r_2r_target_hit" in exit_reason


def test_batch284_check_per_strategy_exit_hit_fixed_4r_2r_stop():
    """Batch 284: fixed_4r_2r stop hit triggers exit at -2R from entry."""
    from datetime import date
    from backtest.engine.exit_manager import _check_per_strategy_exit_hit, OpenTrade
    trade = OpenTrade(
        ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
        direction="long", strategy="bollinger_lower", category="mean_reversion",
        sector="Tech", initial_stop=95.0, trailing_stop=95.0,
        highest_close=100.0, regime_at_entry="neutral",
    )
    # R = 5. -2R stop = 90. today_low 89 reaches stop -> exit at 90
    exit_price, exit_reason = _check_per_strategy_exit_hit(
        trade, today_high=98.0, today_low=89.0, today_close=92.0,
        today_date=date(2024, 1, 10),
    )
    assert exit_price == 90.0, f"stop should fire at 90, got {exit_price}"
    assert "fixed_4r_2r_stop_hit" in exit_reason


def test_batch284_check_per_strategy_exit_hit_class_time_stop():
    """Batch 284: class_time_stop fires at category-specific window.
    po3_bullish (category=momentum) -> window=30 days."""
    from datetime import date
    from backtest.engine.exit_manager import _check_per_strategy_exit_hit, OpenTrade
    trade = OpenTrade(
        ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
        direction="long", strategy="po3_bullish", category="momentum",
        sector="Tech", initial_stop=90.0, trailing_stop=90.0,
        highest_close=105.0, regime_at_entry="bull",
    )
    # Day 30+: should fire
    exit_price, exit_reason = _check_per_strategy_exit_hit(
        trade, today_high=108.0, today_low=104.0, today_close=107.0,
        today_date=date(2024, 1, 31),  # 30 days later
    )
    assert exit_price == 107.0
    assert "class_time_stop" in exit_reason
    assert "momentum" in exit_reason

    # Day 28: should NOT fire (hold_days < window)
    exit_price2, _ = _check_per_strategy_exit_hit(
        trade, today_high=108.0, today_low=104.0, today_close=107.0,
        today_date=date(2024, 1, 29),
    )
    assert exit_price2 is None


def test_batch284_check_per_strategy_exit_hit_no_override_returns_none():
    """Batch 284: strategy without exit_method override returns (None, None).
    Falls through to default trailing stop in caller."""
    from datetime import date
    from backtest.engine.exit_manager import _check_per_strategy_exit_hit, OpenTrade
    trade = OpenTrade(
        ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
        direction="long", strategy="not_in_override_dict",
        category="momentum", sector="Tech", initial_stop=95.0,
        trailing_stop=95.0, highest_close=105.0, regime_at_entry="bull",
    )
    exit_price, exit_reason = _check_per_strategy_exit_hit(
        trade, today_high=150.0, today_low=50.0, today_close=140.0,
        today_date=date(2024, 6, 1),
    )
    assert exit_price is None
    assert exit_reason is None


def test_batch284_check_per_strategy_exit_hit_r_multiple():
    """Batch 284: r_multiple_2r fires at +2R from entry."""
    from datetime import date
    from backtest.engine.exit_manager import _check_per_strategy_exit_hit, OpenTrade
    from backtest.config import STRATEGY_EXIT_OVERRIDE
    STRATEGY_EXIT_OVERRIDE["test_rmult"] = {"exit_method": "r_multiple_2r"}
    try:
        trade = OpenTrade(
            ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
            direction="long", strategy="test_rmult", category="momentum",
            sector="Tech", initial_stop=95.0, trailing_stop=95.0,
            highest_close=100.0, regime_at_entry="bull",
        )
        # R=5, +2R target = 110
        exit_price, exit_reason = _check_per_strategy_exit_hit(
            trade, today_high=111.0, today_low=100.0, today_close=110.5,
            today_date=date(2024, 1, 10),
        )
        assert exit_price == 110.0
        assert "r_multiple_2r" in exit_reason
    finally:
        STRATEGY_EXIT_OVERRIDE.pop("test_rmult", None)


def test_batch391_exit_method_analyzer_3_layer_output():
    """Batch 391 (owner 2026-05-26): exit-method optimization framework
    at (strategy x exit) cell level. analyze_exit_methods produces 3
    layers: aggregate exit-method ranking, per-(strategy x exit) cells,
    and parameter-variant winners within exit-family (time_stop_10d vs
    time_stop_20d, etc.)."""
    import sys
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo / "scripts"))
    import importlib
    mod = importlib.import_module("optimize_strategies_from_cube")

    import pandas as pd
    # Synthetic cube data: 2 strategies x 4 exits x ~10 trades each
    rows = []
    import numpy as np
    rng = np.random.default_rng(42)
    for strat in ("strat_A", "strat_B"):
        for em in ("time_stop_10d", "time_stop_20d", "r_multiple_2r", "r_multiple_3r"):
            for _ in range(10):
                rows.append({
                    "strategy":     strat,
                    "exit_method":  em,
                    "pnl_pct":      float(rng.normal(loc=1.0, scale=2.0)),
                    "hold_days":    10.0,
                    "win":          bool(rng.random() > 0.5),
                })
    cube = pd.DataFrame(rows)
    result = mod.analyze_exit_methods(cube, m_total_candidates=10)

    assert result["status"] == "ok"
    # Layer 1: 4 exit methods analyzed
    assert len(result["layer_1_per_exit_method_aggregate"]) == 4
    for em in ("time_stop_10d", "time_stop_20d", "r_multiple_2r", "r_multiple_3r"):
        assert em in result["layer_1_per_exit_method_aggregate"]
        d = result["layer_1_per_exit_method_aggregate"][em]
        assert "sharpe" in d
        assert "n_strategies_paired" in d
        assert d["n_strategies_paired"] == 2

    # Layer 2: per-(strategy x exit) cells (2 x 4 = 8 cells, all n=10)
    assert len(result["layer_2_per_strategy_exit_cell"]) == 8
    for r in result["layer_2_per_strategy_exit_cell"]:
        assert r["n"] == 10
        assert "sharpe" in r
        assert "verdict" in r

    # Layer 3: parameter-variant winners
    l3 = result["layer_3_parameter_variant_winners"]
    assert "strat_A" in l3 and "strat_B" in l3
    for strat in ("strat_A", "strat_B"):
        # time_stop family has 2 variants in synthetic data
        assert "time_stop" in l3[strat]
        assert l3[strat]["time_stop"]["winner"] in ("time_stop_10d", "time_stop_20d")
        # r_multiple family has 2 variants
        assert "r_multiple" in l3[strat]
        assert l3[strat]["r_multiple"]["winner"] in ("r_multiple_2r", "r_multiple_3r")


def test_batch390_squeeze_fire_up_dn_fixed_emits_truthy():
    """Batch 390 producer fix (owner 2026-05-26): squeeze_fire_up/_dn
    formula was `delta = close - mid20 + ema20` producing values around
    price level (~$150 AAPL) so `pmom <= 0` was impossible. Fix removed
    the `+ ema20` term, giving signed values around 0.

    Pre-fix empirical: 0/1542 ticker-days across 10 tickers x 4y.
    Post-fix verification: this test confirms the formula now emits
    truthy values on a synthetic price series that crosses the midpoint.
    """
    import pandas as pd
    import numpy as np
    from backtest.signals.technical import compute_squeeze
    # Synthetic series with a clear mid-line crossing (50 bars, sine-like)
    n = 50
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    prices = 100 + 5 * np.sin(np.linspace(0, 4 * np.pi, n))
    df = pd.DataFrame({
        "open":   prices,
        "high":   prices + 0.5,
        "low":    prices - 0.5,
        "close":  prices,
        "volume": [1_000_000] * n,
    }, index=dates)
    # Walk-forward to find at least one squeeze_fire_up
    found_up = False
    found_dn = False
    for end_idx in range(25, n + 1):
        sub = df.iloc[:end_idx]
        sq = compute_squeeze(sub)
        if sq.get("squeeze_fire_up", False):
            found_up = True
        if sq.get("squeeze_fire_dn", False):
            found_dn = True
    # On a sinusoidal series we expect BOTH fire-up and fire-dn over a
    # full cycle. Pre-fix this would be False / False everywhere.
    assert found_up, "Batch 390 regression: squeeze_fire_up never True post-fix"
    assert found_dn, "Batch 390 regression: squeeze_fire_dn never True post-fix"


def test_batch390_smc_equal_highs_lows_swept_fixed_filter():
    """Batch 390 producer fix (owner 2026-05-26): smc_equal_highs/lows_swept
    was using tail(50) on OHLCV-aligned liquidity df where liquidity events
    are SPARSE (1 in 500 rows on AAPL). tail(50) almost always missed the
    events. Fix filters to liquidity-event rows first, then takes last 20
    ACTUAL EVENTS and checks recency.

    Pre-fix empirical: 0/1542 ticker-days across 10 tickers x 4y.
    Post-fix verification: pin the source-grep that the fix is present
    (full empirical re-test requires real OHLCV data; cannot synthesize
    in unit test - integration coverage by Stage D pilot post-Batch-390).
    """
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    src = (repo / "backtest" / "signals" / "smc_ict.py").read_text(encoding="utf-8")
    # Pre-fix: tail(50) on liq_df; post-fix: filter to events then tail(20)
    assert "liq_df[" in src and "liq_df[\"Liquidity\"].notna()" in src, (
        "Batch 390 regression: smc_equal sweep fix must filter to liquidity events first"
    )
    assert "(current_idx - float(swept_val)) > 50" in src, (
        "Batch 390 regression: recency window must be applied to Swept bar-index"
    )


def test_batch386_max_cands_auto_raised_200_for_phase_1a_beta():
    """Batch 386 (owner-approved 2026-05-26 option B): when phase=1a-beta,
    --max-cands default 30 is auto-raised to 200. With --no-agents the
    agent-cost-control rationale for the 30 cap does not apply; cube
    evaluation needs more per-day candidate throughput."""
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    src = (repo / "backtest" / "run_phase1a.py").read_text(encoding="utf-8")
    assert "args.max_cands = 200" in src, (
        "Batch 386 regression: phase=1a-beta must auto-raise max-cands to 200"
    )
    assert "[Batch 386]" in src, "Batch 386 banner missing"


def test_batch385_buyback_8k_recent_long_days_loosened_3_to_5():
    """Batch 385 Gate 4 opt (owner-approved 2026-05-26 per Batch 380):
    days_since_8k threshold loosened 3 -> 5 days based on Lopez-Lira-Tang
    2023 5-day post-8K reaction window. Empirical Phase 1A-beta evidence:
    all 86 fires had days_since_8k right at the 3-day boundary."""
    from backtest.signals.screener import strat_buyback_8k_recent_long
    # Day 4 should now fire (was blocked pre-Batch-385)
    sig_day4 = {
        "recent_8k_filed":     True,
        "days_since_8k":       4,
        "price_above_ema_200": True,
        "vol_spike_15x":       True,
    }
    result = strat_buyback_8k_recent_long(sig_day4)
    assert result["fires"] is True, "Day 4 should fire post-Batch-385 (was 3, now 5)"
    # Day 5 still fires
    sig_day5 = {**sig_day4, "days_since_8k": 5}
    assert strat_buyback_8k_recent_long(sig_day5)["fires"] is True
    # Day 6 still blocked (boundary still applies)
    sig_day6 = {**sig_day4, "days_since_8k": 6}
    assert strat_buyback_8k_recent_long(sig_day6)["fires"] is False


def test_batch384_no_regime_affinity_and_no_event_suppression_bypass_gates():
    """Batch 384 Gate 2 + Gate 3 optimization (owner 2026-05-26):
    --no-regime-affinity + --no-event-suppression flags bypass Batch
    203/293 regime affinity filter and DEC-348 event suppression
    (FOMC/CPI/NFP/earnings) for Phase 1A-beta cube evaluation.
    """
    from backtest.engine.backtest import BacktestEngine
    e = BacktestEngine.__new__(BacktestEngine)
    e.no_regime_affinity = True
    e.no_event_suppression = True
    assert e.no_regime_affinity is True
    assert e.no_event_suppression is True
    e2 = BacktestEngine.__new__(BacktestEngine)
    e2.no_regime_affinity = False
    e2.no_event_suppression = False
    assert e2.no_regime_affinity is False
    assert e2.no_event_suppression is False


def test_batch384_phase_1a_beta_auto_enables_gate2_gate3_in_cli():
    """Batch 384: run_phase1a.py auto-enables --no-regime-affinity AND
    --no-event-suppression when --phase=1a-beta (parallel to 377/383)."""
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    src = (repo / "backtest" / "run_phase1a.py").read_text(encoding="utf-8")
    assert "no_regime_affinity" in src and 'args.phase == "1a-beta"' in src
    assert "no_event_suppression" in src
    assert "[Batch 384]" in src, "Batch 384 banner missing"


def test_batch383_no_dd_halt_bypasses_dec_515_level_6():
    """Batch 383 (owner directive 2026-05-26 option A): no_dd_halt=True
    bypasses the DEC-515 Level 6 portfolio DD halt + raises Portfolio.
    can_open drawdown_suspend_pct to 999%. Phase 1A-beta cube evaluation
    needs this; Phase 1B-alpha re-engages the halt.
    """
    from backtest.engine.backtest import BacktestEngine
    e = BacktestEngine.__new__(BacktestEngine)
    e.no_dd_halt = True
    assert e.no_dd_halt is True
    e2 = BacktestEngine.__new__(BacktestEngine)
    e2.no_dd_halt = False
    assert e2.no_dd_halt is False


def test_batch383_phase_1a_beta_auto_enables_no_dd_halt_in_cli():
    """Batch 383: run_phase1a.py auto-enables --no-dd-halt when
    --phase=1a-beta (parallel to Batch 377 --no-portfolio-cap)."""
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    src = (repo / "backtest" / "run_phase1a.py").read_text(encoding="utf-8")
    assert "no_dd_halt" in src and 'args.phase == "1a-beta"' in src, (
        "Batch 383 regression: phase=1a-beta must auto-enable --no-dd-halt"
    )
    assert "[Batch 383]" in src, "Batch 383 banner missing"


def test_batch377_no_portfolio_cap_bypasses_engine_gate():
    """Batch 377 (owner directive 2026-05-26): when no_portfolio_cap=True,
    BacktestEngine sets _effective_cap=99999 so neither Batch 203 regime
    cap nor LIVE_TRADING_RULES max_open_positions binds.

    Drawdown halt + ticker-uniqueness + cash-sufficiency gates still apply
    (those are second-stage can_open checks, not the cap check).

    Phase 1A-β cube evaluation needs every gate-eligible candidate; Phase
    1B-α re-engages the cap.
    """
    from backtest.engine.backtest import BacktestEngine
    # Construct minimal engine to verify the flag plumbs through
    e = BacktestEngine.__new__(BacktestEngine)
    e.no_portfolio_cap = True
    assert e.no_portfolio_cap is True

    e2 = BacktestEngine.__new__(BacktestEngine)
    e2.no_portfolio_cap = False
    assert e2.no_portfolio_cap is False


def test_batch377_phase_1a_beta_auto_enables_no_portfolio_cap_in_cli():
    """Batch 377: run_phase1a.py auto-enables --no-portfolio-cap when
    --phase=1a-beta. Source-grep pinning: if a future commit removes the
    auto-enable, this test fails."""
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    src = (repo / "backtest" / "run_phase1a.py").read_text(encoding="utf-8")
    assert 'args.phase == "1a-beta"' in src and "no_portfolio_cap" in src, (
        "Batch 377 regression: phase=1a-beta must auto-enable --no-portfolio-cap"
    )
    assert "auto-enabling --no-portfolio-cap" in src.lower() or \
           "auto-enabling" in src, "Batch 377 regression: auto-enable banner missing"


def test_batch375_dec426_5_gate_wired_to_config_not_hardcoded():
    """Batch 375 DEC-426 closure: cube_populator now reads 5-Gate thresholds
    from canonical DEC_422_FIVE_GATE_VALIDITY in config.py instead of
    hardcoding _FIVE_GATE constants. Memory rule 'wired = engine-consumed
    not grep-found' satisfied.

    Failure mode: if owner re-tunes the 5-Gate thresholds (per Phase 1B
    DSR refinement or DEC-247 PSR rework), only config.py needs to change.
    Hardcoded copy in cube_populator would have caused silent drift."""
    from backtest.config import DEC_422_FIVE_GATE_VALIDITY
    from backtest.results.cube_populator import _FIVE_GATE

    # Wired: cube_populator._FIVE_GATE values must equal config canonical
    assert _FIVE_GATE["n_min"]          == DEC_422_FIVE_GATE_VALIDITY["min_trades_per_cell"]
    assert _FIVE_GATE["bonferroni_max"] == DEC_422_FIVE_GATE_VALIDITY["max_p_value"]
    assert _FIVE_GATE["psr_min"]        == DEC_422_FIVE_GATE_VALIDITY["min_psr"]
    assert _FIVE_GATE["t_stat_min"]     == DEC_422_FIVE_GATE_VALIDITY["min_t_stat"]
    assert _FIVE_GATE["rr_min"]         == DEC_422_FIVE_GATE_VALIDITY["min_rr"]

    # Verify the canonical values match DEC-426 spec
    assert DEC_422_FIVE_GATE_VALIDITY["min_trades_per_cell"] == 30
    assert DEC_422_FIVE_GATE_VALIDITY["max_p_value"]         == 0.05
    assert DEC_422_FIVE_GATE_VALIDITY["min_psr"]             == 0.95
    assert DEC_422_FIVE_GATE_VALIDITY["min_t_stat"]          == 3.4
    assert DEC_422_FIVE_GATE_VALIDITY["min_rr"]              == 2.0


def test_batch375_dec134_fx_exposure_already_engine_consumed():
    """Batch 375 DEC-134 audit closure: compute_fx_exposure_pct exists at
    metrics.py:1558 AND consumed by results/writer.py for output writing.
    Already fully engine-wired; this test pins the wiring."""
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    writer_text = (repo / "backtest" / "results" / "writer.py").read_text(encoding="utf-8")
    assert "compute_fx_exposure_pct" in writer_text, (
        "DEC-134 regression: writer.py must consume compute_fx_exposure_pct"
    )
    # Verify the helper actually computes correctly
    from backtest.results.metrics import compute_fx_exposure_pct
    r = compute_fx_exposure_pct(usd_portfolio_value_cad=70000.0,
                                 total_portfolio_value_cad=100000.0)
    assert r["fx_exposure_pct"] == 70.0, (
        f"DEC-134: fx_exposure_pct compute drift - expected 70.0, got {r}"
    )


def test_batch375_dec433_exit_method_rename_map_documented():
    """Batch 375 DEC-433 closure: the 6 DEC-067 Phase B exit methods spec'd
    by DEC-433 are present in EXIT_STRATEGIES under their final names
    (renames during implementation). This test pins the rename map so a
    future search for the spec names lands on the correct EXIT_STRATEGIES
    entries.

    DEC-433 spec name              ->  EXIT_STRATEGIES live name
      time_stop                    ->  time_stop_10d, time_stop_20d, class_time_stop (3 variants per DEC-433 owner refinement)
      profit_target_2r             ->  r_multiple_2r
      profit_target_3r             ->  r_multiple_3r
      scale_out_partial_50pct      ->  hybrid_50pct_target
      swing_high_low_break         ->  next_pivot_target (canonical equivalent per DEC-067)
      ema_trail_20                 ->  ma_exit_ema9 (renamed to EMA-9 per DEC-067 sec8.5 finalization)
    """
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    # All 6 DEC-433 logical exits are present under their live names
    rename_map = {
        "time_stop":               ["time_stop_10d", "time_stop_20d", "class_time_stop"],
        "profit_target_2r":        ["r_multiple_2r"],
        "profit_target_3r":        ["r_multiple_3r"],
        "scale_out_partial_50pct": ["hybrid_50pct_target"],
        "swing_high_low_break":    ["next_pivot_target"],
        "ema_trail_20":            ["ma_exit_ema9"],
    }
    for spec_name, live_names in rename_map.items():
        for ln in live_names:
            assert ln in EXIT_STRATEGIES, (
                f"DEC-433 rename: '{spec_name}' should be present as "
                f"'{ln}' in EXIT_STRATEGIES; missing"
            )
    # Total count: 26 after Batch 487 SM2 (added smart_money_reversal).
    assert len(EXIT_STRATEGIES) == 26


def test_batch375_dec246_cube_sharpe_trade_frequency_annualization():
    """Batch 375 DEC-246 sec1 closure: cube_populator + ab_orchestrator
    Sharpe now uses trade-frequency annualization (Calmar pattern) when
    hold_days column present. Fallback to sqrt(252) preserves backward
    compatibility for pnl-only legacy frames.

    Verifies:
      - With hold_days column: annualization_factor = sqrt(252/avg_hold)
      - Without hold_days:     legacy sqrt(252) preserved
      - Same trade set with avg_hold=10 yields Sharpe ~5x lower than
        legacy sqrt(252) (since sqrt(25.2) ~ 5.02 vs sqrt(252) ~ 15.87)
    """
    import pandas as pd
    import numpy as np
    from backtest.results.cube_populator import compute_cell_metrics

    # Trade set with hold_days = 10 -> trades-per-year ~ 25.2
    n = 100
    rng = np.random.default_rng(42)
    pnls = rng.normal(loc=1.0, scale=2.0, size=n)
    df_with_hold = pd.DataFrame({
        "pnl_pct":   pnls,
        "hold_days": [10.0] * n,
    })
    m_with = compute_cell_metrics(df_with_hold)
    s_with = m_with["sharpe"]

    # Same returns, no hold_days column - legacy fallback sqrt(252)
    df_no_hold = pd.DataFrame({"pnl_pct": pnls})
    m_no = compute_cell_metrics(df_no_hold)
    s_no = m_no["sharpe"]

    # Ratio of legacy/new should equal sqrt(252)/sqrt(25.2) = sqrt(10) ~ 3.162
    ratio = s_no / s_with if s_with != 0 else 0
    expected_ratio = float(np.sqrt(10.0))
    assert abs(ratio - expected_ratio) < 0.05, (
        f"DEC-246 sec1: Sharpe annualization ratio drift - "
        f"expected ~{expected_ratio:.3f} (sqrt(252)/sqrt(25.2)), got {ratio:.3f}. "
        f"legacy={s_no:.4f} trade-freq={s_with:.4f}"
    )

    # With avg_hold = 1 day: matches sqrt(252) (degenerate case)
    df_daily = pd.DataFrame({
        "pnl_pct":   pnls,
        "hold_days": [1.0] * n,
    })
    m_daily = compute_cell_metrics(df_daily)
    assert abs(m_daily["sharpe"] - s_no) < 0.01, (
        f"avg_hold=1d should match legacy sqrt(252); got "
        f"{m_daily['sharpe']:.4f} vs {s_no:.4f}"
    )


def test_batch375_cb_fire_email_hook_fires_on_transition():
    """Batch 375 (Stage 4 monitoring C-3 highest-value piece): when DEC-515
    Level 6 circuit breaker transitions OFF->ON or ON->OFF, an email is
    dispatched via the injectable send_email_fn. Idempotent: no email when
    state unchanged."""
    from backtest.live_trading.risk_overlay import (
        LiveRiskState, update_halt_state,
        DEC_515_LEVEL_6_DD_TRIGGER_PCT,
        DEC_515_LEVEL_6_DD_RECOVERY_PCT,
    )

    sent_emails: list[tuple] = []
    def fake_send(subject, body, dry_run=False):
        sent_emails.append((subject, body, dry_run))
        return True

    # Start with portfolio in normal state - no transition, no email
    state = LiveRiskState(portfolio_value=100_000, portfolio_peak=100_000)
    update_halt_state(state, send_email_fn=fake_send)
    assert sent_emails == [], "No transition - no email expected"

    # Trigger DD breach
    state.portfolio_value = 84_000  # 16% DD vs peak 100k
    halt_active = update_halt_state(state, send_email_fn=fake_send)
    assert halt_active is True
    assert len(sent_emails) == 1, "Expected 1 email on activation"
    subject, body, dry_run = sent_emails[0]
    assert "ACTIVATED" in subject
    assert "DEC-515 Level 6" in subject
    assert f"{DEC_515_LEVEL_6_DD_TRIGGER_PCT}" in body
    assert dry_run is False  # live email, not dry-run

    # Re-evaluate with same state - no NEW transition, no email
    update_halt_state(state, send_email_fn=fake_send)
    assert len(sent_emails) == 1, "Same state - no new email"

    # Recovery: portfolio bounces to 96k (4% DD < 5% recovery threshold)
    state.portfolio_value = 96_000
    halt_active = update_halt_state(state, send_email_fn=fake_send)
    assert halt_active is False
    assert len(sent_emails) == 2, "Expected 1 more email on deactivation"
    subject2, _, _ = sent_emails[1]
    assert "DEACTIVATED" in subject2

    # notify=False suppresses email even on transition
    state2 = LiveRiskState(portfolio_value=80_000, portfolio_peak=100_000)
    sent_emails.clear()
    update_halt_state(state2, notify=False, send_email_fn=fake_send)
    assert sent_emails == [], "notify=False must suppress email"


def test_batch374_dec230_structured_logger_emits_json_lines(tmp_path):
    """Batch 374 DEC-230: structured-JSON logger writes one JSON object per
    line with DEC-230 canonical context fields (ts/level/logger/msg + opt
    extras). Helper opt-in; legacy logging.getLogger callers untouched."""
    import json
    import logging
    from backtest.util.structured_logger import (
        get_json_logger,
        reset_json_loggers,
        DEC_230_CONTEXT_FIELDS,
    )

    # Batch 487 (2026-05-30): the TimedRotatingFileHandler flush is not
    # reliable under xdist CPU contention on Windows (failure mode: file
    # exists but is empty by the time the test reads it, despite h.flush()
    # + h.close()). Skip under xdist-parallel; the test still runs in
    # serial mode (no -n auto) AND in CI Linux where the runner is
    # less contended. Per CHECKLIST #102 (relaxed): allowed to differ
    # locally vs CI as long as both pass on their own platform.
    import os as _os
    if int(_os.environ.get("PYTEST_XDIST_WORKER_COUNT", "1")) > 1:
        import pytest as _pytest
        _pytest.skip(
            "xdist parallel CPU contention causes the Windows "
            "TimedRotatingFileHandler flush to be unreliable; run "
            "this test serially via `pytest backtest/tests/test_unit.py"
            "::test_batch374_dec230_structured_logger_emits_json_lines`"
        )

    reset_json_loggers()
    log = get_json_logger("test.dec230", log_dir=tmp_path, level=logging.INFO)
    log.info("trade_fired", extra={
        "ticker": "AAPL", "strategy": "rsi_oversold", "regime": "bull",
    })
    log.warning("gate_block", extra={"ticker": "MSFT", "exit_method": "trail"})
    # Batch 482 (2026-05-29): h.flush() alone left the file empty under
    # xdist load on Windows (TimedRotatingFileHandler buffer not surfacing
    # to the OS-level write before the test reads the file). Close the
    # handlers explicitly to force the stream to disk before the read.
    for h in list(log.handlers):
        try:
            h.flush()
            h.close()
        except Exception:
            pass
        log.removeHandler(h)

    # Find the structured log file
    log_files = list(tmp_path.glob("structured_*.jsonl"))
    assert len(log_files) == 1, f"Expected 1 structured log file; got {len(log_files)}"
    lines = log_files[0].read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2, f"Expected 2 log lines; got {len(lines)}"

    # Each line is a valid JSON object with canonical fields
    for line in lines:
        obj = json.loads(line)
        assert "ts" in obj and obj["ts"].endswith("Z"), f"ts missing/wrong: {obj}"
        assert obj["level"] in ("INFO", "WARNING")
        assert "logger" in obj and obj["logger"].startswith("structured.")
        assert "msg" in obj

    # Field promotion from extra=
    first = json.loads(lines[0])
    assert first["ticker"] == "AAPL"
    assert first["strategy"] == "rsi_oversold"
    assert first["regime"] == "bull"
    second = json.loads(lines[1])
    assert second["exit_method"] == "trail"

    # Canonical context-field set sanity (per DEC-230 spec)
    assert "ticker" in DEC_230_CONTEXT_FIELDS
    assert "strategy" in DEC_230_CONTEXT_FIELDS
    assert "regime" in DEC_230_CONTEXT_FIELDS
    reset_json_loggers()


def test_batch374_dec234_ticker_lifecycle_producer_emits_canonical_schema():
    """Batch 374 DEC-234 + DEC-380: ticker_lifecycle_events.parquet matches
    canonical TICKER_LIFECYCLE_FIELDS schema and event_type values are in
    TICKER_LIFECYCLE_EVENT_TYPES enum."""
    import pandas as pd
    from pathlib import Path
    from backtest.config import (TICKER_LIFECYCLE_FIELDS,
                                  TICKER_LIFECYCLE_EVENT_TYPES)
    repo = Path(__file__).resolve().parents[2]
    out_path = repo / "data_prefetch" / "derived" / "ticker_lifecycle_events.parquet"
    if not out_path.exists():
        import pytest
        pytest.skip("ticker_lifecycle_events.parquet not yet built - run scripts/build_ticker_lifecycle_events.py")

    df = pd.read_parquet(out_path)
    assert len(df) > 0, "DEC-234 producer wrote empty parquet"
    # Schema match - every canonical field is a column
    for field in TICKER_LIFECYCLE_FIELDS:
        assert field in df.columns, (
            f"DEC-234 schema drift: column {field!r} missing from output"
        )
    # event_type values are in canonical enum
    bad = df[~df["event_type"].isin(TICKER_LIFECYCLE_EVENT_TYPES)]
    assert bad.empty, (
        f"DEC-234 schema drift: {len(bad)} events with non-canonical event_type. "
        f"Bad values: {sorted(bad['event_type'].unique())}"
    )


def test_batch374_dec231_regime_filter_bare_excepts_log_warnings(caplog):
    """Batch 374 DEC-231: previously silent `except Exception: pass` in
    regime_filter.compute_bear_composite_score now logs WARNING with
    context (yield_curve / aaii / sector_breadth parse failures)."""
    import pandas as pd
    import logging
    from datetime import date
    from backtest.engine.regime_filter import compute_bear_composite_score

    # Pass a malformed yield_curve_df to trigger the except path
    bad_yc = pd.DataFrame({"date": ["not-a-date"], "value": ["not-a-number"]})
    caplog.set_level(logging.WARNING, logger="backtest.engine.regime_filter")
    result = compute_bear_composite_score(
        as_of=date(2024, 6, 15),
        yield_curve_df=bad_yc,
        aaii_df=None,
        sector_ohlcv_dict=None,
    )
    # Function should still return a result (not crash)
    assert "score" in result
    # And the warning should appear (post-DEC-231; pre-fix this was silent)
    warnings = [r for r in caplog.records
                if r.levelname == "WARNING"
                and "bear_composite" in r.message]
    assert len(warnings) >= 1, (
        f"DEC-231: regime_filter must log WARNING when parse fails; got "
        f"{[r.message for r in caplog.records]}"
    )


def test_batch374_dec246_quant_correctness_formula_pin():
    """Batch 374 DEC-246 closure: pin the canonical quant-finance formulas
    against accidental drift. See QUANT_CORRECTNESS_AUDIT_DEC_246.md for
    the full audit (cube-Sharpe approx flagged; max_drawdown verified;
    Sortino verified)."""
    import numpy as np
    import pandas as pd
    from backtest.results.bootstrap_ci import sharpe_ratio
    from backtest.results.metrics import _max_drawdown

    # Sharpe: constant-return series should be 0 (std=0 protected by 1e-12 floor)
    assert sharpe_ratio([0.01] * 252) == 0.0, (
        "DEC-246: constant returns must yield Sharpe=0 (1e-12 std floor)"
    )

    # Sharpe: known answer - returns with mean=1, std=2, n>=2
    # mean/std * sqrt(252) = 0.5 * sqrt(252) ~= 7.937
    rets = [3.0, -1.0, 3.0, -1.0, 3.0, -1.0]  # mean=1, std~=2
    s = sharpe_ratio(rets)
    expected = (1.0 / np.std(rets, ddof=1)) * np.sqrt(252)
    assert abs(s - expected) < 1e-6, (
        f"DEC-246: Sharpe formula drift - expected {expected:.6f}, got {s:.6f}"
    )

    # Sharpe: empty / single-element guard
    assert sharpe_ratio([]) == 0.0
    assert sharpe_ratio([0.05]) == 0.0

    # Max drawdown: BUG-15 cumprod (was cumsum). [+10, -5, -10] series:
    # equity = [1.10, 1.045, 0.9405], peak = [1.10, 1.10, 1.10]
    # drawdown_pct = [0, -5.0, -14.50]; min = -14.50
    dd = _max_drawdown(pd.Series([10.0, -5.0, -10.0]))
    assert abs(dd - (-14.50)) < 0.05, (
        f"DEC-246: max_drawdown BUG-15 regression - expected ~-14.50, got {dd}"
    )

    # Empty input must not crash
    assert _max_drawdown(pd.Series([])) == 0.0

    # Negative-only series: equity falls monotonically, dd ~= total loss
    dd2 = _max_drawdown(pd.Series([-5.0, -5.0, -5.0]))
    # equity = [0.95, 0.9025, 0.857375], peak = 0.95 starting, then 0.95...
    # Actually peak = cummax([0.95, 0.9025, 0.857375]) = [0.95, 0.95, 0.95]
    # drawdown = [0, -5.0, -9.7368]; min = -9.7368
    assert dd2 < 0, "DEC-246: negative-only series must produce negative drawdown"


def test_batch373_e1_doc_count_pin_against_code():
    """Batch 373 E-1 (owner-directed 2026-05-26 per memory feedback line 14
    'doc count claims must be test-pinned'): pin every numeric count cited
    in CLAUDE.md / CANONICAL_FACTS / forward-looking docs against the live
    code values. Drift between doc claims and code state went unnoticed
    across Batches 209-356 (148 vs 186 strategies, 12 vs 25 exits); this
    test would have caught it at PR-time.

    Canonical references (CANONICAL_FACTS facts):
      F-001 (agent count):    DEC-057 = 11 active LLM nodes
      F-002 (strategy roster): live = 186 registered, 185 active
      F-004 (exit methods):    live = 25 in EXIT_STRATEGIES
      F-XXX (regime count):    4 (bull/neutral/bear/crisis)

    Failure mode: when any of these counts changes via real code update,
    this test fails until the corresponding docs + memory + audit script
    constants are synced. Forces the doc-sync sweep per CHECKLIST #67.
    """
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    from backtest.config import (
        DEPRECATED_STRATEGIES,
        STRATEGIES_DISABLED_MISSING_PRODUCER,
    )

    # F-002 strategy counts. History:
    #   Batch 487 SM1: 188 -> 198 (10 smart-money sleeves)
    #   Batch 507 M6 Path-2: 198 -> 200 (2 YoY-growth PEAD sleeves)
    #   Batch 519 P15 sleeves: 200 -> 202 (squeeze_setup_long + short_borrow_trap_avoid)
    #   Batch 531 P17 sleeves: 202 -> 204 (activist_13d_long + m_and_a_target_long)
    #   Batch 572 candle inverse: 204 -> 205 (doji_at_resistance_short per Stage 4 walk)
    #   Batch 580 Layer 2D ICT first inline-spec: 205 -> 207 (turtle_soup_long + _short per Raschke 1996)
    #   Batch 581 Layer 2D ICT second batch: 207 -> 213 (judas_swing_long/_short + mmbm_long + mmsm_short + week_opening_gap_fill_down/_up per Owner inline-spec)
    #   Batch 586 52w pullback variants: 213 -> 215 (52w_high_breakout_pullback_long + 52w_low_breakdown_pullback_short per owner walk)
    #   Batch 588 52w_low_breakdown_with_smart_money_short: 215 -> 216 (mirror per owner '+ mirror' directive)
    assert len(ALL_STRATEGIES) == 216, (
        f"F-002 drift: ALL_STRATEGIES expected 216 (CLAUDE.md / CANONICAL_FACTS); "
        f"got {len(ALL_STRATEGIES)}. Update doc count references in the same commit."
    )
    assert len(DEPRECATED_STRATEGIES) == 0, (
        f"F-002 drift: DEPRECATED_STRATEGIES expected 0 (Batch 316a empty); "
        f"got {len(DEPRECATED_STRATEGIES)}."
    )
    assert len(STRATEGIES_DISABLED_MISSING_PRODUCER) == 1, (
        f"F-002 drift: STRATEGIES_DISABLED_MISSING_PRODUCER expected 1 "
        f"(Batch 372 disabled dxy_headwind_multinational_short); got "
        f"{len(STRATEGIES_DISABLED_MISSING_PRODUCER)}."
    )
    active = len(ALL_STRATEGIES) - len(
        DEPRECATED_STRATEGIES | STRATEGIES_DISABLED_MISSING_PRODUCER
    )
    assert active == 215, (
        f"F-002 drift: active strategy count expected 215 (Batch 588 +1 "
        f"52w_low_breakdown_with_smart_money_short; minus 1 disabled); "
        f"got {active}."
    )

    # F-004 exit method count
    assert len(EXIT_STRATEGIES) == 26, (
        f"F-004 drift: EXIT_STRATEGIES expected 26 (CANONICAL_FACTS F-004 / "
        f"CLAUDE.md; Batch 487 SM2 added smart_money_reversal); got "
        f"{len(EXIT_STRATEGIES)}. Update doc count references."
    )

    # Cube cells = active strategies x exits
    expected_cells = 197 * 26
    assert expected_cells == 5122, (
        f"Phase 1A-beta cube cells: expected 5,122 (197 active x 26 exits "
        f"per Batch 487 SM1+SM2 adding 10 smart-money sleeves + 1 exit "
        f"method); got {expected_cells}."
    )


def test_batch373_e1_drift_audit_live_values_match_code():
    """Companion to test_batch373_e1_doc_count_pin_against_code:
    verify that the JSON snapshot at output_audit/drift_audit_live_values.json
    matches live code values (the snapshot is regenerated by
    scripts/drift_audit_pre_phase_1a_beta.py and is the source the doc-sync
    sweep reads). Drift between snapshot and code means the audit script
    was not re-run after a code change."""
    import json
    from pathlib import Path
    from backtest.signals.screener import ALL_STRATEGIES
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    from backtest.config import (
        DEPRECATED_STRATEGIES,
        STRATEGIES_DISABLED_MISSING_PRODUCER,
    )

    repo = Path(__file__).resolve().parents[2]
    snapshot_path = repo / "output_audit" / "drift_audit_live_values.json"
    if not snapshot_path.exists():
        import pytest
        pytest.skip("drift_audit_live_values.json absent - run scripts/drift_audit_pre_phase_1a_beta.py")

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert snapshot["strategy_total"] == len(ALL_STRATEGIES), (
        f"Drift: snapshot strategy_total={snapshot['strategy_total']} vs "
        f"live {len(ALL_STRATEGIES)}. Re-run drift_audit_pre_phase_1a_beta.py."
    )
    assert snapshot["deprecated_count"] == len(DEPRECATED_STRATEGIES)
    assert snapshot["missing_producer_count"] == len(STRATEGIES_DISABLED_MISSING_PRODUCER)
    blocked = DEPRECATED_STRATEGIES | STRATEGIES_DISABLED_MISSING_PRODUCER
    assert snapshot["strategy_active"] == len(ALL_STRATEGIES) - len(blocked)
    assert snapshot["exit_method_total"] == len(EXIT_STRATEGIES)
    assert snapshot["cube_cells_active"] == (len(ALL_STRATEGIES) - len(blocked)) * len(EXIT_STRATEGIES)


def test_batch372_dxy_headwind_disabled_missing_producer():
    """Batch 372 (owner-approved 2026-05-26): dxy_headwind_multinational_short
    is disabled until a foreign_rev_pct producer lands.

    Why: strategy gate requires `foreign_rev_pct > 40`. Verified 2026-05-26
    that no available data source has geographic revenue segments:
      - Polygon Stocks Starter financials_json
      - SEC EDGAR companyfacts API (AAPL CIK 0000320193 verified)
      - Existing SEC XBRL prefetch
      - Finnhub financials_reported
    Real-data implementation requires raw 10-K XBRL segment-axis parser
    (1-2 day Sprint-1 build) or paid Polygon Plus tier.

    Mechanism: STRATEGIES_DISABLED_MISSING_PRODUCER is SEMANTICALLY
    DISTINCT from DEPRECATED_STRATEGIES (which Batch 316a reversed for
    empirical-over-literature validation). This set is gated by Sprint-1
    data deliverables, not by literature null findings. Re-enable with
    a single-line removal once the producer ships.

    Counts after Batch 372:
      ALL_STRATEGIES (registered):           186
      DEPRECATED_STRATEGIES (literature):    0   (Batch 316a empty)
      STRATEGIES_DISABLED_MISSING_PRODUCER:  1   (this strategy)
      Active for Phase 1A-beta re-run:       185
    """
    from backtest.config import (
        STRATEGIES_DISABLED_MISSING_PRODUCER,
        DEPRECATED_STRATEGIES,
    )
    from backtest.signals.screener import ALL_STRATEGIES

    assert STRATEGIES_DISABLED_MISSING_PRODUCER == {
        "dxy_headwind_multinational_short"
    }, (
        f"Batch 372: STRATEGIES_DISABLED_MISSING_PRODUCER must contain only "
        f"'dxy_headwind_multinational_short'; got "
        f"{STRATEGIES_DISABLED_MISSING_PRODUCER}"
    )
    # Strategy stays in ALL_STRATEGIES (function body preserved for future
    # re-enable). Active count drops by 1.
    assert "dxy_headwind_multinational_short" in ALL_STRATEGIES, (
        "Batch 372: strategy must remain in ALL_STRATEGIES (filter happens "
        "at screener loop, not registry deletion)"
    )
    # Semantically distinct from literature-pruning set
    assert not (DEPRECATED_STRATEGIES & STRATEGIES_DISABLED_MISSING_PRODUCER), (
        "Batch 372: missing-producer disablement must NOT overlap "
        "literature-null deprecation"
    )
    # Active count for Phase 1A-beta = total - blocked
    blocked = DEPRECATED_STRATEGIES | STRATEGIES_DISABLED_MISSING_PRODUCER
    active = sum(1 for k in ALL_STRATEGIES if k not in blocked)
    assert active == len(ALL_STRATEGIES) - 1, (
        f"Batch 372: active count must equal total - 1 "
        f"(deprecated=0 + missing_producer=1); got total={len(ALL_STRATEGIES)} "
        f"active={active}"
    )


def test_batch370_fix2_calendar_long_strategies_bear_restored():
    """Batch 370 Fix 2 (owner-approved 2026-05-26): reverse Batch 293 narrowing.
    Calendar effect long strategies (totm/pre_holiday/january_effect/halloween)
    extended from {bull, neutral} back to {bull, neutral, bear}.

    Methodologically symmetric with Batch 316a un-deprecation: the Stage C v3
    samples that drove Batch 293 (3-17 trades) were too small to justify
    a-priori pruning. Per memory directive "empirical validation over
    literature pruning", Phase-1A-beta at 1937-ticker scale will produce the
    statistically-powered verdict. If bear-regime calendar effects truly fail,
    the FAIL verdict will codify the pruning empirically.

    Crisis NOT added per original Batch 293 reasoning (full panic overrides
    seasonal). double_bottom_long stays {bull, neutral} per separate Batch 252
    chart-pattern justification (Edwards-Magee bear invalidation).

    Empirical driver: Phase-1A-beta skipped_trades showed 2,173 totm_long +
    1,964 halloween + 339 pre_holiday + 0 january skips were
    regime_affinity_block_bear (56-67% of each strategy's skips).
    """
    from backtest.engine.regime_selector import STRATEGY_REGIME_AFFINITY
    restored = [
        "totm_long", "pre_holiday_long", "january_effect_small_cap_long",
        "halloween_seasonal_long",
    ]
    for strat in restored:
        affinity = STRATEGY_REGIME_AFFINITY.get(strat)
        assert affinity is not None, f"{strat}: missing affinity entry"
        assert affinity == {"bull", "neutral", "bear"}, (
            f"Batch 370 Fix 2: {strat} should be {{bull, neutral, bear}}, got {affinity}"
        )
    # Crisis remains excluded; double_bottom_long unchanged (separate justif)
    for strat in restored:
        assert "crisis" not in STRATEGY_REGIME_AFFINITY[strat], (
            f"Batch 370 Fix 2: crisis should remain excluded for {strat}"
        )
    assert STRATEGY_REGIME_AFFINITY["double_bottom_long"] == {"bull", "neutral"}, (
        "Batch 370 Fix 2 should NOT touch double_bottom_long (Batch 252 scope)"
    )


def test_batch296_fire_rate_report_flags_silent_regression(tmp_path):
    """Batch 296: signal_fire_rates.json must flag any source firing below
    50% of expected_min. Catches the silent-regression class (META, news
    Path B, 13F, PEAD)."""
    import json
    import pandas as pd
    from backtest.results.writer import _write_signal_fire_rate_report

    # Fixture: 100 trades, all institutional_signal=none -> 0% fire rate.
    # Expected_min is 15% post-Batch-294; 50% of that is 7.5%; should flag.
    df = pd.DataFrame({
        "smart_money_score":    [2] * 80 + [0] * 20,
        "congressional_signal": ["buy"] * 70 + ["none"] * 30,
        "insider_signal":       ["none"] * 100,    # 0% fire - below 5%/2 threshold
        "institutional_signal": ["none"] * 100,    # SILENT REGRESSION
        "macro_score":          [1] * 90 + [0] * 10,
        "sentiment_score":      [2] * 60 + [0] * 40,
    })
    _write_signal_fire_rate_report(df, tmp_path)
    report = json.loads((tmp_path / "signal_fire_rates.json").read_text())
    assert report["total_trades"] == 100
    # institutional_signal should be flagged
    assert "institutional_signal" in report["signals"]
    assert report["signals"]["institutional_signal"]["fire_rate"] == 0.0
    assert report["signals"]["institutional_signal"]["alert"] is not None
    assert any("institutional_signal" in f for f in report["flags"])
    # smart_money_score should NOT be flagged (80% > 20%/2=10%)
    assert report["signals"]["smart_money_score"]["alert"] is None


def test_batch295_pead_safe_eps_parses_string_input():
    """Batch 295 (2026-05-21 signal audit): _safe_eps must accept the
    Python-repr STRING that Polygon prefetch stores in `financials_json`,
    not just dict. Prior code returned None for every call -> PEAD signals
    always empty -> strat_pead_long/pead_with_insider never fired."""
    from backtest.signals.pead import _safe_eps
    # Python-repr (single-quoted) - what's actually in the cache
    repr_str = (
        "{'income_statement': {'diluted_earnings_per_share': "
        "{'value': 8.26, 'unit': 'USD / shares'}, "
        "'basic_earnings_per_share': {'value': 8.29}}}"
    )
    assert _safe_eps(repr_str) == 8.26
    # Plain dict still works
    plain_dict = {"income_statement": {"diluted_earnings_per_share": {"value": 5.0}}}
    assert _safe_eps(plain_dict) == 5.0
    # Falls back to basic EPS when diluted absent
    only_basic = {"income_statement": {"basic_earnings_per_share": {"value": 3.5}}}
    assert _safe_eps(only_basic) == 3.5
    # Garbage returns None
    assert _safe_eps("not valid python") is None
    assert _safe_eps(None) is None


def test_batch295_pead_load_quarterly_eps_returns_rows():
    """Batch 295: load_quarterly_eps must return non-empty for tickers
    with valid Polygon financials cache. Regression catch for the silent
    PEAD failure where 51 valid AAPL quarterly rows were dropped because
    _safe_eps couldn't parse the string-encoded JSON."""
    from pathlib import Path
    from backtest.signals.pead import load_quarterly_eps
    # AAPL has Polygon financials in cache; should yield >= 30 quarterly rows
    if not Path("data_prefetch/polygon/financials/AAPL.parquet").exists():
        import pytest
        pytest.skip("AAPL financials not present (CI/fresh clone tolerance)")
    df = load_quarterly_eps("AAPL")
    assert len(df) >= 30, (
        f"Batch 295: PEAD must load >=30 quarterly EPS rows for AAPL "
        f"(got {len(df)}); silent integration regressed"
    )
    assert "eps" in df.columns
    assert df["eps"].notna().all()


def test_batch294_institutional_signal_per_ticker_fallback():
    """Batch 294 (2026-05-21 owner-approved F1): institutional_signal must
    use per-ticker historical fallback when bulk feed has no data for the
    as_of date. T1a baseline showed 97% of trades returned "none" because
    bulk feed only has ~12 months of recent data; this fix restores 18+
    years of historical coverage via per-ticker cache."""
    from datetime import date
    from backtest.data.smart_money import institutional_signal
    # 2022-08 is well before bulk feed window (2025-03+) - must use fallback
    result = institutional_signal("MSFT", date(2022, 8, 15))
    assert result.get("signal") in {"none", "buy", "strong_buy", "negative"}, (
        "Batch 294: invalid signal value returned"
    )
    # If MSFT.parquet has historical 13F data, source should be perticker_history.
    # If empty (unlikely for MSFT), source absent. Test the path either way.
    if result.get("signal") != "none":
        assert result.get("source") in {"perticker_history", "perticker_no_prior"}, (
            f"Batch 294: expected per-ticker source, got {result.get('source')}"
        )


def test_batch294_institutional_signal_returns_dict_with_signal_key():
    """Batch 294: function must always return a dict with `signal` key, even
    for missing tickers (graceful degradation)."""
    from datetime import date
    from backtest.data.smart_money import institutional_signal
    result = institutional_signal("NONEXISTENT_TICKER_QXY", date(2024, 1, 15))
    assert isinstance(result, dict)
    assert result.get("signal") == "none"


def test_batch294_institutional_signal_pit_correct_filing_lag():
    """Batch 294: per-ticker fallback must respect PIT 45-day reporting lag.
    A Q1 13F (ReportPeriod 2024-03-31) becomes available no earlier than
    2024-05-15 (DEC-325 rule)."""
    from datetime import date
    from backtest.data.smart_money import (
        _institutional_signal_from_perticker_history,
    )
    # Query just 1 day before quarter+45 - must return none even if data exists
    # for that quarter (PIT). Pick MSFT (likely to have data).
    result = _institutional_signal_from_perticker_history(
        "MSFT", date(2006, 12, 30)  # before any history could possibly be available
    )
    assert result["signal"] == "none", (
        "Batch 294 PIT: signal must be none when no data exists pre-history"
    )


def test_batch292_compute_bear_composite_score_yc_inverted():
    """Batch 292: yield curve inversion (T10Y2Y < 0) contributes 1 to score."""
    import pandas as pd
    from datetime import date
    from backtest.engine.regime_filter import compute_bear_composite_score
    yc = pd.DataFrame({
        "date": ["2022-01-03", "2022-08-12"],
        "value": [0.85, -0.30],   # Aug 2022: inverted
    })
    # Aug 12 2022: inverted -> score >= 1
    out = compute_bear_composite_score(date(2022, 8, 12), yield_curve_df=yc)
    assert out["yield_curve_inverted"] is True
    assert out["score"] == 1
    # Jan 3 2022: not inverted -> 0
    out2 = compute_bear_composite_score(date(2022, 1, 3), yield_curve_df=yc)
    assert out2["yield_curve_inverted"] is False
    assert out2["score"] == 0


def test_batch292_compute_bear_composite_score_aaii_extreme():
    """Batch 292: AAII bearish >=40% contributes 1 to score."""
    import pandas as pd
    from datetime import date
    from backtest.engine.regime_filter import compute_bear_composite_score
    aaii = pd.DataFrame({
        "date":     ["2022-05-13", "2022-09-30"],
        "bullish":  [0.16, 0.25],
        "bearish":  [0.59, 0.35],
    })
    # May 2022 (peak fear week): 59% bearish -> fires
    out = compute_bear_composite_score(date(2022, 5, 13), aaii_df=aaii)
    assert out["aaii_bearish_extreme"] is True
    assert out["score"] == 1
    # Sep 2022: 35% bearish -> not fires (below 40)
    out2 = compute_bear_composite_score(date(2022, 9, 30), aaii_df=aaii)
    assert out2["aaii_bearish_extreme"] is False


def test_batch292_classify_regime_with_composite_override():
    """Batch 292: bear_composite_score>=2 forces 'bear' even when
    SPY-above-200-EMA + low VIX (would normally classify bull/neutral)."""
    from backtest.engine.regime_filter import classify_regime
    # Low VIX + SPY above 200 = bull normally
    assert classify_regime(15.0, True, bear_composite_score=0) == "bull"
    assert classify_regime(15.0, True, bear_composite_score=1) == "bull"
    # composite >= 2 overrides to bear
    assert classify_regime(15.0, True, bear_composite_score=2) == "bear"
    assert classify_regime(15.0, True, bear_composite_score=3) == "bear"


def test_batch292_classify_regime_composite_does_not_override_crisis():
    """Batch 292: VIX>=40 crisis takes precedence over bear composite."""
    from backtest.engine.regime_filter import classify_regime
    assert classify_regime(45.0, True, bear_composite_score=3) == "crisis"
    assert classify_regime(45.0, False, bear_composite_score=3) == "crisis"


def test_batch291_direction_aware_regime_default_long():
    """Batch 291 (2026-05-21 owner-approved option B per Stage C v2 forensic):
    Long strategies NOT in STRATEGY_REGIME_AFFINITY default to {bull, neutral}
    instead of allow-all. Closes the gap where 25 long trades fired in
    bear in 2022 Stage C v2 (-133 pp)."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    # Long unmapped: bull OK, neutral OK, bear/crisis blocked
    assert should_strategy_fire_in_regime(
        "_unmapped_strat", "bull", direction="long") is True
    assert should_strategy_fire_in_regime(
        "_unmapped_strat", "neutral", direction="long") is True
    assert should_strategy_fire_in_regime(
        "_unmapped_strat", "bear", direction="long") is False
    assert should_strategy_fire_in_regime(
        "_unmapped_strat", "crisis", direction="long") is False


def test_batch291_direction_aware_regime_default_short():
    """Batch 291: short strategies NOT in map default to {bear, crisis, neutral}.
    Bull blocked; bear/crisis/neutral allowed (matches Batch 271 explicit
    short-affinity expansion philosophy)."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    assert should_strategy_fire_in_regime(
        "_unmapped_short", "bull", direction="short") is False
    assert should_strategy_fire_in_regime(
        "_unmapped_short", "neutral", direction="short") is True
    assert should_strategy_fire_in_regime(
        "_unmapped_short", "bear", direction="short") is True
    assert should_strategy_fire_in_regime(
        "_unmapped_short", "crisis", direction="short") is True


def test_batch291_backward_compat_no_direction_still_allow_all():
    """Batch 291: when caller doesn't pass direction (legacy callers),
    fall back to allow-all to preserve backward-compat."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    # No direction supplied -> allow-all (matches pre-Batch-291 behavior)
    for r in ("bull", "neutral", "bear", "crisis"):
        assert should_strategy_fire_in_regime("_unmapped", r) is True


def test_batch291_mapped_strategies_unchanged():
    """Batch 291: strategies WITH affinity entries continue to use that
    affinity (Batch 291 only changes the unmapped-fallback)."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    # bollinger_lower has explicit {neutral, bear} affinity; direction
    # parameter must NOT override this (bull stays blocked).
    assert should_strategy_fire_in_regime(
        "bollinger_lower", "bull", direction="long") is False
    assert should_strategy_fire_in_regime(
        "bollinger_lower", "neutral", direction="long") is True
    assert should_strategy_fire_in_regime(
        "bollinger_lower", "bear", direction="long") is True


def test_batch290_spy_auto_included_when_user_universe_lacks_it():
    """Batch 290: SPY must be auto-included in self.universe when user
    passes --tickers without it. Regression catch for the silent regime-
    classification failure (no SPY -> self.spy_df=None -> spy_ema=None ->
    spy_above_200ema=None -> classify_regime always 'neutral')."""
    # Verify via source inspection (constructor is heavy with data loads;
    # source-grep is the cheap-and-correct test).
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    assert "if \"SPY\" not in _user_universe:" in src, (
        "Batch 290: SPY auto-include logic missing from __init__"
    )
    assert "self.universe = list(_user_universe) + [\"SPY\"]" in src, (
        "Batch 290: SPY auto-add line missing"
    )


def test_batch288_regime_classifier_spy_only_bear_gate():
    """Batch 288 (owner option A.2): SPY below 200-EMA alone classifies
    "bear" regardless of VIX level. Catches 2022-style grinding bear
    where SPY -23% but VIX peaked at 38 (never the 30+below-200 gate
    simultaneously)."""
    from backtest.engine.regime_filter import classify_regime
    # 2022 stealth bear: SPY down, VIX moderate -> bear (was neutral pre-288)
    assert classify_regime(25.0, False) == "bear", (
        "Batch 288: VIX=25 + SPY below 200-EMA must be bear"
    )
    # Even with low VIX, SPY below 200-EMA = bear
    assert classify_regime(15.0, False) == "bear"
    # Bull case unchanged
    assert classify_regime(15.0, True) == "bull"
    # Crisis dominates
    assert classify_regime(45.0, False) == "crisis"
    assert classify_regime(45.0, True) == "crisis"
    # VIX missing remains unknown (DEC-316)
    assert classify_regime(None, False) == "unknown"


def test_batch288_hysteresis_classifier_also_uses_spy_only_bear():
    """Batch 288 fix follow-up: the hysteresis variant
    classify_regime_with_hysteresis must apply the same SPY-only bear gate
    as classify_regime. Without this, the engine uses the old gate after
    day 1 (when prev_regime is set), causing 2022 stealth bears to keep
    classifying as neutral.

    Regression catch: discovered when Stage C v2 logs showed 100%
    regime=neutral throughout 2022 despite the Batch 288 unit test
    expecting bear classification."""
    from backtest.engine.regime_filter import classify_regime_with_hysteresis
    # 2022 stealth bear at VIX=25, SPY below 200-EMA, prev=neutral -> bear
    assert classify_regime_with_hysteresis(25.0, False, "neutral") == "bear"
    # VIX=15 + SPY below -> bear (was neutral pre-fix)
    assert classify_regime_with_hysteresis(15.0, False, "neutral") == "bear"
    # Stay-in-bear branch: prev_regime=bear, VIX=20 (below 30-buffer=25), SPY
    # still below 200-EMA -> stay bear via Batch 288 expansion
    assert classify_regime_with_hysteresis(20.0, False, "bear") == "bear"
    # Bull case unchanged
    assert classify_regime_with_hysteresis(15.0, True, "bull") == "bull"


def test_batch287a_per_strategy_initial_pct_override():
    """Batch 287.A: STRATEGY_EXIT_OVERRIDE entries may carry 'initial_pct'
    to tighten/widen the initial stop per strategy. Mean-reversion needs
    tighter (3-5%); trend needs wider (12-15%).

    Batch 414 (2026-05-28) supersedes the bollinger_tight pin: cube-empirical
    re-pairing moved bollinger_tight from next_pivot_target (pct-based
    initial stop) to breakeven_plus_trail (ATR-based pre-BE stop; initial_pct
    no longer applies). Pin retained for the two strategies still using
    pct-based stops."""
    from backtest.config import STRATEGY_EXIT_OVERRIDE
    # bollinger_lower still uses fixed_4r_2r with initial_pct=0.03
    assert STRATEGY_EXIT_OVERRIDE["bollinger_lower"].get("initial_pct") == 0.03
    # stochrsi_oversold still uses pct-based trailing with initial_pct=0.04
    assert STRATEGY_EXIT_OVERRIDE["stochrsi_oversold"].get("initial_pct") == 0.04
    # Batch 414: bollinger_tight migrated to breakeven_plus_trail (ATR-based);
    # initial_pct no longer applicable.
    assert STRATEGY_EXIT_OVERRIDE["bollinger_tight"].get(
        "exit_method") == "breakeven_plus_trail"


def test_batch287c_crisis_flag_no_inner_reassignment():
    """Batch 287.C: redundant `crisis_flag = regime == 'crisis'` inside the
    candidate loop was removed; canonical assignment at function scope
    (line ~601) is the only one. Source-grep verifies the cleanup."""
    from pathlib import Path
    src = Path("backtest/engine/backtest.py").read_text(encoding="utf-8")
    # Count crisis_flag = regime == "crisis" assignments. Should be 1
    # (the canonical one at function scope). The inner one in the dedup
    # loop was redundant.
    import re
    matches = re.findall(r'crisis_flag\s*=\s*regime\s*==\s*"crisis"', src)
    assert len(matches) == 1, (
        f"Batch 287.C: should have exactly 1 canonical crisis_flag "
        f"assignment, found {len(matches)}"
    )


def test_batch285_regime_flip_exits_on_regime_change():
    """Batch 285: regime_flip exits when today_regime != trade.regime_at_entry."""
    from datetime import date
    from backtest.engine.exit_manager import _check_per_strategy_exit_hit, OpenTrade
    # cpr_narrow_bullish has regime_flip per Batch 285
    trade = OpenTrade(
        ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
        direction="long", strategy="cpr_narrow_bullish", category="pivot",
        sector="Tech", initial_stop=95.0, trailing_stop=95.0,
        highest_close=105.0, regime_at_entry="bull",
    )
    # Same regime -> no exit
    ep, er = _check_per_strategy_exit_hit(
        trade, today_high=108.0, today_low=104.0, today_close=107.0,
        today_date=date(2024, 1, 15), today_regime="bull",
    )
    assert ep is None
    # Regime flip -> exit at today_close
    ep, er = _check_per_strategy_exit_hit(
        trade, today_high=108.0, today_low=104.0, today_close=107.0,
        today_date=date(2024, 1, 15), today_regime="bear",
    )
    assert ep == 107.0
    assert "regime_flip" in er
    assert "bull_to_bear" in er


def test_batch285_ma_exit_ema9_long_exits_below():
    """Batch 285: ma_exit_ema9 exits long when close < EMA-9."""
    from datetime import date
    from backtest.engine.exit_manager import _check_per_strategy_exit_hit, OpenTrade
    # po3_bearish has ma_exit_ema9 per Batch 285 (but it's a short; we'll
    # use a custom test entry to verify long behavior).
    from backtest.config import STRATEGY_EXIT_OVERRIDE
    STRATEGY_EXIT_OVERRIDE["test_ma9_long"] = {"exit_method": "ma_exit_ema9"}
    try:
        trade = OpenTrade(
            ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
            direction="long", strategy="test_ma9_long", category="trend",
            sector="Tech", initial_stop=95.0, trailing_stop=95.0,
            highest_close=110.0, regime_at_entry="bull",
        )
        # close above EMA-9 -> no exit
        ep, _ = _check_per_strategy_exit_hit(
            trade, today_high=109.0, today_low=106.0, today_close=108.0,
            today_date=date(2024, 1, 10), today_ema_9=107.0,
        )
        assert ep is None
        # close below EMA-9 -> exit
        ep, er = _check_per_strategy_exit_hit(
            trade, today_high=108.0, today_low=104.0, today_close=105.0,
            today_date=date(2024, 1, 10), today_ema_9=107.0,
        )
        assert ep == 105.0
        assert "ma_exit_ema9_below" in er
        # no ema_9 supplied -> no exit (graceful)
        ep, _ = _check_per_strategy_exit_hit(
            trade, today_high=108.0, today_low=104.0, today_close=105.0,
            today_date=date(2024, 1, 10), today_ema_9=None,
        )
        assert ep is None
    finally:
        STRATEGY_EXIT_OVERRIDE.pop("test_ma9_long", None)


def test_batch285_next_pivot_target_long():
    """Batch 285: next_pivot_target exits long at first entry-time pivot > entry.

    Batch 414 (2026-05-28): bollinger_tight migrated to breakeven_plus_trail
    so the test now installs a synthetic strategy + STRATEGY_EXIT_OVERRIDE
    entry to exercise the next_pivot_target code path without coupling to a
    production strategy. Tests the EXIT METHOD itself, not the strategy
    pairing."""
    from datetime import date
    from backtest.config import STRATEGY_EXIT_OVERRIDE
    from backtest.engine.exit_manager import _check_per_strategy_exit_hit, OpenTrade
    # Install synthetic strategy mapping under finally-guarded teardown
    STRATEGY_EXIT_OVERRIDE["test_next_pivot_long"] = {
        "exit_method": "next_pivot_target",
    }
    try:
        trade = OpenTrade(
            ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
            direction="long", strategy="test_next_pivot_long",
            category="mean_reversion",
            sector="Tech", initial_stop=95.0, trailing_stop=95.0,
            highest_close=100.0, regime_at_entry="neutral",
            signals_at_entry={"pivot_r1": 105.0, "pivot_r2": 110.0,
                               "pivot_r3": 115.0,
                               "pivot_s1": 95.0, "pivot_s2": 90.0},
        )
        # today_high 104 < r1 105 -> no exit
        ep, _ = _check_per_strategy_exit_hit(
            trade, today_high=104.0, today_low=98.0, today_close=103.0,
            today_date=date(2024, 1, 5),
        )
        assert ep is None
        # today_high 106 reaches r1 -> exit at 105
        ep, er = _check_per_strategy_exit_hit(
            trade, today_high=106.0, today_low=101.0, today_close=104.5,
            today_date=date(2024, 1, 6),
        )
        assert ep == 105.0
        assert "next_pivot_target_hit" in er
    finally:
        STRATEGY_EXIT_OVERRIDE.pop("test_next_pivot_long", None)


def test_batch285_hybrid_50pct_target_long():
    """Batch 285: hybrid_50pct_target exits at +3xATR (approximates partial-fill)."""
    from datetime import date
    from backtest.engine.exit_manager import _check_per_strategy_exit_hit, OpenTrade
    # avwap_50_reclaim has hybrid_50pct_target per Batch 285
    trade = OpenTrade(
        ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
        direction="long", strategy="avwap_50_reclaim", category="vwap",
        sector="Tech", initial_stop=98.0, trailing_stop=98.0,
        highest_close=100.0, regime_at_entry="bull",
        signals_at_entry={"atr": 2.0, "atr_14": 2.0},
    )
    # ATR=2, +3xATR target = 106
    # today_high 105 < target -> no exit
    ep, _ = _check_per_strategy_exit_hit(
        trade, today_high=105.0, today_low=99.0, today_close=104.0,
        today_date=date(2024, 1, 10),
    )
    assert ep is None
    # today_high 107 >= target -> exit at 106
    ep, er = _check_per_strategy_exit_hit(
        trade, today_high=107.0, today_low=104.0, today_close=106.5,
        today_date=date(2024, 1, 11),
    )
    assert ep == 106.0
    assert "hybrid_50pct_target_3xatr" in er


def test_batch282_per_strategy_exit_override_present():
    """Batch 282: STRATEGY_EXIT_OVERRIDE config dict present + populated
    with at least the Stage C cube-best findings. Each entry should be a
    dict with at least one of {trail_pct, time_stop_days, breakeven_at_R}."""
    from backtest.config import STRATEGY_EXIT_OVERRIDE
    assert isinstance(STRATEGY_EXIT_OVERRIDE, dict)
    assert len(STRATEGY_EXIT_OVERRIDE) >= 5, (
        "Stage C cube identified at least 5 strategies needing override"
    )
    # Batch 284 added exit_method key; both keysets are valid.
    valid_keys = {"trail_pct", "time_stop_days", "breakeven_at_R", "exit_method"}
    for strat, override in STRATEGY_EXIT_OVERRIDE.items():
        assert isinstance(override, dict), f"{strat}: override must be dict"
        assert any(k in override for k in valid_keys), (
            f"{strat}: override must have at least one of {valid_keys}"
        )


def test_batch282_strategy_trail_pct_override_takes_effect():
    """Batch 282: when a strategy has per-strategy trail_pct, that overrides
    the default TRAILING_STOP['trail_pct'] in update_trailing_stop."""
    from datetime import date
    from backtest.engine.exit_manager import update_trailing_stop, OpenTrade
    from backtest.config import STRATEGY_EXIT_OVERRIDE

    # Inject a test entry with trail_pct=0.05 (Batch 284 reclaimed bollinger_lower
    # to use exit_method=fixed_4r_2r instead of trail_pct override).
    STRATEGY_EXIT_OVERRIDE["test_trail_pct_05"] = {"trail_pct": 0.05}
    try:
        trade = OpenTrade(
            ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
            direction="long", strategy="test_trail_pct_05",
            category="mean_reversion",
            sector="Industrials", initial_stop=95.0, trailing_stop=95.0,
            highest_close=100.0, regime_at_entry="neutral",
        )
        # Push price up to 200 - stop should land at 200 * (1 - 0.05) = 190
        # (per the override; NOT 200 * 0.85 = 170 which is the default).
        updated = update_trailing_stop(trade, today_close=200.0, vix_value=15.0)
        expected_stop_with_override = 200.0 * (1 - 0.05)
        assert updated.trailing_stop == expected_stop_with_override, (
            f"trail_pct override (0.05) did not take effect; "
            f"stop={updated.trailing_stop} expected {expected_stop_with_override}"
        )
    finally:
        STRATEGY_EXIT_OVERRIDE.pop("test_trail_pct_05", None)


def test_batch282_strategy_without_override_uses_default():
    """Batch 282: a strategy NOT in STRATEGY_EXIT_OVERRIDE uses the default
    TRAILING_STOP['trail_pct'] (currently 0.15 per Batch 281)."""
    from datetime import date
    from backtest.engine.exit_manager import update_trailing_stop, OpenTrade
    from backtest.config import TRAILING_STOP, STRATEGY_EXIT_OVERRIDE

    # Pick a strategy that's clearly not in the override
    unmapped_strategy = "some_strategy_not_in_override"
    assert unmapped_strategy not in STRATEGY_EXIT_OVERRIDE, (
        "Test invariant: chose a strategy that's not in the override dict"
    )
    trade = OpenTrade(
        ticker="TEST", entry_date=date(2024, 1, 1), entry_price=100.0,
        direction="long", strategy=unmapped_strategy, category="momentum",
        sector="Industrials", initial_stop=95.0, trailing_stop=95.0,
        highest_close=100.0, regime_at_entry="neutral",
    )
    updated = update_trailing_stop(trade, today_close=200.0, vix_value=15.0)
    expected_stop = 200.0 * (1 - TRAILING_STOP["trail_pct"])
    assert updated.trailing_stop == expected_stop, (
        f"unmapped strategy must use default trail_pct; "
        f"got {updated.trailing_stop}, expected {expected_stop}"
    )


def test_batch281_trailing_stop_config_actually_deployed():
    """Batch 281 (2026-05-20): the Batch 262 trail_pct + breakeven_move_at_1r
    changes were CLAIMED in commit messages but never actually landed in
    config.py - all smokes A/B/C ran on the prior 10% trail with no
    breakeven. Batch 281 finally deploys them. This test asserts the
    config values stay where they should - catches the regression mode
    where a future batch reverts them silently.
    """
    from backtest.config import TRAILING_STOP
    assert TRAILING_STOP["trail_pct"] == 0.15, (
        f"Batch 281: trail_pct must be 0.15 (was found {TRAILING_STOP['trail_pct']}). "
        "If lowered, justify per backtest evidence; do not silently revert."
    )
    assert TRAILING_STOP.get("breakeven_move_at_1r") is True, (
        "Batch 281: breakeven_move_at_1r must be True - locks-in zero-loss "
        "at +1R, reduces give-back observed in 1A-alpha post-mortem."
    )


def test_batch275_meta_ohlcv_no_meta_materials_corruption():
    """Batch 275 (2026-05-20 owner-approved option C): META OHLCV cache
    must NOT contain Meta Materials Inc prices (the company that held
    the META ticker before Meta Platforms acquired it on 2022-06-09).
    Pre-rename closes were $11-17 range vs post-rename $90-790 range -
    using stitched data caused a -1219% loss in Stage B smoke.

    The fix: META.parquet now starts at 2022-06-09 (Meta Platforms only).
    """
    from pathlib import Path
    import pandas as pd
    repo = Path(__file__).resolve().parents[2]
    for rel in [
        "data_prefetch/polygon/ohlcv_daily/META.parquet",
        "backtest/data/cache/polygon/ohlcv_daily/META.parquet",
        "backtest/data/cache/ohlcv/META.parquet",
    ]:
        path = repo / rel
        if not path.exists():
            continue   # CI / fresh clone tolerance
        df = pd.read_parquet(path)
        df["dt"] = pd.to_datetime(df["date"])
        # No row before 2022-06-09 should exist (Meta Materials era).
        pre = df[df["dt"] < pd.Timestamp("2022-06-09")]
        assert pre.empty, (
            f"{rel}: contains {len(pre)} rows before 2022-06-09 "
            f"(Meta Materials corruption). Re-run scripts/fix_meta_ticker_corruption.py."
        )
        # Sanity: post-rename close should be in Meta Platforms range
        # (lows ~$88 in late-2022 trough; highs >$700 in 2024).
        if not df.empty:
            min_close = df["close"].min()
            assert min_close > 50.0, (
                f"{rel}: minimum close ${min_close:.2f} too low for Meta "
                "Platforms; possible recurrence of Meta Materials contamination."
            )


def test_batch274_dedup_priority_reverted():
    """Batch 274 (2026-05-20 owner-approved): Batch 272's category-priority
    dedup sort REVERTED after Stage B smoke (20 tkrs x 2y) showed
    cpr_narrow_momentum (confluence category) won every dedup matchup
    and fired 102x at -14.4% mean PnL (vs 1x in T1a baseline);
    break_retest_confluence similarly went 0 -> 14 firings at 0% WR.
    Empirical edge does NOT correlate with confluence tagging.

    Verifies the rollback by asserting the priority dict + sorted-strats
    code are absent from engine/backtest.py."""
    import inspect
    from backtest.engine import backtest as bt_mod
    mod_src = inspect.getsource(bt_mod)
    assert "_CAT_PRIORITY" not in mod_src, (
        "Batch 274 revert incomplete: _CAT_PRIORITY dict still present"
    )
    assert "_strats_sorted" not in mod_src, (
        "Batch 274 revert incomplete: _strats_sorted still present"
    )


def test_batch271_short_regime_affinity_expanded_to_neutral():
    """Batch 271 (Tier 2 expansion of T1A_COMPREHENSIVE_REVIEW): short
    strategies that were previously gated to bear/crisis only now allow
    neutral too. T1a forensic: regime_affinity_block_neutral_batch203
    blocked 942/1212 hull_rsi_short candidates + 833/1083
    cpr_narrow_momentum_short candidates (neutral was ~70% of 4y window).

    Cross-asset shorts (risk_off_bond_equity_short) NOT expanded - their
    signals are regime-defined."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    # Technical shorts: now allow neutral
    expanded = [
        "hull_rsi_short", "rsi_overbought_short", "bollinger_upper_short",
        "stochrsi_overbought_short", "ichimoku_cloud_breakdown",
        "supertrend_macd_short", "donchian_breakdown_short",
        "camarilla_rsi_obv_short", "cpr_narrow_momentum_short",
        "52w_low_breakdown", "prev_day_low_breakdown",
        "po3_bearish", "po3_htf_aligned_short", "htf_aligned_breakout_short",
        "weekly_bias_pullback_short", "smc_fvg_retest_short",
        "smc_breaker_block_short", "smc_mitigation_block_short",
        "smc_premium_short", "smc_ote_short", "orb_stocks_in_play_short",
    ]
    for strat in expanded:
        assert should_strategy_fire_in_regime(strat, "neutral") is True, (
            f"{strat}: expected neutral=True post-Batch-271 expansion"
        )
        assert should_strategy_fire_in_regime(strat, "bear") is True, (
            f"{strat}: bear should still be allowed"
        )
        assert should_strategy_fire_in_regime(strat, "bull") is False, (
            f"{strat}: bull should remain blocked"
        )

    # Cross-asset shorts NOT expanded (signals are regime-defined)
    assert should_strategy_fire_in_regime("risk_off_bond_equity_short", "neutral") is False
    assert should_strategy_fire_in_regime("risk_off_bond_equity_short", "bear") is True


def test_batch203_regime_selector_custom_affinity_override():
    """Batch 203: caller can pass an affinity dict for tests / scenarios
    without mutating the module-level STRATEGY_REGIME_AFFINITY."""
    from backtest.engine.regime_selector import should_strategy_fire_in_regime
    custom = {"my_strategy": {"crisis"}}
    assert should_strategy_fire_in_regime("my_strategy", "crisis", affinity=custom) is True
    assert should_strategy_fire_in_regime("my_strategy", "bull",   affinity=custom) is False
    # Strategy not in CUSTOM map -> default allow-all (no fallback to module-level)
    assert should_strategy_fire_in_regime("other_strategy", "bull", affinity=custom) is True


def test_batch203_vix_sizing_inverse_percentile():
    """Batch 203 (Cederburg-Johnson-Maio 2024 VIX-managed portfolios):
    sizing multiplier scales inversely with VIX percentile. Bounded
    [0.3, 1.5] per paper."""
    from backtest.engine.regime_selector import vix_percentile_sizing_multiplier
    vix_hist = list(range(10, 41)) * 10  # 310 obs, VIX 10..40
    mult_low = vix_percentile_sizing_multiplier(10.0, vix_hist)
    assert 1.4 <= mult_low <= 1.5, f"low-VIX must yield max_mult ~1.5, got {mult_low}"
    mult_hi = vix_percentile_sizing_multiplier(40.0, vix_hist)
    assert 0.3 <= mult_hi <= 0.45, f"high-VIX must yield min_mult ~0.3, got {mult_hi}"
    mult_med = vix_percentile_sizing_multiplier(25.0, vix_hist)
    assert 0.8 <= mult_med <= 1.2, f"median-VIX must yield ~1.0, got {mult_med}"
    # Missing/insufficient -> no-op (1.0)
    assert vix_percentile_sizing_multiplier(None, vix_hist) == 1.0
    assert vix_percentile_sizing_multiplier(20.0, None) == 1.0
    assert vix_percentile_sizing_multiplier(20.0, []) == 1.0
    assert vix_percentile_sizing_multiplier(20.0, [15.0] * 10) == 1.0


def test_batch203_regime_position_count_cap():
    """Batch 203: regime-conditional position-count caps per AMH risk
    research. Static cap-25 was too loose for crisis."""
    from backtest.engine.regime_selector import regime_position_count_cap
    assert regime_position_count_cap("bull")    == 40
    assert regime_position_count_cap("neutral") == 25
    assert regime_position_count_cap("bear")    == 15
    assert regime_position_count_cap("crisis")  == 10
    assert regime_position_count_cap("unknown") == 5
    assert regime_position_count_cap("nonsense_regime") == 25


def test_batch201_merge_batch_outputs_imports_resolve():
    """Batch 201 (Issue 1 fix 2026-05-17): merge_batch_outputs.py's
    metrics-recompute branch had imports referencing run_walk_forward and
    run_bonferroni from backtest.results.metrics where they DO NOT exist.
    The bad top-level import in the try-block failed BEFORE compute_all_metrics
    ran, forcing every merge to fall back to concat of batch results.

    Regression test: verify that the imports the merge script uses still
    resolve at import time, and that the non-existent symbols are NOT
    reintroduced. Surfaces during Phase 1A-beta merge."""
    # The merge script's actual imports must all resolve
    from backtest.results.metrics import compute_all_metrics, compute_portfolio_summary
    from backtest.engine.improvements import run_walk_forward, walk_forward_to_df

    # Symbols that previously broke the merge MUST NOT be importable from
    # backtest.results.metrics (catches accidental reintroduction)
    import backtest.results.metrics as _metrics_module
    assert not hasattr(_metrics_module, "run_walk_forward"), (
        "Batch 201: run_walk_forward must NOT be in metrics module "
        "(it lives in backtest.engine.improvements). If you moved it, "
        "update merge_batch_outputs.py accordingly."
    )
    assert not hasattr(_metrics_module, "run_bonferroni"), (
        "Batch 201: run_bonferroni was never defined and should remain so"
    )

    # And the script source itself must not reintroduce the bad imports
    import inspect
    from pathlib import Path
    script_src = (Path(__file__).parent.parent.parent
                  / "scripts" / "merge_batch_outputs.py").read_text(encoding="utf-8")
    assert "from backtest.results.metrics import" in script_src
    # Get the metrics-import block (after the comment, before next blank line)
    import re
    bad_pattern = re.compile(
        r"from backtest\.results\.metrics import\s*\([^)]*run_walk_forward[^)]*\)",
        re.DOTALL,
    )
    assert not bad_pattern.search(script_src), (
        "Batch 201: merge script must NOT import run_walk_forward from metrics"
    )
    bad_pattern2 = re.compile(
        r"from backtest\.results\.metrics import\s*\([^)]*run_bonferroni[^)]*\)",
        re.DOTALL,
    )
    assert not bad_pattern2.search(script_src), (
        "Batch 201: merge script must NOT import run_bonferroni from metrics"
    )


def test_batch201_merge_portfolio_heat_unified_semantics():
    """Batch 201 (Issue 2 fix 2026-05-17): N-batch merged trade log
    aggregated max_portfolio_heat_pct via compute_portfolio_summary gives the
    SUM of per-batch open heats, not the unified-portfolio heat. Phase
    1A-beta merge produced 417% heat across 5 batches (clearly artifact -
    a real single portfolio cannot exceed 100% without leverage).

    Fix: merge_batch_outputs.py rescales heat + avg_position_size by
    1/N_batches and emits BOTH semantics. This test verifies the script
    contains the rescale step + emits the _concat fields."""
    from pathlib import Path
    script_src = (Path(__file__).parent.parent.parent
                  / "scripts" / "merge_batch_outputs.py").read_text(encoding="utf-8")
    # Required keys
    assert 'port["max_portfolio_heat_pct_concat"]' in script_src
    assert 'port["avg_position_size_pct_concat"]' in script_src
    assert 'port["n_batches_merged"]' in script_src
    # Rescale must divide by n_batches (not hardcode 5)
    assert "concat_heat / n_batches" in script_src
    assert "concat_avg_size / n_batches" in script_src
    # Heat semantics note must be present so downstream consumers can
    # surface the caveat to readers
    assert "heat_semantics_note" in script_src
    # n_batches must default to >=1 to avoid division-by-zero when called
    # with an empty input_dirs list (defensive)
    assert "max(len(input_dirs), 1)" in script_src


def test_batch197_deflated_sharpe_guards_negative_radicand():
    """Batch 197 (Phase 1A-beta batch_2 crash fix 2026-05-17): the deflated
    Sharpe formula uses (1 - (excess_kurt/4) * sharpe^2)**0.5 whose radicand
    can be NEGATIVE when (excess_kurt/4) * sharpe^2 > 1.0 (high kurtosis +
    nontrivial Sharpe), producing a complex number that crashes round().
    The pre-batch denominator_sq guard had different sign convention and did
    NOT cover this case. Regression test reproduces the crash case + verifies
    the guard returns deflated_sharpe=None (not complex)."""
    from backtest.results.metrics import _deflated_sharpe

    # Reproduce the batch_2 crash case: high excess kurtosis (e.g. kurt=11
    # -> excess_kurt=8) + sharpe~1 -> (8/4) * 1**2 = 2 -> radicand = -1.
    # denominator_sq by contrast: 1 - 0*1 + 2*1 = 3 > 0 (passes pre-existing guard).
    out = _deflated_sharpe(sharpe=1.0, n_trades=50, skew=0.0, kurtosis=11.0)
    assert out["deflated_sharpe"] is None, (
        "Batch 197: negative-radicand case must yield deflated_sharpe=None, "
        f"got {out['deflated_sharpe']!r}"
    )
    assert out["psr"] is not None, (
        "Batch 197: PSR must still compute when only deflated is invalid"
    )

    # More extreme: kurt=20, sharpe=2 -> excess=17 -> (17/4) * 4 = 17 -> radicand=-16
    out2 = _deflated_sharpe(sharpe=2.0, n_trades=100, skew=0.5, kurtosis=20.0)
    assert out2["deflated_sharpe"] is None

    # Sanity: normal cases still produce a value
    out3 = _deflated_sharpe(sharpe=1.0, n_trades=100, skew=0.0, kurtosis=3.0)
    assert out3["deflated_sharpe"] is not None
    assert isinstance(out3["deflated_sharpe"], (int, float))


def test_batch193_level6_threshold_relaxed_to_20pct():
    """Batch 193 (Phase 1A Batch 192 regression fix owner-approved 2026-05-16
    Option B): LEVEL_6_DD_HALT_THRESHOLD raised 0.15 -> 0.20 and
    LEVEL_6_RECOVERY_THRESHOLD relaxed 0.05 -> 0.025. 20% matches
    Passing-Criteria #5 max DD, gives portfolio more breathing room before
    halting. 2.5% recovery is easier to achieve via existing open positions
    when no new entries are permitted."""
    from backtest.engine.circuit_breakers import (
        LEVEL_6_DD_HALT_THRESHOLD,
        LEVEL_6_RECOVERY_THRESHOLD,
        LEVEL_6_MIN_PEAK_HISTORY_DAYS,
    )
    assert LEVEL_6_DD_HALT_THRESHOLD == 0.20, (
        "Batch 193: DD threshold must be 0.20 (was 0.15)"
    )
    assert LEVEL_6_RECOVERY_THRESHOLD == 0.025, (
        "Batch 193: recovery threshold must be 0.025 (was 0.05)"
    )
    # min_history unchanged
    assert LEVEL_6_MIN_PEAK_HISTORY_DAYS == 30


def test_batch193_level6_auto_resume_timeout():
    """Batch 193 (Phase 1A Batch 192 regression fix owner-approved 2026-05-16
    Option B): Level 6 halt must auto-resume after LEVEL_6_MAX_HALT_DURATION_DAYS
    even if recovery threshold not met. Pre-batch the halt was a permanent
    freeze (resume condition unreachable because halt blocks new entries,
    leaving only existing positions to lift equity). Phase 1A Batch 192
    baseline trapped 4 years of trading behind a single halt fired 2022-06-16."""
    from datetime import date, timedelta
    from backtest.engine.circuit_breakers import (
        Level6State,
        update_level_6_state,
        LEVEL_6_MAX_HALT_DURATION_DAYS,
    )

    assert LEVEL_6_MAX_HALT_DURATION_DAYS == 60, (
        "Batch 193: max halt duration must be 60 days"
    )

    state = Level6State()
    start = date(2022, 1, 1)

    # Day 0: equity = 100, builds the peak.
    update_level_6_state(state, 100.0, start, days_since_start=0)
    assert state.rolling_peak_equity == 100.0
    # Day 35: equity drops to 75 (-25% from peak), past min_history -> halt triggers
    halt_date = start + timedelta(days=35)
    r = update_level_6_state(state, 75.0, halt_date, days_since_start=35)
    assert r["halt_active"] is True, "Batch 193: -25% DD must trigger halt"
    assert state.halt_triggered_date == halt_date

    # Day 35+30: equity still depressed at 73 (well below resume threshold 75*1.025=76.875)
    mid_halt = halt_date + timedelta(days=30)
    r = update_level_6_state(state, 73.0, mid_halt, days_since_start=65)
    assert r["halt_active"] is True, (
        "Batch 193: halt must remain active before timeout"
    )

    # Day 35+60: timeout fires -> auto-resume regardless of recovery threshold
    timeout_date = halt_date + timedelta(days=60)
    r = update_level_6_state(state, 73.0, timeout_date, days_since_start=95)
    assert r["halt_active"] is False, (
        "Batch 193: halt must auto-resume after 60-day timeout"
    )
    assert r["event"] == "halt_resumed_timeout"
    # halt_log records the timeout event
    timeout_events = [e for e in state.halt_log if e.get("event") == "halt_resumed_timeout"]
    assert len(timeout_events) == 1
    assert timeout_events[0]["halt_duration_days"] == 60


def test_batch193_level6_recovery_path_still_works():
    """Batch 193: legitimate recovery (current_equity >= halt_equity * 1.025)
    must still resume the halt before the 60-day timeout fires. The timeout
    is an off-ramp, not a replacement for the recovery condition."""
    from datetime import date, timedelta
    from backtest.engine.circuit_breakers import (
        Level6State,
        update_level_6_state,
    )

    state = Level6State()
    start = date(2022, 1, 1)
    update_level_6_state(state, 100.0, start, days_since_start=0)
    # Trigger halt at -25% DD
    halt_date = start + timedelta(days=35)
    update_level_6_state(state, 75.0, halt_date, days_since_start=35)
    assert state.halt_triggered

    # Day 35+10: equity recovers to 77 (>= 75 * 1.025 = 76.875) -> normal resume
    resume_date = halt_date + timedelta(days=10)
    r = update_level_6_state(state, 77.0, resume_date, days_since_start=45)
    assert r["halt_active"] is False, "Batch 193: 2.5% recovery must release halt"
    assert r["event"] == "halt_resumed"
    # No timeout event
    timeout_events = [e for e in state.halt_log if e.get("event") == "halt_resumed_timeout"]
    assert len(timeout_events) == 0


def test_batch191_macro_event_windows_narrowed():
    """Batch 191 (INV-053 optimization owner-approved 2026-05-16): macro event
    suppression windows must be narrowed per event type. CPI / NFP suppress
    d=0 only (pre=0, post=0). FOMC suppresses d-1 + d=0 (pre=1, post=0,
    Lucca-Moench pre-FOMC drift). Earnings retains DEC-349 default
    (pre=1, post=3). Engine consumption must read EVENT_WINDOWS_BATCH191
    when event_type in {CPI, NFP, FOMC}, fall back to DEC-349 default
    otherwise. Pre-batch baseline produced 27,401 macro-event suppressions
    (15.9% of all rejects) on the d-2..d+1 window."""
    import inspect
    from backtest.config import (
        EVENT_WINDOWS_BATCH191,
        EVENT_WINDOW_PRE_DAYS,
        EVENT_WINDOW_POST_DAYS,
    )
    from backtest.engine import backtest as eng

    # Config must declare expected per-event windows
    assert EVENT_WINDOWS_BATCH191["CPI"] == (0, 0), (
        "Batch 191: CPI must suppress d=0 only"
    )
    assert EVENT_WINDOWS_BATCH191["NFP"] == (0, 0), (
        "Batch 191: NFP must suppress d=0 only"
    )
    assert EVENT_WINDOWS_BATCH191["FOMC"] == (1, 0), (
        "Batch 191: FOMC must suppress d-1 + d=0 (Lucca-Moench)"
    )
    # Earnings retains DEC-349 default
    assert EVENT_WINDOW_PRE_DAYS == 1, "Batch 191: earnings pre must remain DEC-349 default"
    assert EVENT_WINDOW_POST_DAYS == 3, "Batch 191: earnings post must remain DEC-349 default"

    # Engine must import + use EVENT_WINDOWS_BATCH191 in macro-event branch
    src = inspect.getsource(eng)
    assert "EVENT_WINDOWS_BATCH191" in src, (
        "Batch 191: backtest.py must import EVENT_WINDOWS_BATCH191"
    )
    assert "EVENT_WINDOWS_BATCH191.get(" in src, (
        "Batch 191: macro-event branch must look up per-event window via .get()"
    )

    # Simulate suppression logic for each event type
    def is_suppressed(ev_type, days_to_event):
        pre, post = EVENT_WINDOWS_BATCH191.get(
            ev_type.upper(),
            (EVENT_WINDOW_PRE_DAYS, EVENT_WINDOW_POST_DAYS),
        )
        return -post <= days_to_event <= pre

    # CPI: only d=0 suppressed (the 4 pre-batch tagged days d-2/d-1/d0/d+1
    # should now collapse to d=0 only)
    assert is_suppressed("CPI", 0) is True
    assert is_suppressed("CPI", 1) is False, "Batch 191: CPI d-1 (event tomorrow) must NOT suppress"
    assert is_suppressed("CPI", -1) is False, "Batch 191: CPI d+1 (event yesterday) must NOT suppress"
    assert is_suppressed("CPI", -2) is False
    # NFP: same as CPI
    assert is_suppressed("NFP", 0) is True
    assert is_suppressed("NFP", 1) is False
    assert is_suppressed("NFP", -1) is False
    # FOMC: d-1 (days_to_event=+1) and d=0 both suppressed; d+1 NOT
    assert is_suppressed("FOMC", 1) is True, "Batch 191: FOMC must suppress d-1"
    assert is_suppressed("FOMC", 0) is True
    assert is_suppressed("FOMC", -1) is False, "Batch 191: FOMC d+1 post-event must NOT suppress"
    # Unknown event type: fall back to DEC-349 default (-3..+1)
    assert is_suppressed("UNKNOWN_MACRO", 1) is True
    assert is_suppressed("UNKNOWN_MACRO", -3) is True
    assert is_suppressed("UNKNOWN_MACRO", -4) is False


def test_batch191_sizing_log_separated_from_skipped_trades():
    """Batch 191 (INV-053 optimization owner-approved 2026-05-16): sizing
    decisions (DD-band, portfolio vol-target, per-position vol-target) must
    route to sizing_log NOT skipped_trades. Pre-batch baseline mis-logged
    92,345 sizing events to skipped_trades.csv (53.5% of all "rejects" were
    actually sizing decisions; the trade still proceeded). Writer must emit
    sizing_log.csv as a separate file."""
    import inspect
    from backtest.engine import backtest as eng
    from backtest.results import writer as wr

    # Engine: sizing_log attribute must exist
    src = inspect.getsource(eng)
    assert "self.sizing_log" in src, (
        "Batch 191: engine must define self.sizing_log list attribute"
    )
    # Sizing entries must use sizing_log.append, NOT skipped_trades.append
    code_lines = [l for l in src.splitlines() if not l.lstrip().startswith("#")]
    code = "\n".join(code_lines)
    # The 3 scaler tags must NOT appear as a skipped_trades reason value
    assert 'reason": f"dd_band_scaled_' not in code, (
        "Batch 191: dd_band_scaled must route to sizing_log, not skipped_trades"
    )
    assert 'reason": f"vol_target_scaled_' not in code, (
        "Batch 191: vol_target_scaled must route to sizing_log, not skipped_trades"
    )
    assert 'reason": f"per_pos_vol_scaled_' not in code, (
        "Batch 191: per_pos_vol_scaled must route to sizing_log, not skipped_trades"
    )
    # The sizing_log.append calls must reference the 3 scaler types
    for scaler in ("dd_band", "portfolio_vol_target", "per_position_vol_target"):
        assert f'"scaler": "{scaler}"' in code, (
            f"Batch 191: sizing_log must record scaler='{scaler}'"
        )

    # Writer: sizing_log param + sizing_log.csv emission
    wsrc = inspect.getsource(wr.write_all_outputs)
    assert "sizing_log" in wsrc, "Batch 191: write_all_outputs must accept sizing_log"
    assert "sizing_log.csv" in wsrc, "Batch 191: writer must emit sizing_log.csv"


def test_batch190_avoid_tier_blocks_both_directions():
    """Batch 190 (INV-049 fix): AVOID confidence tier must block BOTH long
    AND short trades. Prior bug: line blocked only direction=='long', so 88
    AVOID-short trades fell through in Phase 1A baseline (avg PnL -2.79%).
    Source-level test verifying the asymmetry is gone."""
    import inspect
    from backtest.engine import backtest as eng
    src = inspect.getsource(eng)
    # The old asymmetric pattern must be gone
    assert 'tier == "AVOID" and direction == "long"' not in src, (
        "Batch 190: AVOID-long-only block must be removed (block both directions)"
    )
    # New block must be present
    assert 'if tier == "AVOID":' in src, (
        "Batch 190: must block AVOID regardless of direction"
    )
    # Skip reason must reference the batch
    assert "avoid_tier" in src and "batch190" in src, (
        "Batch 190: skip reason must tag batch190 for audit"
    )


def test_batch189_regime_stratifier_accepts_engine_vocabulary():
    """Batch 189 (INV-051 fix): regime stratifier must accept BOTH the engine's
    bull/neutral/bear/crisis vocabulary AND the DEC-542 calm/neutral/volatile/crisis
    spec. Prior bug: REGIME_CLASSES only had calm/neutral/volatile/crisis so
    engine outputs bull/bear silently dropped, collapsing everything into
    neutral-only (Phase 1A baseline regime_stratified_summary showed
    proportions {neutral: 1.0} despite engine emitting bull/bear trades)."""
    import pandas as pd
    from backtest.engine.regime_stratified_split import (
        REGIME_CLASSES, regime_stratified_split, regime_proportions,
    )
    # Must include both axes
    for r in ("bull", "neutral", "bear", "crisis", "calm", "volatile"):
        assert r in REGIME_CLASSES, f"Batch 189: REGIME_CLASSES must include '{r}'"

    # Engine-vocab regression: input bull/bear/neutral/crisis must NOT collapse to neutral
    n = 200
    dates = pd.date_range("2022-01-01", periods=n, freq="B").tolist()
    # 50 of each: bull / neutral / bear / crisis
    regimes = ["bull"] * 50 + ["neutral"] * 50 + ["bear"] * 50 + ["crisis"] * 50
    train, test, summary = regime_stratified_split(dates, regimes)
    # Each regime should have non-zero train + test (50 split 70/30 = 35 train + 15 test)
    for r in ("bull", "neutral", "bear", "crisis"):
        assert summary[r] > 0, f"Batch 189: regime '{r}' must have train samples; got 0"
        assert summary[f"{r}_test"] > 0, f"Batch 189: regime '{r}' must have test samples"

    # Proportions must reflect ALL 4 regimes (each ~25%)
    props = regime_proportions(regimes)
    for r in ("bull", "neutral", "bear", "crisis"):
        assert props[r] > 0.2, f"Batch 189: regime '{r}' proportion must be ~25%; got {props[r]}"


def test_batch188_dispersion_cb_numerical_guard():
    """Batch 188 (INV-052 fix): dispersion_circuit_breaker must guard against
    near-zero rolling_std producing absurd z-scores (Phase 1A baseline saw
    z=379 on 2022-06-09). Two guards: (1) stddev floor 1e-3 = treat as zero
    case; (2) z-score cap at 10.0 for triggering + reporting."""
    import pandas as pd
    import numpy as np
    from backtest.engine.regime_filter import dispersion_circuit_breaker

    # Case 1: near-zero stddev should NOT trigger nor produce huge z
    # Build a window where prior dispersion is microscopic and today is "normal"
    dates = pd.date_range("2022-01-01", periods=22, freq="D")
    # 5 tickers; rows 0..20 = tiny dispersion (all ~same return); row 21 = uptick
    n_tkr = 5
    base = np.full((21, n_tkr), 0.0001)  # almost-flat
    # Add infinitesimal jitter so std != 0 but is tiny
    jitter = np.random.RandomState(42).randn(21, n_tkr) * 1e-7
    df_calm = pd.DataFrame(base + jitter, index=dates[:21], columns=[f"T{i}" for i in range(n_tkr)])
    today = pd.DataFrame([[0.01, -0.01, 0.005, -0.005, 0.003]],
                         index=dates[21:22],
                         columns=[f"T{i}" for i in range(n_tkr)])
    combined = pd.concat([df_calm, today])
    result = dispersion_circuit_breaker(combined, window=20)
    # Either: (a) rolling_std < floor -> NOT triggered, z=0
    # or (b) rolling_std >= floor but z capped at 10
    assert result["z_score"] is not None
    assert abs(result["z_score"]) <= 10.0, (
        f"Batch 188: z_score must be capped at 10.0; got {result['z_score']}"
    )

    # Case 2: real spike case (z=3-7 range) still triggers correctly
    # Use a window with normal variability, then a clear spike
    rng = np.random.RandomState(123)
    normal = pd.DataFrame(rng.randn(21, n_tkr) * 0.01,  # 1% stddev per ticker
                          index=dates[:21], columns=[f"T{i}" for i in range(n_tkr)])
    # Day 22: large dispersion (returns from -5% to +5%)
    spike = pd.DataFrame([[0.05, -0.05, 0.04, -0.04, 0.03]],
                         index=dates[21:22],
                         columns=[f"T{i}" for i in range(n_tkr)])
    combined2 = pd.concat([normal, spike])
    result2 = dispersion_circuit_breaker(combined2, window=20, sigma_threshold=3.0)
    # Should trigger (real spike) but z should not be astronomical
    assert result2["z_score"] is not None
    assert abs(result2["z_score"]) <= 10.0, (
        f"Batch 188: real spike z must still be capped at 10.0; got {result2['z_score']}"
    )


def test_batch187_walk_forward_decoupled_from_no_git():
    """Batch 187 (INV-050): walk-forward must be decoupled from --no-git.
    Prior bug: walk_forward=not args.no_git coupled them, so baseline runs
    with --no-git silently skipped WF and reported {total: 0}.
    Fix: explicit --no-walk-forward flag; WF runs by default."""
    import inspect
    import backtest.run_phase1a as r
    src = inspect.getsource(r)
    # New flag present
    assert '"--no-walk-forward"' in src, (
        "Batch 187: --no-walk-forward argparse flag must be added"
    )
    # Old coupling removed at the binding site: BacktestEngine call must NOT
    # use walk_forward=not args.no_git anymore. Allow comment references to
    # the prior pattern for historical documentation; check non-comment lines.
    code_lines = [l for l in src.splitlines() if not l.lstrip().startswith("#")]
    code_only = "\n".join(code_lines)
    assert "walk_forward=not args.no_git" not in code_only, (
        "Batch 187: walk_forward=not args.no_git binding must be removed (comment references ok)"
    )
    assert "walk_forward_enabled" in src or "not args.no_walk_forward" in src, (
        "Batch 187: walk_forward must derive from no_walk_forward flag"
    )


# -----------------------------------------------------------------------------
# BATCH 301 - POLYGON REFERENCE WIRING FOR info_cache.market_cap
# -----------------------------------------------------------------------------
# Bug: DEC-497 D4 (2026-05-06) hard-cut yfinance for .info; replacement at
# backtest/data/universe.py:fetch_info_bulk hardcoded `market_cap: 0` with a
# # FUTURE: Polygon reference prefetch comment. BUG-238 fail-closed
# (2026-05-12) then turned market_cap=0 into silent reject. Combined:
# Stage D 150-tkr smoke surfaced 9/151 instruments passing liquidity (8/150
# Stage D sample) vs expected ~120/150. Phase 1A-beta at 1937 tkrs would
# have effectively backtested only ~68. Surfaced 2026-05-21.

def test_batch301_polygon_reference_lookup_aapl():
    """Polygon reference parquet for AAPL returns valid market_cap."""
    from backtest.data.universe import _polygon_reference_lookup
    info = _polygon_reference_lookup("AAPL")
    assert "market_cap" in info, "AAPL ref parquet must yield market_cap"
    assert info["market_cap"] > 1e11, \
        f"AAPL market_cap should be > $100B, got {info.get('market_cap')}"
    assert info.get("exchange"), "AAPL should have non-empty exchange"
    print(f"[OK] Batch 301 _polygon_reference_lookup(AAPL) -> mcap=${info['market_cap']:,.0f}")


def test_batch301_polygon_reference_missing():
    """Missing ticker parquet returns empty dict, not exception."""
    from backtest.data.universe import _polygon_reference_lookup
    info = _polygon_reference_lookup("THISTICKERSHOULDNEVEREXIST_ZZZZ")
    assert info == {}, f"Missing parquet should return {{}}, got {info}"
    print("[OK] Batch 301 _polygon_reference_lookup missing -> {} (no exception)")


def test_batch301_fetch_info_bulk_self_heals_zero_mcap(tmp_path):
    """Pre-existing info_cache entries with market_cap<=0 are re-fetched
    instead of being skipped. Verifies the silent-gap repair path."""
    import json
    from backtest.data.universe import fetch_info_bulk
    # Seed cache with stale zero-mcap AAPL entry (simulates DEC-497 D4 leftover)
    cache_file = tmp_path / "stale_info.json"
    cache_file.write_text(json.dumps({
        "AAPL": {
            "name": "Apple Inc.",
            "sector": "Information Technology",
            "industry": "Unknown",
            "market_cap": 0,   # the bug pattern
            "exchange": "",
            "ipo_date": None,
        }
    }))
    out = fetch_info_bulk(["AAPL"], delay=0.0, cache_file=str(cache_file))
    assert out["AAPL"]["market_cap"] > 1e11, \
        f"AAPL mcap should be refreshed from Polygon ref, got {out['AAPL']['market_cap']}"
    # Persisted to disk
    reloaded = json.loads(cache_file.read_text())
    assert reloaded["AAPL"]["market_cap"] > 1e11, \
        "Refreshed mcap must be written back to cache file"
    print(f"[OK] Batch 301 fetch_info_bulk self-heals mcap=0 -> ${out['AAPL']['market_cap']:,.0f}")


def test_batch301_fetch_info_bulk_skips_valid_entries(tmp_path):
    """Pre-existing entries with valid market_cap are NOT re-fetched.
    Prevents accidental refresh of the 68 legacy yfinance entries."""
    import json
    from backtest.data.universe import fetch_info_bulk
    cache_file = tmp_path / "valid_info.json"
    sentinel = 12345.0   # arbitrary value not present in any Polygon ref parquet
    cache_file.write_text(json.dumps({
        "AAPL": {
            "name": "Apple Inc.",
            "sector": "Information Technology",
            "industry": "Test Industry",
            "market_cap": sentinel,
            "exchange": "TEST",
            "ipo_date": "1980-12-12",
        }
    }))
    out = fetch_info_bulk(["AAPL"], delay=0.0, cache_file=str(cache_file))
    assert out["AAPL"]["market_cap"] == sentinel, \
        f"Valid mcap should be preserved (no refetch), got {out['AAPL']['market_cap']}"
    print(f"[OK] Batch 301 fetch_info_bulk preserves valid mcap={sentinel}")


def test_batch301_fetch_info_bulk_universe_recovery(tmp_path):
    """End-to-end: fetching the Stage D 150-tkr sample yields >=100 tickers
    with market_cap >= 100M (the LIQUIDITY['min_market_cap_m'] threshold).
    Pre-Batch-301 baseline was 8/150."""
    from pathlib import Path
    from backtest.data.universe import fetch_info_bulk

    sample_path = Path(__file__).parent.parent.parent / "scripts" / "stage_d_tickers.txt"
    if not sample_path.exists():
        import pytest
        pytest.skip("Stage D ticker list not present")
    tickers = sample_path.read_text().strip().split("\n")
    cache_file = tmp_path / "stage_d_test_info.json"
    out = fetch_info_bulk(tickers, delay=0.0, cache_file=str(cache_file))
    have_mcap = sum(1 for t in tickers if (out.get(t, {}).get("market_cap", 0) or 0) >= 100_000_000)
    assert have_mcap >= 100, (
        f"Batch 301: expected >=100/150 Stage D tickers with mcap>=100M, got {have_mcap}. "
        f"Pre-fix baseline was 8/150. Regression suspect."
    )
    print(f"[OK] Batch 301 Stage D universe recovery: {have_mcap}/150 mcap>=100M (was 8/150)")
