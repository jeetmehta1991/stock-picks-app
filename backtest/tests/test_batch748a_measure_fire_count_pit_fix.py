# Source: B748a + owner approval 2026-06-13 "Approved measure_fire_count.py per-bar or per-year PIT filter" per CHECKLIST #77
"""B748a pin tests: measure_fire_count.py PIT-discipline fix.

PER S4-B747 FINDING + owner approval 2026-06-13: the prior
`tickers_full = _load_t1a_tickers(end)` call applied the PIT filter at the
END date, silently excluding the 111 historical-removed names. B748a
replaced it with `_load_t1a_tickers_union_over_window(start, end)` which
returns the UNION of all T1a tickers PIT-active at any point in the window.

Per-bar PIT is enforced implicitly: OHLCV parquets for delisted names end
at the removal date, so the per-bar loop naturally stops computing signals
past that point.

These pins lock the post-B748a behavior + guard against regression.
"""
from __future__ import annotations

from datetime import date

from scripts.measure_fire_count import (
    _load_t1a_tickers,
    _load_t1a_tickers_union_over_window,
)


# -------------------------------------------------------------------------
# Window-union loader invariants
# -------------------------------------------------------------------------
def test_b748a_pin1_window_union_returns_614_for_full_window():
    """Full T1a window [2020-01-01, 2026-05-31] should yield all 614 T1a
    members (503 currently-active + 111 historical-removed).
    """
    tickers = _load_t1a_tickers_union_over_window(
        date(2020, 1, 1), date(2026, 5, 31)
    )
    assert len(tickers) == 614, f"expected 614 union; got {len(tickers)}"


def test_b748a_pin2_window_union_strictly_superset_of_end_snapshot():
    """The window-union universe must be a STRICT SUPERSET of the END-snapshot
    universe (the prior PIT-INCORRECT behavior). Concretely: 614 vs 503;
    delta = 111 historical-removed names.
    """
    start, end = date(2020, 1, 1), date(2026, 5, 31)
    end_snap = set(_load_t1a_tickers(end))
    union = set(_load_t1a_tickers_union_over_window(start, end))
    assert union > end_snap, "window-union must be strict superset of end-snapshot"
    added = union - end_snap
    assert len(added) == 111, (
        f"expected 111 names added by window-union; got {len(added)}"
    )


def test_b748a_pin3_window_union_includes_known_historical_removed_names():
    """Spot-check: known M&A absorbed + index-rotation names that were in
    T1a during the window must appear in the union.
    """
    union = set(_load_t1a_tickers_union_over_window(
        date(2020, 1, 1), date(2026, 5, 31)
    ))
    expected_historical = {
        "AAL",   # AAL removed 2024-09-23
        "AAP",   # Advance Auto Parts removed 2023-08-25
        "ABMD",  # Abiomed removed 2022-12-22 (J&J acquisition)
        "ALK",   # Alaska Air removed 2023-12-18
        "ALXN",  # Alexion removed 2021-07-21 (AstraZeneca acquisition)
    }
    missing = expected_historical - union
    assert not missing, f"window-union missing known historical names: {missing}"


def test_b748a_pin4_window_union_excludes_tickers_with_removal_before_start():
    """Tickers removed before the window START should NOT appear (they were
    not active during any bar of the measurement window).

    Sanity probe: choose a window AFTER the removal of AAL (2024-09-23) +
    confirm AAL is NOT in the union.
    """
    post_aal = _load_t1a_tickers_union_over_window(
        date(2025, 1, 1), date(2026, 5, 31)
    )
    assert "AAL" not in post_aal, (
        "AAL removed 2024-09-23; window starts 2025-01-01 -- AAL must be excluded"
    )


def test_b748a_pin5_window_union_is_sorted_for_deterministic_sharding():
    """B694 AWS sharding splits the ticker list by index; the loader must
    return sorted output so shard membership is deterministic across runs.
    """
    tickers = _load_t1a_tickers_union_over_window(
        date(2020, 1, 1), date(2026, 5, 31)
    )
    assert tickers == sorted(tickers), "loader must return sorted ticker list"


def test_b748a_pin6_single_as_of_loader_retained():
    """The legacy `_load_t1a_tickers(as_of)` single-as_of loader is retained
    for tests + per-snapshot probes; B748a only changes the production caller.
    Sanity check it still works.
    """
    end_snap = _load_t1a_tickers(date(2026, 5, 31))
    assert len(end_snap) > 400, f"end-snapshot loader broken: got {len(end_snap)} tickers"
    assert len(end_snap) == 503, f"expected 503 end-snapshot; got {len(end_snap)}"


def test_b748a_pin7_window_union_handles_zero_length_window():
    """Degenerate single-day window: the union should still return at least the
    end-snapshot. This is a defensive pin for future callers that pass
    start == end.
    """
    same = _load_t1a_tickers_union_over_window(
        date(2026, 5, 31), date(2026, 5, 31)
    )
    # The window-overlap mask filters removed > start, so removed_date == 2026-05-31
    # would be excluded. End-snapshot is 503; this should be >= 503.
    assert len(same) >= 500, f"degenerate single-day window broke: got {len(same)} tickers"
