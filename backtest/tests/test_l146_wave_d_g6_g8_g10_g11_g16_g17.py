"""Wave D regression tests — G6 + G8 + G10 + G11 + G16 + G17 (Pass 53 Day-9 v8c).

Closes 6 of 13 remaining L146/DEC-507 wiring gaps:
  G6  Polygon events (ticker_change history)         — fetcher.get_ticker_change_history
  G8  pytrends search-volume index                    — sentiment.get_search_attention
  G10 Quiver insider per-ticker fast path             — smart_money.get_insider_transactions_pertkr
  G11 Quiver institutional per-ticker (documented incomplete)
                                                      — smart_money.get_institutional_holdings_pertkr
  G16 Quiver wikipedia mirror (documented broken; not wired — separate
       data_prefetch/wikipedia/ already consumed; Quiver mirror is empty)
  G17 Quiver micro-datasets — patentmomentum / corporatedonors / sec13f bulk:
       smart_money.get_patent_momentum / get_corporate_donations / get_sec13f_holdings
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# G6 ticker_change_history
# ---------------------------------------------------------------------------
def test_g6_ticker_change_history_aapl():
    from backtest.data.fetcher import get_ticker_change_history
    events = get_ticker_change_history("AAPL")
    assert len(events) >= 1
    # AAPL had a 2003 ticker_change event in the prefetch
    assert events[0]["event_type"] == "ticker_change"
    assert events[0]["event_date"] == "2003-09-10"


def test_g6_ticker_change_unknown_ticker_safe():
    from backtest.data.fetcher import get_ticker_change_history
    assert get_ticker_change_history("ZZZZ_NOT_REAL") == []


# ---------------------------------------------------------------------------
# G8 search_attention (pytrends)
# ---------------------------------------------------------------------------
def test_g8_search_attention_aapl():
    from backtest.data.sentiment import get_search_attention
    s = get_search_attention("AAPL", date(2024, 6, 15), lookback_days=30)
    assert s["rows_in_window"] >= 1
    assert 0 <= s["avg_svi"] <= 100
    assert s["trend"] in {"rising", "falling", "flat", "unknown"}


def test_g8_search_attention_unknown_safe():
    from backtest.data.sentiment import get_search_attention
    s = get_search_attention("ZZZZ_NOT_REAL", date(2024, 6, 15), 30)
    assert s["avg_svi"] is None
    assert s["rows_in_window"] == 0


# ---------------------------------------------------------------------------
# G10 insider per-ticker fast path
# ---------------------------------------------------------------------------
def test_g10_insider_per_ticker_returns_data():
    from backtest.data.smart_money import get_insider_transactions_pertkr
    r = get_insider_transactions_pertkr("AAPL", date(2024, 12, 15), 90)
    assert r["rows_in_window"] >= 1
    assert r["source"] in {"per_ticker", "bulk"}
    assert r["buy_count"] >= 0 and r["sell_count"] >= 0


def test_g10_insider_unknown_ticker_safe():
    from backtest.data.smart_money import get_insider_transactions_pertkr
    r = get_insider_transactions_pertkr("ZZZZ_NOT_REAL", date(2024, 12, 15), 90)
    assert r["rows_in_window"] == 0


# ---------------------------------------------------------------------------
# G11 institutional per-ticker (documented as incomplete)
# ---------------------------------------------------------------------------
def test_g11_institutional_pertkr_warns_when_empty():
    from backtest.data.smart_money import get_institutional_holdings_pertkr
    r = get_institutional_holdings_pertkr("AAPL")
    # AAPL specifically is empty in per-ticker prefetch; warning must surface
    if not r["is_complete"]:
        assert r["warning"] is not None
        assert "institutional_signal" in r["warning"]


# ---------------------------------------------------------------------------
# G16 documented as broken; verify the assumption holds
# ---------------------------------------------------------------------------
def test_g16_quiver_wikipedia_mirror_documented_empty():
    """L146 audit found Quiver wikipedia mirror is empty for sampled tickers.
    This test asserts the documented state (so if the prefetch is fixed in
    future, the test fails loud and reminds us to wire it)."""
    qw = REPO_ROOT / "data_prefetch" / "quiver" / "wikipedia"
    if not qw.exists():
        pytest.skip("Quiver wikipedia mirror dir absent")
    files = list(qw.glob("*.parquet"))[:30]
    if not files:
        pytest.skip("Quiver wikipedia mirror has no files")
    import pandas as pd
    nonempty = 0
    for p in files:
        try:
            if len(pd.read_parquet(p)) > 0:
                nonempty += 1
        except Exception:
            pass
    # If most files are now non-empty, the prefetch was repaired and we should
    # wire it — fail loud.
    assert nonempty <= 5, (
        f"Quiver wikipedia mirror has {nonempty}/{len(files)} non-empty files; "
        f"prefetch may have been repaired — wire as a consumer or remove this test"
    )


# ---------------------------------------------------------------------------
# G17 micro-datasets
# ---------------------------------------------------------------------------
def test_g17a_patent_momentum_returns_value_within_coverage():
    """patentmomentum dataset only covers 2013-02 → 2022-01."""
    from backtest.data.smart_money import get_patent_momentum
    r = get_patent_momentum("AAPL", date(2021, 12, 15), 90)
    assert r["found"] is True
    assert isinstance(r["latest_momentum"], float)


def test_g17a_patent_momentum_unknown_ticker_safe():
    from backtest.data.smart_money import get_patent_momentum
    r = get_patent_momentum("ZZZZ_NOT_REAL", date(2021, 12, 15), 90)
    assert r["found"] is False


def test_g17b_corporate_donations_known_ticker():
    """PLUG (Plug Power) was in the corporatedonors sample row."""
    from backtest.data.smart_money import get_corporate_donations
    r = get_corporate_donations("PLUG")
    assert r["found"] is True
    assert r["total_donations_usd"] > 0


def test_g17b_corporate_donations_aapl_absent():
    """AAPL is not in the corporatedonors dataset (sample showed PLUG/ETR/STZ)."""
    from backtest.data.smart_money import get_corporate_donations
    r = get_corporate_donations("AAPL")
    assert r["found"] is False


def test_g17d_sec13f_holdings_returns_funds():
    """sec13f bulk has the LATEST 13F snapshot only (~2026-05). Use a date
    within bulk coverage."""
    from backtest.data.smart_money import get_sec13f_holdings
    r = get_sec13f_holdings("AAPL", date(2026, 5, 5))
    assert r["found"] is True
    assert r["fund_count"] > 100  # AAPL held by many funds
