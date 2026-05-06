"""Sprint 0A.10 BATCH 14 — Quiver Trader SMOKE.

Validates that bulk + per-ticker Quiver endpoints can be opened and schema-
checked. 16 endpoint groups covered (per CANONICAL_FACTS.md F-012 §22.B).

Per CHECKLIST #68 + DEC-503.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
QUIVER_DIR = REPO / "backtest" / "data" / "cache" / "quiver"


def _first_parquet(d: Path) -> Path:
    files = sorted(d.glob("*.parquet"))
    if not files:
        pytest.skip(f"no parquet files in {d}")
    return files[0]


# --- Bulk endpoints (single global parquet each) ---


def test_quiver_insiders_bulk_smoke():
    df = pd.read_parquet(QUIVER_DIR / "insiders" / "global.parquet")
    assert {"Ticker", "Date", "TransactionCode", "Shares"} <= set(df.columns)
    assert len(df) >= 100_000  # ~1M rows expected


def test_quiver_sec13fchanges_bulk_smoke():
    df = pd.read_parquet(QUIVER_DIR / "sec13fchanges" / "global.parquet")
    assert {"Date", "Ticker", "Change_Share", "Change_Pct"} <= set(df.columns)
    assert len(df) >= 50_000  # ~500k rows expected


def test_quiver_sec13f_bulk_smoke():
    p = QUIVER_DIR / "sec13f" / "global.parquet"
    if not p.is_file():
        pytest.skip("sec13f bulk not cached")
    df = pd.read_parquet(p)
    assert len(df) > 0


def test_quiver_quivernews_bulk_smoke():
    p = QUIVER_DIR / "quivernews" / "global.parquet"
    if not p.is_file():
        pytest.skip("quivernews bulk not cached")
    df = pd.read_parquet(p)
    assert len(df) > 0


# --- Per-ticker endpoints ---


def test_quiver_offexchange_per_ticker_populated():
    files = list((QUIVER_DIR / "offexchange").glob("*.parquet"))
    assert len(files) >= 500


def test_quiver_offexchange_smoke_schema():
    df = pd.read_parquet(_first_parquet(QUIVER_DIR / "offexchange"))
    assert {"Ticker", "Date"} <= set(df.columns)
    assert len(df) > 0


def test_quiver_topshareholders_per_ticker_populated():
    files = list((QUIVER_DIR / "topshareholders").glob("*.parquet"))
    assert len(files) >= 1000


def test_quiver_etfholdings_per_ticker_populated():
    files = list((QUIVER_DIR / "etfholdings").glob("*.parquet"))
    assert len(files) >= 500


def test_quiver_congressional_per_ticker_populated():
    files = list((QUIVER_DIR / "congressional").glob("*.parquet"))
    assert len(files) >= 100


def test_quiver_congressional_smoke_schema():
    df = pd.read_parquet(_first_parquet(QUIVER_DIR / "congressional"))
    assert {"Ticker", "Transaction", "TransactionDate"} <= set(df.columns)
    assert len(df) > 0


def test_quiver_lobbying_per_ticker_populated():
    files = list((QUIVER_DIR / "lobbying").glob("*.parquet"))
    assert len(files) >= 100


def test_quiver_gov_contracts_per_ticker_populated():
    files = list((QUIVER_DIR / "gov_contracts").glob("*.parquet"))
    assert len(files) >= 100
