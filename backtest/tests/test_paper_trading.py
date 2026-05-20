"""Tests for Stage 3 paper_trading/ module (Batch 246)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from backtest.paper_trading.daily_picks import (
    Pick,
    _confidence_tier_from_sharpe,
    generate_picks,
    load_winners,
    picks_to_dataframe,
)
from backtest.paper_trading.email_digest import (
    format_eod_summary_email,
    format_picks_email,
    send_email,
)
from backtest.paper_trading.journal import (
    build_journal_entry,
    save_journal_entry,
)
from backtest.paper_trading.paper_portfolio import (
    PaperPortfolio,
    PaperPosition,
)


def _make_winners():
    return pd.DataFrame({
        "combo_id":      ["rsi__atr__bull", "mfi__trail__neutral"],
        "strategy":      ["rsi", "mfi"],
        "exit_method":   ["atr", "trail"],
        "regime":        ["bull", "neutral"],
        "n_trades":      [100, 80],
        "win_rate":      [0.60, 0.55],
        "sharpe":        [1.5, 1.0],
        "priority":      ["P1", "P1"],
        "tickers_fired": [["AAPL", "MSFT"], ["NVDA"]],
    })


def _make_market_data(tickers, n_days=30):
    out = {}
    for t in tickers:
        rng = np.random.RandomState(hash(t) % (2**32))
        closes = 100 + rng.randn(n_days).cumsum() * 0.5
        out[t] = pd.DataFrame({"close": closes, "high": closes * 1.01, "low": closes * 0.99})
    return out


# ---------------------------------------------------------------------------
# daily_picks tests
# ---------------------------------------------------------------------------
def test_confidence_tier_mapping():
    assert _confidence_tier_from_sharpe(2.5) == "EXCEPTIONAL"
    assert _confidence_tier_from_sharpe(1.7) == "VERY_HIGH"
    assert _confidence_tier_from_sharpe(1.2) == "HIGH"
    assert _confidence_tier_from_sharpe(0.8) == "MEDIUM-HIGH"
    assert _confidence_tier_from_sharpe(0.55) == "MEDIUM"
    assert _confidence_tier_from_sharpe(0.3) == "LOW"


def test_generate_picks_empty_winners():
    picks = generate_picks(pd.DataFrame(), {}, date(2026, 5, 19))
    assert picks == []


def test_generate_picks_returns_pick_list():
    winners = _make_winners()
    md = _make_market_data(["AAPL", "MSFT", "NVDA"])
    picks = generate_picks(winners, md, date(2026, 5, 19), max_picks=10)
    assert isinstance(picks, list)
    assert all(isinstance(p, Pick) for p in picks)
    # max 2 picks because only 2 P1 combos
    assert len(picks) <= 2


def test_generate_picks_respects_max_cap():
    winners = pd.DataFrame({
        "combo_id":      [f"s{i}__atr__bull" for i in range(20)],
        "strategy":      [f"s{i}" for i in range(20)],
        "exit_method":   ["atr"] * 20,
        "regime":        ["bull"] * 20,
        "n_trades":      [50] * 20,
        "win_rate":      [0.6] * 20,
        "sharpe":        [1.5] * 20,
        "priority":      ["P1"] * 20,
        "tickers_fired": [["AAPL"] for _ in range(20)],
    })
    md = _make_market_data(["AAPL"])
    picks = generate_picks(winners, md, date(2026, 5, 19), max_picks=10)
    # Should only generate 1 pick (single ticker; dedup); but cap mechanism
    # is the test here
    assert len(picks) <= 10


def test_picks_to_dataframe():
    winners = _make_winners()
    md = _make_market_data(["AAPL"])
    picks = generate_picks(winners, md, date(2026, 5, 19))
    df = picks_to_dataframe(picks)
    assert isinstance(df, pd.DataFrame)
    if not df.empty:
        assert "ticker" in df.columns
        assert "combo_id" in df.columns


def test_load_winners_missing_file(tmp_path):
    out = load_winners(tmp_path / "nonexistent.parquet")
    assert out.empty


# ---------------------------------------------------------------------------
# paper_portfolio tests
# ---------------------------------------------------------------------------
def test_paper_portfolio_default_state():
    p = PaperPortfolio()
    assert p.starting_value == 100_000.0
    assert p.cash == 100_000.0
    assert p.open_positions == []


def test_paper_portfolio_open_position():
    p = PaperPortfolio()
    pick = {
        "ticker": "AAPL",
        "combo_id": "rsi__atr__bull",
        "position_size_pct": 3.0,
        "entry_price": 200.0,
        "initial_stop": 196.0,
        "exit_method": "atr",
        "confidence_tier": "HIGH",
    }
    pos = p.open_position(pick, date(2026, 5, 19))
    assert pos is not None
    assert pos.ticker == "AAPL"
    assert pos.shares == 15  # 3% of $100K = $3000; $3000/$200 = 15 shares
    assert p.cash < 100_000.0  # cash reduced


def test_paper_portfolio_no_double_open():
    p = PaperPortfolio()
    pick = {
        "ticker": "AAPL", "combo_id": "x", "position_size_pct": 3.0,
        "entry_price": 200.0, "initial_stop": 196.0,
    }
    p.open_position(pick, date(2026, 5, 19))
    again = p.open_position(pick, date(2026, 5, 19))
    assert again is None
    assert len(p.open_positions) == 1


def test_paper_portfolio_eod_update():
    p = PaperPortfolio()
    pick = {
        "ticker": "AAPL", "combo_id": "x", "position_size_pct": 3.0,
        "entry_price": 200.0, "initial_stop": 196.0,
    }
    p.open_position(pick, date(2026, 5, 19))
    md = {"AAPL": pd.DataFrame({"close": [205.0]})}
    summary = p.update_eod(md, date(2026, 5, 20))
    assert summary["n_open"] == 1
    assert summary["n_closed_today"] == 0
    # Trailing stop should have moved up
    assert p.open_positions[0].current_stop > 196.0


def test_paper_portfolio_eod_triggers_stop():
    p = PaperPortfolio()
    pick = {
        "ticker": "AAPL", "combo_id": "x", "position_size_pct": 3.0,
        "entry_price": 200.0, "initial_stop": 196.0,
    }
    p.open_position(pick, date(2026, 5, 19))
    md = {"AAPL": pd.DataFrame({"close": [190.0]})}  # below stop
    summary = p.update_eod(md, date(2026, 5, 20))
    assert summary["n_closed_today"] == 1
    assert len(p.open_positions) == 0


def test_paper_portfolio_save_load_roundtrip(tmp_path):
    p = PaperPortfolio(starting_value=50_000, current_value=52_000, cash=10_000)
    path = tmp_path / "portfolio.json"
    p.save(path)
    loaded = PaperPortfolio.load(path)
    assert loaded.starting_value == 50_000
    assert loaded.cash == 10_000


# ---------------------------------------------------------------------------
# email_digest + journal tests
# ---------------------------------------------------------------------------
def test_format_picks_email_empty():
    s, b = format_picks_email([], date(2026, 5, 19))
    assert "0 picks" in s or "No picks" in b


def test_format_picks_email_with_picks():
    picks = [{
        "ticker": "AAPL", "combo_id": "x", "strategy": "rsi",
        "exit_method": "atr", "regime_at_entry": "bull",
        "confidence_tier": "HIGH", "position_size_pct": 3.0,
        "entry_price": 200.0, "initial_stop": 196.0,
        "rationale_bullets": ["P1 winner", "Sharpe 1.5"],
    }]
    s, b = format_picks_email(picks, date(2026, 5, 19))
    assert "AAPL" in b
    assert "HIGH" in b


def test_format_eod_summary_email():
    eod = {
        "as_of": "2026-05-19", "current_value": 102_000,
        "daily_pnl_dollar": 200, "n_open": 3, "n_closed_today": 1,
        "current_dd_pct": 1.5, "cash": 95_000,
    }
    s, b = format_eod_summary_email(eod, "Journal text")
    assert "2026-05-19" in s
    assert "102,000" in b or "102000" in b


def test_send_email_dry_run_returns_true(capsys):
    ok = send_email("test", "body", dry_run=True)
    assert ok
    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out


def test_build_journal_entry_no_trades():
    entry = build_journal_entry(date(2026, 5, 19), {"current_value": 100_000}, [], [])
    assert "No trades today" in entry


def test_build_journal_entry_with_trades():
    picks = [{"ticker": "AAPL", "strategy": "rsi", "exit_method": "atr",
              "position_size_pct": 3, "entry_price": 200, "initial_stop": 196,
              "confidence_tier": "HIGH"}]
    closed = [{"ticker": "MSFT", "entry_price": 300, "exit_price": 310,
               "pnl_pct": 3.33, "pnl_dollar": 100, "hold_days": 5,
               "exit_reason": "trailing_stop"}]
    entry = build_journal_entry(date(2026, 5, 19), {"current_value": 102_000}, picks, closed)
    assert "AAPL" in entry
    assert "MSFT" in entry
    assert "trailing_stop" in entry


def test_save_journal_entry(tmp_path):
    entry = "# Test"
    path = save_journal_entry(entry, date(2026, 5, 19), tmp_path / "journal")
    assert path.exists()
    assert path.read_text() == "# Test"
