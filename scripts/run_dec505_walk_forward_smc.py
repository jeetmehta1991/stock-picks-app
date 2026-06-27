"""DEC-505 4-fold walk-forward harness for 18 SMC strategies.

# Source: Council 132 Option-5/6 sub-agent #5 + DEC-505 + C-1 declaration
# Section 4 PENDING walk-forward fold run per CHECKLIST #77.

Council 132 Option-5/6 sub-agent #5 (2026-06-27): exercise the existing
DEC-505 walk-forward fold spec on the 18 smartmoneyconcepts strategies
documented in `output_audit/smartmoneyconcepts_phase_c_declaration_2026_06_27.md`
item #5 ("Approve DEC-505 walk-forward fold run for 18 SMC strategies
(4 OOS x 1y)").

Scope (Phase B canary single-ticker proof of harness, NOT full universe):
  - Universe: NVDA only (cached `backtest/data/cache/ohlcv/NVDA.parquet`)
  - Date range: 2021-05-05 -> 2026-05-05 (1y warmup + 4 OOS folds)
  - Strategies: 18 strat_smc_* functions discovered dynamically from
    backtest.signals.screener.ALL_STRATEGIES
  - Exit: fixed 5-bar hold (pnl_pct = (exit_close / entry_close) - 1).
    NOT atr_trail_1x (which is the canonical Phase 1A exit) because this
    is a harness proof; full cube replay with all 25 exits is Phase 1A-beta
    scope post-R5.

Phase B short-circuit handling:
  Per B1038 Council 131 Option-A, `backtest/signals/smc_ict.py:127`
  short-circuits compute_smc_signals to return {} when
  backtest.config.SMC_PHASE != "PRODUCTION". This script monkey-patches
  SMC_PHASE = "PRODUCTION" for the duration of the run only (does NOT
  edit config.py; the canary flag stays B-CANARY in production).

DEC-505 4 OOS folds (matching backtest.engine.improvements.run_walk_forward
+ scripts/walk_forward_batch414_cells.py):
  - Warmup: 2021-05-05 -> 2022-05-05 (training only; not OOS-tested)
  - Fold 1: IS 2021-05-05 -> 2022-05-05; OOS 2022-05-05 -> 2023-05-05
  - Fold 2: IS 2021-05-05 -> 2023-05-05; OOS 2023-05-05 -> 2024-05-05
  - Fold 3: IS 2021-05-05 -> 2024-05-05; OOS 2024-05-05 -> 2025-05-05
  - Fold 4: IS 2021-05-05 -> 2025-05-05; OOS 2025-05-05 -> 2026-05-05

Output:
  output_audit/dec505_walk_forward_smc_2026_06_27.json
  Per-strategy per-fold dict with IS_n, IS_sharpe, OOS_n, OOS_sharpe,
  OOS_over_IS ratio.

Usage:
  python scripts/run_dec505_walk_forward_smc.py                  # all 4 folds
  python scripts/run_dec505_walk_forward_smc.py --smoke          # 60-day proof
  python scripts/run_dec505_walk_forward_smc.py --ticker AAPL    # other ticker
  python scripts/run_dec505_walk_forward_smc.py --hold-bars 10   # 10-bar hold

CHECKLIST #13/#22/#23/#29: no live API; reads cached parquet only. L86/L95.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import warnings
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# Suppress noisy upstream warnings
warnings.filterwarnings("ignore")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

logger = logging.getLogger("dec505_smc_wf")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

OUT_JSON = REPO / "output_audit" / "dec505_walk_forward_smc_2026_06_27.json"

# DEC-505 fold definitions (must match run_walk_forward + Batch 414 script).
FOLDS = [
    ("fold_1", date(2021, 5, 5), date(2022, 5, 5),
                date(2022, 5, 5), date(2023, 5, 5)),
    ("fold_2", date(2021, 5, 5), date(2023, 5, 5),
                date(2023, 5, 5), date(2024, 5, 5)),
    ("fold_3", date(2021, 5, 5), date(2024, 5, 5),
                date(2024, 5, 5), date(2025, 5, 5)),
    ("fold_4", date(2021, 5, 5), date(2025, 5, 5),
                date(2025, 5, 5), date(2026, 5, 5)),
]


def _load_ohlcv(ticker: str) -> pd.DataFrame:
    """Load cached OHLCV parquet. No live API per L86/L95 cost discipline."""
    path = REPO / "backtest" / "data" / "cache" / "ohlcv" / f"{ticker}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Cached OHLCV missing for {ticker}: {path}")
    df = pd.read_parquet(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
    df.columns = [c.lower() for c in df.columns]
    needed = {"open", "high", "low", "close", "volume"}
    if not needed.issubset(df.columns):
        raise ValueError(f"OHLCV missing cols: {needed - set(df.columns)}")
    return df.sort_index()


def _enable_smc_production():
    """Monkey-patch SMC_PHASE='PRODUCTION' for this run.

    Per B1038: smc_ict.compute_smc_signals short-circuits to {} when
    backtest.config.SMC_PHASE != 'PRODUCTION'. We override IN-MEMORY ONLY
    so the canary flag stays B-CANARY on disk; the override expires when
    the process exits.
    """
    import backtest.config as cfg
    cfg.SMC_PHASE = "PRODUCTION"
    # Disable panel cache (avoid PIT-risk concerns in B554 + simpler harness)
    if hasattr(cfg, "USE_SMC_PANEL_CACHE"):
        cfg.USE_SMC_PANEL_CACHE = False
    logger.info(f"SMC_PHASE monkey-patched to 'PRODUCTION' for this run only")


def _discover_smc_strategies() -> dict:
    """Pull 18 strat_smc_* callables from ALL_STRATEGIES registry."""
    from backtest.signals.screener import ALL_STRATEGIES
    smc = {k: v for k, v in ALL_STRATEGIES.items() if "smc_" in k}
    logger.info(f"Discovered {len(smc)} SMC strategies in ALL_STRATEGIES")
    return smc


def _compute_signals_at(df: pd.DataFrame, as_of_idx: int,
                        ticker: str) -> dict:
    """Build a signal dict for a single bar (as_of_idx) using cached data.

    Combines compute_smc_signals + a minimal subset of compute_all_signals
    needed by the 18 SMC strategies (price_above_ema_200, below_ema_200,
    rsi_14, vol_spike_2x, force_index_cross_up, borrow_ok).
    """
    from backtest.signals.smc_ict import compute_smc_signals
    from backtest.signals.technical import compute_all_signals

    # Slice point-in-time (no lookahead) - bars [0..as_of_idx] inclusive
    pit_df = df.iloc[:as_of_idx + 1]
    if len(pit_df) < 100:
        return {}

    signals = {}
    # 1. SMC primitives (B1038-gated)
    try:
        signals.update(compute_smc_signals(pit_df, ticker=ticker))
    except Exception as e:
        logger.debug(f"smc_ict at idx={as_of_idx}: {e}")

    # 2. Technical primitives needed by SMC strategy gates
    #    (compute_all_signals is heavy but reliable; skip nothing)
    try:
        signals.update(compute_all_signals(pit_df))
    except Exception as e:
        logger.debug(f"technical at idx={as_of_idx}: {e}")

    # 3. Fallback defaults for SMC strategy gates not always emitted
    signals.setdefault("borrow_ok", True)  # Phase B canary: assume borrow OK
    return signals


def _evaluate_strategy(strat_name: str, strat_fn, signals: dict):
    """Call the strategy gate function; return ('long'|'short'|None).

    Strategy contract observed in screener.py:
      - _strat(fires, direction, ...) -> {'fires': bool, 'direction': 'long'|'short', ...}
      - _strat3(fl, fs, ...) -> {'fires': bool, 'direction': 'long'|'short'|'long_short', ...}
        (long_short = dual-direction; fires on either branch)

    Returns the firing direction string, or None if not fired.
    """
    try:
        result = strat_fn(signals)
    except Exception as e:
        logger.debug(f"{strat_name} fire-check raised: {e}")
        return None

    if isinstance(result, dict):
        if not result.get("fires"):
            return None
        direction = result.get("direction", "long")
        # Normalize 'long_short' to 'long' (dual-strat fires either branch;
        # we treat it as a single entry event for harness purposes)
        if direction not in ("long", "short"):
            direction = "long"
        return direction
    if isinstance(result, bool) and result:
        return "long"
    if isinstance(result, tuple) and any(bool(x) for x in result):
        return "long"
    return None


def _run_backtest(df: pd.DataFrame, ticker: str, smc_strats: dict,
                  hold_bars: int = 5, smoke: bool = False) -> pd.DataFrame:
    """Bar-by-bar single-ticker backtest -> trade rows.

    For each bar, evaluate all 18 SMC strategies. If a strategy fires,
    record an entry; exit hold_bars later at close. PIT discipline: signal
    computation slices df[:bar_idx+1] only (no lookahead).
    """
    start_pos = 100  # warmup for technical indicators
    end_pos = len(df) - hold_bars - 1
    if smoke:
        # B1039: 252-bar smoke window covers 1 trading year - large enough
        # to give 18 SMC strategies a realistic chance to fire confluence
        end_pos = min(start_pos + 252, end_pos)

    trades = []
    bar_count = 0
    smc_fire_count = 0
    t_start = time.time()
    for i in range(start_pos, end_pos + 1):
        bar_count += 1
        signals = _compute_signals_at(df, i, ticker)
        if not signals:
            continue
        # Track whether ANY smc_* signal is True this bar (for sanity check)
        if any(k.startswith("smc_") and v is True
               for k, v in signals.items()):
            smc_fire_count += 1

        entry_date = df.index[i].date()
        entry_close = float(df["close"].iloc[i])
        exit_close = float(df["close"].iloc[i + hold_bars])

        for strat_name, strat_fn in smc_strats.items():
            direction = _evaluate_strategy(strat_name, strat_fn, signals)
            if direction is None:
                continue
            raw_pnl = (exit_close / entry_close) - 1.0
            pnl_pct = raw_pnl if direction == "long" else -raw_pnl
            trades.append({
                "strategy":   strat_name,
                "direction":  direction,
                "entry_date": entry_date,
                "entry_close": round(entry_close, 4),
                "exit_close":  round(exit_close, 4),
                "pnl_pct":     round(pnl_pct, 6),
                "hold_bars":   hold_bars,
            })

        if bar_count % 100 == 0:
            elapsed = time.time() - t_start
            logger.info(f"  bar {bar_count} ({entry_date}): "
                        f"smc_signals_seen={smc_fire_count}, "
                        f"trades_recorded={len(trades)}, "
                        f"elapsed={elapsed:.1f}s")

    elapsed = time.time() - t_start
    logger.info(f"backtest complete: bars={bar_count} "
                f"smc_signals_seen={smc_fire_count} "
                f"trades={len(trades)} elapsed={elapsed:.1f}s")
    return pd.DataFrame(trades)


def _fold_stats(pnl: pd.Series, min_n: int = 5) -> Optional[dict]:
    n = len(pnl)
    if n < min_n:
        return None
    arr = pnl.values
    mean_pp = float(arr.mean())
    std_pp = float(arr.std(ddof=1)) if n > 1 else 0.0
    sharpe = mean_pp / std_pp if std_pp > 0 else 0.0
    # Annualize (5-bar hold ~252/5 = 50.4 trades/yr/strategy max)
    sharpe_ann = sharpe * (252 ** 0.5) if std_pp > 0 else 0.0
    wins = float(arr[arr > 0].sum())
    losses = float(abs(arr[arr < 0].sum()))
    pf = wins / losses if losses > 0 else 999.0
    wr = float((arr > 0).mean())
    return {
        "n":          n,
        "sharpe":     round(sharpe, 4),
        "sharpe_ann": round(sharpe_ann, 3),
        "win_rate":   round(wr, 4),
        "profit_factor": round(pf, 3),
        "mean_pnl_pct": round(mean_pp, 5),
        "total_pnl_pct": round(float(arr.sum()), 5),
    }


def _walk_forward(trades_df: pd.DataFrame, smc_strats: dict) -> dict:
    """Slice trades into 4 DEC-505 folds; compute per-strategy IS/OOS stats."""
    if trades_df.empty:
        return {"_note": "No trades produced; SMC strategies did not fire."}

    trades_df["entry_date"] = pd.to_datetime(trades_df["entry_date"]).dt.date
    results = {}
    for strat_name in smc_strats:
        strat_trades = trades_df[trades_df["strategy"] == strat_name]
        if strat_trades.empty:
            results[strat_name] = {"_note": "no fires", "folds": {}}
            continue
        per_fold = {}
        for fold_name, is_start, is_end, oos_start, oos_end in FOLDS:
            is_mask = ((strat_trades["entry_date"] >= is_start)
                       & (strat_trades["entry_date"] < is_end))
            oos_mask = ((strat_trades["entry_date"] >= oos_start)
                        & (strat_trades["entry_date"] < oos_end))
            is_stats = _fold_stats(strat_trades.loc[is_mask, "pnl_pct"])
            oos_stats = _fold_stats(strat_trades.loc[oos_mask, "pnl_pct"])
            ratio = None
            if (is_stats and oos_stats
                    and is_stats["sharpe_ann"] != 0):
                ratio = round(
                    oos_stats["sharpe_ann"] / is_stats["sharpe_ann"], 3
                )
            per_fold[fold_name] = {
                "is_window":  f"{is_start} -> {is_end}",
                "oos_window": f"{oos_start} -> {oos_end}",
                "is":         is_stats,
                "oos":        oos_stats,
                "oos_over_is_sharpe_ratio": ratio,
            }
        # Per-strategy DEC-505 verdict: how many of 4 OOS folds have
        # sharpe_ann >= 0.7 (the 1A-alpha owner-gate threshold)
        oos_pass_count = sum(
            1 for f in per_fold.values()
            if f["oos"] and f["oos"]["sharpe_ann"] >= 0.7
        )
        oos_fold_count = sum(
            1 for f in per_fold.values() if f["oos"] is not None
        )
        verdict = (
            "INSUFFICIENT_OOS_DATA" if oos_fold_count < 2
            else "ROBUST" if oos_pass_count >= 3
            else "WEAK" if oos_pass_count >= 1
            else "OVERFIT_OR_FAIL"
        )
        results[strat_name] = {
            "total_trades": len(strat_trades),
            "oos_pass_count_of_4": oos_pass_count,
            "oos_folds_with_n_gte_5": oos_fold_count,
            "verdict": verdict,
            "folds": per_fold,
        }
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ticker", default="NVDA",
                     help="cached ticker to backtest (default: NVDA)")
    ap.add_argument("--hold-bars", type=int, default=5,
                     help="fixed-hold exit horizon in bars (default: 5)")
    ap.add_argument("--smoke", action="store_true",
                     help="short 60-bar smoke run for harness verification")
    ap.add_argument("--out", default=str(OUT_JSON),
                     help=f"output JSON path (default: {OUT_JSON})")
    args = ap.parse_args()

    logger.info("=" * 70)
    logger.info("DEC-505 walk-forward harness for 18 SMC strategies (B1039)")
    logger.info(f"  ticker = {args.ticker}")
    logger.info(f"  hold_bars = {args.hold_bars}")
    logger.info(f"  smoke = {args.smoke}")
    logger.info("=" * 70)

    _enable_smc_production()
    smc_strats = _discover_smc_strategies()
    if len(smc_strats) != 18:
        logger.warning(
            f"Expected 18 SMC strategies; found {len(smc_strats)}. "
            "Council 132 sub-agent #5 spec assumed 18."
        )

    df = _load_ohlcv(args.ticker)
    logger.info(f"OHLCV loaded: {df.shape} "
                f"range {df.index.min().date()} -> {df.index.max().date()}")

    trades_df = _run_backtest(
        df, args.ticker, smc_strats,
        hold_bars=args.hold_bars, smoke=args.smoke,
    )

    results = _walk_forward(trades_df, smc_strats)

    payload = {
        "spec":            "DEC-505 4-fold walk-forward (B1038/B1039)",
        "council":         "132 Option-5/6 sub-agent #5",
        "phase_gate":      "smartmoneyconcepts Phase B canary",
        "smc_phase_flag":  "PRODUCTION (in-memory monkey-patch only)",
        "ticker":          args.ticker,
        "hold_bars":       args.hold_bars,
        "smoke":           args.smoke,
        "fold_count":      4,
        "warmup_window":   "2021-05-05 -> 2022-05-05",
        "generated_at":    datetime.utcnow().isoformat() + "Z",
        "total_trades":    int(len(trades_df)),
        "strategies":      results,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    logger.info(f"saved -> {out_path}")

    # Console summary
    logger.info("")
    logger.info("=== Per-strategy verdict summary ===")
    if isinstance(results, dict) and "_note" not in results:
        for strat_name, r in results.items():
            if "verdict" in r:
                logger.info(
                    f"  {strat_name:<40} "
                    f"trades={r['total_trades']:>5} "
                    f"oos_pass={r['oos_pass_count_of_4']}/4 "
                    f"verdict={r['verdict']}"
                )
            else:
                logger.info(f"  {strat_name:<40} {r.get('_note', '')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
