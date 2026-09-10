#!/usr/bin/env python
# Source: data_prefetch/quiver/institutional/{TICKER}.parquet (1,942 per-ticker
# fund-level 13F files; panel measured 2015-03-31..2025-12-31 on MSFT) per
# CHECKLIST #77. The bulk sec13f/sec13fchanges globals are single-snapshot
# 500k-row caps (measured B2657) and are NOT read here.
"""B2659 (S6-B2657b, owner-approved 2026-09-09): the 13F DEPTH precompute.

WHAT IT BUILDS - the two tables from which every depth signal in the S6-B2656
programme derives, at the grain professionals actually use:

  1. depth_by_ticker_quarter.parquet - per (ticker, report_period):
       n_funds_held, n_init, n_exit, breadth_delta (= n_init - n_exit),
       n_add, n_reduce, init_value_sum, top_init_value,
       n_init_smallfiler (initiating funds holding < SMALLFILER_MAX positions
       that quarter - the discretionary tier), n_init_megafiler
       (> MEGAFILER_MIN positions - the passive tier),
       availability_q90 (the filing date by which 90 pct of that
       ticker-quarter's rows were on file - the PIT stamp).
  2. fund_scale.parquet - per (fund, report_period): n_positions,
       total_value. The segregation table.

FLOW SEMANTICS (per ticker, per fund, quarters sorted):
  INIT   = fund absent the previous PRESENT quarter, present now.
  EXIT   = fund present the previous quarter, absent now.
  ADD    = present both, shares increased; REDUCE = decreased.
  The panel's FIRST quarter per ticker classifies nothing (no prior set), so
  counts there are held-only - stated in build_params, not silently.

PIT: a holding becomes knowable at its OWN filing Date, not at quarter end.
The depth row carries availability_q90; a consumer at as_of must require
availability_q90 <= as_of (or re-derive per-fund from the raw panel). This
is DISCLOSED WEAKER than per-fund PIT - the aggregation trades a small
availability tail for a 100x smaller table; the raw panel remains the
per-fund source of truth.

FAIL-CLOSED RECORDS (the B2622/B2635 classes): build_params.json carries the
source dir, file count, thresholds and window; coverage.json names every
ticker file that produced zero usable rows (the b2635 census found 89 empty
vendor files - they are counted here, never silently skipped).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
SRC_DIR = REPO / "data_prefetch" / "quiver" / "institutional"
OUT_DIR = REPO / "data_prefetch" / "derived" / "inst_depth_13f"
SMALLFILER_MAX = 100     # < 100 positions that quarter = discretionary tier
MEGAFILER_MIN = 500      # > 500 positions = passive/index tier
Q90 = 0.90               # availability stamp quantile


def load_one(p: Path) -> pd.DataFrame | None:
    try:
        df = pd.read_parquet(p, columns=["Ticker", "Fund", "ReportPeriod",
                                         "Date", "Shares", "Value"])
    except Exception:
        return None
    if df is None or df.empty:
        return None
    df = df.dropna(subset=["Fund", "ReportPeriod"])
    if df.empty:
        return None
    df["q"] = pd.to_datetime(df["ReportPeriod"], errors="coerce").dt.date
    df["filed"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Shares"] = pd.to_numeric(df["Shares"], errors="coerce").fillna(0)
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce").fillna(0)
    df = df.dropna(subset=["q"])
    # one row per (fund, quarter): a fund can file amendments - keep the
    # LATEST filing's numbers (max filed), never sum duplicates
    df = (df.sort_values("filed")
            .groupby(["Fund", "q"], as_index=False)
            .agg(Shares=("Shares", "last"), Value=("Value", "last"),
                 filed=("filed", "last")))
    return df


def main() -> int:
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC_DIR.glob("*.parquet"))
    scale_acc: dict = {}
    depth_rows: list[dict] = []
    empty_files: list[str] = []
    ticker_frames: dict[str, pd.DataFrame] = {}

    # PASS A: stream every file once - accumulate fund scale, keep the slim
    # per-ticker frame for pass B (Fund/q/Shares/Value/filed only).
    for i, p in enumerate(files):
        df = load_one(p)
        if df is None:
            empty_files.append(p.stem)
            continue
        ticker_frames[p.stem] = df
        for (f, q), v, n in zip(df.groupby(["Fund", "q"]).groups.keys(),
                                df.groupby(["Fund", "q"])["Value"].sum().values,
                                df.groupby(["Fund", "q"])["Shares"].count().values):
            key = (f, q)
            s = scale_acc.get(key)
            if s is None:
                scale_acc[key] = [1, float(v)]
            else:
                s[0] += 1
                s[1] += float(v)
        if (i + 1) % 300 == 0:
            print(f"  pass A {i+1}/{len(files)} files, {time.time()-t0:.0f}s")

    scale = pd.DataFrame(
        [(f, q, n, v) for (f, q), (n, v) in scale_acc.items()],
        columns=["fund", "report_period", "n_positions", "total_value"])
    scale.to_parquet(OUT_DIR / "fund_scale.parquet", index=False)
    small = {(f, q) for (f, q), (n, _) in scale_acc.items() if n < SMALLFILER_MAX}
    mega = {(f, q) for (f, q), (n, _) in scale_acc.items() if n > MEGAFILER_MIN}
    print(f"pass A done: {len(scale):,} fund-quarters, {len(files)} files, "
          f"{len(empty_files)} empty")

    # PASS B: per ticker, quarter-over-quarter fund-set flows.
    for tkr, df in ticker_frames.items():
        quarters = sorted(df["q"].unique())
        by_q = {q: g for q, g in df.groupby("q")}
        prev_funds: set | None = None
        prev_shares: dict | None = None
        for q in quarters:
            g = by_q[q]
            funds = set(g["Fund"])
            shares = dict(zip(g["Fund"], g["Shares"]))
            values = dict(zip(g["Fund"], g["Value"]))
            row = {"ticker": tkr, "report_period": q,
                   "n_funds_held": len(funds),
                   "availability_q90": g["filed"].quantile(Q90),
                   "first_panel_quarter": prev_funds is None}
            if prev_funds is None:
                row.update({"n_init": np.nan, "n_exit": np.nan,
                            "breadth_delta": np.nan, "n_add": np.nan,
                            "n_reduce": np.nan, "init_value_sum": np.nan,
                            "top_init_value": np.nan,
                            "n_init_smallfiler": np.nan,
                            "n_init_megafiler": np.nan})
            else:
                init = funds - prev_funds
                exit_ = prev_funds - funds
                both = funds & prev_funds
                adds = [f for f in both if shares[f] > prev_shares.get(f, 0)]
                reds = [f for f in both if shares[f] < prev_shares.get(f, 0)]
                iv = [values[f] for f in init]
                row.update({
                    "n_init": len(init), "n_exit": len(exit_),
                    "breadth_delta": len(init) - len(exit_),
                    "n_add": len(adds), "n_reduce": len(reds),
                    "init_value_sum": float(sum(iv)) if iv else 0.0,
                    "top_init_value": float(max(iv)) if iv else 0.0,
                    "n_init_smallfiler": sum(1 for f in init if (f, q) in small),
                    "n_init_megafiler": sum(1 for f in init if (f, q) in mega),
                })
            depth_rows.append(row)
            prev_funds, prev_shares = funds, shares

    depth = pd.DataFrame(depth_rows)
    depth.to_parquet(OUT_DIR / "depth_by_ticker_quarter.parquet", index=False)

    (OUT_DIR / "build_params.json").write_text(json.dumps({
        "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_dir": "data_prefetch/quiver/institutional",
        "source_files": len(files), "empty_files": len(empty_files),
        "smallfiler_max_positions": SMALLFILER_MAX,
        "megafiler_min_positions": MEGAFILER_MIN,
        "availability_quantile": Q90,
        "first_panel_quarter_classifies_no_flows": True,
        "builder": "scripts/build_13f_depth_precompute.py B2659"},
        indent=2), encoding="utf-8")
    (OUT_DIR / "coverage.json").write_text(json.dumps({
        "files": len(files), "with_rows": len(files) - len(empty_files),
        "empty": len(empty_files), "empty_tickers": sorted(empty_files)},
        indent=2), encoding="utf-8")

    print(f"wrote {len(depth):,} depth rows / {len(scale):,} fund-scale rows "
          f"in {time.time()-t0:.0f}s -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
