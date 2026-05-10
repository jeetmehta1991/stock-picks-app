"""Sprint 0A.7 (Pass 53 v8h+1 2026-05-10) - Apewisdom SMOKE.

Per-API smoke test for Apewisdom Reddit retail-attention prefetch.

Validates: cache exists, expected schema, smoke subreddit fixtures readable.

Per CHECKLIST #68 + DEC-503 + DEC-502.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
APE_DIR = REPO / "data_prefetch" / "apewisdom"
SUB_DIR = APE_DIR / "subreddits"

EXPECTED_COLS = {"rank", "ticker", "name", "mentions", "upvotes",
                 "rank_24h_ago", "mentions_24h_ago"}

SMOKE_SUBREDDITS = ["wallstreetbets", "stocks", "investing", "options"]


def test_apewisdom_cache_dir_exists():
    assert APE_DIR.is_dir(), f"Apewisdom cache dir missing: {APE_DIR}"


def test_apewisdom_global_parquet_exists():
    p = APE_DIR / "global.parquet"
    assert p.is_file(), "Apewisdom global.parquet missing"


def test_apewisdom_subreddit_dir_exists():
    assert SUB_DIR.is_dir(), f"Apewisdom subreddits dir missing: {SUB_DIR}"


@pytest.mark.parametrize("subreddit", SMOKE_SUBREDDITS)
def test_apewisdom_smoke_subreddit_present(subreddit: str):
    p = SUB_DIR / f"{subreddit}.parquet"
    assert p.is_file(), f"Apewisdom subreddit cache missing: {subreddit}"


@pytest.mark.parametrize("subreddit", SMOKE_SUBREDDITS)
def test_apewisdom_smoke_subreddit_schema(subreddit: str):
    p = SUB_DIR / f"{subreddit}.parquet"
    if not p.is_file():
        pytest.skip(f"Apewisdom {subreddit} cache missing")
    df = pd.read_parquet(p)
    missing = {"ticker", "name", "mentions"} - set(df.columns)
    assert not missing, f"Apewisdom {subreddit} missing core cols: {missing}"


def test_apewisdom_global_has_recent_snapshots():
    p = APE_DIR / "global.parquet"
    if not p.is_file():
        pytest.skip("global.parquet missing")
    df = pd.read_parquet(p)
    assert len(df) >= 50, (
        f"Apewisdom global only has {len(df)} rows; expected at least one full snapshot"
    )
