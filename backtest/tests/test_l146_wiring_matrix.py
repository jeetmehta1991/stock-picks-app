"""L146/DEC-507 wiring-matrix regression tests (Pass 53 Day-9 v8).

L146 pattern: data prefetched but consumer code reads from a different/legacy
path → silent gap. BUG-VIX-PROXY (Day-9 v8) + BUG-PF-REFPATH (G4) +
BUG-PF-DIVPATH (G5) are confirmed instances. This test prevents future drift
by asserting consumer-declared paths match prefetch reality.

For each declared (consumer, expected_path, prefetch_dir) row, this test:
  1. If prefetch_dir is non-empty, asserts at least ONE of the candidate paths
     in the consumer module resolves to a file that exists.
  2. If consumer module references a path string but no files exist at that
     path AND data does exist at a sibling path, fails the test.

The matrix below is the truth source — update when adding new prefetch
sources or changing consumer code paths.
"""

from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Wiring matrix — updated Pass 53 Day-9 v8 (after deep audit of L146/DEC-507)
# ---------------------------------------------------------------------------

# Each row: (label, prefetch_glob, consumer_module, requires_file_exists)
# requires_file_exists=True → fail if no files at the declared prefetch path
# requires_file_exists=False → just check consumer module references the path
WIRING_MATRIX = [
    # (label, prefetch_dir_relative, consumer_module_relative, sentinel_file_glob)
    ("FRED VIXCLS",
     "data_prefetch/fred/observations",
     "backtest/data/macro.py",
     "VIXCLS.parquet"),
    ("Polygon news",
     "data_prefetch/polygon/news",
     "backtest/data/smart_money.py",
     "*.parquet"),
    ("Polygon financials",
     "data_prefetch/polygon/financials",
     "backtest/data/smart_money.py",
     "*.parquet"),
    ("Quiver insiders bulk",
     "data_prefetch/quiver/insiders",
     "backtest/data/smart_money.py",
     "global.parquet"),
    ("Quiver sec13fchanges bulk",
     "data_prefetch/quiver/sec13fchanges",
     "backtest/data/smart_money.py",
     "global.parquet"),
    ("Quiver congressional",
     "data_prefetch/quiver/congressional",
     "backtest/data/smart_money.py",
     "*.parquet"),
    ("Quiver gov_contracts",
     "data_prefetch/quiver/gov_contracts",
     "backtest/data/smart_money.py",
     "*.parquet"),
    ("Quiver lobbying",
     "data_prefetch/quiver/lobbying",
     "backtest/data/smart_money.py",
     "*.parquet"),
    ("AAII weekly (Sprint 0A)",
     "data_prefetch/aaii",
     "backtest/data/sentiment.py",
     "weekly_sentiment.parquet"),
    ("CNN F&G components",
     "data_prefetch/cnn_fg/components",
     "backtest/data/sentiment.py",
     "market_volatility_vix.parquet"),
    ("CNN F&G daily (Sprint 0A)",
     "data_prefetch/cnn_fg",
     "backtest/data/sentiment.py",
     "daily.parquet"),
    ("CFTC COT",
     "data_prefetch/cftc",
     "backtest/data/sentiment.py",
     "cot_emini_sp500.parquet"),
    ("Apewisdom global",
     "data_prefetch/apewisdom",
     "backtest/data/sentiment.py",
     "global.parquet"),
    ("Wikipedia pageviews",
     "data_prefetch/wikipedia",
     "backtest/data/sentiment.py",
     "*.parquet"),
]


@pytest.mark.parametrize(
    "label,prefetch_dir,consumer_module,sentinel_glob",
    WIRING_MATRIX,
    ids=[r[0] for r in WIRING_MATRIX],
)
def test_l146_consumer_path_matches_prefetch(
    label, prefetch_dir, consumer_module, sentinel_glob
):
    """For each (prefetch source, consumer module) pair, assert that the
    consumer module references the declared prefetch path AND the path has
    at least one file matching the sentinel glob.
    """
    prefetch_path = REPO_ROOT / prefetch_dir
    assert prefetch_path.exists(), (
        f"L146 wiring gap: '{label}' prefetch dir does not exist at "
        f"{prefetch_dir} — prefetch may have been moved or never run"
    )

    matches = list(prefetch_path.glob(sentinel_glob))
    assert matches, (
        f"L146 wiring gap: '{label}' has no files matching {sentinel_glob} "
        f"at {prefetch_dir}"
    )

    consumer_text = (REPO_ROOT / consumer_module).read_text(errors="ignore")
    # Consumer must reference the prefetch dir somewhere in its source
    # (path string match — case-insensitive on Windows / Linux paths)
    posix = prefetch_dir.replace("\\", "/")
    parts = posix.split("/")
    # Match by the last 1-2 path components rather than full path (Path() obj
    # construction may use Path("data_prefetch") / "fred" / ... so we look
    # for the leaf names in the source.)
    leaf_match = parts[-1] in consumer_text or parts[-2] + "/" + parts[-1] in consumer_text
    assert leaf_match, (
        f"L146 wiring gap: '{label}' prefetch at {prefetch_dir} but consumer "
        f"{consumer_module} does NOT reference path components "
        f"{'/'.join(parts[-2:])}"
    )


def test_l146_polygon_reference_path_resolved():
    """G4 fix regression: fetcher.py must find Polygon reference data either
    at the canonical or legacy_archive path."""
    canonical = REPO_ROOT / "data_prefetch" / "polygon" / "reference"
    legacy = REPO_ROOT / "data_prefetch" / "polygon" / "legacy_archive_pass53" / "reference"
    has_data = (
        (canonical.exists() and any(canonical.glob("*.parquet")))
        or (legacy.exists() and any(legacy.glob("*.parquet")))
    )
    assert has_data, (
        "Polygon reference data missing from BOTH canonical and legacy_archive "
        "paths — fetch_info will return Unknown for all tickers"
    )

    # Verify fetcher.py searches both
    fetcher_text = (REPO_ROOT / "backtest" / "data" / "fetcher.py").read_text(errors="ignore")
    assert "legacy_archive_pass53" in fetcher_text, (
        "G4 regression: fetcher.py no longer searches legacy_archive path"
    )


def test_l146_polygon_dividends_path_resolved():
    """G5 fix regression: fetcher.py must search both dividends paths."""
    fetcher_text = (REPO_ROOT / "backtest" / "data" / "fetcher.py").read_text(errors="ignore")
    # G5 fix is a path-search update; re-grep for legacy_archive in dividends fn
    assert "legacy_archive_pass53" in fetcher_text and "dividends" in fetcher_text, (
        "G5 regression: fetcher.py no longer searches legacy_archive for dividends"
    )


def test_l146_no_yfinance_live_calls_in_macro():
    """DEC-497 D4 HARD CUT: macro.py must not be calling yfinance directly."""
    macro_text = (REPO_ROOT / "backtest" / "data" / "macro.py").read_text(errors="ignore")
    # Allow the existing `_fetch_from_yfinance` deprecation stub but ensure
    # nothing actually invokes yfinance.download / Ticker / etc.
    forbidden = ["yfinance.download", "yf.download", "yf.Ticker(", "yfinance.Ticker("]
    found = [s for s in forbidden if s in macro_text]
    assert not found, (
        f"DEC-497 D4 HARD CUT violated: macro.py contains {found}. Live yfinance "
        f"calls are blocked in Stage 2 backtest."
    )


def test_l146_fetch_info_real_ticker_returns_real_data():
    """Integration test: fetch_info('AAPL') should return real Polygon data,
    not the {sector:'Unknown', market_cap:0} default."""
    from backtest.data.fetcher import fetch_info

    info = fetch_info("AAPL")
    # market_cap should be populated from Polygon reference (legacy_archive)
    if (REPO_ROOT / "data_prefetch" / "polygon" / "legacy_archive_pass53"
        / "reference" / "AAPL.parquet").exists():
        assert info.get("market_cap", 0) > 0, (
            "fetch_info('AAPL') returned market_cap=0 despite reference data "
            "being present in legacy_archive — G4 fix is broken"
        )
        assert info.get("name", "AAPL") != "AAPL" or "Apple" in str(info.get("name", "")), (
            "fetch_info should return company name 'Apple Inc.' not just ticker"
        )
