#!/usr/bin/env python
"""B2819 (S6-B2752): the SHARED spot check for the no-free-axis smc
registrations (smc_equal_lows_sweep_long, smc_inverse_fvg).

One checker per family is the L754 contract, and the B2724 defect is a checker
re-deriving a condition the strategy does not read - so the gate keys here are
a PER-STRATEGY table, and an unknown strategy is refused rather than guessed.

UNLIKE hub-2, LEG A IS FULLY SIGHTED: every gate key of both strategies is
persisted in signals_at_entry (measured against the 28-key persisted smc_*
census - smc_equal_lows_swept, smc_fvg_bullish_active,
smc_inverse_fvg_bullish/bearish all persist), so the cube-vs-producer
comparison covers the WHOLE gate, not a fragment.

  LEG A - the CUBE's persisted signals for the gate keys
  LEG B - the ENGINE producer (smc_ict.compute_smc_signals) recomputed at the
          same bar with THIS config's knobs
  LEG C - execution correctness (entry bar exists, window, hold_days, pnl)

SAMPLING PROVENANCE (#201): the seeded RNG picks WHICH entries are checked -
row selection is SYNTHETIC (reproducible from --seed); every reported value is
MEASURED. A verdict binds the sampled subset, never the population.
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

# gate keys per strategy and leg, READ from screener source (B2819), never
# recalled. The trend legs of smc_inverse_fvg ride ema-200 keys that are
# persisted technical booleans.
# A term is a persisted key (AND leg) or a TUPLE of keys (any-of / OR leg).
# B2822 CORRECTION: the first shipped table omitted inverse_fvg's THIRD leg -
# vol_spike_2x OR force_index_cross_up (Batch 262's volume confirmation) -
# because the source read stopped at the base keys. Both vol keys are
# persisted at 1.000 coverage (measured on 300 R5 rows), so LEG A sights the
# WHOLE gate once the leg is present; without it cube_would_fire overcounted.
GATES = {
    "smc_equal_lows_sweep_long": {
        "long": ("smc_equal_lows_swept", "smc_fvg_bullish_active"),
    },
    "smc_inverse_fvg": {
        "long": ("smc_inverse_fvg_bullish", "price_above_ema_200",
                 ("vol_spike_2x", "force_index_cross_up")),
        "short": ("smc_inverse_fvg_bearish", "below_ema_200",
                  ("vol_spike_2x", "force_index_cross_up")),
    },
}


def _flat(keys):
    out = []
    for t in keys:
        out.extend(t if isinstance(t, tuple) else (t,))
    return out


def _term_fires(vals: dict, term) -> bool:
    if isinstance(term, tuple):
        return any(bool(vals.get(k)) for k in term)
    return bool(vals.get(term))
# keys the smc producer can recompute; technical keys are cube-only and are
# COUNTED as such rather than silently compared against a producer that
# never emits them (the B2724 shape).
SMC_RECOMPUTABLE = ("smc_equal_lows_swept", "smc_fvg_bullish_active",
                    "smc_inverse_fvg_bullish", "smc_inverse_fvg_bearish")


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
    import ast as _ast
    if not isinstance(raw, str) or not raw.strip():
        return {}
    for reader in (json.loads, _ast.literal_eval):
        try:
            v = reader(raw)
        except (ValueError, SyntaxError, TypeError):
            continue
        if isinstance(v, dict):
            return v
    return {}


def compare_legs(strat, df, when, direction, persisted, knobs) -> dict:
    from backtest.signals import smc_ict
    keys = GATES[strat].get(str(direction).lower())
    if keys is None:
        return {"ok": False, "why": f"unknown direction {direction!r}"}
    idx = df.index.searchsorted(pd.Timestamp(when))
    if idx >= len(df):
        return {"ok": False, "why": "entry bar past the end of the cache"}
    sub = df.iloc[: idx + 1]
    if len(sub) < 120:
        return {"ok": False, "why": f"only {len(sub)} bars before the entry"}

    eng, err = {}, None
    try:
        eng = smc_ict.compute_smc_signals(
            sub, swing_length=knobs["swing_length"],
            liquidity_range_pct=knobs["liquidity_range_pct"],
            event_recency_bars=knobs["event_recency_bars"])
    except Exception as exc:                        # never silent
        err = f"{type(exc).__name__}: {exc}"

    def _b(d, k):
        v = d.get(k)
        return None if v is None else bool(v)

    flat = _flat(keys)
    a = {k: _b(persisted, k) for k in flat}
    smc_keys = [k for k in flat if k in SMC_RECOMPUTABLE]
    b = {k: _b(eng, k) for k in smc_keys}
    disagree = [k for k in smc_keys
                if a[k] is not None and b[k] is not None and a[k] != b[k]]
    a_fire = all(_term_fires(a, t) for t in keys)
    return {"ok": err is None, "why": err or "",
            "cube": a, "engine_smc": b,
            "cube_would_fire": a_fire,
            "keys_comparable": len([k for k in smc_keys if a[k] is not None]),
            "keys_disagree": disagree,
            "technical_keys_cube_only": [k for k in flat
                                         if k not in SMC_RECOMPUTABLE],
            "bar_index": int(idx)}


def check_execution(row, df, start, end) -> dict:
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
    ap.add_argument("--strategy", required=True, choices=sorted(GATES))
    ap.add_argument("--cube", required=True)
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260915)
    # B2820: production defaults rather than required - smc_inverse_fvg's
    # keys are knob-independent (fvg takes no swings; the inverse logic is
    # lookback/tolerance-hardcoded, smc_ict.py:296-360), so forcing its
    # battery call to invent knob values would be the S6-B2136 lie in
    # reverse. A family whose keys DO ride the knobs passes them via the
    # tools flags exactly as before.
    ap.add_argument("--swing-length", type=int, default=20)
    ap.add_argument("--liquidity-range-pct", type=float, default=0.01)
    ap.add_argument("--event-recency-bars", type=int, default=90)
    ap.add_argument("--start", default="2024-05-05")
    ap.add_argument("--end", default="2026-05-05")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    strat = a.strategy

    cube_dir = Path(a.cube)
    if cube_dir.is_file():
        cube_dir = cube_dir.parent
    tl_p = cube_dir / "trade_log.csv"
    if not tl_p.exists():
        raise SystemExit(f"REFUSED: {tl_p} does not exist (fail closed)")
    out_p = Path(a.out) if a.out else (
        ROOT / "output_audit" / f"{cube_dir.name}_{strat}_spot_check.json")

    tl = pd.read_csv(tl_p, low_memory=False)
    tl = tl[tl["strategy"] == strat]
    if tl.empty:
        raise SystemExit(f"REFUSED: no {strat} rows in {tl_p} (fail closed)")
    if "signals_at_entry" not in tl.columns:
        raise SystemExit("REFUSED: no signals_at_entry - LEG A unavailable")

    rows = tl.drop_duplicates(subset=["ticker", "entry_date"]).to_dict("records")
    random.Random(a.seed).shuffle(rows)
    rows = rows[: a.n]
    knobs = {"swing_length": a.swing_length,
             "liquidity_range_pct": a.liquidity_range_pct,
             "event_recency_bars": a.event_recency_bars}

    recs, agree, disagree, skipped = [], 0, 0, 0
    for r in rows:
        df = load_ohlcv(str(r["ticker"]))
        legs = ({"ok": False, "why": "no cached OHLCV"} if df is None else
                compare_legs(strat, df, r["entry_date"], r.get("direction"),
                             _parse_signals(r.get("signals_at_entry")), knobs))
        if not legs.get("ok"):
            skipped += 1
        elif legs["keys_disagree"]:
            disagree += 1
        else:
            agree += 1
        recs.append({"ticker": r["ticker"], "entry_date": str(r["entry_date"]),
                     "direction": r.get("direction"), "legs": legs,
                     "execution": check_execution(r, df, a.start, a.end)})

    rec = {"strategy": strat, "cube": str(cube_dir), "knobs": knobs,
           "sampled": len(recs), "seed": a.seed,
           "smc_keys_agree": agree, "smc_keys_disagree": disagree,
           "unevaluable": skipped,
           "legs_disclosure": (
               "TWO PRODUCERS plus execution checks: LEG A is the cube's "
               "persisted signals (FULL gate coverage - every key persists), "
               "LEG B recomputes the SMC keys only; technical keys "
               "(ema/below) are cube-only and counted as such. An A-vs-B "
               "disagreement localises to persist path or producer."),
           "rows": recs}
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
    print(f"VERDICT: {agree} agree / {disagree} disagree / {skipped} "
          f"unevaluable of {len(recs)} sampled")
    print(f"wrote {out_p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
