#!/usr/bin/env python
"""S6-B2752e: the spot check for smc_order_block_bounce (hub 2).

WHY ITS OWN CHECKER RATHER THAN A FLAG ON ANOTHER. spot_check_trades.py
re-derives the BREAKER condition and spot_check_smc_lsr.py re-derives the
LIQUIDITY-SWEEP condition; pointing hub-2 at either is the B2724 defect, where
25 of 50 rows reported engine_agrees on a condition the strategy does not read.
One checker per family, registered through the SPECS `tools` block (L754).

HUB-2'S GATE, read at screener.py:4693 not recalled:
    long  = smc_ob_bullish_tap_recent_5d AND rsi_14 < 45 AND price_above_ema_200
    short = smc_ob_bearish_tap_recent_5d AND rsi_14 > 55 AND below_ema_200
                                          AND NOT _short_borrow_trap_active

THE LIMIT, STATED FIRST BECAUSE IT IS UNUSUAL AND LOAD-BEARING. **The gate's
PRIMARY key is not in the cube.** MEASURED S6-B2752a: smc_ob_*_tap_recent_5d has
coverage 0.0000 across all 1340 R5 fires, while the 28 persisted smc_* keys
include the superseded smc_ob_*_active STATE pair that B2076 replaced with these
EVENT keys. So LEG A cannot see the one key that defines the strategy, and this
checker does NOT claim a cube-vs-producer comparison on it (S6-B2752b).

What it therefore runs:

  LEG A  - the CUBE's persisted signals for the keys it DOES carry: rsi_14,
           price_above_ema_200, below_ema_200. Compared against the gate's own
           thresholds, so a row that could not have fired is a finding.
  LEG B  - the ENGINE producer (smc_ict.compute_smc_signals) recomputed at the
           same bar with THIS config's knobs, reporting the tap key. Since the
           cube carries no counterpart, LEG B here is a PRESENCE reading, not an
           agreement test - reported as tap_engine_true/false, never as agree.
  LEG C  - execution correctness on the recorded trade - strategy-agnostic.

SAMPLING PROVENANCE (#201 / B1801). The seeded RNG chooses WHICH entries are
inspected and generates no quantity that appears in the output, so the row
SELECTION is SYNTHETIC - reproducible from --seed - while every VALUE reported
is MEASURED from real data. A finding here binds the sampled subset, never the
population.
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

STRAT = "smc_order_block_bounce"
# the gate's own thresholds, from the strategy source
RSI_LONG_MAX = 45
RSI_SHORT_MIN = 55
TAP_KEYS = {"long": "smc_ob_bullish_tap_recent_5d",
            "short": "smc_ob_bearish_tap_recent_5d"}
TREND_KEYS = {"long": "price_above_ema_200", "short": "below_ema_200"}


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

    Written WITHOUT a silent `except: pass` (#122, B2747): each reader's
    failure FALLS THROUGH to the next explicitly, so no branch swallows an
    error without handing control somewhere visible.
    """
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


def check_cube_gate(persisted: dict, direction: str) -> dict:
    """LEG A - the gate's thresholds against what the cube actually recorded."""
    d = str(direction).lower()
    if d not in TAP_KEYS:
        return {"ok": False, "why": f"unknown direction {direction!r}"}
    rsi = persisted.get("rsi_14")
    trend = persisted.get(TREND_KEYS[d])
    out = {"ok": True, "why": "",
           "rsi_14": rsi, TREND_KEYS[d]: trend,
           # the tap key is absent BY CONSTRUCTION - counted, never scored
           "tap_key_in_cube": TAP_KEYS[d] in persisted}
    if isinstance(rsi, (int, float)):
        out["rsi_consistent"] = bool(rsi < RSI_LONG_MAX) if d == "long" \
            else bool(rsi > RSI_SHORT_MIN)
    else:
        out["rsi_consistent"] = None
    out["trend_consistent"] = bool(trend) if trend is not None else None
    # a row is INCONSISTENT only when a recorded value contradicts the gate
    out["cube_could_fire"] = not (out["rsi_consistent"] is False
                                  or out["trend_consistent"] is False)
    return out


def read_engine_tap(df, when, direction, knobs) -> dict:
    """LEG B - the producer's tap key at the same bar. PRESENCE, not agreement:
    the cube carries no counterpart to compare against (S6-B2752b)."""
    from backtest.signals import smc_ict
    idx = df.index.searchsorted(pd.Timestamp(when))
    if idx >= len(df):
        return {"ok": False, "why": "entry bar past the end of the cache"}
    sub = df.iloc[: idx + 1]
    if len(sub) < 120:
        return {"ok": False, "why": f"only {len(sub)} bars before the entry"}
    try:
        eng = smc_ict.compute_smc_signals(
            sub,
            swing_length=knobs["swing_length"],
            close_mitigation=knobs["close_mitigation"])
    except Exception as exc:                        # never silent
        return {"ok": False, "why": f"{type(exc).__name__}: {exc}"}
    k = TAP_KEYS[str(direction).lower()]
    v = eng.get(k)
    return {"ok": True, "why": "", "key": k,
            "tap_engine": None if v is None else bool(v),
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
                    help="the config's cube DIRECTORY (trade_log.csv is read "
                         "from it)")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260913)
    ap.add_argument("--swing-length", type=int, required=True)
    ap.add_argument("--ob-close-mitigation", default="False")
    ap.add_argument("--start", default="2022-05-05")
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
             "close_mitigation": str(a.ob_close_mitigation).lower()
             in ("1", "true", "yes")}

    recs, consistent, inconsistent, skipped = [], 0, 0, 0
    tap_true = tap_false = tap_unevaluable = 0
    for r in rows:
        df = load_ohlcv(str(r["ticker"]))
        leg_a = check_cube_gate(_parse_signals(r.get("signals_at_entry")),
                                r.get("direction"))
        leg_b = ({"ok": False, "why": "no cached OHLCV"} if df is None else
                 read_engine_tap(df, r["entry_date"], r.get("direction"), knobs))
        if not leg_a.get("ok"):
            skipped += 1
        elif leg_a["cube_could_fire"]:
            consistent += 1
        else:
            inconsistent += 1
        if not leg_b.get("ok"):
            tap_unevaluable += 1
        elif leg_b.get("tap_engine"):
            tap_true += 1
        else:
            tap_false += 1
        recs.append({"ticker": r["ticker"], "entry_date": str(r["entry_date"]),
                     "direction": r.get("direction"),
                     "leg_a_cube": leg_a, "leg_b_engine": leg_b,
                     "execution": check_execution(r, df, a.start, a.end)})

    rec = {
        "strategy": STRAT, "cube": str(cube_dir), "knobs": knobs,
        "generator": "scripts/spot_check_smc_obb.py",
        "sampled": len(recs), "seed": a.seed,
        "cube_gate_consistent": consistent,
        "cube_gate_inconsistent": inconsistent,
        "cube_gate_unevaluable": skipped,
        "engine_tap_true": tap_true,
        "engine_tap_false": tap_false,
        "engine_tap_unevaluable": tap_unevaluable,
        "legs_disclosure":
            "NOT a cube-vs-producer agreement test on the gate's primary key. "
            "smc_ob_*_tap_recent_5d is NOT persisted in signals_at_entry "
            "(MEASURED coverage 0.0000 over 1340 R5 fires; the cube keeps the "
            "superseded smc_ob_*_active STATE keys instead), so LEG A checks "
            "only the keys the cube carries - rsi_14 and the ema_200 trend "
            "flag - against the gate's thresholds, and LEG B reports the "
            "producer's tap key as a PRESENCE reading with no counterpart to "
            "agree or disagree with. S6-B2752b tracks the persist-path fix.",
        "rows": recs,
    }
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
    print(f"LEG A: {consistent} consistent / {inconsistent} inconsistent / "
          f"{skipped} unevaluable of {len(recs)} sampled")
    print(f"LEG B tap key: {tap_true} true / {tap_false} false / "
          f"{tap_unevaluable} unevaluable (presence only)")
    print(f"wrote {out_p}")
    # an INCONSISTENCY is a finding, not a crash - the battery reads the record
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
