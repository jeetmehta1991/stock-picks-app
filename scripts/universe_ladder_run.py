"""Universe ladder for S6-B1508a / S6-B1512a - owner-approved B1514.

Runs the engine at 5 / 10 / 20 / 50 / 100 / 200 / 381 tickers to answer TWO
questions that no single-ticker run can:

  1. WALL-CLOCK SCALING. One ticker measured 42.9 min. Whether 381 is 381x that
     or far less is unmeasured, and two extrapolations this session were 9x and
     23pct light (L367, L377), so the ladder measures instead of projecting.

  2. ENTRY-COUNT SCALING (the more important one). A 1-ticker run took 8 AAPL
     entries where R5's 381-ticker run took 6 (L376). If universe size drives
     WHICH entries are taken, no small-universe shortcut exists and every
     resimulation must run at 381 to stay comparable to the R5 baseline.

RUNGS ARE NESTED - rung N's tickers are a strict superset of rung N-1's - so
successive rungs differ ONLY in universe size. A non-nested ladder would confound
size with composition.

TICKER ORDER is deterministic and stated: descending R5 fire-count for the target
strategy, then alphabetical. That front-loads tickers that actually fire, so the
small rungs carry signal rather than empty universes (the SP50 failure, L365).

SENTINELS are armed per rung and TRIP LOUDLY:
  S1 wall-clock    - elapsed exceeds 2x the ladder's own projection
  S2 entry ratio   - entries/ticker deviates >2x from the R5 baseline rate
  S3 zero-fire     - a rung produces no entries for the target strategy
  S4 exit contract - any entry not carrying exactly 26 exit rows (CHECKLIST #130)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
R5_CUBE = REPO / "output_r5_rung4_chunk1" / "trade_exit_detail.csv"
STRATEGY = "smc_breaker_block_long"
RUNGS = [5, 10, 20, 50, 100, 200, 381]
EXPECTED_EXITS = 26


def build_ladder() -> tuple[list[str], dict]:
    """Nested ticker order + the R5 baseline facts the sentinels compare against."""
    c = pd.read_csv(R5_CUBE, low_memory=False,
                    usecols=["strategy", "ticker", "entry_date"])
    universe = sorted(c.ticker.unique())
    g = c[c.strategy == STRATEGY]
    entries = g.groupby(["ticker", "entry_date"]).ngroups
    fires = g.groupby("ticker").apply(
        lambda d: d.groupby("entry_date").ngroups, include_groups=False)
    order = sorted(universe, key=lambda t: (-int(fires.get(t, 0)), t))
    base = {"r5_universe": len(universe),
            "r5_entries": int(entries),
            "r5_tickers_fired": int((fires > 0).sum()),
            "r5_entries_per_ticker": round(entries / len(universe), 4)}
    return order, base


def sentinels(rung: int, elapsed: float, proj: float | None,
              out_dir: Path, base: dict) -> list[str]:
    """Return TRIPPED sentinel messages. Empty list = all clear."""
    trips = []
    if proj and elapsed > 2 * proj:
        trips.append(f"S1 WALL-CLOCK: {elapsed/60:.1f} min vs projection "
                     f"{proj/60:.1f} min (>2x)")
    f = out_dir / "trade_exit_detail.csv"
    if not f.exists():
        trips.append(f"S3 ZERO-FIRE: no cube written at {f}")
        return trips
    d = pd.read_csv(f, low_memory=False,
                    usecols=["strategy", "ticker", "entry_date", "exit_method"])
    g = d[d.strategy == STRATEGY]
    n_entries = g.groupby(["ticker", "entry_date"]).ngroups
    if n_entries == 0:
        trips.append(f"S3 ZERO-FIRE: 0 entries for {STRATEGY} at rung {rung}")
        return trips
    rate = n_entries / rung
    ratio = rate / base["r5_entries_per_ticker"] if base["r5_entries_per_ticker"] else 0
    if ratio > 2 or ratio < 0.5:
        trips.append(f"S2 ENTRY RATIO: {rate:.4f}/ticker vs R5 "
                     f"{base['r5_entries_per_ticker']:.4f} = {ratio:.2f}x (outside 0.5-2.0)")
    bad = g.groupby(["ticker", "entry_date"]).exit_method.nunique()
    off = bad[bad != EXPECTED_EXITS]
    if len(off):
        trips.append(f"S4 EXIT CONTRACT: {len(off)} entries not carrying exactly "
                     f"{EXPECTED_EXITS} exits (CHECKLIST #130); sample {off.head(3).to_dict()}")
    return trips


def metrics(out_dir: Path) -> dict:
    """All Table B metrics for this rung, via the canonical evaluator."""
    sys.path.insert(0, str(REPO / "scripts"))
    import roster_core as rc
    f = out_dir / "trade_exit_detail.csv"
    if not f.exists():
        return {"error": "no cube"}
    cube = rc.load_cube(f)
    g = cube[cube.strategy == STRATEGY]
    if g.empty:
        return {"entries": 0}
    ent = g.groupby(["ticker", "entry_date"]).ngroups
    pick, _ = rc.select_exit(rc.in_sample(g))
    out = {"entries": ent, "exits": int(g.exit_method.nunique()), "exit": pick}
    if pick:
        hb = rc.holdout(g)[lambda d: d.exit_method == pick]
        fp = int((g.exit_method == pick).sum())
        res = rc.evaluate(hb["pnl_pct"], hb["hold_days"], full_period_n=fp)
        out.update({"holdout_n": len(hb), "full_period_n": fp})
        if res:
            out.update({k: res.get(k) for k in
                        ("sharpe", "sortino", "psr", "profit_factor", "payoff",
                         "expectancy", "win_rate", "p", "ci_lo")})
            out["gates"] = {k: bool(res["gates"][k]) for k in rc.LIVE_GATES}
            out["gates_passed"] = sum(out["gates"].values())
        else:
            out["verdict"] = "BELOW_POWER_FLOOR"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rungs", default="", help="comma list; default all")
    ap.add_argument("--max-run-hours", type=float, default=8.0)
    ap.add_argument("--state", default="output_audit/b1514_ladder_state.json")
    a = ap.parse_args()

    order, base = build_ladder()
    print(f"R5 baseline: {base}")
    rungs = [int(x) for x in a.rungs.split(",")] if a.rungs else RUNGS

    state_p = Path(a.state)
    state = json.loads(state_p.read_text()) if state_p.exists() else {
        "baseline": base, "rungs": []}
    per_ticker = None
    for done in state["rungs"]:
        if done.get("elapsed_sec") and done.get("rung"):
            per_ticker = done["elapsed_sec"] / done["rung"]

    for rung in rungs:
        if any(r["rung"] == rung for r in state["rungs"]):
            print(f"rung {rung}: already done, skipping")
            continue
        tick = order[:rung]
        tf = Path(f"output_audit/_ladder_{rung}.txt")
        tf.write_text("\n".join(tick) + "\n")
        out_dir = REPO / f"output_ladder_{rung}"
        proj = per_ticker * rung if per_ticker else None
        print(f"\n=== RUNG {rung} ===  projection: "
              f"{f'{proj/60:.1f} min' if proj else 'unknown (first rung)'}")
        t0 = time.time()
        cmd = [sys.executable, "backtest/run_phase1a.py",
               "--tickers-file", str(tf), "--phase", "1a-beta", "--cube-isolation",
               "--no-agents", "--no-news", "--no-git", "--no-walk-forward",
               "--start", "2022-05-05", "--end", "2026-05-05",
               "--max-run-hours", str(a.max_run_hours),
               "--output-dir", str(out_dir)]
        log = Path(f"output_audit/b1514_rung_{rung}.log")
        with open(log, "w", encoding="utf-8") as fh:
            rc_code = subprocess.call(cmd, stdout=fh, stderr=subprocess.STDOUT,
                                      cwd=str(REPO))
        elapsed = time.time() - t0
        trips = sentinels(rung, elapsed, proj, out_dir, base)
        row = {"rung": rung, "exit_code": rc_code,
               "elapsed_sec": round(elapsed, 1),
               "sec_per_ticker": round(elapsed / rung, 2),
               "projection_sec": round(proj, 1) if proj else None,
               "sentinels_tripped": trips, "metrics": metrics(out_dir)}
        state["rungs"].append(row)
        state_p.write_text(json.dumps(state, indent=2, default=str))
        print(f"rung {rung}: exit={rc_code} elapsed={elapsed/60:.1f} min "
              f"({elapsed/rung:.1f} s/ticker)")
        print(f"  metrics: {row['metrics']}")
        if trips:
            print("  SENTINELS TRIPPED:")
            for t in trips:
                print(f"    {t}")
            print("  HALTING LADDER - report to owner before continuing.")
            return 2
        if rc_code != 0:
            print(f"  NON-ZERO EXIT - halting. See {log}")
            return 3
        per_ticker = elapsed / rung
    print(f"\nladder complete; state -> {a.state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
