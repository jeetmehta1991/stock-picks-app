#!/usr/bin/env python3
"""Batch 527 (2026-05-31) -- trade_log byte-level diff tool.

Source: per CHECKLIST #77.
Queue rows: DET1 (cross-platform verification once Batch 520 CI pin
merges + DET1 workflow regenerates Linux baseline) + #9 (R3 vs R4
cube comparison once R4 unpauses).

Purpose: pytest's parity tests catch large semantic regressions
(row count, exact column equality, float-tolerance), but they don't
SHOW you the diff -- they just fail. When investigating why R3 and
R4 cubes diverge, OR why the engine emits slightly different output
on Windows vs Linux, you want a per-row inspection.

This tool ingests two trade_log.csv files and emits:

  (1) Per-row aligned diff (by trade_id when present, else by
      (ticker, entry_date, strategy)) showing every column that
      differs with a tolerance threshold for floats.
  (2) Set-level summary: trades in A but not B, B but not A, in both.
  (3) Per-column stats: how many rows differ per column +
      max/mean/p99 difference magnitude for numeric cols.
  (4) Roster diff: which (strategy, regime) cells gained / lost
      trades.

Output:
  Plain-text human report to stdout by default (--format text)
  JSON to stdout for downstream consumers (--format json)

Usage:
  python scripts/diff_trade_logs.py \\
      --a output_batch395_final/trade_log.csv \\
      --b output_batch395_r4/trade_log.csv \\
      --float-rtol 1e-6 --float-atol 1e-9
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


# Columns compared by string equality (categorical / id / text)
EXACT_COLS_DEFAULT = (
    "ticker", "entry_date", "exit_date", "direction", "strategy",
    "category", "sector", "confidence_tier", "regime", "exit_reason",
    "win", "trade_id",
)

# Columns compared with float tolerance (numeric)
TOL_COLS_DEFAULT = (
    "entry_price", "exit_price", "initial_stop", "highest_close",
    "trailing_stop_at_exit", "pnl_pct", "pnl_dollar", "hold_days",
    "max_adverse_excursion", "max_favourable_excursion",
)


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Stable sort + reset index so two trade_logs align canonically."""
    sort_cols = [c for c in ("trade_id", "ticker", "entry_date", "strategy")
                 if c in df.columns]
    return df.sort_values(sort_cols).reset_index(drop=True)


def _build_key(df: pd.DataFrame) -> pd.Series:
    """Build the alignment key. Prefer trade_id; fall back to
    (ticker, entry_date, strategy) composite."""
    if "trade_id" in df.columns and df["trade_id"].notna().all():
        return df["trade_id"].astype(str)
    parts = []
    for col in ("ticker", "entry_date", "strategy"):
        if col not in df.columns:
            raise ValueError(f"Cannot build alignment key -- column "
                             f"{col} missing AND trade_id unavailable.")
        parts.append(df[col].astype(str))
    return parts[0].str.cat(parts[1:], sep="|")


def set_level_summary(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    """Trades in A only, B only, both."""
    key_a = set(_build_key(a))
    key_b = set(_build_key(b))
    return {
        "n_a":            len(key_a),
        "n_b":            len(key_b),
        "in_a_not_b":     len(key_a - key_b),
        "in_b_not_a":     len(key_b - key_a),
        "in_both":        len(key_a & key_b),
        "sample_a_only": sorted(key_a - key_b)[:10],
        "sample_b_only": sorted(key_b - key_a)[:10],
    }


def per_column_diff_stats(
    a: pd.DataFrame, b: pd.DataFrame,
    exact_cols: tuple[str, ...] = EXACT_COLS_DEFAULT,
    tol_cols:   tuple[str, ...] = TOL_COLS_DEFAULT,
    float_rtol: float = 1e-6,
    float_atol: float = 1e-9,
) -> dict:
    """Align by key + compute per-column diff stats. Only rows present
    in BOTH dataframes are scored (set-difference is in set_level_summary).
    """
    a = _normalize(a)
    b = _normalize(b)
    key_a = _build_key(a)
    key_b = _build_key(b)
    common = sorted(set(key_a) & set(key_b))
    if not common:
        return {"n_common": 0, "exact": {}, "tol": {},
                "duplicate_keys_a": int(key_a.duplicated().sum()),
                "duplicate_keys_b": int(key_b.duplicated().sum())}
    # Dedupe duplicates BEFORE reindex (set_index + reindex fails on
    # duplicate axis labels; real trade_logs occasionally have
    # cross-batch-overlap duplicates per Batch 500 merge note).
    # Keep first occurrence per key.
    a_idx = a.set_index(key_a)
    b_idx = b.set_index(key_b)
    n_dupes_a = int(a_idx.index.duplicated().sum())
    n_dupes_b = int(b_idx.index.duplicated().sum())
    a_idx = a_idx[~a_idx.index.duplicated(keep="first")]
    b_idx = b_idx[~b_idx.index.duplicated(keep="first")]
    a2 = a_idx.reindex(common)
    b2 = b_idx.reindex(common)

    out: dict = {
        "n_common":          len(common),
        "duplicate_keys_a":  n_dupes_a,
        "duplicate_keys_b":  n_dupes_b,
        "exact":             {},
        "tol":               {},
    }

    for col in exact_cols:
        if col not in a2.columns or col not in b2.columns:
            continue
        diff_mask = a2[col].astype(str) != b2[col].astype(str)
        n_diff = int(diff_mask.sum())
        sample = []
        if n_diff > 0:
            sub = pd.DataFrame({
                "key": [common[i] for i in np.where(diff_mask.values)[0][:5]],
                "a":   a2.loc[diff_mask, col].astype(str).head(5).tolist(),
                "b":   b2.loc[diff_mask, col].astype(str).head(5).tolist(),
            })
            sample = sub.to_dict(orient="records")
        out["exact"][col] = {
            "n_diff":     n_diff,
            "n_compared": int(diff_mask.size),
            "diff_pct":   round(n_diff / diff_mask.size, 6),
            "samples":    sample,
        }

    for col in tol_cols:
        if col not in a2.columns or col not in b2.columns:
            continue
        av = pd.to_numeric(a2[col], errors="coerce")
        bv = pd.to_numeric(b2[col], errors="coerce")
        both_nan = av.isna() & bv.isna()
        either_nan = (av.isna() ^ bv.isna())
        valid = ~(both_nan | either_nan)
        n_either_nan = int(either_nan.sum())
        if not valid.any():
            out["tol"][col] = {"n_valid": 0, "either_nan": n_either_nan,
                                "max_abs_diff": None}
            continue
        diff = np.abs(av[valid].values - bv[valid].values)
        atol = float_atol + float_rtol * np.abs(bv[valid].values)
        out_of_tol = int((diff > atol).sum())
        out["tol"][col] = {
            "n_valid":         int(valid.sum()),
            "either_nan":      n_either_nan,
            "n_out_of_tol":    out_of_tol,
            "max_abs_diff":    float(diff.max()) if diff.size else 0.0,
            "mean_abs_diff":   float(diff.mean()) if diff.size else 0.0,
            "p99_abs_diff":    float(np.percentile(diff, 99)) if diff.size else 0.0,
        }

    return out


def roster_diff(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    """(strategy, regime) cells: trade counts in A vs B."""
    out: dict = {"cells_gained": [], "cells_lost": [],
                  "cells_changed": []}
    if "strategy" not in a.columns or "strategy" not in b.columns:
        return out
    grp_cols = [c for c in ("strategy", "regime") if c in a.columns
                                                  and c in b.columns]
    if not grp_cols:
        return out
    ca = a.groupby(grp_cols, dropna=False).size().rename("n_a")
    cb = b.groupby(grp_cols, dropna=False).size().rename("n_b")
    merged = pd.concat([ca, cb], axis=1).fillna(0).astype(int)
    merged["delta"] = merged["n_b"] - merged["n_a"]
    for idx, row in merged.iterrows():
        cell = {"cell": list(idx) if isinstance(idx, tuple) else [idx],
                "n_a":   int(row["n_a"]),
                "n_b":   int(row["n_b"]),
                "delta": int(row["delta"])}
        if row["n_a"] == 0 and row["n_b"] > 0:
            out["cells_gained"].append(cell)
        elif row["n_b"] == 0 and row["n_a"] > 0:
            out["cells_lost"].append(cell)
        elif row["delta"] != 0:
            out["cells_changed"].append(cell)
    # Sort changed by abs delta desc, head 20
    out["cells_changed"].sort(key=lambda x: abs(x["delta"]), reverse=True)
    out["cells_changed"] = out["cells_changed"][:20]
    return out


def run_diff(
    a_path: Path, b_path: Path,
    float_rtol: float = 1e-6, float_atol: float = 1e-9,
) -> dict:
    a = pd.read_csv(a_path, low_memory=False)
    b = pd.read_csv(b_path, low_memory=False)
    return {
        "a_path":       str(a_path),
        "b_path":       str(b_path),
        "set_summary":  set_level_summary(a, b),
        "col_diffs":    per_column_diff_stats(
            a, b, float_rtol=float_rtol, float_atol=float_atol,
        ),
        "roster_diff":  roster_diff(a, b),
    }


def _print_text(result: dict) -> None:
    print(f"=== trade_log diff ===")
    print(f"A: {result['a_path']}")
    print(f"B: {result['b_path']}")
    print()
    s = result["set_summary"]
    print("[set summary]")
    print(f"  rows A={s['n_a']}  B={s['n_b']}  both={s['in_both']}")
    print(f"  A-only: {s['in_a_not_b']}  B-only: {s['in_b_not_a']}")
    if s["sample_a_only"]:
        print(f"  sample A-only: {s['sample_a_only'][:5]}")
    if s["sample_b_only"]:
        print(f"  sample B-only: {s['sample_b_only'][:5]}")
    print()

    cd = result["col_diffs"]
    print(f"[per-column diff -- {cd['n_common']} rows in common]")
    if cd["exact"]:
        print("  exact (string equality):")
        for col, st in cd["exact"].items():
            if st["n_diff"] > 0:
                print(f"    {col:25s} diff={st['n_diff']:6d} "
                      f"/ {st['n_compared']:6d}  ({st['diff_pct']:.4%})")
    if cd["tol"]:
        print("  tol (float):")
        for col, st in cd["tol"].items():
            if st.get("n_out_of_tol", 0) > 0:
                print(f"    {col:25s} out_of_tol={st['n_out_of_tol']:6d} "
                      f"max_diff={st['max_abs_diff']:.6g} "
                      f"p99={st['p99_abs_diff']:.6g}")
    print()

    rd = result["roster_diff"]
    print(f"[roster diff -- (strategy, regime) cells]")
    print(f"  gained (0 -> >0 trades): {len(rd['cells_gained'])}")
    print(f"  lost   (>0 -> 0 trades): {len(rd['cells_lost'])}")
    if rd["cells_changed"]:
        print(f"  changed (top 10 by |delta|):")
        for c in rd["cells_changed"][:10]:
            print(f"    {c['cell']:!s:50s} A={c['n_a']:5d} "
                  f"B={c['n_b']:5d}  delta={c['delta']:+d}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--a", required=True, type=Path,
                   help="first trade_log.csv")
    p.add_argument("--b", required=True, type=Path,
                   help="second trade_log.csv")
    p.add_argument("--float-rtol", type=float, default=1e-6)
    p.add_argument("--float-atol", type=float, default=1e-9)
    p.add_argument("--format", choices=("text", "json"), default="text")
    args = p.parse_args()

    for path in (args.a, args.b):
        if not path.exists():
            print(f"ERROR: {path} not found", file=sys.stderr)
            return 2

    result = run_diff(args.a, args.b,
                      float_rtol=args.float_rtol,
                      float_atol=args.float_atol)
    if args.format == "json":
        print(json.dumps(result, indent=2, default=str))
    else:
        try:
            _print_text(result)
        except (KeyError, TypeError):
            # fall back to JSON if text formatter fails on schema drift
            print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
