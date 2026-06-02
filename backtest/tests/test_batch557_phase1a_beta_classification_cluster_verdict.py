"""Batch 557 (2026-06-02) -- Phase 1A-beta producer-zero forensic:
classification_change cluster verdict.

Source: per CHECKLIST #77, owner directive 2026-06-02 "C then A".
Queue: Phase 1A-beta producer-zero classification cluster.

Audit findings:
  - 10 classification_change_* strategies showed PRODUCER_LAYER_ZERO
    in the 2026-05-26 single-batch 1A-beta run.
  - Producer `get_classification_change_signals` is WIRED into
    screen_instrument (verified via grep).
  - Producer emits correct signal dict when ticker has a recent event.
  - Producer source data `Backtesting universe/sector_history.csv` has
    ONLY 2 reclassification events in our 2021+ backtest window:
      V  2023-03-17 (IT -> Financials)
      MA 2023-03-17 (IT -> Financials)
  - Both moves are OUT of growth sectors -> only enable
    classification_change_from_tech variant; the to_tech / to_defensive
    variants have zero eligible events by data.
  - Compound predicates (price_above_ema_200 / vol_spike / MACD / etc)
    further narrow the eligible bars within the 90-day V/MA windows.

Verdict: zero-fire is DATA-DRIVEN, not code-driven. No code change
in this batch. Action item surfaced for owner: expand
sector_history.csv with additional GICS reclassifications from
2021-2026 (S&P DJI press release primary; L88 manual-verification
discipline required). See SECTOR_HISTORY_EXPANSION TODO in
EXECUTION_QUEUE.md (added separately).

Pins:

  (1) Producer wires correctly into screener.screen_instrument
  (2) Producer emits expected key set for V on 2023-04-01 (within
      90d of 2023-03-17 reclassification)
  (3) Producer emits empty dict for AAPL (no event in sector_history)
  (4) All 10 classification_change_* strategy fns remain registered
  (5) sector_history.csv has the expected 2 events in 2021+ window
      (regression guard: if new events get added, this test reminds
      to re-audit the cluster's zero-fire status)
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest


def test_batch557_producer_wired_to_screener():
    """Producer function must be imported + called in
    screen_instrument (regression guard for the wiring)."""
    import inspect
    from backtest.signals import screener
    src = inspect.getsource(screener)
    assert "get_classification_change_signals" in src, (
        "screener must import the classification_change producer"
    )
    assert "get_classification_change_signals(ticker, as_of)" in src, (
        "screener must call the producer with (ticker, as_of)"
    )


def test_batch557_producer_emits_v_2023_reclassification():
    """V (Visa) moved IT -> Financials 2023-03-17. Producer should
    emit `classification_changed_recent=True` + `from_tech=True`
    for any as_of in [2023-03-17, 2023-06-15] (90d window)."""
    from backtest.data.universe import get_classification_change_signals
    out = get_classification_change_signals("V", date(2023, 4, 1))
    assert out, "producer should emit non-empty dict for V 2023-04-01"
    assert out["classification_changed_recent"] is True
    assert out["prior_sector"] == "Information Technology"
    assert out["new_sector"] == "Financials"
    assert out["classification_change_from_tech"] is True
    # NOT into growth/defensive (Financials is neither bucket)
    assert out["classification_change_to_tech"] is False
    assert out["classification_change_to_defensive"] is False


def test_batch557_producer_returns_empty_for_no_event_ticker():
    """AAPL has never been reclassified in our sector_history.csv.
    Producer must return empty dict on any as_of."""
    from backtest.data.universe import get_classification_change_signals
    out = get_classification_change_signals("AAPL", date(2023, 4, 1))
    assert out == {}, f"AAPL should return empty dict; got {out}"
    out2 = get_classification_change_signals("AAPL", date(2024, 1, 1))
    assert out2 == {}


def test_batch557_producer_window_expiry():
    """V's classification change was 2023-03-17. By 2023-07-01 (>90
    days), the producer should return empty (window expired)."""
    from backtest.data.universe import get_classification_change_signals
    out = get_classification_change_signals("V", date(2023, 7, 1))
    assert out == {}, f"V at 2023-07-01 should be window-expired; got {out}"


def test_batch557_ten_classification_strategies_registered():
    """All 10 classification_change_* strategy fns must remain
    registered. Regression guard against silent deprecation."""
    from backtest.signals import screener
    expected = [
        "strat_classification_change_recent_long",
        "strat_classification_change_to_tech_long",
        "strat_classification_change_to_defensive_short",
        "strat_classification_change_volume_long",
        "strat_classification_change_momentum_long",
        "strat_classification_change_from_tech_short",
        "strat_classification_change_breakout_long",
        "strat_classification_change_with_institutional_long",
        "strat_classification_change_with_insider_long",
        "strat_classification_change_oversold_long",
    ]
    missing = [n for n in expected if not hasattr(screener, n)]
    assert not missing, f"missing classification strategy fns: {missing}"


def test_batch557_sector_history_data_gap_pin():
    """Batch 561 update (2026-06-02): sector_history.csv expanded to
    cover the full 2023-03-17 GICS reclassification batch (13 of 14
    affected names; FLT excluded due to OHLCV cache rename gap).

    This pin documents the CURRENT count + tickers so a future
    expansion (e.g. adding individual 2024/2025/2026 reclassifications
    or restoring FLT after cache fix) prompts a cluster re-audit."""
    repo_root = Path(__file__).parent.parent.parent
    csv_path = repo_root / "Backtesting universe" / "sector_history.csv"
    if not csv_path.exists():
        pytest.skip("sector_history.csv absent")
    df = pd.read_csv(csv_path, comment="#")
    df["added_date"] = pd.to_datetime(df["added_date"], errors="coerce")
    events_2021_plus = df[df["added_date"] >= "2021-01-01"]
    n = len(events_2021_plus)
    # Batch 561 expansion: 13 tickers x 1 added_date row = 13 events.
    assert n == 13, (
        f"sector_history.csv has {n} events 2021+; expected 13 from "
        f"the 2023-03-17 batch (V/MA/PYPL/FISV/FIS/GPN/JKHY -> "
        f"Financials, ADP/PAYX/BR -> Industrials, TGT/DG/DLTR -> "
        f"Consumer Staples). If new events added: GOOD -- re-audit "
        f"the classification_change cluster's fire rates and update "
        f"this test pin."
    )
    expected_syms = {
        # IT -> Financials (7; FLT excluded per OHLCV cache gap)
        "V", "MA", "PYPL", "FISV", "FIS", "GPN", "JKHY",
        # IT -> Industrials (3)
        "ADP", "PAYX", "BR",
        # Consumer Discretionary -> Consumer Staples (3)
        "TGT", "DG", "DLTR",
    }
    syms = set(events_2021_plus["Symbol"].tolist())
    assert syms == expected_syms, (
        f"expected {expected_syms} in 2021+ window; got {syms}"
    )
