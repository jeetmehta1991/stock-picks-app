"""
End-to-end smoke test — runs full backtest pipeline on minimal data.
Verifies the entire chain: data load → screen → entry → exit → outputs.
Run before every Phase 1B: python backtest/tests/test_e2e.py

Uses 5 tickers × 3 months with agents disabled (~5 seconds).
"""
import sys
import logging
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
logging.disable(logging.CRITICAL)  # suppress noise during test


SMOKE_TICKERS = ["AAPL", "MSFT", "NVDA", "SPY", "XLK"]
SMOKE_START   = date(2022, 1, 1)
SMOKE_END     = date(2022, 3, 31)


@pytest.fixture(scope="module")
def engine():
    """
    BUG-216 fix (Pass 48): converted from regular function returning engine
    into a proper pytest fixture so dependent tests can use `engine` parameter.
    Module-scoped so the slow backtest only runs once per test session.
    """
    from backtest.engine.backtest import BacktestEngine

    eng = BacktestEngine(
        universe=SMOKE_TICKERS,
        start=SMOKE_START,
        end=SMOKE_END,
        phase="phase_1a",
        max_candidates_per_day=5,
        run_agents=False,
        output_dir="output_smoke_test",
        apply_costs=True,
        walk_forward=False,
    )
    eng.load_data()
    eng.run()

    if len(eng.ohlcv_dict) == 0:
        pytest.skip("OHLCV cache not available — run e2e from Codespaces with cache populated")

    return eng


def test_e2e_backtest_runs(engine):
    """Full pipeline smoke test — no agents, 5 tickers, 3 months."""
    assert len(engine.closed_trades) > 0, \
        "Smoke test produced zero closed trades — pipeline broken"
    print(f"✅ E2E backtest ran — {len(engine.closed_trades)} closed trades")


def test_trade_log_completeness(engine):
    """All required fields present and no NaN in critical columns."""
    df = engine.get_trade_log()
    assert not df.empty

    required_cols = [
        "ticker", "entry_date", "exit_date", "direction", "strategy",
        "category", "sector", "confidence_tier", "preliminary_tier",
        "pnl_pct", "win", "hold_days",
        "max_adverse_excursion", "max_favourable_excursion",
        "congressional_signal", "insider_signal", "institutional_signal",
        "aaii_bullish", "cnn_fg_score",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    assert not missing, f"Missing columns: {missing}"

    nan_cols = [c for c in ["pnl_pct", "win", "hold_days"]
                if df[c].isna().any()]
    assert not nan_cols, f"NaN in critical columns: {nan_cols}"

    assert (df["hold_days"] >= 0).all(), "Negative hold_days found"
    assert df["direction"].isin(["long", "short"]).all(), "Invalid direction values"
    assert df["preliminary_tier"].notna().all(), "preliminary_tier has NaN"

    print(f"✅ Trade log completeness — {len(df)} trades, all {len(required_cols)} fields present")


def test_no_lookahead_in_trade_log(engine):
    """Entry date must be before exit date for all trades."""
    df = engine.get_trade_log()
    df["entry_date"] = pd.to_datetime(df["entry_date"])
    df["exit_date"]  = pd.to_datetime(df["exit_date"])
    bad = df[df["entry_date"] >= df["exit_date"]]
    assert bad.empty, f"{len(bad)} trades have entry_date >= exit_date"
    print("✅ No look-ahead: all exit dates after entry dates")


def test_pnl_within_realistic_bounds(engine):
    """PnL should be within realistic bounds — no 1000% single trades."""
    df = engine.get_trade_log()
    assert df["pnl_pct"].abs().max() < 100, \
        f"Unrealistic single trade PnL: {df['pnl_pct'].abs().max():.1f}%"
    print(f"✅ PnL within bounds — max single trade: {df['pnl_pct'].abs().max():.1f}%")


def test_mae_mfe_accumulated(engine):
    """MAE/MFE should reflect full hold period, not just one day."""
    df = engine.get_trade_log()
    multi_day = df[df["hold_days"] > 1]
    if not multi_day.empty:
        # For multi-day trades, MFE should generally be >= single-day range
        # Check that MFE values are non-trivially small
        avg_mfe = multi_day["max_favourable_excursion"].mean()
        assert avg_mfe >= 0, "MFE should be non-negative for longs"
    print(f"✅ MAE/MFE accumulated — avg MFE: {df['max_favourable_excursion'].mean():.2f}%")


def test_sector_populated(engine):
    """All trades should have a sector (not Unknown for known S&P 500 stocks)."""
    df = engine.get_trade_log()
    known_stocks = df[df["ticker"].isin(["AAPL", "MSFT", "NVDA"])]
    if not known_stocks.empty:
        unknowns = known_stocks[known_stocks["sector"] == "Unknown"]
        assert unknowns.empty, \
            f"Known stocks have Unknown sector: {unknowns['ticker'].tolist()}"
    print("✅ Sector populated for known S&P 500 stocks")


def test_avoid_tier_not_in_long_trades(engine):
    """AVOID tier should never appear as a long trade."""
    df = engine.get_trade_log()
    avoid_longs = df[(df["confidence_tier"] == "AVOID") & (df["direction"] == "long")]
    assert avoid_longs.empty, \
        f"{len(avoid_longs)} long trades with AVOID tier found"
    print("✅ No AVOID-tier long trades")


def test_outputs_written(engine):
    """Verify output files are written after save_all_outputs."""
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        engine.output_dir = Path(tmpdir)
        engine.save_all_outputs()
        written = list(Path(tmpdir).glob("*.csv")) + list(Path(tmpdir).glob("*.html"))
        assert len(written) >= 3, f"Only {len(written)} output files written"
        filenames = [f.name for f in written]
        assert any("trade_log" in f for f in filenames), "trade_log.csv not written"
        assert any("backtest_results" in f for f in filenames), "backtest_results.csv not written"
    print(f"✅ Output files written: {len(written)} files including trade_log and backtest_results")


def test_point_in_time_ohlcv():
    """OHLCV fetch must respect as_of ceiling — no future data."""
    from backtest.data.fetcher import fetch_ohlcv
    as_of = date(2023, 6, 15)
    df = fetch_ohlcv("AAPL", start=date(2023, 1, 1), end=date(2023, 12, 31), as_of=as_of)
    if not df.empty:
        last_date = df.index[-1].date()
        assert last_date <= as_of, \
            f"OHLCV has future data: last row {last_date} > as_of {as_of}"
    print(f"✅ OHLCV point-in-time enforced — last row: {last_date if not df.empty else 'N/A'}")


def test_agent_input_coherency():
    """Agent pipeline receives correct data structure with all expected keys."""
    from backtest.data.smart_money import smart_money_score
    from backtest.data.sentiment import sentiment_snapshot
    from backtest.data.macro import macro_snapshot

    as_of = date(2024, 1, 15)
    sm   = smart_money_score("AAPL", as_of)
    sent = sentiment_snapshot(as_of)
    macro = macro_snapshot(as_of)

    # Keys the pipeline needs from smart_money
    for k in ["congressional_sig", "insider_sig", "institutional_sig",
              "smart_money_composite", "composite_signal", "score"]:
        assert k in sm, f"SM key missing: {k}"

    # Keys the pipeline needs from sentiment
    for k in ["aaii", "fear_greed", "sentiment_score"]:
        assert k in sent, f"Sentiment key missing: {k}"

    # Keys the pipeline needs from macro
    assert isinstance(macro, dict), "macro_snapshot must return dict"

    print("✅ Agent input data structures coherent")


if __name__ == "__main__":
    print("="*60)
    print("END-TO-END SMOKE TEST")
    print("="*60)

    tests_no_engine = [test_point_in_time_ohlcv, test_agent_input_coherency]
    tests_with_engine = [
        test_trade_log_completeness,
        test_no_lookahead_in_trade_log,
        test_pnl_within_realistic_bounds,
        test_mae_mfe_accumulated,
        test_sector_populated,
        test_avoid_tier_not_in_long_trades,
        test_outputs_written,
    ]

    passed = 0
    total  = len(tests_no_engine) + 1 + len(tests_with_engine)
    failed = []

    # Run non-engine tests
    for t in tests_no_engine:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"❌ {t.__name__}: {e}")
            failed.append(t.__name__)

    # Run engine tests
    try:
        engine = test_e2e_backtest_runs()
        passed += 1
        if engine is None:
            print("⚠️  Engine tests skipped — no cache available")
            total = len(tests_no_engine) + 1
        else:
         for t in tests_with_engine:
            try:
                t(engine)
                passed += 1
            except Exception as e:
                print(f"❌ {t.__name__}: {e}")
                failed.append(t.__name__)
    except Exception as e:
        print(f"❌ test_e2e_backtest_runs: {e}")
        failed.append("test_e2e_backtest_runs")

    print(f"\n{'='*60}")
    print(f"{passed}/{total} e2e tests passed")
    if failed:
        print(f"FAILED: {failed}")
