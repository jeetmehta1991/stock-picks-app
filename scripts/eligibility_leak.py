#!/usr/bin/env python
"""S6-B3134a part C (owner-approved A + C, 2026-09-29): the GRADER-SIDE
eligibility guard. It asks, of every entry already in a cube, the question
the fixed engine asks on the screen day (entry_date = as_of,
backtest.BacktestEngine._process_day/3781), through the SAME predicate the engine uses
(backtest/data/eligibility.py - jan1_reason / daily_reason, L593):

  carry:<reason>   the ticker was NOT in its year's Jan-1 set. The pre-B3135
                   engine could only enter it through the open-trade carry
                   (M2); <reason> is its Jan-1 failure.
  daily:<reason>   in the Jan-1 set but not screenable that day under
                   daily_subtract_v1 (M1): not-member-today / close<min-today.
  unknown:<why>    cannot be classified (no cached OHLCV for the ticker) -
                   reported apart, never counted as a leak or as clean.
  ""               screenable under daily_subtract_v1.

OPT-IN, never default-on in a shared loader: that would silently re-grade
the closed roster, the admissions and the in-flight waterfall ranking.
Two uses:
  (i)  the landing battery's `eligibility_leak` lens (run_postconfig.py
       lenses) - report-only: INFO with the counts on a clean cube and on
       a cube built before B3135 (no stamp = jan1_legacy: the leak is the
       known, ticketed S6-B3134a class, so a WARN would reopen step 6 on
       every re-run of an old cube - L721), WARN when entries cannot be
       classified (a guard that cannot see says so), and FAIL when a cube
       STAMPED daily_subtract_v1 still carries a leaked entry - the engine
       fix regressed;
  (ii) --roster: the one-shot LABEL re-score of the graded Phase 1B lines.
       Each line is REPRODUCED from its own cube first (#290 - a re-scorer
       that cannot reproduce the recorded row publishes nothing for it),
       then scored with its leaked entries removed. Labels only: no roster
       line changes here; any removal is a per-line owner ruling.

Frames are the engine's own (backtest.data.cache.get_ohlcv_bulk from
DATA_LOAD_START, probe=True - a cache miss never becomes a live fetch);
membership is get_sp500_constituents_pit (out on the removal date).

Exit codes (--cube): 0 report written; 2 a daily-stamped cube carries a
leaked entry (REGRESSION); 3 input unreadable.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "EXECUTION_QUEUE.md").is_file():          # L846 marker rule
    raise SystemExit(f"eligibility_leak: {ROOT} is not the repo root (L846)")
for _p in (ROOT, ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from backtest.data import eligibility as E               # noqa: E402

LENS = "eligibility_leak"
CLEAN = ""


class Classifier:
    """Per (ticker, screen day): carry:<r> / daily:<r> / unknown:<why> / "".
    Membership and Jan-1 answers are cached; frames are loaded once."""

    def __init__(self, tickers, end, frames=None, members_fn=None,
                 master=None, tiers_fn=None):
        from backtest.config import DATA_LOAD_START, LIQUIDITY
        self.min_price = LIQUIDITY["min_price"]
        self.min_vol = LIQUIDITY["min_avg_volume"]
        if frames is None:
            from backtest.data.cache import get_ohlcv_bulk
            frames = get_ohlcv_bulk(sorted(set(tickers)), start=DATA_LOAD_START,
                                    end=end, probe=True)
        self.frames = {}
        for t, df in (frames or {}).items():
            if df is None or len(df) == 0:
                continue
            df = df.copy()
            df.index = pd.to_datetime(df.index)
            self.frames[t] = df
        if members_fn is None:
            from backtest.data.universe import get_sp500_constituents_pit
            members_fn = get_sp500_constituents_pit
        self._members_fn = members_fn
        if master is None:
            from backtest.data.universe import get_t1a_master_set
            master = get_t1a_master_set()
        self.master = set(master)
        # S6-B3136c: the SAME per-day tier windows the engine reads (a
        # default DailyTiers runs the per-tier file check - B3139 - and
        # refuses on a missing, unreadable or unwindowed tier file)
        self._tiers = E.DailyTiers(fn=tiers_fn)
        self._pit: dict = {}
        self._jan1: dict = {}

    def members(self, d: date) -> set:
        if d not in self._pit:
            self._pit[d] = set(self._members_fn(d)) if self.master else set()
        return self._pit[d]

    def jan1(self, ticker: str, year: int):
        k = (ticker, year)
        if k not in self._jan1:
            ref = date(year, 1, 1)
            df = self.frames[ticker]
            self._jan1[k] = E.jan1_reason(
                df[df.index.date <= ref], ticker, self.master,
                self.members(ref), self.min_price, self.min_vol)
        return self._jan1[k]

    def classify(self, ticker: str, d: date) -> str:
        if ticker not in self.frames:
            return "unknown:no-ohlcv"
        r = self.jan1(ticker, d.year)
        if r is not None:
            return f"carry:{r}"
        df = self.frames[ticker]
        sliced = df[df.index.date <= d]          # >= 30 bars: it passed Jan 1
        r = E.daily_reason(ticker, float(sliced["close"].iloc[-1]),
                           self.master, self.members(d), self.min_price,
                           tiers_today=self._tiers.members(d))
        return CLEAN if r is None else f"daily:{r}"


def _as_date(x) -> date:
    return pd.Timestamp(str(x)[:10]).date()


def classify_entries(frame: pd.DataFrame, clf: Classifier) -> pd.Series:
    """A leak reason per row of `frame` (columns ticker, entry_date),
    computed once per distinct (ticker, entry day)."""
    keys = list(zip(frame["ticker"].astype(str),
                    frame["entry_date"].map(_as_date)))
    memo = {k: clf.classify(*k) for k in sorted(set(keys))}
    return pd.Series([memo[k] for k in keys], index=frame.index, dtype=object)


def reason_class(r: str) -> str:
    return "clean" if r == CLEAN else r.split(":", 1)[0]


def cube_report(cube_dir, strategy=None, frames=None, members_fn=None,
                master=None, tiers_fn=None) -> dict:
    """The eligibility read of one cube: its stamp, the rule its rows were
    screened under, and every entry classified. Raises on an unreadable stamp
    (L642) - the caller decides how loudly."""
    cube_dir = Path(cube_dir)
    stamp = E.read_stamp(cube_dir)
    built = E.built_mode(stamp)
    ted = pd.read_csv(cube_dir / "trade_exit_detail.csv", low_memory=False,
                      usecols=lambda c: c in {"strategy", "ticker", "entry_date"})
    if strategy:
        ted = ted[ted["strategy"] == strategy]
    ent = ted.drop_duplicates(["strategy", "ticker", "entry_date"]).copy()
    rep = {"cube": cube_dir.name, "stamp": stamp, "built_mode": built,
           "strategy": strategy, "entries": int(len(ent))}
    if ent.empty:
        rep.update(leaked=0, unknown=0, by_reason={}, per_strategy={},
                   verdict="EMPTY")
        return rep
    end = max(_as_date(x) for x in ent["entry_date"])
    clf = Classifier(ent["ticker"].astype(str).unique(), end, frames=frames,
                     members_fn=members_fn, master=master,
                     tiers_fn=tiers_fn)
    ent["reason"] = classify_entries(ent, clf)
    ent["cls"] = ent["reason"].map(reason_class)
    leaked = int(ent["cls"].isin(["carry", "daily"]).sum())
    unknown = int((ent["cls"] == "unknown").sum())
    by_reason = {k: int(v) for k, v in
                 ent.loc[ent["reason"] != CLEAN, "reason"].value_counts().items()}
    per = {}
    for s, g in ent.groupby("strategy"):
        per[str(s)] = {"entries": int(len(g)),
                       "carry": int((g["cls"] == "carry").sum()),
                       "daily": int((g["cls"] == "daily").sum()),
                       "unknown": int((g["cls"] == "unknown").sum())}
    if built == E.MODE_DAILY and leaked:
        verdict = "REGRESSION"
    elif leaked:
        verdict = "LEGACY-LEAKS"
    else:
        verdict = "CLEAN"
    rep.update(leaked=leaked, unknown=unknown, by_reason=by_reason,
               per_strategy=per, verdict=verdict,
               tickers_without_ohlcv=sorted(
                   set(ent.loc[ent["cls"] == "unknown", "ticker"].astype(str))))
    return rep


def lens_row(rep: dict) -> tuple:
    """The battery row: FAIL on a daily-stamped cube carrying a leak (the fix
    regressed), WARN on unclassifiable entries, INFO otherwise - including a
    pre-B3135 cube's leaks, whose counts are printed (see the module doc)."""
    n, lk, un = rep["entries"], rep.get("leaked", 0), rep.get("unknown", 0)
    carry = sum(v for k, v in rep.get("by_reason", {}).items()
                if k.startswith("carry:"))
    daily = sum(v for k, v in rep.get("by_reason", {}).items()
                if k.startswith("daily:"))
    ev = (f"{lk} of {n} entries not screenable under daily_subtract_v1 "
          f"(carry {carry} / daily {daily}); {un} unclassifiable; cube built "
          f"under {rep['built_mode']} "
          f"({'no stamp' if rep.get('stamp') is None else 'stamped'})")
    if rep.get("verdict") == "REGRESSION":
        return (LENS, "FAIL", "REGRESSION - the cube is stamped "
                              "daily_subtract_v1 yet " + ev)
    if un:
        return (LENS, "WARN", ev + " - unclassified entries were not checked")
    if lk:
        return (LENS, "INFO", ev + " - graded numbers include these entries "
                                   "(S6-B3134a)")
    return (LENS, "INFO", ev)


# ------------------------------------------------------------------ roster
def _score_clean(sub: pd.DataFrame, clf: Classifier, score_fn) -> dict:
    """Classify a reproduced line's rows and score it with its leaked rows
    removed. `score_fn` is the scorer that reproduced the line (so the clean
    score is on the same basis)."""
    reasons = classify_entries(sub, clf)
    cls = reasons.map(reason_class)
    leak = cls.isin(["carry", "daily"])
    clean = sub[~leak]
    out = {"rows": int(len(sub)), "leaked_rows": int(leak.sum()),
           "unknown_rows": int((cls == "unknown").sum()),
           "by_reason": {k: int(v) for k, v in
                         reasons[reasons != CLEAN].value_counts().items()},
           "leaked_holdout_rows": int(
               (leak & sub["entry_date"].map(_as_date).ge(_HO_START())).sum()),
           "leaked_pnl_sum": float(sub.loc[leak, "pnl_pct"].sum()),
           "total_pnl_sum": float(sub["pnl_pct"].sum())}
    # the SAME scorer on both sets: any label change is the removal's alone
    out["with_leaks_score"] = score_fn(sub)
    out["clean_score"] = score_fn(clean) if int(leak.sum()) else None
    return out


def _HO_START():
    import roster_core as rc
    return rc.HO_START


def _gates(ev) -> dict | None:
    if not ev:
        return None
    keep = ("sharpe", "ci_lo", "psr", "profit_factor", "sortino", "n",
            "all_live_gates", "n_gates", "gates")
    return {k: ev.get(k) for k in keep if k in ev}


def roster_rescore(root: Path = ROOT, only=None) -> dict:
    """(ii): every graded Phase 1B line reproduced from its own cube, then
    re-scored without its leaked entries. Reproduction failures publish
    nothing for the line (NOT-REPRODUCED)."""
    import rescore_admissions_net as ran
    import roster_core as rc
    rows = []
    frames_cache: dict = {}

    def clf_for(sub):
        tick = sorted(set(sub["ticker"].astype(str)))
        end = max(_as_date(x) for x in sub["entry_date"])
        key = (tuple(tick), end)
        if key not in frames_cache:
            frames_cache[key] = Classifier(tick, end)
        return frames_cache[key]

    def score_admission(sub):
        sc = ran.score_both(sub)
        return {"holdout_n": sc["holdout_n"], "full_period_n": sc["full_period_n"],
                "raw": _gates(sc["raw"]), "net": _gates(sc["net"])}

    adm_doc = json.load(open(root / "output_audit" / "phase_1b_step2_admissions.json",
                             encoding="utf-8"))
    for adm in adm_doc["admissions"]:
        strat = adm["strategy"]
        if only and strat not in only:
            continue
        rec = {"line": strat, "role": "STEP2_ADMISSION", "exit": adm["exit"]}
        try:
            if strat == "smc_breaker_block_long":
                res, sub = reproduce_smc_line(adm, root)
            elif strat == "three_white_soldiers":
                res, sub = ran.reproduce_tws_line(adm)
            else:
                art = json.load(open(root / adm["grid_artifact"], encoding="utf-8"))
                res, sub = ran.reproduce_r5_line(adm, art)
        except Exception as exc:                      # noqa: BLE001 - per line
            res, sub = {"status": "NOT-REPRODUCED", "reason": repr(exc)[:200]}, None
        if sub is None or res.get("status") not in ("RESCORED", "REPRODUCED"):
            rec.update(status="NOT-REPRODUCED",
                       reason=res.get("reason") or res.get("mismatches"),
                       fresh=res.get("fresh"),
                       identity_reproduced=res.get("identity_reproduced"))
            rows.append(rec)
            continue
        scorer = (res.pop("_scorer", None) or score_admission)
        rec.update(status="REPRODUCED", **_score_clean(sub, clf_for(sub), scorer))
        rows.append(rec)
    roster = json.load(open(root / "output_audit" / "b1453_phase_1b_roster.json",
                            encoding="utf-8"))
    for cell in roster.get("roster", []):
        if only and cell["strategy"] not in only:
            continue
        rec = {"line": cell["strategy"], "role": "FUNNEL_CELL", "exit": cell["exit"]}
        try:
            res, sub, scorer = reproduce_funnel_cell(cell, root, rc)
        except Exception as exc:                      # noqa: BLE001 - per line
            res, sub, scorer = {"status": "NOT-REPRODUCED",
                                "reason": repr(exc)[:200]}, None, None
        if sub is None:
            rec.update(status="NOT-REPRODUCED", reason=res.get("reason"),
                       fresh=res.get("fresh"),
                       identity_reproduced=res.get("identity_reproduced"))
            rows.append(rec)
            continue
        rec.update(status="REPRODUCED", **_score_clean(sub, clf_for(sub), scorer))
        rows.append(rec)
    return {"metric_code": rc.metric_code_fingerprint(),   # S6-B3136 (B3139)
            "_doc": ("S6-B3134a part C (ii): one-shot LABEL re-score of the "
                     "graded Phase 1B lines - each line reproduced from its "
                     "own cube (#290) then scored with the entries the fixed "
                     "engine would not take removed. Labels only; no line "
                     "changes; any removal is a per-line owner ruling."),
            "predicate": "backtest/data/eligibility.py (jan1_reason, daily_reason)",
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "rows": rows}


def _mismatches(got: dict, want: dict, keys=("sharpe", "ci_lo", "psr",
                                              "profit_factor", "sortino")):
    bad = []
    for k in keys:
        w, g = want.get(k), got.get(k)
        if w is not None and (g is None or abs(float(g) - float(w)) > 1e-3):
            bad.append(f"{k} {g} != {w}")
    return bad


def reproduce_smc_line(adm: dict, root: Path):
    """smc_breaker_block_long: its family grader (tighten_breaker_block.py)
    derived the admitted combination's trade set from the Step-2 cube by
    re-diagnosing every fire (diagnose_fire at the grid's P1 swing length,
    the admitted close_mitigation) and keeping the survivors of the admitted
    caps (survives). Reproduced with the grader's OWN two functions; fires,
    holdout_n, full_period_n and the gate values must equal the admitted
    grid row (net basis - load_cube)."""
    import roster_core as rc
    import tighten_breaker_block as tbb
    art_rel = adm["grid_artifact"]
    art = json.load(open(root / art_rel, encoding="utf-8"))
    combo = adm.get("combination") or {}
    row = next((r for r in art.get("results", [])
                if r.get("exit") == adm["exit"]
                and all(r.get(k) == v for k, v in combo.items())), None)
    if row is None:
        return {"status": "NOT-REPRODUCED",
                "reason": "admitted combination row not in its grid"}, None
    name = Path(art_rel).name
    if not name.endswith("_grid_auto.json"):
        return {"status": "NOT-REPRODUCED",
                "reason": f"cannot derive the cube from {name}"}, None
    cdir = root / name[: -len("_grid_auto.json")]
    swing = int((art.get("config") or {}).get("P1_swing_length"))
    g_all = rc.load_cube(cdir / "trade_exit_detail.csv")
    g = g_all[g_all["strategy"] == adm["strategy"]]
    fires = g[["ticker", "entry_date"]].drop_duplicates()
    keep = set()
    for t in sorted(fires["ticker"].astype(str).unique()):
        df = tbb._load_ohlcv(t)
        if df is None:
            continue
        for when in fires[fires["ticker"] == t]["entry_date"]:
            d = tbb.diagnose_fire(df, pd.Timestamp(when), swing_length=swing,
                                  close_mitigation=combo.get("close_mitigation"))
            if d and tbb.survives(d, combo.get("break_pct_max"),
                                  combo.get("age_bars_max"), combo.get("tail_n")):
                keep.add((t, when))
    sub = g[[(str(r.ticker), r.entry_date) in keep for r in g.itertuples()]]
    sub = sub[sub["exit_method"] == adm["exit"]]

    def score(x):
        ho = rc.holdout(x)
        ev = rc.evaluate(ho["pnl_pct"], ho["hold_days"], min_n=10,
                         full_period_n=len(x))
        return {"holdout_n": int(len(ho)), "full_period_n": int(len(x)),
                "net": _gates(ev)}
    got = score(sub)
    ident = []
    if len(keep) != int(row.get("fires", -1)):
        ident.append(f"fires {len(keep)} != {row.get('fires')}")
    for k in ("holdout_n", "full_period_n"):
        if got[k] != int(row.get(k, -1)):
            ident.append(f"{k} {got[k]} != {row.get(k)}")
    bad = ident + _mismatches(got["net"] or {}, row)
    if bad:
        # S6-B3136 (B3137): the FRESH evaluation rides beside the named
        # drift; identity_reproduced says whether the trade set itself
        # reproduced (only then is `fresh` the same line on current code)
        if ident:
            # S6-B3139h: a count mismatch names its own make-up
            import free_level_window as _flw
            bad = bad + [_flw.gap_breakdown(g_all, adm["exit"])]
        return {"status": "NOT-REPRODUCED", "reason": bad, "fresh": got,
                "identity_reproduced": not ident}, None
    return {"status": "REPRODUCED", "_scorer": score}, sub


def reproduce_funnel_cell(cell: dict, root: Path, rc):
    """A funnel cell (build_phase_1b_roster.py main): its cube's (strategy,
    direction) rows at the recorded exit, roster_core's net basis, the
    holdout [HO_START, HO_END), evaluate at the funnel's default power floor
    with full_period_n = the cell's rows at that exit. The holdout n and the
    gate values must equal the roster record."""
    cube = {"R5": root / "output_r5_merged_1_7"}.get(cell.get("cube"))
    if cube is None:
        return {"reason": f"unknown funnel cube {cell.get('cube')!r}"}, None, None
    df = rc.load_cube(cube / "trade_exit_detail.csv", chunksize=500_000)
    sub = df[(df["strategy"] == cell["strategy"])
             & (df["direction"] == cell["direction"])
             & (df["exit_method"] == cell["exit"])]
    del df

    def score(x):
        ho = rc.holdout(x)
        ev = rc.evaluate(ho["pnl_pct"], ho["hold_days"], full_period_n=len(x))
        return {"holdout_n": int(len(ho)), "full_period_n": int(len(x)),
                "net": _gates(ev)}
    got = score(sub)
    want = cell.get("holdout") or {}
    ident = []
    if int(want.get("n", -1)) != got["holdout_n"]:
        ident.append(f"holdout n {got['holdout_n']} != {want.get('n')}")
    bad = ident + _mismatches(got["net"] or {}, want)
    if ident:
        # S6-B3139h: a count mismatch names its own make-up
        import free_level_window as _flw
        bad = bad + [_flw.window_note(sub)]
    if bad:
        return ({"reason": bad, "fresh": got, "identity_reproduced": not ident},
                None, None)
    return {"status": "REPRODUCED"}, sub, score


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--cube", help="a cube dir: classify its entries")
    g.add_argument("--roster", action="store_true",
                   help="one-shot label re-score of the graded Phase 1B lines")
    ap.add_argument("--strategy", default=None)
    ap.add_argument("--only", default=None,
                    help="--roster: comma-separated lines to re-score (default all)")
    ap.add_argument("--out", default=None, help="JSON path")
    a = ap.parse_args(argv)
    if a.cube:
        try:
            rep = cube_report(a.cube, a.strategy)
        except (OSError, ValueError) as exc:
            print(f"[FAIL] unreadable input: {exc!r}")
            return 3
        row = lens_row(rep)
        print(f"[{row[1]}] {row[2]}")
        doc = rep
        rc_ = 2 if rep.get("verdict") == "REGRESSION" else 0
    else:
        doc = roster_rescore(only=set(a.only.split(",")) if a.only else None)
        for r in doc["rows"]:
            cs = (r.get("clean_score") or {}).get("net") or {}
            print(f"{r['line']:45s} {r['status']:15s} leaked "
                  f"{r.get('leaked_rows', '-')}/{r.get('rows', '-')} "
                  f"clean net sharpe {cs.get('sharpe', '-')} "
                  f"all-six {cs.get('all_live_gates', '-')}")
        rc_ = 0 if all(r["status"] == "REPRODUCED" for r in doc["rows"]) else 3
    if a.out:
        Path(a.out).write_text(json.dumps(doc, indent=1, default=str) + "\n",
                               encoding="utf-8", newline="\n")
        print("wrote", a.out)
    return rc_


if __name__ == "__main__":
    raise SystemExit(main())
