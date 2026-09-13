#!/usr/bin/env python
"""S6-B2769: the offline re-derivation that makes hub-1's P2 and P3 gradable
without an engine run - IN THE TIGHTENING DIRECTION ONLY.

WHAT THIS IS AND IS NOT. The persistence census (S6-B2769) measured that 30 of
32 persisted smc_* keys are BOOLEANS already evaluated at the run's knob values,
so a stored `smc_liquidity_swept_dn=True` cannot say what it would be at a
different liquidity_range_pct. That is why hub-1's 0-of-3 subset_safe reading is
CORRECT and why "re-pricing" was refused. The breaker family gets 300 free
combinations a different way: tighten_breaker_block.diagnose_fire RECOMPUTES the
OB events from raw OHLCV per fire and survives() post-filters them offline. This
file is that mechanism for the liquidity family.

IT CALLS THE LIBRARY, IT DOES NOT RE-IMPLEMENT IT. spot_check_smc_lsr.py's
docstring declines to hand-write `_smc.liquidity` / `_smc.bos_choch` as "a fourth
implementation of library code and a new divergence surface", and that objection
would apply here too - except the breaker's precedent calls `_smc.ob` rather
than reimplementing it, and so does this: `_smc.swing_highs_lows`,
`_smc.liquidity` and `_smc.bos_choch` are invoked exactly as production invokes
them. No primitive is re-derived by hand.

WHY TIGHTENING ONLY. A LOOSER level admits bars the recorded cube never
evaluated - the fire set would have to grow, and nothing offline can invent
trades. A TIGHTER level can only remove fires, so the survivor set is a strict
subset of what the engine already recorded and every statistic over it is
honest. The grader must therefore never offer a level looser than the cube's.

HOW PRODUCTION DECIDES, reproduced exactly (smc_ict.py:263, :458-466, :503-509):
    current_idx = len(ohlc) - 1                     # a POSITION
    _most_recent_event_within(series, current_idx, recency_bars)
        -> the LAST non-zero event's VALUE, if current_idx - its_index <= recency
The library returns RangeIndex-indexed frames even from a DatetimeIndex input
(VERIFIED on AAPL), so that subtraction is position arithmetic. Note the helper
reads the LAST event only: if the most recent liquidity event is an UP-sweep,
swept_dn is False no matter how recent an earlier DOWN-sweep was. This file
records (age, value) rather than a per-direction age, so that asymmetry is
preserved rather than smoothed away.

SAMPLING PROVENANCE (#201 / B1801). When --n is set, a seeded RNG chooses WHICH
fires are diagnosed. That row SELECTION is therefore SYNTHETIC - reproducible
from --seed, and a different seed diagnoses a different subset - while every
VALUE reported (each event's age and sign, the reproduction rate, the survivor
counts) is MEASURED from real OHLCV through the production primitives. A figure
from this file binds the sampled subset, never the population, and the artifact
records `sampled` beside `diagnosed` so a reader can see which it is. Pass
--n 0 to diagnose every fire and remove the sampling question entirely.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backtest.signals import smc_ict as _S  # noqa: E402

_smc = _S._smc
STRAT = "smc_liquidity_sweep_reversal"

# P2 band, from the SPECS entry. PRODUCTION FIRST - the grader may only offer
# levels at or below the cube's own, and ordering them this way makes a
# violation visible in the artifact rather than implicit.
RANGE_BAND = [0.01, 0.005]
PRODUCTION_RANGE = 0.01
PRODUCTION_RECENCY = 90
# P3 band restricted to the tightening half of [30, 60, 90, 120, 180]
RECENCY_BAND = [90, 60, 30]

# the engine's own warmup floor for this family (breaker uses the same)
MIN_BARS = 250


def _last_event(series: pd.Series, current_idx: int) -> tuple:
    """(age_bars, value) of the LAST non-zero event, or (None, None).

    Deliberately NOT filtered by a recency window: the window is what we want
    to vary offline, so the AGE is recorded and compared later. This is the
    only place production's semantics are re-expressed, and it is one line of
    it - `_most_recent_event_within` applies the cap, this returns the distance.
    """
    nz = series[series.fillna(0) != 0]
    if nz.empty:
        return (None, None)
    last = nz.index[-1]
    return (int(current_idx - last), int(nz.iloc[-1]))


def diagnose_fire(df: pd.DataFrame, when, swing_length: int = 20,
                  range_levels=None) -> dict | None:
    """Per-fire event geometry for hub-1, at every candidate P2 level.

    PIT preserved: the producer sees df.iloc[:i+1] only, exactly as production.
    Returns None when the bar cannot be located or the warmup floor is unmet -
    a fire that cannot be re-derived is DROPPED and counted, never guessed
    (S6-B1584a: a biased 60pct subsample is worse than a smaller honest one).
    """
    levels = list(RANGE_BAND if range_levels is None else range_levels)
    locs = df.index.get_indexer([pd.Timestamp(when)], method="pad")
    i = int(locs[0])
    if i < MIN_BARS:
        return None
    sub = df.iloc[:i + 1]
    current_idx = len(sub) - 1           # smc_ict.py:263
    try:
        swings = _smc.swing_highs_lows(sub, swing_length=swing_length)
        bos_df = _smc.bos_choch(sub, swings)
    except Exception as exc:                       # never silent
        return {"error": f"{type(exc).__name__}: {exc}"}
    if bos_df is None or "BOS" not in bos_df.columns:
        return None

    bos_age, bos_val = _last_event(bos_df["BOS"], current_idx)
    choch_age, choch_val = (_last_event(bos_df["CHOCH"], current_idx)
                            if "CHOCH" in bos_df.columns else (None, None))

    liq = {}
    for r in levels:
        try:
            ldf = _smc.liquidity(sub, swings, range_percent=float(r))
        except Exception as exc:
            liq[str(r)] = {"error": f"{type(exc).__name__}: {exc}"}
            continue
        if ldf is None or "Liquidity" not in ldf.columns:
            liq[str(r)] = {"age": None, "val": None}
            continue
        a, v = _last_event(ldf["Liquidity"], current_idx)
        liq[str(r)] = {"age": a, "val": v}

    return {"bar_index": i, "swing_length": swing_length,
            "bos": {"age": bos_age, "val": bos_val},
            "choch": {"age": choch_age, "val": choch_val},
            "liq": liq}


def survives(diag: dict, direction: str, range_pct: float,
             recency: int) -> bool | None:
    """Would this fire still fire at (range_pct, recency)?

    Reproduces the strategy gate exactly:
        long  = swept_dn  AND (choch_bullish OR bos_bullish)
        short = swept_up  AND (choch_bearish OR bos_bearish)
    None when the level was not diagnosed - an unknown is never a survival.
    """
    if not isinstance(diag, dict) or "liq" not in diag:
        return None
    cell = diag["liq"].get(str(range_pct))
    if not isinstance(cell, dict) or "age" not in cell:
        return None
    d = str(direction).lower()
    if d not in ("long", "short"):
        return None
    want_liq = -1 if d == "long" else 1       # swept_dn for long
    want_conf = 1 if d == "long" else -1      # bullish for long

    if cell["age"] is None or cell["age"] > recency or cell["val"] != want_liq:
        return False
    for k in ("choch", "bos"):
        e = diag.get(k) or {}
        if (e.get("age") is not None and e["age"] <= recency
                and e.get("val") == want_conf):
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", default="output_r5_merged_1_7",
                    help="cube DIRECTORY whose trade_log.csv names the fires")
    ap.add_argument("--n", type=int, default=200,
                    help="fires to diagnose; 0 = all")
    ap.add_argument("--seed", type=int, default=20260913)
    ap.add_argument("--swing-length", type=int, default=20)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()

    cube = Path(a.cube)
    tl_p = cube / "trade_log.csv"
    if not tl_p.exists():
        raise SystemExit(f"REFUSED: {tl_p} does not exist (fail closed)")
    tl = pd.read_csv(tl_p, low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "direction"])
    fam = tl[tl.strategy == STRAT].drop_duplicates(["ticker", "entry_date"])
    if fam.empty:
        raise SystemExit(f"REFUSED: no {STRAT} rows in {tl_p}")
    rows = fam.to_dict("records")
    if a.n:
        random.Random(a.seed).shuffle(rows)
        rows = rows[: a.n]

    from backtest.data.cache import _cache_path
    cache: dict[str, pd.DataFrame | None] = {}

    def ohlc(tkr: str):
        if tkr not in cache:
            p = _cache_path(tkr)
            if not p.exists():
                cache[tkr] = None
            else:
                d = pd.read_parquet(p)
                if "date" not in d.columns:
                    cache[tkr] = None
                else:
                    d["date"] = pd.to_datetime(d["date"])
                    cache[tkr] = d.set_index("date").sort_index()
        return cache[tkr]

    diags, dropped = [], {"no_cache": 0, "not_derivable": 0, "producer_error": 0}
    for r in rows:
        df = ohlc(str(r["ticker"]))
        if df is None:
            dropped["no_cache"] += 1
            continue
        d = diagnose_fire(df, r["entry_date"], swing_length=a.swing_length)
        if d is None:
            dropped["not_derivable"] += 1
            continue
        if "error" in d:
            dropped["producer_error"] += 1
            continue
        d["ticker"] = r["ticker"]
        d["entry_date"] = str(r["entry_date"])
        d["direction"] = r.get("direction")
        diags.append(d)

    # THE REPRODUCTION CONTROL. At the cube's own knobs every diagnosed fire
    # must survive - the engine recorded it firing there. A shortfall means the
    # re-derivation disagrees with the producer and NOTHING below it is usable
    # (S6-B1584a: cfg2 was graded at the wrong swing_length and lost 167 of 420
    # fires as a biased subsample).
    repro = sum(1 for d in diags
                if survives(d, d["direction"], PRODUCTION_RANGE,
                            PRODUCTION_RECENCY))
    rate = (repro / len(diags)) if diags else 0.0

    grid = []
    for rg in RANGE_BAND:
        for rc in RECENCY_BAND:
            kept = sum(1 for d in diags
                       if survives(d, d["direction"], rg, rc))
            grid.append({"liquidity_range_pct": rg, "event_recency_bars": rc,
                         "fires_kept": kept,
                         "share_of_reproduced": round(kept / repro, 4)
                         if repro else None,
                         "is_production": rg == PRODUCTION_RANGE
                         and rc == PRODUCTION_RECENCY})

    rec = {"strategy": STRAT,
           "generator": "scripts/diagnose_smc_lsr.py",
           "cube": str(cube),
           "swing_length": a.swing_length,
           "sampled": len(rows), "diagnosed": len(diags), "dropped": dropped,
           "reproduction": {
               "at": {"liquidity_range_pct": PRODUCTION_RANGE,
                      "event_recency_bars": PRODUCTION_RECENCY},
               "survivors": repro, "of": len(diags), "rate": round(rate, 4),
               "note": ("every diagnosed fire MUST survive at the cube's own "
                        "knobs - the engine recorded it firing there. A rate "
                        "below 1.0 means the re-derivation disagrees with the "
                        "producer and the grid below is NOT usable")},
           "direction_limit": ("TIGHTENING ONLY. A looser level admits bars the "
                               "cube never evaluated; nothing offline can "
                               "invent trades. Every level here is at or below "
                               "production"),
           "grid": grid,
           "diagnoses": diags}
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"diagnosed {len(diags)} of {len(rows)} in {time.time()-t0:.0f}s "
          f"({dropped})")
    print(f"REPRODUCTION at production knobs: {repro} of {len(diags)} "
          f"({rate:.1%})")
    for g in grid:
        print(f"  range={g['liquidity_range_pct']:<6} "
              f"recency={g['event_recency_bars']:<4} "
              f"kept={g['fires_kept']}"
              f"{'   <- production' if g['is_production'] else ''}")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
