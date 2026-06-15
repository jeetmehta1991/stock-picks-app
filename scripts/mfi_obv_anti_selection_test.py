"""scripts/mfi_obv_anti_selection_test.py

# Source: B766 council reviewer rec #43 + B709 conditional-add-test methodology
# per CHECKLIST #77 + #108
# per memory: feedback_no_a_priori_strategy_pruning.md + feedback_no_prior_edge_consolidate_before_tune.md

PURPOSE.
Test reviewer's claim that obv_bullish gate ANTI-SELECTS mean-reversion
opportunities in strat_mfi_oversold. Methodology: 4-cell measurement on
T1a sample x 2024-2025:

  +-------------------------------+--------------------------+
  |             | obv_bullish=True | obv_bullish=False     |
  +-------------+------------------+-----------------------+
  | mfi_14<20   | n_a / pnl_a      | n_b / pnl_b           |
  +-------------+------------------+-----------------------+

If pnl_b > pnl_a (forward returns BETTER when obv is NOT bullish),
anti-selection confirmed -> reviewer right -> drop obv_bullish gate.
If pnl_b < pnl_a, obv_bullish gate is HELPING -> keep gate.

Forward returns at 10-day horizon (B768 edge-prior precedent).
"""
from __future__ import annotations
import argparse, json, logging, os, sys, time
from datetime import date
from pathlib import Path
import pandas as pd, numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
logger = logging.getLogger("mfi_obv_anti_selection_test")
REPO_ROOT = Path(_REPO)
OHLCV_DIR = REPO_ROOT / "data_prefetch" / "polygon" / "ohlcv_daily"
T1A_PATH = REPO_ROOT / "Backtesting universe" / "Tier 1A Universe_SP500 Tickers_Jan 2020 to May 2026.csv"
OUTPUT_DIR = REPO_ROOT / "output_audit"


def _load_t1a(start: date, end: date) -> list[str]:
    df = pd.read_csv(T1A_PATH, comment="#")
    added = pd.to_datetime(df["added_date"], errors="coerce").dt.date
    removed = pd.to_datetime(df["removed_date"], errors="coerce").dt.date
    mask = ((added.isna()) | (added <= end)) & ((removed.isna()) | (removed > start))
    return sorted(df[mask]["Symbol"].astype(str).str.upper().unique().tolist())


def _load_ohlcv(ticker: str):
    fpath = OHLCV_DIR / f"{ticker}.parquet"
    if not fpath.exists():
        return None
    try:
        df = pd.read_parquet(fpath)
    except Exception:
        return None
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"]).set_index("date").sort_index()
    df.columns = [c.lower() for c in df.columns]
    needed = {"open", "high", "low", "close", "volume"}
    if not needed.issubset(set(df.columns)):
        return None
    return df


def run_test(start: date, end: date, max_tickers: int, horizon_days: int = 10) -> dict:
    """4-cell test of mfi_14<20 x obv_bullish on forward 10-day returns."""
    from backtest.signals.technical import compute_all_signals
    tickers_all = _load_t1a(start, end)
    tickers = tickers_all[:max_tickers]
    cells = {
        "mfi_oversold_AND_obv_bullish": {"n": 0, "sum_pnl_bps": 0.0, "wins": 0},
        "mfi_oversold_AND_NOT_obv_bullish": {"n": 0, "sum_pnl_bps": 0.0, "wins": 0},
        "mfi_NOT_oversold_AND_obv_bullish": {"n": 0, "sum_pnl_bps": 0.0, "wins": 0},
        "mfi_NOT_oversold_AND_NOT_obv_bullish": {"n": 0, "sum_pnl_bps": 0.0, "wins": 0},
    }
    n_tickers_done = 0
    n_cache_misses = 0
    n_bars_total = 0
    t0 = time.time()
    for ticker in tickers:
        df = _load_ohlcv(ticker)
        if df is None:
            n_cache_misses += 1
            continue
        # B789 bug-fix: DO NOT pre-filter to [start, end] because compute_all_signals
        # needs historical bars BEFORE start for MFI/OBV warmup. Walk full df + only
        # evaluate bars whose DATE is within [start, end] window.
        if len(df) < 280:
            continue
        # Walk bars; compute signals at each, then forward 10-day return
        n_used = 0
        for i in range(250, len(df) - horizon_days):
            bar_date = df.index[i].date()
            if bar_date < start or bar_date > end:
                continue
            sub = df.iloc[: i + 1]
            try:
                sigs = compute_all_signals(sub)
            except Exception:
                continue
            # B789 bug-fix: MFI signal is emitted as `mfi` (float), not `mfi_14`.
            # Also `mfi_oversold` boolean is direct. Use either.
            mfi_val = sigs.get("mfi")
            obv_bull = sigs.get("obv_bullish")
            if mfi_val is None:
                continue
            mfi_oversold = float(mfi_val) < 20
            obv_b = bool(obv_bull) if obv_bull is not None else False
            entry_close = float(df["close"].iloc[i])
            exit_close = float(df["close"].iloc[i + horizon_days])
            if entry_close <= 0:
                continue
            pnl_bps = 10000.0 * (exit_close - entry_close) / entry_close
            # Pick cell
            if mfi_oversold and obv_b:
                key = "mfi_oversold_AND_obv_bullish"
            elif mfi_oversold and not obv_b:
                key = "mfi_oversold_AND_NOT_obv_bullish"
            elif (not mfi_oversold) and obv_b:
                key = "mfi_NOT_oversold_AND_obv_bullish"
            else:
                key = "mfi_NOT_oversold_AND_NOT_obv_bullish"
            cells[key]["n"] += 1
            cells[key]["sum_pnl_bps"] += pnl_bps
            if pnl_bps > 0:
                cells[key]["wins"] += 1
            n_used += 1
            n_bars_total += 1
        n_tickers_done += 1
        if n_tickers_done % 5 == 0:
            elapsed = time.time() - t0
            logger.info(
                "Progress: %d/%d tickers done; %d bars accumulated; %.1fs elapsed",
                n_tickers_done, len(tickers), n_bars_total, elapsed,
            )
    # Compute mean + hit rate per cell
    summary = {}
    for k, v in cells.items():
        n = v["n"]
        if n == 0:
            summary[k] = {"n": 0, "mean_pnl_bps": None, "hit_rate": None}
        else:
            summary[k] = {
                "n": n,
                "mean_pnl_bps": round(v["sum_pnl_bps"] / n, 1),
                "hit_rate": round(v["wins"] / n, 4),
            }
    # B709-style anti-selection verdict (B789 #43 refined per smoke finding)
    a = summary["mfi_oversold_AND_obv_bullish"]
    b = summary["mfi_oversold_AND_NOT_obv_bullish"]
    verdict = None
    # B789 EXTREME case: if a is empty (gate so restrictive the strategy can't
    # fire), that itself confirms anti-selection -- the gate prevents firing
    # during the very oversold conditions the strategy is supposed to detect.
    if a["n"] == 0 and b["n"] >= 10:
        verdict = (
            f"ANTI_SELECTION_CONFIRMED_EXTREME (obv_bullish gate produces ZERO fires "
            f"during MFI-oversold; NOT-obv_bullish cell shows {b['n']} obs / "
            f"{b['mean_pnl_bps']:.1f}bps/10d / hit={b['hit_rate']:.3f})"
        )
    elif a["n"] >= 30 and b["n"] >= 30:
        a_pnl = a["mean_pnl_bps"]
        b_pnl = b["mean_pnl_bps"]
        if b_pnl is not None and a_pnl is not None:
            lift = b_pnl - a_pnl
            if lift > 20:
                verdict = (
                    f"ANTI_SELECTION_CONFIRMED (NOT-obv_bullish +{lift:.0f}bps/10d "
                    f"higher; a={a['mean_pnl_bps']:.1f}bps vs b={b_pnl:.1f}bps)"
                )
            elif lift < -20:
                verdict = (
                    f"OBV_BULLISH_HELPS (gate adds +{-lift:.0f}bps/10d positive lift; "
                    f"a={a_pnl:.1f}bps vs b={b_pnl:.1f}bps)"
                )
            else:
                verdict = f"NEUTRAL (lift within +/- 20bps; a={a_pnl:.1f} vs b={b_pnl:.1f})"
        else:
            verdict = "INSUFFICIENT_DATA"
    else:
        verdict = f"INSUFFICIENT_DATA (a={a['n']} b={b['n']} - both need >=30 OR a==0+b>=10)"
    return {
        "meta": {
            "as_of_run": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "start": str(start), "end": str(end),
            "n_tickers_universe": len(tickers_all),
            "n_tickers_probed": len(tickers),
            "n_tickers_done": n_tickers_done,
            "n_cache_misses": n_cache_misses,
            "n_bars_total": n_bars_total,
            "horizon_days": horizon_days,
            "runtime_seconds": round(time.time() - t0, 1),
        },
        "cells": summary,
        "verdict": verdict,
    }


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="B789 #43 MFI obv anti-selection test")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--demo", action="store_true")
    p.add_argument("--full", action="store_true")
    p.add_argument("--max-tickers", type=int, default=None)
    p.add_argument("--start", default="2024-01-01")
    p.add_argument("--end", default="2024-12-31")
    args = p.parse_args(argv)
    if args.smoke:
        max_tk, start, end, tag = 5, date(2024, 1, 1), date(2024, 12, 31), "smoke"
    elif args.demo:
        max_tk, start, end, tag = 30, date(2024, 1, 1), date(2024, 12, 31), "demo"
    elif args.full:
        max_tk, start, end, tag = 503, date(2020, 1, 1), date(2025, 12, 31), "full"
    else:
        max_tk = args.max_tickers or 5
        start = date.fromisoformat(args.start); end = date.fromisoformat(args.end)
        tag = "custom"
    out = run_test(start, end, max_tk)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"b789_43_mfi_obv_anti_selection_{tag}.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\n=== mfi_obv_anti_selection_test {tag} ===")
    print(f"n_bars: {out['meta']['n_bars_total']}")
    for k, v in out["cells"].items():
        print(f"  {k:45s} | n={v['n']:>6d} | mean_pnl@10d={v['mean_pnl_bps']!s:>8s}bps | hit={v['hit_rate']!s}")
    print(f"VERDICT: {out['verdict']}")
    print(f"Output: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
