"""Batch 344 (333b consumer) 2026-05-25: read multi-quarter institutional
persistence precompute + emit signals dict keys.

Source: data_prefetch/derived/institutional_persistence_t1a/{YYYY-01-01}.parquet
Producer script: scripts/build_institutional_persistence_precompute.py

Picks the most recent snapshot <= as_of so a backtest day uses the
quarterly-frozen persistence metrics that would have been observable
to a real-world quant on that date (PIT respect already embedded by
the producer's 45-day reporting lag filter).

No-op when precompute directory is missing or has no usable snapshot.

Yan-Zhang 2009 RFS: institutional persistence forecasts 1-3 month alpha.
Frazzini-Lamont 2008: cross-fund consensus over multiple quarters
distinguishes informed positioning from noise.
"""
from __future__ import annotations

from datetime import date as _date
from pathlib import Path
from typing import Optional

import pandas as pd


# S6-B2484: resolved through the SHARED helper the producer uses, so the
# two cannot drift. Untagged -> the production path, unchanged.
def _resolve_precompute_dir():
    import sys as _sys
    _root = Path(__file__).parent.parent.parent
    _sys.path.insert(0, str(_root / "scripts"))
    from build_institutional_persistence_precompute import (
        persistence_cache_dir as _pcd)
    return _pcd(_root)


_PRECOMPUTE_DIR = _resolve_precompute_dir()

# Module-level cache: dict[snapshot_iso] -> DataFrame keyed by ticker.
_CACHE: dict = {}
# Sorted list of (date, path) for snapshot enumeration; built once per session.
_SNAPSHOTS: Optional[list] = None


def _load_snapshots() -> list:
    """Enumerate persistence-precompute parquets at module level.

    Returns list of (snapshot_date, path) tuples sorted ascending.
    Empty list when precompute dir missing.
    """
    global _SNAPSHOTS
    if _SNAPSHOTS is not None:
        return _SNAPSHOTS
    if not _PRECOMPUTE_DIR.exists():
        _SNAPSHOTS = []
        return _SNAPSHOTS
    snaps = []
    for p in sorted(_PRECOMPUTE_DIR.glob("*.parquet")):
        try:
            d = _date.fromisoformat(p.stem)
            snaps.append((d, p))
        except ValueError:
            continue
    _SNAPSHOTS = snaps
    return _SNAPSHOTS


def _load_snapshot_df(snapshot_path: Path) -> pd.DataFrame:
    """Load a per-snapshot DataFrame, indexed by ticker for O(1) lookup.
    Module-cached by snapshot path."""
    key = str(snapshot_path)
    if key in _CACHE:
        return _CACHE[key]
    try:
        df = pd.read_parquet(snapshot_path)
        if not df.empty and "ticker" in df.columns:
            df = df.set_index("ticker")
        _CACHE[key] = df
    except Exception:
        _CACHE[key] = pd.DataFrame()
    return _CACHE[key]


def compute_persistence_signals(ticker: str, as_of: _date) -> dict:
    """Return per-ticker multi-quarter persistence signal dict.

    Keys returned (all absent when no usable data):
      persistent_holders_4q
      persistent_holders_8q
      avg_position_age_quarters
      committed_growth_holders
      total_active_holders
      institutional_persistence_strong   (bool; persistent_holders_4q >= 10)
      institutional_persistence_growing  (bool; committed_growth_holders >= 5)

    No-op when:
      - Precompute directory missing.
      - No snapshot <= as_of.
      - Ticker absent from the most recent eligible snapshot.
    """
    snaps = _load_snapshots()
    if not snaps:
        return {}
    # Pick most recent snapshot <= as_of
    eligible = [(d, p) for d, p in snaps if d <= as_of]
    if not eligible:
        return {}
    snap_date, snap_path = eligible[-1]
    df = _load_snapshot_df(snap_path)
    if df is None or df.empty or ticker not in df.index:
        return {}
    row = df.loc[ticker]
    # Handle multi-row case defensively (shouldn't happen but just in case)
    if isinstance(row, pd.DataFrame):
        row = row.iloc[0]
    p4q = int(row.get("persistent_holders_4q", 0) or 0)
    p8q = int(row.get("persistent_holders_8q", 0) or 0)
    avg_age = float(row.get("avg_position_age_quarters", 0) or 0)
    committed = int(row.get("committed_growth_holders", 0) or 0)
    active = int(row.get("total_active_holders", 0) or 0)
    return {
        "persistent_holders_4q":              p4q,
        "persistent_holders_8q":              p8q,
        "avg_position_age_quarters":          round(avg_age, 2),
        "committed_growth_holders":           committed,
        "total_active_holders":               active,
        "institutional_persistence_strong":   p4q >= 10,
        "institutional_persistence_growing":  committed >= 5,
    }
