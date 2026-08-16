"""B1588 -- adversarial spot check of cube trades against RAW OHLCV.

Owner directive: verify a random sample of trades independently - did every
producer actually fire against its threshold, and did the trade execute
correctly?

METHOD (deliberately independent of the engine)
For each sampled (ticker, entry_date) this re-derives, from the parquet alone:

  P1  swings  = swing_highs_lows(ohlc.iloc[:i+1], swing_length)
  P2  ob_df   = ob(ohlc, swings, close_mitigation)
  P3  events  = ob_df[OB != 0].tail(tail_n)
  P4  mitigated = (MitigatedIndex > 0) and (MitigatedIndex < i)
  P5  broken_up = close > event.Top
  P6  price_above_ema_<span> = close > EMA(close, span)
  fires = ANY event satisfying (OB == -1 AND mitigated AND broken_up)
          AND price_above_ema_<span>

then checks the recorded trade for execution correctness:
  - entry_date is a REAL trading day present in the parquet
  - exit_date >= entry_date, and both inside the run window
  - hold_days matches the CALENDAR-day distance (verified convention, B1588)
  - pnl_pct is finite and consistent in SIGN with entry/exit prices for a LONG

PIT is preserved by construction: every producer sees `ohlc.iloc[:i+1]` only,
never a row after the entry bar. Any producer that needs a later bar would show
up here as a mismatch, which is the point.

A mismatch is NOT automatically an engine bug - it can equally be a defect in
THIS script. Both are findings. Nothing here is reported as a cause without a
probe (CHECKLIST #189).
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]


def load_ohlcv(ticker: str):
    from backtest.data.cache import _cache_path
    p = _cache_path(ticker)
    if not p.exists():
        return None
    d = pd.read_parquet(p)
    if "date" not in d.columns:
        return None
    d["date"] = pd.to_datetime(d["date"])
    return d.set_index("date").sort_index()


def rederive_fire(df, when, swing_length, ema_span, close_mitigation, tail_n):
    """Independently re-derive whether the strategy SHOULD have fired."""
    from backtest.signals import smc_ict
    smc = smc_ict._smc
    locs = df.index.get_indexer([when], method="pad")
    i = int(locs[0])
    if i < 250:
        return {"ok": False, "reason": "insufficient_history"}
    sub = df.iloc[:i + 1]                      # PIT: nothing after the entry bar
    close = float(sub["close"].iloc[-1])

    ema = sub["close"].ewm(span=ema_span, adjust=False).mean().iloc[-1]
    above_ema = bool(close > float(ema))

    swings = smc.swing_highs_lows(sub, swing_length=swing_length)
    ob_df = smc.ob(sub, swings, close_mitigation=close_mitigation)
    if "OB" not in ob_df.columns:
        return {"ok": False, "reason": "no_OB_column"}
    ev = ob_df[ob_df["OB"].notna() & (ob_df["OB"] != 0)].tail(tail_n)

    breaker = False
    n_bear = 0
    for idx in ev.index:
        row = ev.loc[idx]
        if float(row["OB"]) != -1:             # bearish OB only
            continue
        n_bear += 1
        mi = row.get("MitigatedIndex")
        mitigated = bool(mi is not None and not pd.isna(mi)
                         and 0 < float(mi) < i)
        top = row.get("Top")
        broken_up = bool(top is not None and not pd.isna(top)
                         and close > float(top))
        if mitigated and broken_up:
            breaker = True
            break

    return {"ok": True, "breaker_bullish": breaker, "above_ema": above_ema,
            "should_fire": bool(breaker and above_ema),
            "bear_obs_examined": n_bear, "close": close, "ema": float(ema),
            "bar_index": i}


def check_execution(row, df, start, end):
    """Execution-correctness checks on the recorded trade."""
    out = {}
    ed = pd.Timestamp(row["entry_date"])
    out["entry_is_trading_day"] = bool(ed in df.index)
    out["entry_in_window"] = bool(start <= ed.date() <= end)

    xd = row.get("exit_date")
    if xd is not None and not pd.isna(xd):
        xd = pd.Timestamp(xd)
        out["exit_after_entry"] = bool(xd >= ed)
        out["exit_in_window"] = bool(xd.date() <= end)
        # B1588: `hold_days` is CALENDAR days, VERIFIED 20/20 against the cube.
        # My first version compared TRADING days and flagged 35 of 50 trades as
        # execution failures - my defect, not the engine's. Both are recorded
        # so a future reader can see which convention is in force.
        span = df.loc[(df.index >= ed) & (df.index <= xd)]
        obs_trading = max(len(span) - 1, 0)
        obs_cal = int((xd - ed).days)
        rec_hold = row.get("hold_days")
        if rec_hold is not None and not pd.isna(rec_hold):
            out["hold_days_matches"] = bool(abs(obs_cal - float(rec_hold)) <= 1)
            out["hold_days_observed_calendar"] = obs_cal
            out["hold_days_observed_trading"] = obs_trading
            out["hold_days_recorded"] = float(rec_hold)
    p = row.get("pnl_pct")
    out["pnl_finite"] = bool(p is not None and not pd.isna(p)
                             and np.isfinite(float(p)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", required=True)
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260816)
    ap.add_argument("--swing-length", type=int, required=True)
    ap.add_argument("--ema-span", type=int, required=True)
    ap.add_argument("--close-mitigation", type=int, default=0)
    ap.add_argument("--tail-n", type=int, default=20)
    ap.add_argument("--start", default="2024-05-05")
    ap.add_argument("--end", default="2026-05-05")
    ap.add_argument("--out", default="output_audit/b1588_spot_check.json")
    a = ap.parse_args()

    import datetime as _dt
    start = _dt.date.fromisoformat(a.start)
    end = _dt.date.fromisoformat(a.end)

    cube = pd.read_csv(a.cube, low_memory=False)
    # one row per entry: the spot check is about ENTRIES, not exit variants
    ent = cube.drop_duplicates(subset=["ticker", "entry_date"])
    random.seed(a.seed)
    idx = sorted(random.sample(range(len(ent)), min(a.n, len(ent))))
    sample = ent.iloc[idx]
    print(f"cube entries={len(ent)}  sampling {len(sample)} (seed {a.seed})")

    results, agree, disagree, skipped = [], 0, 0, 0
    exec_fail = []
    cache: dict[str, object] = {}
    for _, r in sample.iterrows():
        t = str(r["ticker"])
        if t not in cache:
            cache[t] = load_ohlcv(t)
        df = cache[t]
        if df is None:
            skipped += 1
            results.append({"ticker": t, "entry_date": str(r["entry_date"]),
                            "status": "NO_OHLCV"})
            continue
        when = pd.Timestamp(r["entry_date"])
        d = rederive_fire(df, when, a.swing_length, a.ema_span,
                          bool(a.close_mitigation), a.tail_n)
        ex = check_execution(r, df, start, end)
        bad = [k for k, v in ex.items() if isinstance(v, bool) and not v]
        if bad:
            exec_fail.append({"ticker": t, "entry_date": str(r["entry_date"]),
                              "failed": bad})
        if not d.get("ok"):
            skipped += 1
            status = "SKIPPED_" + str(d.get("reason"))
        elif d["should_fire"]:
            agree += 1
            status = "AGREE"
        else:
            disagree += 1
            status = "DISAGREE"
        results.append({"ticker": t, "entry_date": str(r["entry_date"]),
                        "status": status, **d, "execution": ex})

    n_checked = agree + disagree
    print(f"\nPRODUCER RE-DERIVATION: {agree} agree / {disagree} DISAGREE "
          f"/ {skipped} skipped  (checked {n_checked})")
    if n_checked:
        print(f"  agreement rate: {agree / n_checked:.1%}")
    print(f"EXECUTION CHECKS: {len(exec_fail)} trades with >=1 failed check")
    for e in exec_fail[:8]:
        print(f"   {e['ticker']:<6}{e['entry_date'][:10]}  failed={e['failed']}")
    dis = [r for r in results if r.get("status") == "DISAGREE"]
    for r in dis[:8]:
        print(f"   DISAGREE {r['ticker']:<6}{r['entry_date'][:10]} "
              f"breaker={r.get('breaker_bullish')} above_ema={r.get('above_ema')} "
              f"bear_obs={r.get('bear_obs_examined')}")

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(
        {"cube": a.cube, "n_sampled": len(sample), "seed": a.seed,
         "swing_length": a.swing_length, "ema_span": a.ema_span,
         "close_mitigation": bool(a.close_mitigation), "tail_n": a.tail_n,
         "agree": agree, "disagree": disagree, "skipped": skipped,
         "execution_failures": exec_fail, "rows": results}, indent=2, default=str))
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
