"""Producer-parameter sandbox - S6-OPT-196 Phase 1, Option C (owner-approved B1500).

Varies SMC producer parameters WITHOUT touching production signals. Safe by
construction: `compute_smc_signals` is already fully parameterised, so the
sandbox passes different arguments rather than mutating any shared default.
Nothing here writes to a production signal namespace.

Gate 0 (ISOLATION) runs first and must pass: calling with the production
defaults must reproduce production signal values EXACTLY. If it does not, the
sandbox is not measuring what it claims and the run aborts.

First deliverable is measurement, not optimisation (B1500 council): wall-clock
per config and fire-count sensitivity. Grid size stays open pending S6-B1499a.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import pandas as pd

from backtest.signals.smc_ict import compute_smc_signals

# Production defaults, READ from smc_ict.py:75-82 at B1500. The isolation gate
# below pins these - if the source defaults drift, Gate 0 fails loudly rather
# than silently comparing against a stale baseline.
PRODUCTION_DEFAULTS = {
    "swing_length": 20,
    "fvg_lookback": 5,
    "liquidity_range_pct": 0.01,
    "dealing_range_lookback": 50,
    "event_recency_bars": 90,
}

# Signals consumed by smc_breaker_block_long (READ from screener.py at B1500).
CONSUMED = ("smc_breaker_block_bullish", "price_above_ema_200")


def _load_ohlcv(ticker: str) -> pd.DataFrame:
    """Load cached OHLCV. Local only - no live API (Stage 2 HARD CUT)."""
    for rel in (f"backtest/data/cache/ohlcv/{ticker}.parquet",
                f"data/cache/ohlcv/{ticker}.parquet"):
        p = Path(rel)
        if p.exists():
            df = pd.read_parquet(p)
            if not isinstance(df.index, pd.DatetimeIndex) and "date" in df.columns:
                df = df.set_index("date")
            return df.sort_index()
    raise FileNotFoundError(f"no cached OHLCV for {ticker}")


def _walk(df: pd.DataFrame, params: dict, start: str, end: str,
          min_history: int = 250) -> dict:
    """Point-in-time walk: at each bar, compute signals from history only.

    Slicing to `df.iloc[:i + 1]` is what keeps this PIT - the producer never
    sees a bar beyond the one being evaluated.
    """
    idx = df.index
    mask = (idx >= pd.Timestamp(start)) & (idx <= pd.Timestamp(end))
    fires, breaker_true, bars = 0, 0, 0
    for i in range(len(df)):
        if not mask[i] or i < min_history:
            continue
        bars += 1
        s = compute_smc_signals(df.iloc[:i + 1], **params)
        if s.get("smc_breaker_block_bullish", False):
            breaker_true += 1
            # price_above_ema_200 comes from technical.py in production; the
            # sandbox varies only SMC params, so this leg is held constant and
            # its contribution is measured separately (see EMA-variant work).
            fires += 1
    return {"bars_evaluated": bars,
            "breaker_bullish_true": breaker_true,
            "fires_smc_leg": fires}


def gate_0_isolation(df: pd.DataFrame, start: str, end: str) -> bool:
    """Defaults-in must equal defaults-implicit. Proves zero production drift."""
    explicit = _walk(df, dict(PRODUCTION_DEFAULTS), start, end)
    implicit = _walk(df, {}, start, end)
    ok = explicit == implicit
    print(f"GATE 0 ISOLATION: {'PASS' if ok else 'FAIL'}")
    print(f"  explicit defaults: {explicit}")
    print(f"  implicit defaults: {implicit}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--start", default="2022-05-05")
    ap.add_argument("--end", default="2025-05-05")  # IS window; holdout LOCKED
    ap.add_argument("--recency", default="90", help="comma list")
    ap.add_argument("--swing", default="20", help="comma list")
    ap.add_argument("--out", default="output_audit/b1500_sandbox.json")
    a = ap.parse_args()

    df = _load_ohlcv(a.ticker)
    print(f"{a.ticker}: {len(df)} bars {df.index[0].date()}..{df.index[-1].date()}")

    if not gate_0_isolation(df, a.start, a.end):
        print("ABORT: isolation gate failed - sandbox is not neutral.")
        return 1

    recency = [int(x) for x in a.recency.split(",")]
    swing = [int(x) for x in a.swing.split(",")]
    results = []
    for r, sw in itertools.product(recency, swing):
        params = dict(PRODUCTION_DEFAULTS, event_recency_bars=r, swing_length=sw)
        t0 = time.time()
        m = _walk(df, params, a.start, a.end)
        elapsed = time.time() - t0
        row = {"event_recency_bars": r, "swing_length": sw,
               "elapsed_sec": round(elapsed, 1), **m}
        results.append(row)
        print(f"  recency={r:4d} swing={sw:3d}  "
              f"breaker_true={m['breaker_bullish_true']:5d}  {elapsed:6.1f}s")

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(
        {"ticker": a.ticker, "window": [a.start, a.end],
         "production_defaults": PRODUCTION_DEFAULTS,
         "results": results}, indent=2))
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
