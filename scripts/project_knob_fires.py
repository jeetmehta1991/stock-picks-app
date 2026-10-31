#!/usr/bin/env python
"""S6-B3248 / S6-B3304 (B3139q-r165): the FIRE PROJECTION an engine-level run
publishes before it launches - the owner's launch word of 2026-10-28 names it
('knob, tests, fire projection, leverage line'), and L685 asks a run that must
generate its own events for an expected count from a MEASURED rate first.

MEASURED, then SCALED. The family's registered producer (SPECS
tools.spot_check: producer and keys_by_leg) runs on every bar of the Step-1
window - half-open, its end the IS/HO boundary, which is holdout - for a
seeded sample of the Step-1 universe (phase_table.resolve(1)) - once at
production and once per arm, the arm's knobs set by config_knobs.applied
(never a reload, S6-B3386). Each arm's ratio of fired bars to production's
scales the status view's projected Step-1 fires at the current gate
(projected_current_gate).

ASSUMED, and written on the artifact: the strategy's OTHER gate legs fire
independently of the knob. The projection is not a bound in either direction
(L812 - an engine run's occupancy is not simulated).

PROVENANCE: RANDOM-SAMPLING-OF-REAL-DATA - the seed picks which tickers;
every count is measured on cached OHLCV.

    python scripts/project_knob_fires.py --strategy squeeze_breakout \\
        --arm SQUEEZE_KC_MULT=1.5 --arm SQUEEZE_PRIOR_N=1 --sample 50 --out p.json

Each --arm is ONE engine run's vector, ENV=VALUE pairs joined by commas; an
unnamed knob runs at production. --workers N splits the sampled tickers into
N chunks counted in separate processes (each applies every arm's knobs in its
own process); 1, the default, counts in this process. Exit 0 when every arm
was projected; 2 when an input is refused (an env that is not the strategy's
knob, a level off its band, no producer registered, no status row).
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
STATUS = ROOT / "output_audit" / "strategy_optimisation_status.json"


def _resolve(ref: str):
    mod, _, fn = str(ref).partition(":")
    if not mod or not fn:
        raise SystemExit(f"REFUSED: {ref!r} is not 'module:function'")
    return getattr(importlib.import_module(mod), fn)


def status_row(strategy: str) -> dict | None:
    """The strategy's row of the status view (projected Step-1 fires)."""
    try:
        view = json.loads(STATUS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return next((r for r in view.get("rows") or [] if r.get("strategy") == strategy), None)


def parse_arm(text: str, knobs: dict) -> dict:
    """'ENV=V,ENV2=V2' -> {ENV: 'V'}; refuses an env that is not one of the
    strategy's knobs and a level outside the knob's registered band."""
    out = {}
    for part in [x for x in str(text).split(",") if x.strip()]:
        env, sep, val = part.partition("=")
        env, val = env.strip(), val.strip()
        if not sep or env not in knobs:
            raise ValueError(f"{part!r} - {env!r} is not a knob of this "
                             f"strategy (its knobs: {sorted(knobs)})")
        band = knobs[env]
        if not any(_same(val, b) for b in band):
            raise ValueError(f"{env}={val} is off the registered band {band}")
        out[env] = val
    if not out:
        raise ValueError(f"arm {text!r} names no knob")
    return out


def _same(a, b) -> bool:
    try:
        return abs(float(a) - float(b)) <= 1e-9
    except (TypeError, ValueError):
        return str(a) == str(b)


def count_fires(producer, keys_by_leg: dict, frames: list, label: str = "") -> dict:
    """{leg: bars whose leg key fires} over every (df, positions) frame,
    the producer called on the PIT prefix ending at each position (the
    spot checks' slice, df.iloc[:i + 1]). Progress goes to stderr."""
    out = {leg: 0 for leg in keys_by_leg}
    for n, (df, positions) in enumerate(frames, 1):
        for i in positions:
            sig = producer(df.iloc[:i + 1]) or {}
            for leg, key in keys_by_leg.items():
                if sig.get(key):
                    out[leg] += 1
        if label and (n % 20 == 0 or n == len(frames)):
            print(f"  {label}: {n} of {len(frames)} tickers, {out}",
                  file=sys.stderr, flush=True)
    return out


def chunk_counts(job: tuple) -> dict:
    """One chunk of tickers: its window bars, its missing tickers, and the
    fired bars at production and under each arm - the unit a worker runs;
    --workers 1 runs the one chunk in this process."""
    tickers, start, end, producer_ref, keys, arms = job
    import config_knobs
    import spot_check_trades
    frames, missing, bars = [], [], 0
    for tk in tickers:
        df = spot_check_trades.load_ohlcv(tk)
        if df is None or df.empty:
            missing.append(tk)
            continue
        idx = pd.DatetimeIndex(df.index)
        pos = [i for i, d in enumerate(idx) if start <= str(d.date()) < end]
        if not pos:
            missing.append(tk)
            continue
        frames.append((df, pos))
        bars += len(pos)
    producer = _resolve(producer_ref)
    prod = count_fires(producer, keys, frames, label="production")
    got = []
    for arm in arms:
        with config_knobs.applied(arm):
            got.append(count_fires(producer, keys, frames, label=str(arm)))
    return {"frames": len(frames), "missing": missing, "bars": bars,
            "production": prod, "arms": got}


def _add(a: dict, b: dict) -> dict:
    return {k: a.get(k, 0) + b.get(k, 0) for k in set(a) | set(b)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--arm", action="append", required=True,
                    help="ONE engine run's vector: ENV=VALUE[,ENV=VALUE]")
    ap.add_argument("--sample", type=int, default=50,
                    help="tickers drawn from the Step-1 universe (seeded)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--workers", type=int, default=1,
                    help="processes counting ticker chunks (1 = in process)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    from producer_variant_table import SPECS
    entry = SPECS.get(a.strategy)
    sc = ((entry or {}).get("tools") or {}).get("spot_check") or {}
    if not sc.get("producer") or not isinstance(sc.get("keys_by_leg"), dict):
        print(f"REFUSED: SPECS[{a.strategy!r}] registers no producer and keys_by_leg "
              "(tools.spot_check) - nothing to project (fail closed, L642)")
        return 2
    knobs = {p["env"]: list(p.get("band") or []) for p in entry["params"] if p.get("env")}
    try:
        arms = [parse_arm(x, knobs) for x in a.arm]
    except ValueError as exc:
        print(f"REFUSED: {exc}")
        return 2
    row = status_row(a.strategy)
    if not row or not row.get("projected_current_gate"):
        print(f"REFUSED: no status row with projected_current_gate for {a.strategy}")
        return 2
    import phase_table
    ph = phase_table.resolve(1)
    start, end = ph["window"]["start"], ph["window"]["end"]
    tickers = [t.strip() for t in (ROOT / ph["tickers_file"]).read_text(
        encoding="utf-8").splitlines() if t.strip() and not t.startswith("#")]
    sample = (sorted(random.Random(a.seed).sample(tickers, a.sample))
              if a.sample < len(tickers) else sorted(tickers))
    keys = dict(sc["keys_by_leg"])
    n_jobs = max(1, min(a.workers, len(sample)))
    jobs = [(sample[k::n_jobs], start, end, sc["producer"], keys, arms)
            for k in range(n_jobs)]
    if n_jobs == 1:
        parts = [chunk_counts(jobs[0])]
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=n_jobs) as ex:
            parts = list(ex.map(chunk_counts, jobs))
    prod = {leg: 0 for leg in keys}
    got_all = [{leg: 0 for leg in keys} for _ in arms]
    missing, bars, with_bars = [], 0, 0
    for p in parts:
        prod = _add(prod, p["production"])
        got_all = [_add(g, x) for g, x in zip(got_all, p["arms"])]
        missing += p["missing"]
        bars += p["bars"]
        with_bars += p["frames"]
    base = float(row["projected_current_gate"])
    results = []
    for arm, got in zip(arms, got_all):
        tot_p, tot_a = sum(prod.values()), sum(got.values())
        ratio = (tot_a / tot_p) if tot_p else None
        results.append({"arm": arm, "fired_bars": got,
                        "ratio_to_production": None if ratio is None else round(ratio, 4),
                        "projected_step1_fires": (None if ratio is None
                                                  else round(base * ratio, 1))})
    doc = {"strategy": a.strategy, "generator": "scripts/project_knob_fires.py",
           "window": {"start": start, "end": end}, "universe": ph["tickers_file"],
           "sample": {"seed": a.seed, "tickers": len(sample),
                      "with_bars": with_bars, "missing": sorted(missing),
                      "window_bars": bars, "workers": n_jobs},
           "producer": sc["producer"], "keys_by_leg": keys,
           "production_fired_bars": prod,
           "production_projection": {"projected_current_gate": base,
                                     "source": "output_audit/strategy_optimisation_status.json"},
           "arms": results,
           "assumption": ("the strategy's other gate legs fire independently of "
                          "the knob - not measured; not a bound in either "
                          "direction (L812, occupancy unsimulated)"),
           "provenance": ("RANDOM-SAMPLING-OF-REAL-DATA (the seed picks which "
                          "tickers; every count is measured on cached OHLCV)")}
    Path(a.out).write_text(json.dumps(doc, indent=1, default=str), encoding="utf-8")
    for r in results:
        print(json.dumps({k: r[k] for k in ("arm", "ratio_to_production",
                                               "projected_step1_fires")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
