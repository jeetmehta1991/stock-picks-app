"""Batch 528 (2026-05-31) -- P16 sub-feed completion tests.

Source: per CHECKLIST #77.
Queue row: EXECUTION_QUEUE.md item P16 (PARTIAL-RESOLVED -> RESOLVED).

Pins for the 3 newly-wired Quiver alt-data producers:

  compute_patentmomentum_signals   -- global feed, ticker lookup
  compute_offexchange_signals      -- per-ticker file, OTC + DPI
  compute_corporatedonors_signals  -- global feed, donation aggregates

Each producer:
  (a) returns {} on no data (silent-failure for backward compat)
  (b) returns expected dict keys on real-data hit
  (c) respects the as_of cutoff (PIT correctness)
  (d) is wired into screen_instrument via silent-failure logger
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# patentmomentum
# ---------------------------------------------------------------------------

def test_batch528_patent_returns_empty_for_unknown_ticker():
    from backtest.signals.congressional_alt_data import (
        compute_patentmomentum_signals,
    )
    out = compute_patentmomentum_signals("___NONEXISTENT___",
                                          date(2024, 6, 1))
    assert out == {}


def test_batch528_patent_returns_dict_with_expected_keys(monkeypatch):
    """Inject a synthetic 3-row DataFrame for ZZZZ and assert keys."""
    from backtest.signals import congressional_alt_data as mod
    fake = pd.DataFrame({
        "ticker":   ["ZZZZ", "ZZZZ", "ZZZZ"],
        "date":     pd.to_datetime(["2024-01-15", "2024-03-15",
                                     "2024-05-15"]),
        "momentum": [0.5, 0.7, 0.9],
    })
    monkeypatch.setattr(mod, "_PATENT_DF_CACHE", fake)
    out = mod.compute_patentmomentum_signals("ZZZZ", date(2024, 6, 1))
    assert set(out.keys()) == {
        "patent_momentum_recent",
        "patent_momentum_90d_avg",
        "patent_momentum_above_avg",
    }
    assert out["patent_momentum_recent"] == pytest.approx(0.9)
    # 90d avg = mean of rows in [Mar 15, May 15] window = (0.7 + 0.9) / 2 = 0.8
    assert out["patent_momentum_90d_avg"] == pytest.approx(0.8)
    assert out["patent_momentum_above_avg"] is True


def test_batch528_patent_respects_as_of_pit_cutoff(monkeypatch):
    """Row dated AFTER as_of must be excluded."""
    from backtest.signals import congressional_alt_data as mod
    fake = pd.DataFrame({
        "ticker":   ["ZZZZ"] * 3,
        "date":     pd.to_datetime(["2024-01-15", "2024-06-15",
                                     "2024-09-15"]),
        "momentum": [0.5, 0.7, 0.9],
    })
    monkeypatch.setattr(mod, "_PATENT_DF_CACHE", fake)
    # as_of = May 1 -> only the Jan 15 row qualifies
    out = mod.compute_patentmomentum_signals("ZZZZ", date(2024, 5, 1))
    assert out["patent_momentum_recent"] == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# offexchange
# ---------------------------------------------------------------------------

def test_batch528_offex_returns_empty_for_unknown_ticker():
    from backtest.signals.congressional_alt_data import (
        compute_offexchange_signals,
    )
    out = compute_offexchange_signals("___NONEXISTENT___",
                                       date(2024, 6, 1))
    assert out == {}


def test_batch528_offex_returns_dict_with_expected_keys_real_data():
    """Real-data smoke: AAPL has offexchange data per Batch 528
    cache inventory; producer must emit OTC + DPI keys."""
    from backtest.signals.congressional_alt_data import (
        compute_offexchange_signals,
    )
    out = compute_offexchange_signals("AAPL", date(2024, 6, 1))
    if not out:
        pytest.skip("AAPL offexchange data missing from local cache")
    expected = {"otc_short_ratio_recent", "otc_volume_recent",
                "dpi_recent", "dpi_30d_avg", "dpi_elevated"}
    assert expected.issubset(out.keys()), (
        f"missing keys: {expected - set(out.keys())}"
    )
    # Sanity: OTC short ratio is in [0, 1]
    assert 0.0 <= out["otc_short_ratio_recent"] <= 1.0
    assert 0.0 <= out["dpi_recent"] <= 1.0


def test_batch528_offex_respects_as_of_pit_cutoff(tmp_path, monkeypatch):
    """as_of cutoff filters out rows dated after it."""
    from backtest.signals import congressional_alt_data as mod
    fake_dir = tmp_path / "offexchange"
    fake_dir.mkdir()
    df = pd.DataFrame({
        "Ticker":    ["ZZZZ"] * 3,
        "Date":      pd.to_datetime(["2024-01-15", "2024-06-15",
                                      "2024-09-15"]),
        "OTC_Short": [100, 200, 300],
        "OTC_Total": [1000, 2000, 3000],
        "DPI":       [0.10, 0.20, 0.30],
    })
    df.to_parquet(fake_dir / "ZZZZ.parquet", index=False)
    monkeypatch.setattr(mod, "_OFFEXCHANGE_DIR", fake_dir)
    out = mod.compute_offexchange_signals("ZZZZ", date(2024, 5, 1))
    # Only Jan 15 row qualifies -> DPI=0.10
    assert out["dpi_recent"] == pytest.approx(0.10)


# ---------------------------------------------------------------------------
# corporatedonors
# ---------------------------------------------------------------------------

def test_batch528_donors_returns_empty_for_unknown_ticker():
    from backtest.signals.congressional_alt_data import (
        compute_corporatedonors_signals,
    )
    out = compute_corporatedonors_signals("___NONEXISTENT___",
                                            date(2024, 6, 1))
    assert out == {}


def test_batch528_donors_returns_dict_with_expected_keys(monkeypatch):
    from backtest.signals import congressional_alt_data as mod
    fake = pd.DataFrame({
        "Ticker":             ["ZZZZ"] * 4,
        "TransactionDate":    pd.to_datetime([
            "2024-01-15", "2024-03-15", "2024-05-15", "2024-09-15"]),
        "TransactionAmount":  [1000, 2500, 5000, 9999],
        "CommitteeName":      ["PAC A", "PAC B", "PAC A", "PAC C"],
    })
    monkeypatch.setattr(mod, "_DONORS_DF_CACHE", fake)
    # as_of = July 1 -> 3 rows in window (last is excluded)
    out = mod.compute_corporatedonors_signals("ZZZZ", date(2024, 7, 1))
    assert out["corp_donations_count_1y"] == 3
    assert out["corp_donations_1y"] == pytest.approx(8500.0)
    assert out["corp_donations_unique_pacs"] == 2


def test_batch528_donors_respects_lookback_window(monkeypatch):
    """Rows older than lookback_days are excluded."""
    from backtest.signals import congressional_alt_data as mod
    fake = pd.DataFrame({
        "Ticker":             ["ZZZZ"] * 2,
        "TransactionDate":    pd.to_datetime(["2022-01-15", "2024-05-15"]),
        "TransactionAmount":  [1000, 5000],
        "CommitteeName":      ["PAC A", "PAC B"],
    })
    monkeypatch.setattr(mod, "_DONORS_DF_CACHE", fake)
    out = mod.compute_corporatedonors_signals("ZZZZ", date(2024, 6, 1),
                                                lookback_days=365)
    # 2022 row is > 365d before as_of -> excluded
    assert out["corp_donations_count_1y"] == 1
    assert out["corp_donations_1y"] == pytest.approx(5000.0)


# ---------------------------------------------------------------------------
# Wire-in regression guard
# ---------------------------------------------------------------------------

def test_batch528_all_4_p16_producers_wired_in_screener():
    """All 4 P16 sub-feeds must be referenced in screener.py
    (housetrading + gov_contracts from Batch 473; lobbying from
    Batch 480; patentmomentum + offexchange + corporatedonors from
    Batch 528). Drift here means a producer became unwired silently."""
    text = (REPO / "backtest" / "signals" / "screener.py").read_text(
        encoding="utf-8")
    required = [
        "compute_housetrading_signals",
        "compute_gov_contracts_signals",
        "compute_lobbying_signals",
        "compute_patentmomentum_signals",
        "compute_offexchange_signals",
        "compute_corporatedonors_signals",
    ]
    missing = [name for name in required if name not in text]
    assert not missing, (
        f"P16 producers missing wire-in: {missing}. Re-add the silent-"
        f"failure-logger try/except blocks in screen_instrument."
    )


def test_batch528_silent_failure_pattern_used_for_all_3_new_producers():
    """Each new producer must be guarded by `_log_silent_producer_failure`
    so a runtime error doesn't crash the screener inner loop."""
    text = (REPO / "backtest" / "signals" / "screener.py").read_text(
        encoding="utf-8")
    for name in ("patentmomentum", "offexchange", "corporatedonors"):
        assert f'_log_silent_producer_failure("{name}"' in text, (
            f"{name} producer not guarded by silent-failure logger -- "
            f"add the try/except + log call per Batch 458 convention."
        )
