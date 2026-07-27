"""scripts/measure_clause_admission.py (B1394) -- BAR-LEVEL leave-one-out clause admission.

Resolves S6-B1393-BAR-LEVEL-CLAUSE-FIRE-RATE.

WHY THIS EXISTS
Lens A Dim A/B are computed on trades that FIRED. In an AND-stack every gate is True at
every fire by construction, so Dim B reports 100% for all of them and cannot tell a genuine
no-op from a hard requirement; Dim A likewise reports "BINDING" for essentially every
threshold because the observed extreme sits against the cutoff by construction (L241). Neither
can answer the only question that matters for loosening a gate: **how many more trades would
we admit if this clause were relaxed?** Answering it requires the bars where the clause was
FALSE, which are absent from the trade log, and `skipped_trades.csv` carries no signal values.

WHAT IT MEASURES
Over bars in the IS window (the holdout is never touched), for each strategy:
  base_rate    fraction of bars where the strategy fires today
  loo_rate[c]  fraction of bars where it fires when clause `c` is forced to a PASSING value
  lift[c]      loo_rate[c] / base_rate

  lift ~= 1.0  -> relaxing `c` admits nothing new: `c` is a NO-OP on this population (drop it)
  lift large   -> `c` is the binding constraint: relaxing it is where the trades come from
  base_rate 0  -> strategy is starved; lift is reported as None (undefined, not "infinite")

METHOD NOTE - why leave-one-out by CALLING THE REAL FUNCTION rather than parsing the gate
expression: the strategies mix AND, OR, defaults and helper calls (`_short_borrow_trap_active`).
Any regex reconstruction of that logic would be wrong somewhere and silently so. Instead we
mutate one key in the signal dict and invoke `ALL_STRATEGIES[name](s)` itself, so whatever the
real boolean structure is, it is honoured exactly.

Signals are produced by REUSING `measure_fire_count._precompute_signals_for_ticker` - the same
per-bar producer stack the fire-count measurement uses - rather than a second implementation.

Usage:
  python scripts/measure_clause_admission.py --max-tickers 40 --strategies poc_magnet_long
  python scripts/measure_clause_admission.py --max-tickers 40 --from-optimizer-dir output_optimization_candidates_r6_is_only
"""
from __future__ import annotations

import argparse
import json
import pickle
import re
import sys
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from backtest.signals.screener import ALL_STRATEGIES  # noqa: E402
import measure_fire_count as MFC  # noqa: E402  (reuse its producer stack + loaders)

IS_START, IS_END = date(2022, 5, 5), date(2025, 5, 5)   # holdout (>= IS_END) never touched


def clauses_of(strategy: str, source: str) -> list[tuple[str, str, float | None]]:
    """Return [(signal_key, op, threshold_or_None)] for every s.get(...) gate in the body."""
    m = re.search(rf'def strat_{re.escape(strategy)}\(s\):(.+?)(?=\ndef strat_|\nALL_STRATEGIES|\Z)',
                  source, re.DOTALL)
    if not m:
        return []
    body = m.group(1)
    out: dict[str, tuple[str, float | None]] = {}
    for k, op, num in re.findall(
            r's\.get\(["\']([a-z_][a-z_0-9]*)["\']\s*,[^)]*\)\s*([<>=!]{1,2})\s*([0-9.]+)', body):
        out[k] = (op, float(num))
    for k in re.findall(r's\.get\(["\']([a-z_][a-z_0-9]*)', body):
        out.setdefault(k, ("bool", None))
    return [(k, op, th) for k, (op, th) in out.items()]


SWEEP_MULT = (1.10, 1.25, 1.50, 2.00)   # candidate relaxations of a numeric threshold


def relaxed_threshold(op: str, th: float, mult: float) -> float:
    """The candidate threshold when a gate is loosened by `mult`. For a `>` gate loosening
    means a LOWER bar; for a `<` gate it means a HIGHER ceiling."""
    return th / mult if op in (">", ">=") else th * mult


def satisfies(op: str, val, th: float) -> bool:
    if not isinstance(val, (int, float)) or isinstance(val, bool):
        return False
    if op in (">", ">="):
        return val >= th
    if op in ("<", "<="):
        return val <= th
    return val == th


def passing_value(op: str, th: float | None, cur):
    """The most permissive value for this clause - what it looks like when it cannot block."""
    if op == "bool" or th is None:
        return True
    if op in (">", ">="):
        return th * 1.5 + 1.0 if th >= 0 else th * 0.5 + 1.0
    if op in ("<", "<="):
        return th * 0.5 - 1.0 if th >= 0 else th * 1.5 - 1.0
    if op in ("==",):
        return th
    return cur


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategies", nargs="+", default=None)
    ap.add_argument("--from-optimizer-dir", default=None,
                    help="take the strategy list from an optimizer output dir")
    ap.add_argument("--max-tickers", type=int, default=40)
    ap.add_argument("--start", default=IS_START.isoformat())
    ap.add_argument("--end", default=IS_END.isoformat(),
                    help="EXCLUSIVE upper bound; defaults to the holdout boundary")
    ap.add_argument("--output", default="output_audit/b1394_clause_admission.json")
    args = ap.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    end = datetime.strptime(args.end, "%Y-%m-%d").date()
    if end > IS_END:
        print(f"[FATAL] --end {end} reaches into the holdout (>= {IS_END}). Refusing: this "
              f"measurement exists to keep gate decisions holdout-free.")
        return 2

    names = args.strategies or []
    if args.from_optimizer_dir:
        names = sorted(p.stem for p in (REPO / args.from_optimizer_dir).glob("*.json"))
    names = [n for n in names if n in ALL_STRATEGIES]
    if not names:
        print("[ERROR] no valid strategies selected")
        return 1

    source = (REPO / "backtest" / "signals" / "screener.py").read_text(encoding="utf-8")
    gates = {n: clauses_of(n, source) for n in names}

    tickers = MFC._load_t1a_tickers_union_over_window(start, end)[: args.max_tickers]
    print(f"[INFO] {len(names)} strategies x {len(tickers)} tickers, bars {start} -> {end} (IS only)")

    # B1397: EVENT-vs-STATE must be decided EMPIRICALLY, not by name. The probe showed the
    # loo_rate>0.95 rule catches only a naked trigger; a trigger AND-ed with one filter slips
    # through and lands at the TOP of the "relaxable" list (ema_50_200_death_cross, lift 200).
    # An EVENT signal is intrinsically rare - True on a few percent of bars - and cannot be
    # "loosened": the crossover either happened or it did not. So record each signal's OWN
    # True-rate over bars and use that, which needs no name list and cannot go stale.
    sig_true = {}   # signal key -> [n_true, n_bool_seen, n_numeric_seen]
    stats = {n: {"bars": 0, "base": 0, "loo": {c[0]: 0 for c in gates[n]}} for n in names}
    watched = {k for n in names for k, _op, _th in gates[n]}
    # B1400 THE SWEEP. `lift` is a full-removal CEILING; it cannot say what 0.03 -> 0.04
    # admits, so it cannot be used to CHOOSE a threshold. For each numeric-threshold clause we
    # re-evaluate the strategy at candidate relaxed thresholds, admitting a bar only when its
    # ACTUAL signal value satisfies the CANDIDATE threshold - which simulates the edited gate
    # exactly. Alongside each candidate we accumulate the FORWARD RETURN of the bars it newly
    # admits: a loosening that admits negative-expectancy trades is loosening into noise, which
    # is the entire risk of this exercise, and admission counts alone cannot detect it.
    HOLD = 10   # forward horizon in bars; matches the time_stop_10d exit family
    sweep = {n: {k: {m: [0, 0.0] for m in SWEEP_MULT}      # [n_new_admitted, sum_fwd_ret]
                 for k, _op, th in gates[n] if th is not None} for n in names}
    # B1403: SIGNAL CACHE. Profiling showed per-bar signal precompute is ~428s/ticker while the
    # entire leave-one-out + sweep evaluation costs <0.01s per 2000 calls - i.e. 99.9% of
    # runtime is recomputing signals the R5 cube already computed once. Cache them per
    # (ticker, window) so the expensive pass happens ONCE and every subsequent iteration of
    # this analysis - and any other bar-level study - is effectively free.
    cache_dir = REPO / "output_audit" / "_signal_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    for ti, tk in enumerate(tickers, 1):
        cpath = cache_dir / f"{tk}_{start}_{end}.pkl"
        per_bar = None
        if cpath.exists():
            try:
                per_bar = pickle.loads(cpath.read_bytes())
            except Exception:
                per_bar = None      # corrupt cache entry -> recompute, never fail the run
        if per_bar is None:
            df = MFC._load_ohlcv(tk)
            if df is None or df.empty:
                continue
            try:
                per_bar = MFC._precompute_signals_for_ticker(df, tk, start, end)
            except Exception as exc:
                print(f"  [skip] {tk}: {exc}")
                continue
            try:
                cpath.write_bytes(pickle.dumps(per_bar, protocol=pickle.HIGHEST_PROTOCOL))
            except Exception as exc:
                print(f"  [cache-write failed for {tk}: {exc}]")
        else:
            df = MFC._load_ohlcv(tk)
            if df is None or df.empty:
                continue
        # forward return per bar date, for scoring what a loosened gate would newly admit
        closes = df["close"] if "close" in df.columns else df.get("Close")
        fwd = {}
        if closes is not None:
            c = closes.reset_index(drop=True)
            idx_of = {d.date(): i for i, d in enumerate(df.index)}
            for d, i in idx_of.items():
                j = i + HOLD
                if j < len(c) and c.iloc[i]:
                    fwd[d] = float((c.iloc[j] - c.iloc[i]) / c.iloc[i] * 100.0)
        for _bar_date, sig in per_bar:
            for k in watched:
                if k in sig:
                    # [n_true, n_bool_seen, n_numeric_seen] - booleans and numerics must be
                    # counted separately: a numeric never satisfies `is True`, so lumping them
                    # together reports own_rate 0.0 for every threshold signal and makes the
                    # EVENT rule fire on the wrong things.
                    e = sig_true.setdefault(k, [0, 0, 0])
                    if isinstance(sig[k], bool):
                        e[1] += 1
                        if sig[k]:
                            e[0] += 1
                    elif isinstance(sig[k], (int, float)):
                        e[2] += 1
            for n in names:
                fn = ALL_STRATEGIES[n]
                st = stats[n]
                st["bars"] += 1
                try:
                    base = fn(sig)
                    base_fires = bool(base.get("fires") if isinstance(base, dict)
                                      else getattr(base, "fires", False))
                except Exception:
                    continue
                if base_fires:
                    st["base"] += 1
                for k, op, th in gates[n]:
                    s2 = dict(sig)
                    s2[k] = passing_value(op, th, sig.get(k))
                    try:
                        r = fn(s2)
                        if bool(r.get("fires") if isinstance(r, dict) else getattr(r, "fires", False)):
                            st["loo"][k] += 1
                    except Exception:
                        pass
                    # B1400 sweep: only meaningful for a numeric threshold on a bar that does
                    # not already fire - we are counting what a RELAXED threshold would ADD.
                    if th is None or base_fires:
                        continue
                    val = sig.get(k)
                    if not isinstance(val, (int, float)) or isinstance(val, bool):
                        continue
                    for m in SWEEP_MULT:
                        if not satisfies(op, val, relaxed_threshold(op, th, m)):
                            continue      # still blocked even at the relaxed threshold
                        s3 = dict(sig)
                        s3[k] = passing_value(op, th, val)   # let it through the ORIGINAL gate
                        try:
                            r3 = fn(s3)
                            if bool(r3.get("fires") if isinstance(r3, dict)
                                    else getattr(r3, "fires", False)):
                                cellw = sweep[n][k][m]
                                cellw[0] += 1
                                fr = fwd.get(_bar_date)
                                if fr is not None:
                                    cellw[1] += fr
                        except Exception:
                            pass
        if ti % 5 == 0:
            print(f"  ... {ti}/{len(tickers)} tickers")

    results = []
    for n in names:
        st = stats[n]
        bars = st["bars"] or 1
        base_rate = st["base"] / bars
        cl = []
        for k, _op, _th in gates[n]:
            loo_rate = st["loo"][k] / bars
            # B1394 classification. The TRIGGER case matters: for an EVENT clause (a crossover
            # or breakout HAPPENED), forcing it to a passing value makes the strategy fire on
            # essentially every bar - loo_rate ~ 1.0. That is not "relaxing a filter", it is
            # deleting the strategy's reason to exist, so its lift must NOT be read as
            # admission headroom. Only FILTER/THRESHOLD clauses are legitimately loosenable.
            tn, nb, nn = sig_true.get(k, [0, 0, 0])
            own_rate = (tn / nb) if nb else None      # None for a numeric-only signal
            # B1399 (5th defect, and the most useful one): a signal that was NEVER PRESENT in
            # any bar's signal dict means the PRODUCER EMITS NOTHING for it. `s.get(k, False)`
            # then returns the default forever, so the gate is permanently blocking (or
            # permanently inert) and the strategy is broken, not merely tight. Such a clause
            # previously landed in BINDING or NO-OP depending on whether other absent gates
            # happened to mask it - both labels are wrong and both would send us tuning a
            # threshold on a strategy whose producer never runs.
            absent = (nb == 0 and nn == 0)
            # EVENT = the signal itself is intrinsically rare. Decided from data, before the
            # lift rules, because a rare EVENT can show a huge lift and would otherwise sit at
            # the top of the relaxable list while being unloosenable by nature. A boolean that
            # was NEVER true in the sample is not evidence of relaxability either - it is
            # either an even rarer event or an unpopulated producer, so it gets its own bucket
            # rather than defaulting into BINDING.
            never_true = own_rate is not None and tn == 0
            is_event = own_rate is not None and 0 < own_rate < 0.05
            # Ordering principle (L243): BINDING is a POSITIVE conclusion and must be reached
            # only when the evidence supports it. Every not-established case gets an explicit
            # bucket, so "relaxable" is never the fallback for missing information.
            if absent:
                verdict = ("ABSENT-PRODUCER (signal never present in any bar - the gate reads "
                           "its default forever; fix the producer, do NOT tune this gate)")
            elif base_rate <= 0:
                verdict = "UNDEFINED (base fire rate 0 - strategy starved on this sample)"
            elif never_true:
                verdict = (f"NEVER-TRUE in sample ({nb} bars seen, 0 true) - rare event or "
                           f"unpopulated producer; NOT evidence of relaxability")
            elif loo_rate > 0.95:
                verdict = "TRIGGER (forcing it true fires ~every bar - relaxation is meaningless)"
            elif is_event:
                verdict = (f"EVENT (signal true on only {own_rate:.1%} of bars - it either "
                           f"happened or it did not; not loosenable)")
            elif loo_rate / base_rate < 1.02:
                verdict = "NO-OP (relaxing admits nothing new - candidate to DROP)"
            else:
                verdict = "BINDING (relaxable filter - this is where trades would come from)"
            entry = {"clause": k, "loo_rate": round(loo_rate, 6),
                     "signal_own_rate": round(own_rate, 6) if own_rate is not None else None,
                     "lift": round(loo_rate / base_rate, 3) if base_rate > 0 else None,
                     "verdict": verdict}
            # B1400: the admission CURVE + the quality of what each relaxation would admit.
            # This is what turns "this gate binds" into an implementable threshold value.
            sw = sweep.get(n, {}).get(k)
            if sw:
                entry["sweep"] = [
                    {"multiple": m,
                     "new_threshold": round(relaxed_threshold(
                         next(o for kk, o, _t in gates[n] if kk == k),
                         next(t for kk, _o, t in gates[n] if kk == k), m), 5),
                     "extra_fires": sw[m][0],
                     "fires_after": st["base"] + sw[m][0],
                     "mean_fwd_return_of_new_pct": (round(sw[m][1] / sw[m][0], 3)
                                                    if sw[m][0] else None)}
                    for m in SWEEP_MULT]
            cl.append(entry)
        cl.sort(key=lambda c: -(c["lift"] or 0))
        results.append({"strategy": n, "bars_evaluated": st["bars"],
                        "base_fires": st["base"], "base_rate": round(base_rate, 6),
                        "clauses": cl})

    out = REPO / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"window": [str(start), str(end)], "n_tickers": len(tickers),
                               "holdout_touched": False, "results": results},
                              indent=2), encoding="utf-8")
    # B1394 fix: the summary must show the top RELAXABLE clause. Sorting all clauses by lift
    # put TRIGGER clauses at the top (macd_fast_crossover's crossover, lift 8.94) under a
    # header reading "top binding clause" - re-introducing, in the summary view, exactly the
    # misread the TRIGGER classification exists to prevent.
    print(f"\n{'strategy':<40}{'base rate':>11}{'top RELAXABLE clause':>34}{'lift':>8}")
    for r in sorted(results, key=lambda r: -r["base_rate"]):
        rel = [c for c in r["clauses"] if c["verdict"].startswith("BINDING")]
        top = rel[0] if rel else {}
        label = str(top.get("clause", "- none relaxable -"))[:32]
        print(f"  {r['strategy']:<38}{r['base_rate']:>11.5f}{label:>34}"
              f"{str(top.get('lift', '-')):>8}")
    def _by(pfx):
        return [(r["strategy"], c["clause"], c["lift"]) for r in results for c in r["clauses"]
                if c["verdict"].startswith(pfx)]
    noop, trig, bind, evt = _by("NO-OP"), _by("TRIGGER"), _by("BINDING"), _by("EVENT")
    absent_cl = _by("ABSENT-PRODUCER")
    print(f"\n[RESULT] across {len(results)} strategies: {len(noop)} NO-OP | "
          f"{len(bind)} BINDING (relaxable) | {len(trig)} TRIGGER + {len(evt)} EVENT "
          f"(not loosenable) | {len(absent_cl)} ABSENT-PRODUCER (broken, fix upstream)")
    if absent_cl:
        print("  ABSENT-PRODUCER clauses - the producer emits nothing; these are BUGS, not gates:")
        for s, c, _l in absent_cl[:25]:
            print(f"     {s:<40} {c}")
    print("  NO-OP clauses - relaxing admits nothing new, candidates to DROP:")
    for s, c, _l in noop[:25]:
        print(f"     {s:<40} {c}")
    print("  Top BINDING clauses - where additional trades would actually come from:")
    for s, c, l in sorted(bind, key=lambda x: -(x[2] or 0))[:15]:
        print(f"     {s:<40} {c:<30} lift={l}")
    print(f"[OK] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
