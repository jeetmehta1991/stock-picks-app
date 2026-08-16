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
# B1575: was output_r5_rung4_chunk1 - an ABANDONED alphabetically-
# partitioned chunk (380/381 tickers A-C, no MSFT/NVDA/GOOGL, 248
# tickers the real R5 never ran). L445. The real baseline is
# output_r5_merged_1_7 (544 tickers, A-Z).
R5_CUBE = Path("output_r5_merged_1_7/trade_exit_detail.csv")

# Candidate levels. Each list ANCHORS at the production default (last element)
# so "no change" is always in the grid and the baseline is reproducible.
# P5 break_pct_max: NEW-GATE, OWNER-APPROVED B1507. Production has no such
# parameter (`close > top` is strict). Band from the B1501 measurement: real
# retests 0.5-2.7pct, stale latches 7.5-60pct, empty gap 3-7pct. UPPER bound
# per L359 - a breaker block is a RETEST, so closer is stricter.
BREAK_PCT_MAX = [0.01, 0.02, 0.03, 0.05, None]   # None = production (no cap)
AGE_BARS_MAX = [60, 120, 180, 250, None]         # None = production (no cap)
TAIL_N = [3, 5, 10, 20]                          # 20 = production
# P2 close_mitigation (READ smc.py:380). False = mitigated on high/low (production);
# True = mitigated only on CLOSE, strictly fewer mitigations => strictly fewer fires.
CLOSE_MITIGATION = [True, False]                 # False = production


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
                  swing_length: int = 20,
                  close_mitigation: bool = False) -> dict | None:
    """Recover age_bars / break_pct / rank for the OB events qualifying at `when`.

    PIT preserved: the producer sees ohlc.iloc[:i+1] only, exactly as production.
    """
    locs = df.index.get_indexer([when], method="pad")
    i = int(locs[0])
    if i < 250:
        return None
    sub = df.iloc[:i + 1]
    swings = _smc.swing_highs_lows(sub, swing_length=swing_length)
    ob_df = _smc.ob(sub, swings, close_mitigation=close_mitigation)
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
    ap.add_argument("--cube", default="", help="cube to grade against; default R5")
    ap.add_argument("--tickers-file", default="")
    # S6-B1584a: the grader RE-DERIVES every fire from OHLCV. Re-deriving
    # with different producer params than the run that made the cube means
    # fires cannot reproduce and are DROPPED. cfg2 ran sw=10, was graded at
    # the hardcoded 20, and lost 167 of 420 fires - a biased 60pct
    # subsample, not a random one.
    ap.add_argument("--swing-length", type=int, default=20,
                    help="SMC_SWING_LENGTH the CUBE was generated with")
    # S6-B1584c (owner ruling 2026-08-15): Step 1 ranks on 100 tickers x 2y,
    # ~1/5 the ticker-days MIN_N=30 was calibrated for. 30 produced
    # NO_EXIT_SELECTABLE on 84-92pct of combinations - a sample-size verdict
    # dressed as an exit-quality one. NEVER changes roster_core.MIN_N.
    ap.add_argument("--min-n", type=int, default=10,
                    help="SEARCH-phase min trades (owner: 10)")
    ap.add_argument("--max-diag-loss", type=float, default=0.02,
                    help="abort if more than this fraction of fires cannot be re-diagnosed")
    a = ap.parse_args()

    cube = rc.load_cube(Path(a.cube) if a.cube else R5_CUBE)
    g = cube[cube["strategy"] == STRATEGY].copy()
    # load_cube yields entry_date as datetime.date; roster_core's window
    # helpers compare against date objects, so do NOT convert to datetime64.
    fires = g[["ticker", "entry_date"]].drop_duplicates()
    print(f"R5 baseline: {len(fires)} fires x {g.exit_method.nunique()} exits "
          f"= {len(g)} cube rows")

    tickers = sorted(fires.ticker.unique())
    if a.tickers_file:
        allow = {l.strip() for l in open(a.tickers_file) if l.strip()}
        before = len(tickers)
        tickers = [t for t in tickers if t in allow]
        fires = fires[fires.ticker.isin(tickers)]
        print(f"ticker filter {a.tickers_file}: {before} -> {len(tickers)} tickers, "
              f"{len(fires)} fires retained")
    if a.limit_tickers:
        tickers = tickers[:a.limit_tickers]

    # One instrumented pass per fire; results reused by every combination.
    diags: dict[bool, dict] = {cm: {} for cm in CLOSE_MITIGATION}
    for t in tickers:
        df = _load_ohlcv(t)
        if df is None:
            continue
        for when in fires[fires.ticker == t].entry_date:
            for cm in CLOSE_MITIGATION:
                d = diagnose_fire(df, pd.Timestamp(when),
                                  swing_length=a.swing_length,
                                  close_mitigation=cm)
                if d:
                    diags[cm][(t, when)] = d
    # S6-B1586: the loss gate must apply to the UNION of branches, not each
    # one. close_mitigation is a SWEPT dimension: cm=True is a strictly tighter
    # variant that is SUPPOSED to find fewer order blocks. Checking each branch
    # separately flagged a variant doing its job as a 4pct failure. A fire is
    # genuinely un-reproducible only if NO branch can diagnose it - that is what
    # indicates the grader cannot reconstruct what the engine did.
    union = set()
    for cm in CLOSE_MITIGATION:
        union |= set(diags[cm].keys())
    n_f = len(fires)
    union_loss = 1.0 - (len(union) / n_f) if n_f else 0.0
    for cm in CLOSE_MITIGATION:
        print(f"close_mitigation={cm}: diagnosed {len(diags[cm])} of {n_f} "
              f"fires (branch-level; tighter branches legitimately find fewer)")
    print(f"UNION across branches: {len(union)} of {n_f} "
          f"({union_loss:.1%} un-reproducible)")
    for cm in [CLOSE_MITIGATION[0]]:
        n_d = len(union)
        loss = union_loss
        print(f"close_mitigation={cm}: diagnosed {n_d} of {n_f} fires "
              f"({loss:.1%} lost)")
        # S6-B1584b: this line ALWAYS printed the shortfall and nothing
        # ever asserted on it, so a 40pct loss sat in plain sight. A silent
        # subsample is worse than a crash - it yields plausible metrics on
        # a biased population.
        if loss > a.max_diag_loss:
            raise SystemExit(
                "FATAL: {:.1%} of fires could not be re-diagnosed (limit {:.1%}). "
                    "The grader re-derives fires from OHLCV; if "
                    "--swing-length ({}) does not match the "
                    "SMC_SWING_LENGTH the cube was RUN with, fires cannot "
                    "reproduce and would be dropped silently, biasing "
                    "every metric. Pass the correct --swing-length or "
                    "raise --max-diag-loss deliberately."
                    .format(loss, a.max_diag_loss, a.swing_length))

    rows = []
    for cm, bmax, amax, tn in itertools.product(
            CLOSE_MITIGATION, BREAK_PCT_MAX, AGE_BARS_MAX, TAIL_N):
        keep = {k for k, d in diags[cm].items() if survives(d, bmax, amax, tn)}
        if not keep:
            rows.append({"close_mitigation": cm, "break_pct_max": bmax,
                         "age_bars_max": amax, "tail_n": tn, "fires": 0,
                         "verdict": "ZERO_FIRES"})
            continue
        sub = g[[(r.ticker, r.entry_date) in keep
                 for r in g.itertuples()]]
        is_m = rc.in_sample(sub)
        ho_m = rc.holdout(sub)
        exit_pick, _ = rc.select_exit(is_m, min_n=a.min_n)
        if exit_pick is None:
            rows.append({"close_mitigation": cm, "break_pct_max": bmax,
                         "age_bars_max": amax, "tail_n": tn, "fires": len(keep),
                         "verdict": "NO_EXIT_SELECTABLE"})
            continue
        hb = ho_m[ho_m.exit_method == exit_pick]
        fp_n = int((sub.exit_method == exit_pick).sum())
        res = rc.evaluate(hb["pnl_pct"], hb["hold_days"],
                          min_n=a.min_n, full_period_n=fp_n)
        row = {"close_mitigation": cm, "break_pct_max": bmax,
               "age_bars_max": amax, "tail_n": tn,
               "fires": len(keep), "exit": exit_pick,
               "holdout_n": len(hb), "full_period_n": fp_n}
        if res is None:
            row["verdict"] = "BELOW_POWER_FLOOR"
        else:
            gates = {k: bool(res["gates"][k]) for k in rc.LIVE_GATES}
            row.update({k: res.get(k) for k in
                        ("sharpe", "sortino", "psr", "profit_factor", "payoff",
                         "expectancy", "win_rate", "p", "ci_lo")})
            row.update({"gates": gates,
                        "gates_passed": sum(gates.values()),
                        "verdict": "PASS" if all(gates.values()) else "FAIL"})
        rows.append(row)

    rows.sort(key=lambda r: (-(r.get("gates_passed") or 0), -(r.get("fires") or 0)))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(
        {"strategy": STRATEGY, "r5_baseline_fires": len(fires),
         # B1517: was len(diags) which, after close_mitigation became the outer
         # key, reported 2 (the number of flag values) instead of the fire count.
         "diagnosed": {str(k): len(v) for k, v in diags.items()},
         "results": rows}, indent=2))

    print(f"\n{'break':>6} {'age':>5} {'tail':>4} {'fires':>6} {'ho_n':>5} "
          f"{'fp_n':>5} {'sharpe':>7} {'pass':>4}  verdict")
    for r in rows[:18]:
        print(f"{str(r['close_mitigation']):>6} {str(r['age_bars_max']):>5} "
              f"{r['tail_n']:>4} {r.get('fires', 0):>6} "
              f"{r.get('holdout_n', 0):>5} {r.get('full_period_n', 0):>5} "
              f"{(f'{r.get(chr(115)+chr(104)+chr(97)+chr(114)+chr(112)+chr(101)):.3f}' if r.get('sharpe') is not None else '-'):>7} "
              f"{str(r.get('gates_passed', '-')):>4}  {r['verdict']}")
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
