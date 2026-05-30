"""Batch 469 (2026-05-29) -- P14 insider-quality differentiation.

Closes queue item P14 (`producer-insider-quality-differentiation`):
extends `backtest.data.smart_money.insider_signal()` to emit additional
signal levels beyond ceo_buy / cluster_buy / cluster_sell.

NEW SIGNAL LEVELS (Quiver-derived; no SEC EDGAR involvement):
  cfo_buy            -- officerTitle regex 'CFO|Chief Financial' in buys
  director_only_buy  -- isDirector=True AND isOfficer=False in buys
  large_dollar_buy   -- PricePerShare * Shares > $1M in buys
  concentrated_sell  -- Shares / (Shares + SharesOwnedFollowing) > 50%
                        in sells (sold-fraction of total holdings)

Composite-signal escalation now also fires "buy" on cfo_buy /
large_dollar_buy and "weak_buy" on director_only_buy. "concentrated_sell"
flows into the cluster_sell composite bucket as a "concentrated_sell"
verdict.

Academic refs:
  Cohen-Malloy-Pomorski 2012 RFS -- "Decoding Inside Information":
    director-only purchases have weaker but still positive predictive
    power vs. C-suite purchases; large-dollar transactions consistently
    outperform small ones.

TESTS BELOW assert each new field flips correctly + the composite
signal updates accordingly.
"""
from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

import numpy as np
import pandas as pd


def _make_quiver_df(rows):
    """rows is iterable of dicts with the relevant Quiver insider columns."""
    return pd.DataFrame(rows)


@patch("backtest.data.smart_money._load_quiver_bulk")
def test_cfo_buy_flag_fires(mock_load):
    from backtest.data.smart_money import insider_signal
    today = date(2024, 6, 1)
    df = _make_quiver_df([{
        "Ticker": "TEST", "Name": "Jane Doe", "Date": "2024-05-25",
        "fileDate": "2024-05-26", "TransactionCode": "P",
        "officerTitle": "CFO and Treasurer", "isDirector": False,
        "isOfficer": True, "Shares": 1000, "PricePerShare": 50,
        "SharesOwnedFollowing": 100_000,
    }])
    mock_load.return_value = df
    out = insider_signal("TEST", today)
    assert out["cfo_buy"] is True
    assert out["ceo_buy"] is False  # CEO regex shouldn't fire on CFO
    assert out["signal"] == "buy"


@patch("backtest.data.smart_money._load_quiver_bulk")
def test_director_only_buy_flag(mock_load):
    from backtest.data.smart_money import insider_signal
    today = date(2024, 6, 1)
    df = _make_quiver_df([{
        "Ticker": "TEST", "Name": "Alex Director", "Date": "2024-05-25",
        "fileDate": "2024-05-26", "TransactionCode": "P",
        "officerTitle": "", "isDirector": True, "isOfficer": False,
        "Shares": 100, "PricePerShare": 50,
        "SharesOwnedFollowing": 10_000,
    }])
    mock_load.return_value = df
    out = insider_signal("TEST", today)
    assert out["director_only_buy"] is True
    # ceo_buy / cfo_buy / large_dollar_buy all false -> composite weak_buy
    assert out["ceo_buy"] is False
    assert out["large_dollar_buy"] is False
    assert out["signal"] == "weak_buy"


@patch("backtest.data.smart_money._load_quiver_bulk")
def test_large_dollar_buy_flag(mock_load):
    from backtest.data.smart_money import insider_signal
    today = date(2024, 6, 1)
    # 50,000 shares * $25 = $1.25M -> over $1M threshold
    df = _make_quiver_df([{
        "Ticker": "TEST", "Name": "Big Money", "Date": "2024-05-25",
        "fileDate": "2024-05-26", "TransactionCode": "P",
        "officerTitle": "", "isDirector": False, "isOfficer": False,
        "Shares": 50_000, "PricePerShare": 25,
        "SharesOwnedFollowing": 500_000,
    }])
    mock_load.return_value = df
    out = insider_signal("TEST", today)
    assert out["large_dollar_buy"] is True
    assert out["signal"] == "buy"


@patch("backtest.data.smart_money._load_quiver_bulk")
def test_small_dollar_does_not_trip_large_dollar_buy(mock_load):
    from backtest.data.smart_money import insider_signal
    today = date(2024, 6, 1)
    # 100 shares * $10 = $1000 -- under threshold
    df = _make_quiver_df([{
        "Ticker": "TEST", "Name": "Small Money", "Date": "2024-05-25",
        "fileDate": "2024-05-26", "TransactionCode": "P",
        "officerTitle": "", "isDirector": False, "isOfficer": False,
        "Shares": 100, "PricePerShare": 10,
        "SharesOwnedFollowing": 10_000,
    }])
    mock_load.return_value = df
    out = insider_signal("TEST", today)
    assert out["large_dollar_buy"] is False
    # Still a buy via the 1+ buy path -> weak_buy
    assert out["signal"] == "weak_buy"


@patch("backtest.data.smart_money._load_quiver_bulk")
def test_concentrated_sell_flag_fires(mock_load):
    from backtest.data.smart_money import insider_signal
    today = date(2024, 6, 1)
    # Sold 800 shares, 100 remaining -> 800 / 900 = 89% > 50%
    df = _make_quiver_df([{
        "Ticker": "TEST", "Name": "Liquidator", "Date": "2024-05-25",
        "fileDate": "2024-05-26", "TransactionCode": "S",
        "officerTitle": "VP", "isDirector": False, "isOfficer": True,
        "Shares": 800, "PricePerShare": 100,
        "SharesOwnedFollowing": 100,
    }])
    mock_load.return_value = df
    out = insider_signal("TEST", today)
    assert out["concentrated_sell"] is True
    assert out["signal"] == "concentrated_sell"


@patch("backtest.data.smart_money._load_quiver_bulk")
def test_routine_trim_does_not_trip_concentrated_sell(mock_load):
    from backtest.data.smart_money import insider_signal
    today = date(2024, 6, 1)
    # Sold 100 shares of 10,000 holdings -> ~1% << 50%
    df = _make_quiver_df([{
        "Ticker": "TEST", "Name": "Trimmer", "Date": "2024-05-25",
        "fileDate": "2024-05-26", "TransactionCode": "S",
        "officerTitle": "VP", "isDirector": False, "isOfficer": True,
        "Shares": 100, "PricePerShare": 100,
        "SharesOwnedFollowing": 10_000,
    }])
    mock_load.return_value = df
    out = insider_signal("TEST", today)
    assert out["concentrated_sell"] is False
    # signal is "none" because no buys + no cluster_sell + no concentrated_sell
    assert out["signal"] in ("none",)


@patch("backtest.data.smart_money._load_quiver_bulk")
def test_signal_dict_includes_all_new_keys(mock_load):
    from backtest.data.smart_money import insider_signal
    today = date(2024, 6, 1)
    df = _make_quiver_df([{
        "Ticker": "TEST", "Name": "Person", "Date": "2024-05-25",
        "fileDate": "2024-05-26", "TransactionCode": "P",
        "officerTitle": "CEO", "isDirector": False, "isOfficer": True,
        "Shares": 10, "PricePerShare": 10,
        "SharesOwnedFollowing": 1000,
    }])
    mock_load.return_value = df
    out = insider_signal("TEST", today)
    for k in ("cfo_buy", "director_only_buy", "large_dollar_buy",
              "concentrated_sell"):
        assert k in out, f"missing {k}"
