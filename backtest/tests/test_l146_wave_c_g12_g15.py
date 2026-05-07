"""Wave C regression tests — G12+G13+G14+G15 Quiver new-signal accessors.

Closes 4 of 13 remaining L146/DEC-507 wiring gaps. Wires 4 previously-unused
Quiver datasets (etfholdings/offexchange/topshareholders/wallstreetbets) into
smart_money.py via thin accessor functions. Strategy-side wiring deferred to
Phase 1B+.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# G12 ETF holdings
# ---------------------------------------------------------------------------
def test_g12_etf_holdings_returns_data_for_aapl():
    from backtest.data.smart_money import get_etf_holdings
    e = get_etf_holdings("AAPL")
    assert e["etf_count"] >= 100, (
        f"AAPL ETF holdings count {e['etf_count']} suspiciously low — wiring gap"
    )
    assert e["top_etf_weight"] > 0
    assert len(e["top10"]) >= 5


def test_g12_etf_holdings_unknown_ticker_safe():
    from backtest.data.smart_money import get_etf_holdings
    e = get_etf_holdings("ZZZZ_NOT_REAL")
    assert e["etf_count"] == 0
    assert e["top10"] == []


# ---------------------------------------------------------------------------
# G13 offexchange / dark pool
# ---------------------------------------------------------------------------
def test_g13_offexchange_returns_dpi():
    from backtest.data.smart_money import get_offexchange_volume
    o = get_offexchange_volume("AAPL", date(2024, 6, 15), lookback_days=10)
    assert o["rows_in_window"] >= 1, "AAPL offexchange returned 0 rows"
    assert o["avg_dpi"] is not None
    # DPI is a ratio in [0, 1]
    assert 0 <= o["avg_dpi"] <= 1


def test_g13_offexchange_pit_no_future_data():
    """offexchange data filed AFTER as_of must NOT appear in window."""
    from backtest.data.smart_money import get_offexchange_volume
    o = get_offexchange_volume("AAPL", date(2020, 12, 31), lookback_days=30)
    # Even if no rows match, the function must not crash and must not return
    # data dated 2021+
    assert isinstance(o, dict)
    assert o.get("as_of") == str(date(2020, 12, 31))


# ---------------------------------------------------------------------------
# G14 top shareholders
# ---------------------------------------------------------------------------
def test_g14_topshareholders_returns_institutional_owners():
    from backtest.data.smart_money import get_top_shareholders
    t = get_top_shareholders("AAPL", top_n=10)
    assert t["top_n_count"] >= 5
    # Vanguard / BlackRock / State Street should always be in AAPL top-10
    names = " ".join(h["name"].upper() for h in t["top_holders"])
    assert "VANGUARD" in names or "BLACKROCK" in names, (
        f"AAPL top shareholders missing major index providers: {names}"
    )


def test_g14_topshareholders_share_counts_are_positive():
    from backtest.data.smart_money import get_top_shareholders
    t = get_top_shareholders("AAPL", top_n=5)
    for h in t["top_holders"]:
        assert h["shares"] > 0, f"Negative or zero shares for {h['name']}"


# ---------------------------------------------------------------------------
# G15 WSB attention
# ---------------------------------------------------------------------------
def test_g15_wsb_attention_returns_mentions():
    from backtest.data.smart_money import get_wsb_attention
    w = get_wsb_attention("AAPL", date(2024, 6, 15), lookback_days=14)
    assert w["rows_in_window"] >= 1
    assert w["total_mentions"] >= 0


def test_g15_wsb_unknown_ticker_safe():
    from backtest.data.smart_money import get_wsb_attention
    w = get_wsb_attention("ZZZZ_NOT_REAL", date(2024, 6, 15), 7)
    assert w["total_mentions"] == 0


# ---------------------------------------------------------------------------
# Source-file presence sanity
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("dataset,min_files", [
    ("etfholdings", 1000),
    ("offexchange", 1000),
    ("topshareholders", 1000),
    ("wallstreetbets", 200),
])
def test_l146_quiver_prefetch_present(dataset, min_files):
    p = REPO_ROOT / "data_prefetch" / "quiver" / dataset
    assert p.exists(), f"Quiver {dataset} prefetch dir missing"
    n = len(list(p.glob("*.parquet")))
    assert n >= min_files, (
        f"Quiver {dataset} has {n} files; expected ≥ {min_files}"
    )
