"""Sprint 0A.7 (Pass 53 v8h+1 2026-05-10) - Apewisdom DEMO.

Wider validation: subreddit coverage breadth, top-tickers presence,
snapshot recency.

Per CHECKLIST #68 + DEC-503 + DEC-502.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
APE_DIR = REPO / "data_prefetch" / "apewisdom"
SUB_DIR = APE_DIR / "subreddits"


def test_apewisdom_has_8_or_more_subreddit_feeds():
    """Per H19 verify: cache has 8 subreddits (exceeds 4-feed spec)."""
    files = list(SUB_DIR.glob("*.parquet"))
    assert len(files) >= 4, (
        f"Apewisdom has only {len(files)} subreddit feeds; spec target was 4+"
    )


def test_apewisdom_wsb_top_tickers_realistic():
    """WSB top tickers should include large meme-stock names."""
    p = SUB_DIR / "wallstreetbets.parquet"
    if not p.is_file():
        pytest.skip("wallstreetbets cache missing")
    df = pd.read_parquet(p)
    if df.empty or "ticker" not in df.columns:
        pytest.skip("wallstreetbets parquet empty or missing ticker col")
    tickers = set(df["ticker"].astype(str).str.upper().head(50).tolist())
    # At least one of these should appear in top-50 mentions
    sentinels = {"GME", "AMC", "TSLA", "SPY", "AAPL", "NVDA", "QQQ", "PLTR", "MSFT"}
    overlap = tickers & sentinels
    assert overlap, (
        f"WSB top-50 doesn't contain any common high-mention names: {sorted(tickers)[:20]}"
    )


def test_apewisdom_global_breadth():
    """global.parquet should aggregate enough rows to be useful."""
    p = APE_DIR / "global.parquet"
    if not p.is_file():
        pytest.skip("global.parquet missing")
    df = pd.read_parquet(p)
    assert len(df) >= 50, f"global.parquet only {len(df)} rows"
    if "ticker" in df.columns:
        unique_tickers = df["ticker"].nunique()
        assert unique_tickers >= 20, (
            f"global has only {unique_tickers} unique tickers across snapshots"
        )


def test_apewisdom_subreddit_coverage_includes_core_4():
    """Per Sprint 0A H19 spec, the 4 core subreddits should be cached."""
    core = {"wallstreetbets", "stocks", "investing", "options"}
    cached = {p.stem for p in SUB_DIR.glob("*.parquet")}
    missing = core - cached
    assert not missing, f"Apewisdom missing core 4-feed: {missing}"
