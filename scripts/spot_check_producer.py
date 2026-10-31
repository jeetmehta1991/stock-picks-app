#!/usr/bin/env python
"""S6-B3248 / S6-B3304 (B3139q-r162): the three-leg spot check for ANY SPECS
family whose swept axes are PRODUCER env knobs - the registry names the
producer, the key each leg's fire reads and an optional independent
re-derivation, so a family joins by registration (#291), never by a copy.

THREE LEGS per sampled landed fire (ticker, entry_date, direction):
  leg A  INDEPENDENT - the family's own raw-bar arithmetic, declared in
         SPECS[<strategy>]['tools']['spot_check']['leg_a'] as
         'module:function' under scripts/, called (df, i, knobs, direction)
         and returning True / False / None. It imports no producer, which is
         what makes the check independent (a check that only calls the
         producer agrees with the engine by construction, L582 / L684).
         A family that declares none is checked on legs B and C only, and
         the artifact says so.
  leg B  PRODUCTION - the declared producer ('module:function', e.g.
         backtest.signals.technical:compute_squeeze) on the PIT slice ending
         AT the entry bar, the arm's knobs set on backtest.config for the
         check (config_knobs.applied, never a reload) - the engine's code.
  leg C  RECORD - the trade log's signals_at_entry value of the leg's key.
A sample AGREES when leg B is True, leg C is True and leg A (when declared)
is True. A leg-C absence (the key not persisted) is SKIPPED with the reason,
never counted as agreement.

PIT: the slice ends AT the entry bar (df.iloc[:i + 1]) - the convention
spot_check_candle MEASURED at 1350 of 1350 landed fires (B2865).

PROVENANCE: RANDOM-SAMPLING-OF-REAL-DATA. The seeded RNG picks WHICH landed
fires are checked; it generates no number. A verdict binds the sampled
subset, never the population.

Exit 0 when every evaluable sample agrees and at least one sample agreed; 1
on any disagreement or execution failure, or when nothing agreed; 2 when the
input cannot be read (REFUSED).

    python scripts/spot_check_producer.py --cube output_x \\
        --strategy squeeze_breakout --kc-mult 1.5 --bb-std 2.0 \\
        --mom-window 20 --kc-period 20 --prior-n 0 --n 50 --out s.json
"""
from __future__ import annotations

import argparse
import importlib
import json
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
for _p in (ROOT, ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def _resolve(ref: str):
    """'module:function' -> the callable (fail closed on a bad reference)."""
    mod, _, fn = str(ref).partition(":")
    if not mod or not fn:
        raise SystemExit(f"REFUSED: {ref!r} is not 'module:function'")
    return getattr(importlib.import_module(mod), fn)


def _parse_signals(raw):
    if not isinstance(raw, str) or not raw.strip():
        return None
    for reader in (json.loads, __import__("ast").literal_eval):
        try:
            d = reader(raw)
            return d if isinstance(d, dict) else None
        except Exception:                                   # noqa: BLE001
            continue
    return None


def main(argv=None) -> int:
    from grade_knob_config import knob_rows
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--strategy", required=True)
    known, _ = pre.parse_known_args(argv)
    strat = known.strategy
    knobs = knob_rows(strat)
    from producer_variant_table import SPECS
    sc = dict((SPECS[strat].get("tools") or {}).get("spot_check") or {})
    if not sc.get("producer") or not isinstance(sc.get("keys_by_leg"), dict):
        print(json.dumps({"verdict": "NOT_COMPARABLE", "reason": (
            f"SPECS[{strat!r}].tools.spot_check declares no producer or no "
            "keys_by_leg - nothing to re-derive (fail closed, L642)")}))
        return 2
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--strategy", required=True)
    for _pid, key, envname, prod in knobs:
        ap.add_argument("--" + key.replace("_", "-"), dest=key, required=True,
                        help=f"the {envname} level of the landed arm "
                             f"(production {prod!r})")
    ap.add_argument("--cube", required=True, help="cube dir (trade_log.csv)")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    # leg B must see THIS arm's knobs: the producer reads config at call time.
    # They are set for this check only and put back after it - never by
    # reloading backtest.config, which rebinds every module-level object and
    # breaks whatever imported one by value (S6-B3386, scripts/config_knobs.py)
    from config_knobs import applied
    knob_vals = {key: getattr(a, key) for _pid, key, _env, _prod in knobs}
    with applied({env: getattr(a, key) for _pid, key, env, _prod in knobs}):
        return _check(a, strat, sc, knob_vals)


def _check(a, strat: str, sc: dict, knob_vals: dict) -> int:
    """Legs A, B and C over the sampled landed fires, at the arm's knobs."""
    producer = _resolve(sc["producer"])
    leg_a = _resolve(sc["leg_a"]) if sc.get("leg_a") else None
    keys_by_leg = dict(sc["keys_by_leg"])

    tl = Path(a.cube) / "trade_log.csv"
    if not tl.exists():
        print(json.dumps({"verdict": "NOT_COMPARABLE", "reason": f"no {tl}"}))
        return 2
    df = pd.read_csv(tl, low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "direction",
                              "signals_at_entry"])
    rows = df[df["strategy"] == strat]
    if rows.empty:
        print(json.dumps({"verdict": "NOT_COMPARABLE",
                          "reason": f"no {strat} rows in {tl.name}"}))
        return 2
    idx = list(rows.index)
    random.Random(a.seed).shuffle(idx)
    idx = idx[:a.n]

    from spot_check_trades import load_ohlcv
    agree = disagree = skipped = failures = 0
    details, skips, cache = [], [], {}
    for ix in idx:
        r = rows.loc[ix]
        tk, when = str(r["ticker"]), str(r["entry_date"])[:10]
        leg = str(r["direction"])
        key = keys_by_leg.get(leg)
        try:
            if key is None:
                skipped += 1
                skips.append({"ticker": tk, "entry_date": when,
                              "reason": f"no key declared for the {leg} leg"})
                continue
            if tk not in cache:
                cache[tk] = load_ohlcv(tk)
            ohlc = cache[tk]
            if ohlc is None:
                skipped += 1
                skips.append({"ticker": tk, "entry_date": when, "reason": "no cached bars"})
                continue
            hit = ohlc.index.searchsorted(pd.Timestamp(when))
            if hit >= len(ohlc) or str(ohlc.index[hit].date()) != when:
                skipped += 1
                skips.append({"ticker": tk, "entry_date": when, "reason": "entry bar not cached"})
                continue
            i = int(hit)
            sig = _parse_signals(r["signals_at_entry"])
            if sig is None or key not in sig:
                skipped += 1
                skips.append({"ticker": tk, "entry_date": when,
                              "reason": f"{key} not persisted at entry"})
                continue
            c_leg = bool(sig[key])
            b_leg = bool(producer(ohlc.iloc[:i + 1]).get(key, False))
            a_leg = (None if leg_a is None
                     else leg_a(ohlc, i, dict(knob_vals), leg))
            ok = b_leg and c_leg and (a_leg is None or a_leg is True)
            if ok:
                agree += 1
            else:
                disagree += 1
                details.append({"ticker": tk, "entry_date": when, "leg": leg,
                                "leg_a_independent": a_leg,
                                "leg_b_production": b_leg, "leg_c_record": c_leg})
        except Exception as exc:                               # noqa: BLE001
            failures += 1
            details.append({"ticker": tk, "entry_date": when,
                            "execution_failure": f"{type(exc).__name__}: {exc}"})
    doc = {"strategy": strat, "cube": str(a.cube), "seed": a.seed,
           "sampled": len(idx), "agree": agree, "disagree": disagree,
           "skipped": skipped, "execution_failures": failures,
           "config": knob_vals,
           "producer": sc["producer"], "keys_by_leg": keys_by_leg,
           "leg_a": sc.get("leg_a") or ("NONE DECLARED - legs B and C only; "
                                        "the check proves the engine ran this "
                                        "arm's knobs, not the producer's math"),
           "detail": details[:25], "skips": skips[:25],
           "provenance": "RANDOM-SAMPLING-OF-REAL-DATA (the seed picks which "
                         "landed fires; every value is measured)",
           "generator": "scripts/spot_check_producer.py"}
    Path(a.out).write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("strategy", "sampled", "agree",
                                          "disagree", "skipped",
                                          "execution_failures")}))
    return 0 if (agree > 0 and disagree == 0 and failures == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
