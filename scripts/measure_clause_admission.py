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

    stats = {n: {"bars": 0, "base": 0, "loo": {c[0]: 0 for c in gates[n]}} for n in names}
    for ti, tk in enumerate(tickers, 1):
        df = MFC._load_ohlcv(tk)
        if df is None or df.empty:
            continue
        try:
            per_bar = MFC._precompute_signals_for_ticker(df, tk, start, end)
        except Exception as exc:
            print(f"  [skip] {tk}: {exc}")
            continue
        for _bar_date, sig in per_bar:
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
            if base_rate <= 0:
                verdict = "UNDEFINED (base fire rate 0 - strategy starved on this sample)"
            elif loo_rate > 0.95:
                verdict = "TRIGGER (forcing it true fires on ~every bar - relaxation is meaningless)"
            elif loo_rate / base_rate < 1.02:
                verdict = "NO-OP (relaxing admits nothing new - candidate to DROP)"
            else:
                verdict = "BINDING (relaxable filter - this is where trades would come from)"
            cl.append({"clause": k, "loo_rate": round(loo_rate, 6),
                       "lift": round(loo_rate / base_rate, 3) if base_rate > 0 else None,
                       "verdict": verdict})
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
    noop, trig, bind = _by("NO-OP"), _by("TRIGGER"), _by("BINDING")
    print(f"\n[RESULT] across {len(results)} strategies: {len(noop)} NO-OP | "
          f"{len(bind)} BINDING (relaxable) | {len(trig)} TRIGGER (not relaxable)")
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
