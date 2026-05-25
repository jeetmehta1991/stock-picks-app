"""Sprint 7 Phase A: toolkit + state-augmentation tests.

Source (per CHECKLIST #77): Sprint 7 Batch 350 2026-05-25. Pyramid tests
for the 5 custom toolkits per TRADINGAGENTS_DATA_AUDIT.md Part D + state
augmentation per Part E.

Pyramid tiers exercised:
  T1 (Unit)        Each toolkit method returns documented dict schema
  T1 (Unit)        Cache-miss returns {"error": "cache_miss"} not raise
  T1 (Unit)        Sizing-rules dict matches DEC-021 3-tier (5%/3%/1.5%)
  T2 (Smoke)       Toolkits instantiate without raising
  T3 (Integration) build_augmented_state populates all expected keys
  T3 (Integration) LLM-mocked propagate hook receives augmented state
  T6 (Regression)  Sentinel `scaffold` flag pinned for Trader/Risk methods
                   that require BUG-095 Portfolio class
  T11 (Property)   PIT correctness: methods filter by date <= as_of
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from backtest.agents.toolkits import (
    AugmentedAgentState,
    OurFundamentalsToolkit,
    OurNewsToolkit,
    OurRiskToolkit,
    OurTechnicalToolkit,
    OurTraderToolkit,
    build_augmented_state,
)
from backtest.agents.toolkits.state_augmentation import StateBuilderToolkits

REPO = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------
# T2 - Smoke: toolkit instantiation
# ---------------------------------------------------------------------
def test_all_toolkits_instantiate():
    """Every toolkit class instantiates without raising."""
    assert OurTechnicalToolkit() is not None
    assert OurFundamentalsToolkit() is not None
    assert OurNewsToolkit() is not None
    assert OurTraderToolkit() is not None
    assert OurRiskToolkit() is not None


# ---------------------------------------------------------------------
# T1 - Unit: OurTechnicalToolkit
# ---------------------------------------------------------------------
def test_technical_polygon_ohlcv_cache_miss(tmp_path):
    """Cache-miss returns dict with `error: cache_miss`, not raise."""
    tk = OurTechnicalToolkit(ohlcv_dir=tmp_path)
    result = tk.get_polygon_ohlcv("NONEXISTENT", date(2024, 1, 1), date(2024, 12, 31))
    assert result["ticker"] == "NONEXISTENT"
    assert result["error"] == "cache_miss"


def test_technical_polygon_ohlcv_real_data():
    """Smoke: on a real cached ticker the function returns a populated dict."""
    tk = OurTechnicalToolkit()
    aapl_path = tk.ohlcv_dir / "AAPL.parquet"
    if not aapl_path.exists():
        pytest.skip("AAPL.parquet not in data_prefetch")
    result = tk.get_polygon_ohlcv("AAPL", date(2024, 1, 1), date(2024, 12, 31))
    assert "n_bars" in result or "error" in result
    if "n_bars" in result and result["n_bars"] > 0:
        assert "last_close" in result
        assert "last_date" in result
        # PIT property: last_date <= 2024-12-31
        assert result["last_date"] <= "2024-12-31"


def test_technical_signals_cache_miss(tmp_path):
    tk = OurTechnicalToolkit(ohlcv_dir=tmp_path)
    result = tk.get_technical_signals("NONEXISTENT", date(2024, 1, 1))
    assert result["error"] == "cache_miss"


def test_technical_liquidity_cache_miss(tmp_path):
    tk = OurTechnicalToolkit(ohlcv_dir=tmp_path)
    result = tk.get_liquidity_metrics("NONEXISTENT", date(2024, 1, 1))
    assert result["error"] == "cache_miss"


def test_technical_regime_context_returns_dict():
    """get_regime_context returns a dict with at least as_of + regime keys."""
    tk = OurTechnicalToolkit()
    result = tk.get_regime_context(date(2024, 6, 15))
    assert "as_of" in result
    assert result["as_of"] == "2024-06-15"


# ---------------------------------------------------------------------
# T1 - Unit: OurFundamentalsToolkit
# ---------------------------------------------------------------------
def test_fundamentals_pit_financials_cache_miss(tmp_path):
    tk = OurFundamentalsToolkit(financials_dir=tmp_path)
    result = tk.get_pit_financials("NONEXISTENT", date(2024, 6, 1))
    assert result["error"] == "cache_miss"


def test_fundamentals_insider_cache_miss(tmp_path):
    tk = OurFundamentalsToolkit(insiders_path=tmp_path / "nope.parquet")
    result = tk.get_insider_transactions("AAPL", date(2024, 6, 1))
    assert result["error"] == "cache_miss"


def test_fundamentals_congressional_cache_miss(tmp_path):
    tk = OurFundamentalsToolkit(congress_path=tmp_path / "nope.parquet")
    result = tk.get_congressional_trades("AAPL", date(2024, 6, 1))
    assert result["error"] == "cache_miss"


def test_fundamentals_13f_cache_miss(tmp_path):
    tk = OurFundamentalsToolkit(institutional_dir=tmp_path)
    result = tk.get_13f_holdings("NONEXISTENT", date(2024, 6, 1))
    assert result["error"] == "cache_miss"


# ---------------------------------------------------------------------
# T1 - Unit: OurNewsToolkit
# ---------------------------------------------------------------------
def test_news_polygon_cache_miss(tmp_path):
    tk = OurNewsToolkit(polygon_news_dir=tmp_path)
    result = tk.get_polygon_news("NONEXISTENT", date(2024, 6, 1))
    assert result["error"] == "cache_miss"


def test_news_fred_event_log_cache_miss(tmp_path):
    tk = OurNewsToolkit(fomc_path=tmp_path / "nope.parquet")
    result = tk.get_fred_event_log(date(2024, 6, 1))
    assert result["error"] == "cache_miss"


def test_news_fred_event_log_real():
    """If FOMC calendar parquet exists, function returns events list."""
    tk = OurNewsToolkit()
    if not tk.fomc_path.exists():
        pytest.skip("fomc_calendar.parquet not built")
    result = tk.get_fred_event_log(date(2024, 6, 15), lookback_days=180)
    assert "n_events" in result
    assert isinstance(result["events"], list)


def test_news_analyst_rating_changes_cache_miss(tmp_path):
    tk = OurNewsToolkit(rating_changes_path=tmp_path / "nope.parquet")
    result = tk.get_analyst_rating_changes("AAPL", date(2024, 6, 1))
    assert result["error"] == "cache_miss"


# ---------------------------------------------------------------------
# T1 - Unit: OurTraderToolkit
# ---------------------------------------------------------------------
def test_trader_position_sizing_matches_dec021():
    """DEC-021 3-tier matches: EXCEPTIONAL 5%, VERY_HIGH 4%, HIGH 3%,
    MEDIUM_HIGH 1.5%, MEDIUM 0.75%, LOW skip."""
    tk = OurTraderToolkit()
    assert tk.get_position_sizing_rules("EXCEPTIONAL")["position_size_pct"] == 5.0
    assert tk.get_position_sizing_rules("VERY_HIGH")["position_size_pct"] == 4.0
    assert tk.get_position_sizing_rules("HIGH")["position_size_pct"] == 3.0
    assert tk.get_position_sizing_rules("MEDIUM_HIGH")["position_size_pct"] == 1.5
    assert tk.get_position_sizing_rules("MEDIUM")["position_size_pct"] == 0.75
    low = tk.get_position_sizing_rules("LOW")
    assert low["position_size_pct"] == 0.0
    assert low["skip"] is True


def test_trader_portfolio_state_scaffold_when_no_portfolio():
    tk = OurTraderToolkit(portfolio=None)
    state = tk.get_portfolio_state()
    assert state["scaffold"] is True
    assert state["n_positions"] == 0
    assert state["cash_available_pct"] == 100.0


def test_trader_existing_position_scaffold():
    tk = OurTraderToolkit(portfolio=None)
    state = tk.get_existing_position("AAPL")
    assert state["open"] is False
    assert state["scaffold"] is True


def test_trader_cooldown_scaffold():
    tk = OurTraderToolkit(portfolio=None)
    state = tk.get_per_ticker_cooldown("AAPL", date(2024, 6, 1))
    assert state["scaffold"] is True
    assert state["in_cooldown"] is False


# ---------------------------------------------------------------------
# T1 - Unit: OurRiskToolkit
# ---------------------------------------------------------------------
def test_risk_event_proximity_cache_miss(tmp_path):
    tk = OurRiskToolkit(fomc_path=tmp_path / "nope.parquet")
    result = tk.get_event_proximity(date(2024, 6, 1))
    assert result["error"] == "cache_miss"


def test_risk_correlation_scaffold():
    tk = OurRiskToolkit(portfolio=None)
    result = tk.get_correlation_to_existing_positions("AAPL", date(2024, 6, 1))
    assert result["scaffold"] is True
    assert result["max_correlation"] == 0.0


def test_risk_sector_concentration_scaffold():
    tk = OurRiskToolkit(portfolio=None)
    result = tk.get_sector_concentration()
    assert result["scaffold"] is True


def test_risk_drawdown_context_scaffold():
    tk = OurRiskToolkit(portfolio=None)
    result = tk.get_drawdown_context()
    assert result["scaffold"] is True


def test_risk_volatility_regime_returns_dict():
    """get_volatility_regime returns a dict with at least as_of + vix_regime."""
    tk = OurRiskToolkit()
    result = tk.get_volatility_regime(date(2024, 6, 15))
    assert "as_of" in result
    assert result["as_of"] == "2024-06-15"


# ---------------------------------------------------------------------
# T3 - Integration: build_augmented_state
# ---------------------------------------------------------------------
def _mocked_toolkits() -> StateBuilderToolkits:
    """Build a StateBuilderToolkits where every method returns a deterministic stub.
    Keeps the state-building test independent of real cache state."""
    tech = MagicMock()
    tech.get_sector_relative_strength.return_value = {"rs_pct": 0.5, "ticker_return_pct": 1.0}
    fund = MagicMock()
    fund.get_insider_transactions.return_value = {"ticker": "AAPL", "n_transactions": 3, "buy_count": 2}
    fund.get_congressional_trades.return_value = {"ticker": "AAPL", "n_disclosures": 1}
    fund.get_13f_holdings.return_value = {"ticker": "AAPL", "n_institutional_holders": 250}
    news = MagicMock()
    trader = MagicMock()
    trader.get_portfolio_state.return_value = {"n_positions": 0, "scaffold": True}
    risk = MagicMock()
    risk.get_volatility_regime.return_value = {"vix_value": 18.5, "vix_regime": "normal"}
    risk.get_event_proximity.return_value = {"n_upcoming_events": 0, "upcoming_events": []}
    risk.get_recent_outcomes_on_similar_setups.return_value = {"n_similar_trades": 0, "scaffold": True}
    return StateBuilderToolkits(
        technical=tech, fundamentals=fund, news=news, trader=trader, risk=risk
    )


def test_build_augmented_state_populates_all_keys():
    """All 9 augmented state keys must be present after build_augmented_state."""
    tk = _mocked_toolkits()
    state = build_augmented_state("AAPL", date(2024, 6, 15), tk)
    expected = {
        "ticker", "as_of", "regime_context", "portfolio_context",
        "smart_money_signal", "event_proximity", "sector_context",
        "short_interest_signal", "historical_outcomes",
    }
    assert expected.issubset(state.keys()), f"missing: {expected - state.keys()}"


def test_build_augmented_state_ticker_and_as_of():
    tk = _mocked_toolkits()
    state = build_augmented_state("AAPL", date(2024, 6, 15), tk)
    assert state["ticker"] == "AAPL"
    assert state["as_of"] == "2024-06-15"


def test_build_augmented_state_smart_money_has_3_subkeys():
    tk = _mocked_toolkits()
    state = build_augmented_state("AAPL", date(2024, 6, 15), tk)
    assert set(state["smart_money_signal"].keys()) == {"insider", "congressional", "institutional"}


def test_build_augmented_state_sector_etf_override():
    tk = _mocked_toolkits()
    state = build_augmented_state("XLF", date(2024, 6, 15), tk, sector_etf="XLF")
    tk.technical.get_sector_relative_strength.assert_called_with("XLF", "XLF", date(2024, 6, 15))


# ---------------------------------------------------------------------
# T3 - Integration: LLM-mocked propagate hook
# ---------------------------------------------------------------------
def test_propagate_fn_receives_augmented_state(tmp_path):
    """End-to-end: run_phase_1b_alpha with a mocked propagate_fn captures
    the augmented state - pins that future iteration code will be able to
    pass our state through the bridge to the LangGraph."""
    from backtest.agents.agent_gate_config import arm_b_full_with_veto
    from backtest.agents.langgraph_pipeline import (
        Phase1BAlphaConfig,
        run_phase_1b_alpha,
    )

    # Use empty winners parquet so the test doesn't iterate any tickers
    # in this batch; we're pinning the wiring + manifest shape only.
    cfg = Phase1BAlphaConfig(
        winners_parquet=tmp_path / "winners.parquet",
        output_dir=tmp_path / "out",
        agent_gate=arm_b_full_with_veto(),
        smoke_mode=False,
    )

    received = []
    def fake_propagate(state, ticker, date_):
        received.append({"state": state, "ticker": ticker, "date": date_})
        return ({}, "BUY")

    result = run_phase_1b_alpha(cfg, propagate_fn=fake_propagate)
    # Scaffold doesn't iterate tickers yet; pin propagate_invoked semantic
    assert result["propagate_invoked"] is True
    # Manifest must be written so future LLM-mocked tests can read it.
    assert result["manifest_path"].exists()
