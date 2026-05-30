#!/usr/bin/env python3
"""Batch 498 (2026-05-31) -- DET1 platform-determinism diagnostic harness.

Queue row: EXECUTION_QUEUE.md item DET1.

Purpose: surface the FIRST point of divergence in indicator output
between Linux (CI / AWS production) and Windows (local development).
Per DET1 finding (Batch 484 CI logs 2026-05-30), the engine produces
COMPLETELY DIFFERENT trade sets on the two platforms (16 vs 15 trades;
different (ticker, strategy, direction) tuples). This script narrows
the diagnosis from "trades differ" -> "this specific indicator differs
at the seed".

Run on each platform (Linux CI runner + Windows local) and diff the
output JSONs. The first indicator whose hash differs is the cause.

Usage:
  python scripts/check_platform_determinism.py
  python scripts/check_platform_determinism.py --output platform_<os>.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parent.parent


def _hash_array(arr: np.ndarray) -> str:
    """SHA-256 of float-array bytes after rounding to 1e-12 to absorb
    truly negligible FP noise (so legitimate platform parity passes;
    only differences > rounding cause mismatch)."""
    if arr is None:
        return "null"
    a = np.asarray(arr, dtype=float)
    rounded = np.round(a, 12)
    # Replace NaN with sentinel for stable hashing
    nan_mask = np.isnan(rounded)
    rounded[nan_mask] = -999999.999999
    return hashlib.sha256(rounded.tobytes()).hexdigest()


def _make_synthetic_ohlcv(n: int = 252) -> pd.DataFrame:
    """Deterministic synthetic OHLCV. Seeded numpy random walk so the
    output is bit-identical across platforms IF numpy / pandas behave
    deterministically (which they do for fixed seed)."""
    rng = np.random.default_rng(seed=42)
    log_returns = rng.normal(loc=0.0005, scale=0.015, size=n)
    close = 100.0 * np.exp(np.cumsum(log_returns))
    # Synthetic OHLC: open = prev close, high/low = close +/- noise
    open_  = np.concatenate(([100.0], close[:-1]))
    noise_high = rng.uniform(0, 0.01, size=n) * close
    noise_low  = rng.uniform(0, 0.01, size=n) * close
    high = np.maximum(open_, close) + noise_high
    low  = np.minimum(open_, close) - noise_low
    volume = rng.integers(low=500_000, high=5_000_000, size=n)
    dates = pd.date_range("2024-01-02", periods=n, freq="B")
    return pd.DataFrame({
        "open":   open_,
        "high":   high,
        "low":    low,
        "close":  close,
        "volume": volume,
    }, index=dates)


def _compute_indicator_fingerprints(df: pd.DataFrame) -> dict:
    """Compute fingerprints for the indicators most likely to drift
    between Linux glibc + Windows MSVC fp libraries. Returns a dict
    {indicator_name: sha256_hex} that future runs can diff.
    """
    out: dict = {}

    # Bedrock numerics (pandas + numpy primitives)
    out["close_raw"]            = _hash_array(df["close"].values)
    out["close_pct_change"]     = _hash_array(df["close"].pct_change().values)
    out["close_log_returns"]    = _hash_array(np.log(df["close"]).diff().values)
    out["close_ema_20"]         = _hash_array(
        df["close"].ewm(span=20, adjust=False).mean().values)
    out["close_sma_20"]         = _hash_array(
        df["close"].rolling(20).mean().values)
    out["close_std_20"]         = _hash_array(
        df["close"].rolling(20).std().values)

    # ATR-style true range
    tr_hl = df["high"] - df["low"]
    tr_hc = (df["high"] - df["close"].shift()).abs()
    tr_lc = (df["low"]  - df["close"].shift()).abs()
    tr = pd.concat([tr_hl, tr_hc, tr_lc], axis=1).max(axis=1)
    out["atr_14"]               = _hash_array(
        tr.rolling(14).mean().values)

    # RSI-like
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    out["rsi_14"]               = _hash_array(rsi.values)

    # Bollinger band width
    mid = df["close"].rolling(20).mean()
    std = df["close"].rolling(20).std()
    bb_width = (4.0 * std) / mid
    out["bollinger_width_20"]   = _hash_array(bb_width.values)

    return out


def _platform_key() -> str:
    return (
        f"{platform.system()}|{platform.release()}|"
        f"py{sys.version_info.major}.{sys.version_info.minor}|"
        f"numpy{np.__version__}|pandas{pd.__version__}"
    )


def run() -> dict:
    df = _make_synthetic_ohlcv()
    return {
        "platform_key":             _platform_key(),
        "python_version":           sys.version.split()[0],
        "numpy_version":             np.__version__,
        "pandas_version":           pd.__version__,
        "system":                    platform.system(),
        "release":                   platform.release(),
        "machine":                   platform.machine(),
        "synthetic_seed":           42,
        "synthetic_n_rows":         len(df),
        "indicator_fingerprints":   _compute_indicator_fingerprints(df),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "-o", default=None,
                         help="Write JSON to this path (default stdout)")
    args = parser.parse_args()
    result = run()
    out_str = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(out_str, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(out_str)


if __name__ == "__main__":
    main()
