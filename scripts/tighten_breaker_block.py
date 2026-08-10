"""Vary tightening levels on smc_breaker_block_long and grade every combination.

THE ECONOMY THAT MAKES THIS FREE: tightening only ever REMOVES fires, so every
tightened variant is a strict SUBSET of R5's fires. The R5 cube already holds
each of those trades under all 26 exits, so a variant is graded by subsetting
the cube -- no resimulation, and the P&L is exact rather than modelled.

Levels are DERIVED, not chosen (L356). Candidate values come from the measured
distributions in B1501: true retests sit at 0.5-2.7pct distance / 45-134 bars
old, latches at 7.5-60pct / 294-469 bars, with an empty gap between. Direction
is an UPPER bound on both axes (L359: a breaker block is a RETEST, so closer
and fresher is stricter).

Gate evaluation delegates to scripts/roster_core.py so the bar is identical to
the one the Phase 1B roster uses. Exit is selected IN-SAMPLE only, then the
holdout is graded once -- the same discipline the roster applies.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import itertools
import json
from pathlib import Path

import pandas as pd

import roster_core as rc

with contextlib.redirect_stdout(io.StringIO()):
    from vendored.smartmoneyconcepts.smartmoneyconcepts import smc as _smc

STRATEGY = "smc_breaker_block_long"
R5_CUBE = Path("output_r5_rung4_chunk1/trade_exit_detail.csv")

# Candidate levels. Each list ANCHORS at the production default (last element)
# so "no change" is always in the grid and the baseline is reproducible.
BREAK_PCT_MAX = [0.01, 0.02, 0.03, 0.05, None]   # None = production (no cap)
AGE_BARS_MAX = [60, 120, 180, 250, None]         # None = production (no cap)
TAIL_N = [3, 5, 10, 20]                          # 20 = production


def _load_ohlcv(ticker: str) -> pd.DataFrame | None:
    for rel in (f"backtest/data/cache/ohlcv/{ticker}.parquet",
                f"data/cache/ohlcv/{ticker}.parquet"):
        p = Path(rel)
        if p.exists():
            df = pd.read_parquet(p)
            if not isinstance(df.index, pd.DatetimeIndex) and "date" in df.columns:
                df = df.set_index("date")
            return df.sort_index()
    return None


def diagnose_fire(df: pd.DataFrame, when: pd.Timestamp,
                  swing_length: int = 20) -> dict | None:
    """Recover age_bars / break_pct / rank for the OB events qualifying at `when`.

    PIT preserved: the producer sees ohlc.iloc[:i+1] only, exactly as production.
    """
    locs = df.index.get_indexer([when], method="pad")
    i = int(locs[0])
    if i < 250:
        return None
    sub = df.iloc[:i + 1]
    swings = _smc.swing_highs_lows(sub, swing_length=swing_length)
    ob_df = _smc.ob(sub, swings)
    if ob_df is None or "OB" not in ob_df.columns:
        return None
    nz = ob_df[ob_df["OB"].fillna(0) != 0]
    if nz.empty:
        return None
    col = "close" if "close" in sub.columns else "Close"
    close = float(sub[col].iloc[-1])
    pos = {lbl: p for p, lbl in enumerate(ob_df.index)}
    out = []
    for rank, (lbl, row) in enumerate(list(nz.tail(max(TAIL_N)).iterrows())[::-1]):
        ob_val, top, bot = row.get("OB"), row.get("Top"), row.get("Bottom")
        mit = row.get("MitigatedIndex")
        if pd.isna(ob_val) or ob_val == 0 or pd.isna(top) or pd.isna(bot):
            continue
        if (not pd.isna(mit)) and mit > 0 and int(mit) < i \
                and ob_val == -1 and close > float(top):
            out.append({"rank": rank,
                        "age_bars": i - pos.get(lbl, i),
                        "break_pct": (close - float(top)) / float(top)})
    return {"events": out} if out else None


def survives(diag: dict, break_max, age_max, tail_n) -> bool:
    """A fire survives if ANY qualifying event satisfies every active cap."""
    for e in diag["events"]:
        if e["rank"] >= tail_n:
            continue
        if break_max is not None and e["break_pct"] > break_max:
            continue
        if age_max is not None and e["age_bars"] > age_max:
            continue
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="output_audit/b1502_tightening_grid.json")
    ap.add_argument("--limit-tickers", type=int, default=0)
    a = ap.parse_args()

    cube = rc.load_cube(R5_CUBE)
    g = cube[cube["strategy"] == STRATEGY].copy()
    # load_cube yields entry_date as datetime.date; roster_core's window
    # helpers compare against date objects, so do NOT convert to datetime64.
    fires = g[["ticker", "entry_date"]].drop_duplicates()
    print(f"R5 baseline: {len(fires)} fires x {g.exit_method.nunique()} exits "
          f"= {len(g)} cube rows")

    tickers = sorted(fires.ticker.unique())
    if a.limit_tickers:
        tickers = tickers[:a.limit_tickers]

    # One instrumented pass per fire; results reused by every combination.
    diags: dict[tuple, dict] = {}
    for t in tickers:
        df = _load_ohlcv(t)
        if df is None:
            continue
        for when in fires[fires.ticker == t].entry_date:
            d = diagnose_fire(df, pd.Timestamp(when))
            if d:
                diags[(t, when)] = d
    print(f"diagnosed {len(diags)} of {len(fires)} fires")

    rows = []
    for bmax, amax, tn in itertools.product(BREAK_PCT_MAX, AGE_BARS_MAX, TAIL_N):
        keep = {k for k, d in diags.items() if survives(d, bmax, amax, tn)}
        if not keep:
            rows.append({"break_pct_max": bmax, "age_bars_max": amax,
                         "tail_n": tn, "fires": 0, "verdict": "ZERO_FIRES"})
            continue
        sub = g[[(r.ticker, r.entry_date) in keep
                 for r in g.itertuples()]]
        is_m = rc.in_sample(sub)
        ho_m = rc.holdout(sub)
        exit_pick, _ = rc.select_exit(is_m)
        if exit_pick is None:
            rows.append({"break_pct_max": bmax, "age_bars_max": amax,
                         "tail_n": tn, "fires": len(keep),
                         "verdict": "NO_EXIT_SELECTABLE"})
            continue
        hb = ho_m[ho_m.exit_method == exit_pick]
        fp_n = int((sub.exit_method == exit_pick).sum())
        res = rc.evaluate(hb["pnl_pct"], hb["hold_days"], full_period_n=fp_n)
        row = {"break_pct_max": bmax, "age_bars_max": amax, "tail_n": tn,
               "fires": len(keep), "exit": exit_pick,
               "holdout_n": len(hb), "full_period_n": fp_n}
        if res is None:
            row["verdict"] = "BELOW_POWER_FLOOR"
        else:
            gates = {k: bool(res["gates"][k]) for k in rc.LIVE_GATES}
            row.update({"sharpe": res.get("sharpe"), "psr": res.get("psr"),
                        "gates": gates,
                        "gates_passed": sum(gates.values()),
                        "verdict": "PASS" if all(gates.values()) else "FAIL"})
        rows.append(row)

    rows.sort(key=lambda r: (-(r.get("gates_passed") or 0), -(r.get("fires") or 0)))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(
        {"strategy": STRATEGY, "r5_baseline_fires": len(fires),
         "diagnosed": len(diags), "results": rows}, indent=2))

    print(f"\n{'break':>6} {'age':>5} {'tail':>4} {'fires':>6} {'ho_n':>5} "
          f"{'fp_n':>5} {'sharpe':>7} {'pass':>4}  verdict")
    for r in rows[:18]:
        print(f"{str(r['break_pct_max']):>6} {str(r['age_bars_max']):>5} "
              f"{r['tail_n']:>4} {r.get('fires', 0):>6} "
              f"{r.get('holdout_n', 0):>5} {r.get('full_period_n', 0):>5} "
              f"{(f'{r.get(chr(115)+chr(104)+chr(97)+chr(114)+chr(112)+chr(101)):.3f}' if r.get('sharpe') is not None else '-'):>7} "
              f"{str(r.get('gates_passed', '-')):>4}  {r['verdict']}")
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
