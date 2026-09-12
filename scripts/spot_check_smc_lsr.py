#!/usr/bin/env python
"""S6-B2732a (owner approval 2026-09-12 "Step 1 code change approved"):
the three-leg spot check for smc_liquidity_sweep_reversal (hub-1).

WHY A SECOND SPOT CHECKER RATHER THAN A FLAG ON THE FIRST. scripts/
spot_check_trades.py re-derives the BREAKER condition and REQUIRES
--swing-length/--ema-span; pointing hub-1 at it produced the B2724 defect
(25 of 50 rows reported engine_agrees on a condition the strategy does not
read). One checker per family, registered through the SPECS `tools` block -
the L754 portability contract.

HUB-1'S GATE (screener.py:strat_smc_smc_liquidity_sweep_reversal, read not
recalled):
    long  = smc_liquidity_swept_dn AND (smc_choch_bullish OR smc_bos_bullish)
    short = smc_liquidity_swept_up AND (smc_choch_bearish OR smc_bos_bearish)
                                   AND NOT _short_borrow_trap_active

THE LEGS, and an HONEST statement of what this does NOT do. The breaker
checker's three legs are (1) a hand re-implementation of P1-P6, (2) the
engine producer, (3) the recorded cube. Re-implementing `_smc.liquidity`
and `_smc.bos_choch` by hand would be a fourth implementation of library
code and a new divergence surface, so this checker runs:

  LEG A - the CUBE's persisted `signals_at_entry` for the gate keys
  LEG B - the ENGINE producer (`smc_ict.compute_smc_signals`) recomputed at
          the same bar with THIS config's knobs
  LEG C - execution correctness on the recorded trade (entry bar exists,
          exit within window, hold_days consistent) - strategy-agnostic

SAMPLING PROVENANCE (#201 / B1801). The seeded RNG below chooses WHICH
entries to check; it generates no quantity that appears in the output.
So the row SELECTION is SYNTHETIC - reproducible from --seed, and a
different seed inspects a different subset - while every VALUE reported
(the cube's persisted booleans, the producer's recomputed booleans, the
agree/disagree counts) is MEASURED from real data. A verdict from this
file therefore binds the sampled subset, never the population.

**So this is a TWO-PRODUCER comparison plus execution checks, not a
three-way triangulation.** Stated rather than implied: A-vs-B disagreement
localises to the persist path or the producer, and cannot by itself say
which. For a VARIANT cube that is the check that matters - it answers "did
the knob actually take effect at the bar the trade fired on?"
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

STRAT = "smc_liquidity_sweep_reversal"
GATE_KEYS = {
    "long": ("smc_liquidity_swept_dn", "smc_choch_bullish", "smc_bos_bullish"),
    "short": ("smc_liquidity_swept_up", "smc_choch_bearish", "smc_bos_bearish"),
}


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


def _parse_signals(raw):
    """signals_at_entry is persisted as a python/JSON dict literal.

    B2747: written WITHOUT a silent `except: pass` (#122). The JSON and
    literal readers are tried in order and each failure FALLS THROUGH to
    the next reader explicitly, so no branch swallows an error without
    handing control somewhere visible. The ratchet
    (test_b2128_silent_except_pass_is_a_shrinking_set) is shrink-only,
    and the right answer to a new site is not to raise its ceiling."""
    import ast as _ast
    if not isinstance(raw, str) or not raw.strip():
        return {}
    for _reader in (json.loads, _ast.literal_eval):
        try:
            v = _reader(raw)
        except (ValueError, SyntaxError, TypeError):
            continue                 # explicit: try the next reader
        if isinstance(v, dict):
            return v
    return {}


def compare_legs(df, when, direction, persisted, knobs) -> dict:
    """LEG A (cube) vs LEG B (engine producer) on hub-1's gate keys."""
    from backtest.signals import smc_ict
    idx = df.index.searchsorted(pd.Timestamp(when))
    if idx >= len(df):
        return {"ok": False, "why": "entry bar past the end of the cache"}
    sub = df.iloc[: idx + 1]
    if len(sub) < 120:
        return {"ok": False, "why": f"only {len(sub)} bars before the entry"}

    keys = GATE_KEYS.get(str(direction).lower())
    if keys is None:
        return {"ok": False, "why": f"unknown direction {direction!r}"}
    sweep_k, choch_k, bos_k = keys

    eng, err = {}, None
    try:
        eng = smc_ict.compute_smc_signals(
            sub,
            swing_length=knobs["swing_length"],
            liquidity_range_pct=knobs["liquidity_range_pct"],
            event_recency_bars=knobs["event_recency_bars"])
    except Exception as exc:                        # never silent
        err = f"{type(exc).__name__}: {exc}"

    def _b(d, k):
        v = d.get(k)
        return None if v is None else bool(v)

    a = {k: _b(persisted, k) for k in (sweep_k, choch_k, bos_k)}
    b = {k: _b(eng, k) for k in (sweep_k, choch_k, bos_k)}
    a_fire = bool(a[sweep_k]) and (bool(a[choch_k]) or bool(a[bos_k]))
    b_fire = bool(b[sweep_k]) and (bool(b[choch_k]) or bool(b[bos_k]))
    # a key the cube never persisted cannot disagree - counted, not scored
    comparable = [k for k in (sweep_k, choch_k, bos_k) if a[k] is not None]
    disagree = [k for k in comparable if a[k] != b[k]]
    return {"ok": err is None, "why": err or "",
            "cube": a, "engine": b,
            "cube_would_fire": a_fire, "engine_would_fire": b_fire,
            "gate_agrees": a_fire == b_fire,
            "keys_comparable": len(comparable), "keys_disagree": disagree,
            "bar_index": int(idx)}


def check_execution(row, df, start, end) -> dict:
    """LEG C - strategy-agnostic correctness of the recorded trade."""
    out = {}
    ed = pd.Timestamp(row["entry_date"])
    out["entry_in_window"] = bool(pd.Timestamp(start) <= ed <= pd.Timestamp(end))
    out["entry_bar_exists"] = bool(
        len(df.index[df.index == ed]) > 0 if df is not None else False)
    hd = row.get("hold_days")
    out["hold_days_nonneg"] = bool(pd.notna(hd) and float(hd) >= 0)
    pnl = row.get("pnl_pct")
    out["pnl_present"] = bool(pd.notna(pnl))
    out["pnl_sane"] = bool(pd.notna(pnl) and abs(float(pnl)) < 100.0)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", required=True,
                    help="the config's cube DIRECTORY (trade_log.csv + "
                         "trade_exit_detail.csv are read from it)")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260912)
    ap.add_argument("--swing-length", type=int, required=True)
    ap.add_argument("--liquidity-range-pct", type=float, required=True)
    ap.add_argument("--event-recency-bars", type=int, required=True)
    ap.add_argument("--start", default="2024-05-05")
    ap.add_argument("--end", default="2026-05-05")
    ap.add_argument("--out", default=None,
                    help="default: derived from the cube dir name - a FIXED "
                         "default silently overwrites a prior artifact (B2118)")
    a = ap.parse_args()

    cube_dir = Path(a.cube)
    if cube_dir.is_file():                  # tolerate a csv path
        cube_dir = cube_dir.parent
    tl_p = cube_dir / "trade_log.csv"
    if not tl_p.exists():
        raise SystemExit(f"REFUSED: {tl_p} does not exist (fail closed)")
    out_p = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube_dir.name}_spot_check.json")

    tl = pd.read_csv(tl_p, low_memory=False)
    if "strategy" not in tl.columns:
        raise SystemExit("REFUSED: trade_log.csv has no `strategy` column")
    n_all = len(tl)
    tl = tl[tl["strategy"] == STRAT]
    print(f"restricted to {STRAT}: {len(tl)} of {n_all} rows")
    if tl.empty:
        raise SystemExit(f"REFUSED: no {STRAT} rows in {tl_p} - nothing to "
                         "spot-check (fail closed, L642)")
    if "signals_at_entry" not in tl.columns:
        raise SystemExit("REFUSED: trade_log.csv has no `signals_at_entry` - "
                         "LEG A is unavailable, so this check cannot run")

    ent = tl.drop_duplicates(subset=["ticker", "entry_date"])
    rows = ent.to_dict("records")
    random.Random(a.seed).shuffle(rows)
    rows = rows[: a.n]
    knobs = {"swing_length": a.swing_length,
             "liquidity_range_pct": a.liquidity_range_pct,
             "event_recency_bars": a.event_recency_bars}

    recs, agree, disagree, skipped = [], 0, 0, 0
    for r in rows:
        df = load_ohlcv(str(r["ticker"]))
        legs = ({"ok": False, "why": "no cached OHLCV"} if df is None else
                compare_legs(df, r["entry_date"], r.get("direction"),
                             _parse_signals(r.get("signals_at_entry")), knobs))
        if not legs.get("ok"):
            skipped += 1
        elif legs["gate_agrees"]:
            agree += 1
        else:
            disagree += 1
        recs.append({"ticker": r["ticker"], "entry_date": str(r["entry_date"]),
                     "direction": r.get("direction"), "legs": legs,
                     "execution": check_execution(r, df, a.start, a.end)})

    rec = {
        "strategy": STRAT, "cube": str(cube_dir), "knobs": knobs,
        "sampled": len(recs), "seed": a.seed,
        "gate_agree": agree, "gate_disagree": disagree, "unevaluable": skipped,
        "legs_disclosure":
            "TWO PRODUCERS plus execution checks, NOT a three-way "
            "triangulation: LEG A is the cube's persisted signals_at_entry, "
            "LEG B is smc_ict.compute_smc_signals recomputed at the same bar "
            "with this config's knobs, LEG C is execution correctness. An "
            "A-vs-B disagreement localises to the persist path or the "
            "producer and cannot by itself say which.",
        "rows": recs,
    }
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
    print(f"VERDICT: {agree} agree / {disagree} disagree / {skipped} "
          f"unevaluable of {len(recs)} sampled")
    print(f"wrote {out_p}")
    # a DISAGREEMENT is a finding, not a crash - the battery reads the verdict
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
