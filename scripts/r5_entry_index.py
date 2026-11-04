"""scripts/r5_entry_index.py (S6-B3397, B3139q-r187) - the R5 baseline's ENTRY
set, built once and cached, for the battery lenses that compare a landed
cube's graded leg with the baseline (runbook 2.4 item 19, step 1.5's
verify-on-completion and the verification table's redundancy row: census
lines 817, 1293 and 588).

The R5 cube (output_r5_merged_1_7/trade_exit_detail.csv, 1.64 GB) carries
one row per (entry x exit); a lens needs only WHICH entries each
registration took - (strategy, direction, ticker, entry_date). Reading the
full file per landing would cost a chunked 1.6 GB read every time, so the
distinct entries are written once beside the cube as _entry_index.parquet
with a stamp naming the source's size and mtime; a source that changes
rebuilds it, and an absent source is reported, never guessed (L642).
Reads entry KEYS only - no outcome, no holdout grade."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
KEY = ["strategy", "direction", "ticker", "entry_date"]


def _paths(source: Path) -> tuple[Path, Path]:
    return source.parent / "_entry_index.parquet", source.parent / "_entry_index.json"


def _stamp(source: Path) -> dict:
    st = source.stat()
    return {"source": source.name, "size": st.st_size, "mtime_ns": st.st_mtime_ns}


def load(source: Path | None = None) -> pd.DataFrame:
    """The distinct R5 entries, from the cache when its stamp matches the
    source's size and mtime, else rebuilt (chunked) and re-cached. Raises
    FileNotFoundError when the source is absent."""
    source = Path(source or SOURCE)
    if not source.exists():
        raise FileNotFoundError(f"R5 baseline cube absent at {source}")
    idx_p, stamp_p = _paths(source)
    want = _stamp(source)
    if idx_p.exists() and stamp_p.exists():
        try:
            got = json.loads(stamp_p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            got = {}
        if {k: got.get(k) for k in want} == want:
            return pd.read_parquet(idx_p)
    parts = [ch.drop_duplicates() for ch in
             pd.read_csv(source, usecols=KEY, dtype=str, chunksize=500_000)]
    idx = pd.concat(parts, ignore_index=True)
    idx["entry_date"] = idx["entry_date"].str[:10]
    idx = idx.drop_duplicates(ignore_index=True)
    tmp = idx_p.with_suffix(".parquet.tmp")
    idx.to_parquet(tmp, index=False)
    os.replace(tmp, idx_p)
    stamp_p.write_text(json.dumps({**want, "rows": int(len(idx))}), encoding="utf-8")
    return idx


def scope(idx: pd.DataFrame, tickers, start, end) -> pd.DataFrame:
    """The baseline's entries on `tickers` with start <= entry_date <= end -
    the landed cube's own universe and window (L376/L378: only a matched
    scope is comparable)."""
    lo, hi = str(start)[:10], str(end)[:10]
    t = set(tickers)
    return idx[idx["ticker"].isin(t) & (idx["entry_date"] >= lo)
               & (idx["entry_date"] <= hi)]
