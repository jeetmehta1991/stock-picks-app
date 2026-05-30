"""Batch 473 (2026-05-29) -- P16 sub-items: housetrading + gov_contracts tests."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest


def _make_house_df(rows):
    return pd.DataFrame(
        [{"Representative": r, "BioGuideID": "X", "Date": pd.Timestamp(d),
          "Ticker": "TEST", "Transaction": tx, "Range": "$1k-$15k",
          "Amount": "1001.0", "last_modified": "2024-06-01"}
         for r, d, tx in rows])


# --------------------------------------------------------------------
# housetrading
# --------------------------------------------------------------------
def test_housetrading_empty_on_missing_file(tmp_path, monkeypatch):
    import backtest.signals.congressional_alt_data as cad
    monkeypatch.setattr(cad, "_HOUSETRADING_DIR", tmp_path)
    out = cad.compute_housetrading_signals("NOEXIST", date.today())
    assert out == {}


def test_housetrading_counts_distinct_buyers(tmp_path, monkeypatch):
    import backtest.signals.congressional_alt_data as cad
    monkeypatch.setattr(cad, "_HOUSETRADING_DIR", tmp_path)
    today = date(2024, 6, 1)
    df = _make_house_df([
        ("Rep A", today - timedelta(days=10), "Purchase"),
        ("Rep B", today - timedelta(days=20), "Purchase"),
        ("Rep C", today - timedelta(days=30), "Purchase"),
        ("Rep D", today - timedelta(days=15), "Sale"),
    ])
    df.to_parquet(tmp_path / "TEST.parquet")
    out = cad.compute_housetrading_signals("TEST", today)
    assert out["house_buy_count_90d"] == 3
    assert out["house_sell_count_90d"] == 1
    assert out["house_net_buy_90d"] == 2
    assert out["house_cluster_buy"] is True
    assert out["house_cluster_sell"] is False


def test_housetrading_ignores_old_transactions(tmp_path, monkeypatch):
    import backtest.signals.congressional_alt_data as cad
    monkeypatch.setattr(cad, "_HOUSETRADING_DIR", tmp_path)
    today = date(2024, 6, 1)
    df = _make_house_df([
        # 200 days old -> outside 90-day window
        ("Rep Old", today - timedelta(days=200), "Purchase"),
    ])
    df.to_parquet(tmp_path / "OLD.parquet")
    out = cad.compute_housetrading_signals("OLD", today)
    assert out["house_buy_count_90d"] == 0


def test_housetrading_pit_drops_post_asof(tmp_path, monkeypatch):
    import backtest.signals.congressional_alt_data as cad
    monkeypatch.setattr(cad, "_HOUSETRADING_DIR", tmp_path)
    today = date(2024, 6, 1)
    df = _make_house_df([
        ("Rep Future", today + timedelta(days=10), "Purchase"),
    ])
    df.to_parquet(tmp_path / "FUT.parquet")
    out = cad.compute_housetrading_signals("FUT", today)
    assert out["house_buy_count_90d"] == 0


# --------------------------------------------------------------------
# gov_contracts
# --------------------------------------------------------------------
def test_gov_contracts_empty_on_missing_file(tmp_path, monkeypatch):
    import backtest.signals.congressional_alt_data as cad
    monkeypatch.setattr(cad, "_GOV_CONTRACTS_DIR", tmp_path)
    out = cad.compute_gov_contracts_signals("NOEXIST", date.today())
    assert out == {}


def test_gov_contracts_emits_last_qtr_and_4q_sum(tmp_path, monkeypatch):
    import backtest.signals.congressional_alt_data as cad
    monkeypatch.setattr(cad, "_GOV_CONTRACTS_DIR", tmp_path)
    df = pd.DataFrame([
        {"Ticker": "T", "Amount": "100.0",  "Qtr": 1, "Year": 2023},
        {"Ticker": "T", "Amount": "200.0",  "Qtr": 2, "Year": 2023},
        {"Ticker": "T", "Amount": "300.0",  "Qtr": 3, "Year": 2023},
        {"Ticker": "T", "Amount": "400.0",  "Qtr": 4, "Year": 2023},
        {"Ticker": "T", "Amount": "500.0",  "Qtr": 1, "Year": 2024},
    ])
    df.to_parquet(tmp_path / "T.parquet")
    # as_of in Q2 2024 -- last quarter <= cutoff is 2024 Q1 (500)
    out = cad.compute_gov_contracts_signals("T", date(2024, 5, 15))
    assert out["gov_contracts_last_qtr_amount"] == 500.0
    # 4q sum = last 4 quarters: 200+300+400+500 = 1400
    assert out["gov_contracts_4q_sum"] == 1400.0
    # qoq = (500 - 400) / 400 = 0.25
    assert out["gov_contracts_qoq_growth"] == pytest.approx(0.25, abs=1e-4)


def test_gov_contracts_pit_drops_future_quarters(tmp_path, monkeypatch):
    import backtest.signals.congressional_alt_data as cad
    monkeypatch.setattr(cad, "_GOV_CONTRACTS_DIR", tmp_path)
    df = pd.DataFrame([
        {"Ticker": "T", "Amount": "100.0", "Qtr": 1, "Year": 2024},
        {"Ticker": "T", "Amount": "200.0", "Qtr": 2, "Year": 2024},  # future
    ])
    df.to_parquet(tmp_path / "T.parquet")
    # as_of in Q1 2024 -- Q2 2024 must be dropped
    out = cad.compute_gov_contracts_signals("T", date(2024, 2, 15))
    assert out["gov_contracts_last_qtr_amount"] == 100.0


# --------------------------------------------------------------------
# lobbying (Batch 480)
# --------------------------------------------------------------------
def _make_lobbying_df(rows):
    return pd.DataFrame([
        {"Date": pd.Timestamp(d), "Amount": str(amt),
         "Client": c, "Issue": "x", "Specific_Issue": "x",
         "Registrant": c, "Ticker": "T"}
        for c, d, amt in rows
    ])


def test_lobbying_empty_on_missing_file(tmp_path, monkeypatch):
    import backtest.signals.congressional_alt_data as cad
    monkeypatch.setattr(cad, "_LOBBYING_DIR", tmp_path)
    out = cad.compute_lobbying_signals("NOEXIST", date.today())
    assert out == {}


def test_lobbying_sums_amounts_in_window(tmp_path, monkeypatch):
    import backtest.signals.congressional_alt_data as cad
    monkeypatch.setattr(cad, "_LOBBYING_DIR", tmp_path)
    today = date(2024, 6, 1)
    df = _make_lobbying_df([
        ("TEST", today - timedelta(days=30),  1_000_000),
        ("TEST", today - timedelta(days=180), 2_000_000),
        ("TEST", today - timedelta(days=500), 5_000_000),  # outside 1y
    ])
    df.to_parquet(tmp_path / "T.parquet")
    out = cad.compute_lobbying_signals("T", today)
    assert out["lobbying_amount_1y"] == 3_000_000.0
    assert out["lobbying_amount_q"]  == 1_000_000.0  # within 90d


def test_lobbying_yoy_growth(tmp_path, monkeypatch):
    import backtest.signals.congressional_alt_data as cad
    monkeypatch.setattr(cad, "_LOBBYING_DIR", tmp_path)
    today = date(2024, 6, 1)
    df = _make_lobbying_df([
        ("TEST", today - timedelta(days=100), 2_000_000),
        ("TEST", today - timedelta(days=500), 1_000_000),
    ])
    df.to_parquet(tmp_path / "T.parquet")
    out = cad.compute_lobbying_signals("T", today)
    # YoY = (2M - 1M) / 1M = 1.0
    assert out["lobbying_amount_yoy"] == pytest.approx(1.0, abs=1e-4)
