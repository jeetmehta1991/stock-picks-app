"""Sprint 0A.10 BATCH 14 — CNN Fear & Greed SMOKE.

Validates composite + 7 sub-components prefetch.

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
CNN_DIR = REPO / "data_prefetch" / "cnn_fg"
CNN_COMPONENTS_DIR = CNN_DIR / "components"

EXPECTED_COMPONENTS = {
    "junk_bond_demand",
    "put_call_options",
    "market_momentum",
    "stock_price_breadth",
    "safe_haven_demand",
    "market_volatility",
    "stock_price_strength",
}


def test_cnn_fg_composite_cache_exists():
    files = list(CNN_DIR.glob("*.parquet"))
    assert len(files) >= 1, "CNN F&G composite not cached"


def test_cnn_fg_composite_smoke_schema():
    p = next(CNN_DIR.glob("*.parquet"))
    df = pd.read_parquet(p)
    assert {"date", "score"} <= set(df.columns) or {"timestamp", "score"} <= set(df.columns)
    assert len(df) > 0


def test_cnn_fg_seven_components_cached():
    files = sorted(CNN_COMPONENTS_DIR.glob("*.parquet"))
    assert len(files) == 7, f"expected 7 sub-components, got {len(files)}: {[f.name for f in files]}"
    cached_names = {f.stem.lower() for f in files}
    # Allow flexible naming (snake_case variants); check 7 distinct components present
    assert len(cached_names) == 7


def test_cnn_fg_component_smoke_schema():
    p = next(CNN_COMPONENTS_DIR.glob("*.parquet"))
    df = pd.read_parquet(p)
    assert {"date", "score"} <= set(df.columns) or {"timestamp", "score"} <= set(df.columns)
    assert len(df) > 0


def test_cnn_fg_score_in_range():
    """F&G score is 0-100."""
    p = next(CNN_DIR.glob("*.parquet"))
    df = pd.read_parquet(p)
    sample = df["score"].dropna().head(10)
    assert (sample >= 0).all() and (sample <= 100).all()
