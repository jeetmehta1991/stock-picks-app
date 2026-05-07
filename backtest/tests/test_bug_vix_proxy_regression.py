"""Regression tests for BUG-VIX-PROXY (Pass 53 Day-9 v8).

Pinning the fix from H3 finding: when ^VIX OHLCV cache is missing, prior code
fell back to VXX ETF and fed its dollar price ($113 in mid-2023) into the
classifier as if it were VIX index points, classifying every day as crisis.

Fix Options A+B+C+D landed together:
  A) Prefetch ^VIX into cache (Codespaces script unchanged)
  B) VXX scale safeguard — if VXX is the only source, classifier uses 30-day
     return-vol instead of raw price
  C) FRED VIXCLS series prefetched into ``data_prefetch/fred/observations/``
     and read by macro.py first (canonical priority)
  D) Fail-loud warning when no canonical VIX source available

These tests guard against future regressions.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
FRED_VIX = REPO_ROOT / "data_prefetch" / "fred" / "observations" / "VIXCLS.parquet"


def _have_fred_vix() -> bool:
    return FRED_VIX.exists()


@pytest.mark.skipif(not _have_fred_vix(),
                    reason="FRED VIXCLS not prefetched — run scripts/prefetch_macro.py")
def test_bug_vix_proxy_fred_vixcls_present_and_real_scale():
    """FRED VIXCLS must be prefetched and on the VIX-index scale, not VXX-price scale.

    VIX index typically ranges 9-90 over 2020-2026. VXX ETN price ranges $20-$130
    over the same period. If our 'VIX' data has values >= 100 routinely, we are
    silently reading VXX prices and the regime classifier is broken.
    """
    df = pd.read_parquet(FRED_VIX)
    assert "value" in df.columns
    assert len(df) > 1000, f"VIXCLS too short ({len(df)} rows) — re-run prefetch"

    p99 = df["value"].quantile(0.99)
    median = df["value"].median()

    # Sanity bounds — VIX has never closed above 100 in history; median is ~17-18
    assert p99 < 100, (
        f"VIX p99 = {p99:.1f} suggests VXX-price corruption (VIX-index never > 100). "
        f"BUG-VIX-PROXY regression."
    )
    assert 8 < median < 35, (
        f"VIX median = {median:.1f} outside historical band (~14-25). "
        f"Likely BUG-VIX-PROXY regression or wrong series ID."
    )


@pytest.mark.skipif(not _have_fred_vix(),
                    reason="FRED VIXCLS not prefetched — run scripts/prefetch_macro.py")
def test_bug_vix_proxy_get_vix_returns_real_index_scale():
    """get_vix() must return real VIX-index values across known calm/stress dates."""
    from backtest.data.macro import get_vix

    # Calm 2023: VIX 12-22 historically
    df = get_vix(date(2023, 6, 1), date(2023, 6, 30), as_of=date(2023, 6, 30))
    assert not df.empty, "get_vix returned empty — FRED prefetch may be unreadable"
    last_v = float(df["vix"].iloc[-1])
    assert 8 < last_v < 30, (
        f"Jun 2023 VIX={last_v:.2f} outside known calm band (12-22). "
        f"BUG-VIX-PROXY regression — likely reading VXX price instead."
    )

    # COVID crash 2020: VIX peaked 82.7 on Mar 16 2020
    df_covid = get_vix(date(2020, 3, 15), date(2020, 3, 25), as_of=date(2020, 3, 25))
    if not df_covid.empty:
        peak = float(df_covid["vix"].max())
        assert peak > 50, f"COVID peak VIX={peak:.1f} too low — wrong data source"


@pytest.mark.skipif(not _have_fred_vix(),
                    reason="FRED VIXCLS not prefetched — run scripts/prefetch_macro.py")
def test_bug_vix_proxy_regime_varies_across_year():
    """Regime classification must produce more than just 'crisis' over a year of
    real history. Pre-fix H3 finding: 100% of 2023 classified as crisis.
    """
    from backtest.data.macro import macro_snapshot
    from backtest.engine.regime_filter import classify_regime

    sample_dates = [
        date(2023, 1, 16),  date(2023, 3, 15),  date(2023, 5, 15),
        date(2023, 7, 17),  date(2023, 9, 15),  date(2023, 11, 15),
    ]
    regimes_with_spy_up = set()
    regimes_with_spy_down = set()
    for d in sample_dates:
        m = macro_snapshot(d)
        v = m.get("vix_value")
        regimes_with_spy_up.add(classify_regime(v, True))
        regimes_with_spy_down.add(classify_regime(v, False))

    # 2023 was calm-bull → with SPY above 200EMA we expect bull, with SPY below we expect neutral
    assert regimes_with_spy_up != {"crisis"}, (
        f"Engine regime path classified all 2023 dates as crisis — BUG-VIX-PROXY regression. "
        f"Got {regimes_with_spy_up}"
    )


def test_bug_vix_proxy_classifier_thresholds_unchanged():
    """Sanity: classify_regime thresholds must not have been weakened to mask the bug."""
    from backtest.engine.regime_filter import classify_regime

    # Thresholds (per DEC-316): crisis>=40, bear>=30+SPY-down, bull<20+SPY-up, else neutral
    assert classify_regime(45.0, True) == "crisis"
    assert classify_regime(45.0, False) == "crisis"
    assert classify_regime(35.0, False) == "bear"
    assert classify_regime(13.0, True) == "bull"
    assert classify_regime(25.0, True) == "neutral"
    assert classify_regime(None, True) == "unknown"  # DEC-316 fail-closed
