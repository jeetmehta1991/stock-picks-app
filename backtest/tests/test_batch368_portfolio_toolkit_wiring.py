"""Stream B2: OurTraderToolkit + OurRiskToolkit Portfolio wiring tests.

Source (per CHECKLIST #77): owner directive 2026-05-26 Stream B2 +
TRADINGAGENTS_DATA_AUDIT.md Sections 23/24. BUG-095 Portfolio class
shipped Batch 328; Stream B2 wires the toolkits' scaffold methods to
real Portfolio queries.

Pyramid tiers exercised:
  T1 (Unit)        get_portfolio_state returns real n_open / cash / drawdown
  T1 (Unit)        get_existing_position returns Position fields
  T1 (Unit)        get_sector_concentration returns max_sector_pct
  T1 (Unit)        get_drawdown_context returns current + max DD + multiplier
  T6 (Regression)  portfolio=None path still returns safe sentinel
                   (preserves Phase 1B-alpha mock-smoke compatibility)
"""
from __future__ import annotations

from datetime import date

import pytest

from backtest.agents.toolkits import OurRiskToolkit, OurTraderToolkit
from backtest.engine.portfolio import Portfolio


# ---------------------------------------------------------------------
# Helper: build a portfolio with 2 open positions for tests
# ---------------------------------------------------------------------
def _make_test_portfolio() -> Portfolio:
    p = Portfolio(starting_capital=100_000.0, benchmark="SPY")
    # Open 2 positions across 2 sectors
    p.add_position(
        ticker="AAPL", sector="Technology", direction="long",
        entry_price=150.0, size_pct=5.0,
        entry_date=date(2024, 6, 1),
    )
    p.add_position(
        ticker="JNJ", sector="Healthcare", direction="long",
        entry_price=160.0, size_pct=3.0,
        entry_date=date(2024, 6, 2),
    )
    # Mark to market once to populate last_mark
    p.mark_to_market(
        prices={"AAPL": 155.0, "JNJ": 162.0},
        today=date(2024, 6, 3),
    )
    return p


# ---------------------------------------------------------------------
# OurTraderToolkit
# ---------------------------------------------------------------------
def test_b2_trader_portfolio_state_with_real_portfolio():
    p = _make_test_portfolio()
    tk = OurTraderToolkit(portfolio=p)
    state = tk.get_portfolio_state()
    assert state["scaffold"] is False
    assert state["n_positions"] == 2
    assert state["starting_capital"] == 100_000.0
    assert state["total_equity"] > 0
    assert "cash_available_pct" in state
    assert "max_drawdown_pct" in state


def test_b2_trader_portfolio_state_no_portfolio_returns_sentinel():
    """Mock-smoke compatibility: portfolio=None path still works."""
    tk = OurTraderToolkit(portfolio=None)
    state = tk.get_portfolio_state()
    assert state["scaffold"] is True
    assert state["n_positions"] == 0
    assert state["cash_available_pct"] == 100.0


def test_b2_trader_existing_position_returns_position_fields():
    p = _make_test_portfolio()
    tk = OurTraderToolkit(portfolio=p)
    aapl = tk.get_existing_position("AAPL")
    assert aapl["open"] is True
    assert aapl["scaffold"] is False
    assert aapl["direction"] == "long"
    assert aapl["entry_price"] == 150.0
    assert aapl["sector"] == "Technology"
    assert aapl["shares"] > 0


def test_b2_trader_existing_position_unowned_ticker():
    p = _make_test_portfolio()
    tk = OurTraderToolkit(portfolio=p)
    msft = tk.get_existing_position("MSFT")
    assert msft["open"] is False
    assert msft["scaffold"] is False


def test_b2_trader_cooldown_remains_scaffold():
    """Per-ticker cooldown returns scaffold when circuit_breaker_log not
    passed (mock-smoke / LLM dry-run path preserved per Batch 373)."""
    p = _make_test_portfolio()
    tk = OurTraderToolkit(portfolio=p)  # no circuit_breaker_log
    result = tk.get_per_ticker_cooldown("AAPL", date(2024, 6, 15))
    assert result["scaffold"] is True
    assert "deferred_reason" in result


def test_b1_batch373_trader_cooldown_real_circuit_breaker_log():
    """Batch 373 Sprint 7 Phase B prep: get_per_ticker_cooldown reads the
    engine's circuit_breaker_log when passed at toolkit init."""
    cb_log = [
        {"date": date(2024, 6, 10), "ticker": "AAPL",
         "level": "L3", "reason": "regime_change"},
        {"date": date(2024, 6, 14), "ticker": "MSFT",
         "level": "L3", "reason": "vol_spike"},
        {"date": date(2024, 5, 20), "ticker": "AAPL",
         "level": "L2", "reason": "drawdown"},
    ]
    p = _make_test_portfolio()
    tk = OurTraderToolkit(portfolio=p, circuit_breaker_log=cb_log)

    # AAPL stopped 2024-06-10; as_of 2024-06-12 => 2 days since => in cooldown 3 days remaining
    r = tk.get_per_ticker_cooldown("AAPL", date(2024, 6, 12))
    assert r["scaffold"] is False
    assert r["in_cooldown"] is True
    assert r["days_remaining"] == 3
    assert r["last_stop_date"] == "2024-06-10"

    # AAPL as_of 2024-06-16 => 6 days since => out of cooldown
    r2 = tk.get_per_ticker_cooldown("AAPL", date(2024, 6, 16))
    assert r2["scaffold"] is False
    assert r2["in_cooldown"] is False
    assert r2["days_remaining"] == 0

    # Ticker with no stop history
    r3 = tk.get_per_ticker_cooldown("GOOGL", date(2024, 6, 12))
    assert r3["scaffold"] is False
    assert r3["in_cooldown"] is False
    assert r3["last_stop_date"] is None

    # Most-recent-only: AAPL has 2 stops; uses 2024-06-10 not 2024-05-20
    r4 = tk.get_per_ticker_cooldown("AAPL", date(2024, 6, 11))
    assert r4["last_stop_date"] == "2024-06-10"
    assert r4["days_remaining"] == 4

    # Future stop ignored (as_of < event date)
    r5 = tk.get_per_ticker_cooldown("AAPL", date(2024, 6, 5))
    assert r5["last_stop_date"] == "2024-05-20"  # only the past one


# ---------------------------------------------------------------------
# OurRiskToolkit
# ---------------------------------------------------------------------
def test_b2_risk_correlation_with_open_positions():
    p = _make_test_portfolio()
    tk = OurRiskToolkit(portfolio=p)
    result = tk.get_correlation_to_existing_positions("MSFT", date(2024, 6, 15))
    assert result["scaffold"] is False
    assert result["n_existing_positions"] == 2
    assert "AAPL" in result["existing_tickers"]
    assert "JNJ" in result["existing_tickers"]


def test_b2_risk_correlation_no_open_positions():
    p = Portfolio(starting_capital=100_000.0)
    tk = OurRiskToolkit(portfolio=p)
    result = tk.get_correlation_to_existing_positions("MSFT", date(2024, 6, 15))
    assert result["scaffold"] is False
    assert result["n_existing_positions"] == 0
    assert result["max_correlation"] == 0.0


def test_b2_risk_correlation_no_portfolio_returns_sentinel():
    tk = OurRiskToolkit(portfolio=None)
    result = tk.get_correlation_to_existing_positions("MSFT", date(2024, 6, 15))
    assert result["scaffold"] is True


def test_b2_risk_sector_concentration_with_2_sectors():
    p = _make_test_portfolio()
    tk = OurRiskToolkit(portfolio=p)
    result = tk.get_sector_concentration()
    assert result["scaffold"] is False
    assert "sectors" in result
    assert "Technology" in result["sectors"]
    assert "Healthcare" in result["sectors"]
    assert result["max_sector_pct"] > 0


def test_b2_risk_sector_concentration_no_portfolio_returns_sentinel():
    tk = OurRiskToolkit(portfolio=None)
    result = tk.get_sector_concentration()
    assert result["scaffold"] is True


def test_b2_risk_drawdown_context_with_portfolio():
    p = _make_test_portfolio()
    tk = OurRiskToolkit(portfolio=p)
    result = tk.get_drawdown_context()
    assert result["scaffold"] is False
    assert "current_drawdown_pct" in result
    assert "max_drawdown_pct" in result
    assert "drawdown_size_multiplier" in result
    # Drawdown multiplier should be valid float
    assert isinstance(result["drawdown_size_multiplier"], float)


def test_b2_risk_drawdown_context_no_portfolio_returns_sentinel():
    tk = OurRiskToolkit(portfolio=None)
    result = tk.get_drawdown_context()
    assert result["scaffold"] is True
    assert result["current_drawdown_pct"] == 0.0
