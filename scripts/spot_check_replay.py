#!/usr/bin/env python
"""S6-B3240 (B3139q-r89): a three-leg spot check by STRATEGY REPLAY, for a
family whose swept knob lives in the STRATEGY layer (LEVER4's gate budget) -
where no producer recompute can see the knob, because the knob changes which
legs must hold, not what any producer emits.

  LEG A - the ENGINE RECORD: each sampled fire's persisted signals_at_entry
          and its recorded direction.
  LEG B - the PRODUCTION CONSUMER: the live strategy function
          (ALL_STRATEGIES[<strategy>]) replayed on LEG A's signals under THIS
          process's config. The battery runs every family subprocess under
          the landed arm's env (run_postconfig, B2576), so config.
          LEVER4_GATE_BUDGET here is the arm's; the replay must fire with the
          recorded direction. The artifact records the knob values it read.
  LEG C - EXECUTION: the entry bar exists in the cached OHLCV, the entry lies
          inside --start..--end, hold_days >= 0, pnl_pct present and |pnl_pct|
          below 100.

A sampled fire whose side's gate reads a key LEG A did not persist (the
S6-B3239 class) cannot be replayed honestly - the replay would read that
key's default - so it is SKIPPED with the key named, never counted as an
agreement. The gate keys per side are the repo's one side model
(build_strategy_status.gate_keys_by_direction, from signals_used_lint).

NO PRECOMPUTE LEG: the knob this checker exists for reads no precompute; a
family whose knob does keeps a checker that re-derives its producer
(spot_check_smc_family, spot_check_candle).

PROVENANCE: RANDOM-SAMPLING-OF-REAL-DATA. The seeded RNG picks WHICH landed
fires are checked (reproducible from --seed); it generates no number. Every
reported value is MEASURED from the cube and the cached bars, and a verdict
binds the sampled subset, never the population.

Exit 0 when every evaluable sample agrees on LEG B and passes LEG C and at
least one sample agreed; 1 on any LEG-B disagreement, LEG-C failure, or a
sample with no agreement at all (the battery records step 4 FAIL); 2 when the
input cannot be read (REFUSED).
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
for _p in (ROOT, ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


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


def load_fires(cube_dir: Path, strat: str) -> pd.DataFrame:
    """The strategy's landed fires, one row per (ticker, entry_date,
    direction), read in chunks (the R5 log is 4.6 GB)."""
    tl_p = cube_dir / "trade_log.csv"
    if not tl_p.exists():
        raise FileNotFoundError(f"{tl_p} does not exist")
    head = list(pd.read_csv(tl_p, nrows=0).columns)
    want = ["strategy", "ticker", "entry_date", "direction", "signals_at_entry",
            "hold_days", "pnl_pct"]
    missing = [c for c in want if c not in head]
    if missing:
        raise ValueError(f"{tl_p} lacks {missing}")
    parts = []
    for ch in pd.read_csv(tl_p, usecols=want, chunksize=200_000, low_memory=False):
        sub = ch[ch["strategy"] == strat]
        if len(sub):
            parts.append(sub)
    if not parts:
        return pd.DataFrame(columns=want)
    return pd.concat(parts).drop_duplicates(["ticker", "entry_date", "direction"])


def replay(fn, sig: dict, direction: str, side_keys) -> tuple[str, str]:
    """('agree' | 'disagree' | 'skipped', why) for one fire."""
    if not sig:
        return "skipped", "empty signals_at_entry"
    absent = sorted(k for k in (side_keys or ()) if sig.get(k) is None)
    if absent:
        return "skipped", f"gate key(s) not persisted: {absent}"
    try:
        r = fn(dict(sig))
    except Exception as exc:                        # never silent
        return "disagree", f"replay raised {type(exc).__name__}: {exc}"
    if r and r.get("fires") and r.get("direction") == direction:
        return "agree", ""
    return "disagree", (f"replay fires={bool(r and r.get('fires'))} "
                        f"direction={r.get('direction') if r else None} "
                        f"vs recorded {direction}")


def check_execution(row, df, start, end) -> list[str]:
    fails = []
    ed = pd.Timestamp(str(row["entry_date"])[:10])
    if not (pd.Timestamp(start) <= ed <= pd.Timestamp(end)):
        fails.append("entry_outside_window")
    if df is None or not len(df.index[df.index == ed]):
        fails.append("entry_bar_missing")
    hd = row.get("hold_days")
    if not (pd.notna(hd) and float(hd) >= 0):
        fails.append("hold_days_negative_or_missing")
    pnl = row.get("pnl_pct")
    if not pd.notna(pnl):
        fails.append("pnl_missing")
    elif abs(float(pnl)) >= 100.0:
        fails.append("pnl_insane")
    return fails


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--cube", required=True)
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--start", default="2022-05-05")
    ap.add_argument("--end", default="2026-05-05")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    from backtest import config as cfg
    from backtest.signals.screener import ALL_STRATEGIES
    fn = ALL_STRATEGIES.get(a.strategy)
    if fn is None:
        print(f"REFUSED: {a.strategy} is not a registered strategy")
        return 2
    cube_dir = Path(a.cube)
    if cube_dir.is_file():
        cube_dir = cube_dir.parent
    try:
        fires = load_fires(cube_dir, a.strategy)
    except (FileNotFoundError, ValueError) as exc:
        print(f"REFUSED: {exc}")
        return 2
    if fires.empty:
        print(f"REFUSED: no {a.strategy} rows in {cube_dir / 'trade_log.csv'}")
        return 2
    import build_strategy_status as bss
    per = bss.gate_keys_by_direction()
    keys_by_dir = per.get(a.strategy) or per.get("strat_" + a.strategy) or {}

    rows = fires.to_dict("records")
    random.Random(a.seed).shuffle(rows)
    rows = rows[: a.n]
    tally = {"agree": 0, "disagree": 0, "skipped": 0}
    recs, exec_fail = [], []
    for r in rows:
        d = str(r["direction"])
        verdict, why = replay(fn, _parse_signals(r.get("signals_at_entry")), d,
                              keys_by_dir.get(d))
        tally[verdict] += 1
        df = load_ohlcv(str(r["ticker"]))
        fails = check_execution(r, df, a.start, a.end)
        if fails:
            exec_fail.append({"ticker": r["ticker"], "entry_date": str(r["entry_date"]),
                              "failed": fails})
        recs.append({"ticker": r["ticker"], "entry_date": str(r["entry_date"]),
                     "direction": d, "leg_b": verdict, "why": why,
                     "execution_failed": fails})
    rec = {"strategy": a.strategy, "cube": str(cube_dir),
           "generator": "scripts/spot_check_replay.py",
           "n_sampled": len(recs), "seed": a.seed,
           "agree": tally["agree"], "disagree": tally["disagree"],
           "skipped": tally["skipped"], "execution_failures": exec_fail,
           "knobs": {"LEVER4_GATE_BUDGET": cfg.LEVER4_GATE_BUDGET,
                     "STRAT_EMA_SPAN": cfg.STRAT_EMA_SPAN},
           "gate_keys_by_side": {k: sorted(v) for k, v in keys_by_dir.items()},
           "legs_disclosure": (
               "LEG A the cube's persisted signals and recorded direction; "
               "LEG B the live strategy function replayed on them under this "
               "process's config (the landed arm's env when the battery runs "
               "it); LEG C execution against the cached bars. No precompute "
               "leg - the knob reads none. A fire whose gate key was not "
               "persisted is skipped, never agreed."),
           "rows": recs}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
    print(f"VERDICT: {tally['agree']} agree / {tally['disagree']} disagree / "
          f"{tally['skipped']} skipped of {len(recs)} sampled; execution "
          f"failures {len(exec_fail)}")
    print(f"wrote {out}")
    # a check that confirmed nothing is not a pass: every sample skipped
    # (no persisted gate keys) exits 1 like a disagreement (L599)
    return 0 if (tally["disagree"] == 0 and not exec_fail
                 and tally["agree"] > 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
