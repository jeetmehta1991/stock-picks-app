"""S6-B3140c (B3139q-r66): the ONE holdout read of a PRE-REGISTERED
free-level row on a landed Step-2 cube.

WHAT. A free-level leg ranks tighter threshold combinations on the in-sample
window only. A row pre-registered BEFORE the Step-2 launch (a combination plus
one exit) may be read on the holdout exactly once. This script is that read.

CONTRACT (fail closed at every step, L642):
  1. The free-levels artifact names its adapter (`grader`) and strategy; the
     adapter module must expose AXES, passes and parse_signals - an adapter
     without them is refused, never guessed (no STRAT constant here, L754).
  2. REPRODUCTION, signals: every covered trade-log row - in-sample AND
     holdout - must re-pass the production gate from its own logged signals.
  3. REPRODUCTION, score: the declared row re-derived on the in-sample window
     must EQUAL the artifact's factorial row at the declared exit (trade count,
     sharpe, ci_lo to the artifact's rounding). A mismatch means this reader
     is not looking at what was pre-registered; nothing is read.
  4. SPEND-ONCE: refuses when --out already exists. The holdout is a one-way
     door; there is no re-roll flag. S6-B3395 Batch 7c: the read also needs
     the owner's word (--ruling / --ruling-ticket, checked against its ledger
     row) and a COMMITTED free-levels artifact, and it is counted in the
     holdout-read ledger (scripts/holdout_reads.py) - a read of a strategy
     the ledger already records refuses unless --rereads names that read.
  5. THE READ: the declared levels select holdout-ENTERED trades; those trades
     at the declared exit are graded with roster_core.evaluate on the net
     basis, full_period_n = the declared row's count at that exit over the
     whole cube (the same construction grade_pairs_config.grade_step2 uses
     for the production line). PASS iff all six LIVE_GATES clear.

Labels written into the artifact: GRID-SELECTED (the row was chosen on
in-sample data), EXPLORATORY (B2085/F24: a banked measurement, no deployment
before the Stage-3 hedge leg), the occupancy caveat (offline trade sets are
not bounds, S6-B3139r) and any coverage disclosure the caller passes.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roster_core as rc  # noqa: E402
import free_level_window as flw  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_ADAPTER_ATTRS = ("AXES", "passes", "parse_signals")


class Refused(Exception):
    """A contract step failed; the holdout is not read."""


def load_adapter(grader_path: str):
    mod_name = Path(str(grader_path)).stem
    mod = importlib.import_module(mod_name)
    missing = [a for a in REQUIRED_ADAPTER_ATTRS if not hasattr(mod, a)]
    if missing:
        raise Refused(f"adapter {mod_name} lacks {missing} - this reader "
                      "only reads adapters exposing AXES/passes/parse_signals")
    return mod


def parse_levels(pairs: list[str], axes) -> dict:
    keys = [ax[1] for ax in axes]
    levels = {k: None for k in keys}
    for p in pairs:
        k, _, v = p.partition("=")
        if k not in levels:
            raise Refused(f"declared level {k!r} is not an adapter axis {keys}")
        levels[k] = None if v == "production" else float(v)
    return levels


def artifact_row(art: dict, levels: dict, exit_name: str) -> dict:
    want = {k: ("production" if v is None else float(v))
            for k, v in levels.items()}
    for r in (art.get("factorial") or {}).get("results") or []:
        combo = {k: (v if v == "production" else float(v))
                 for k, v in (r.get("combo") or {}).items()}
        if combo == want:
            for pe in r.get("per_exit") or []:
                if pe.get("exit") == exit_name:
                    return {"trades_kept": r.get("trades_kept"), **pe}
            raise Refused(f"declared exit {exit_name!r} is not in the "
                          "artifact's per_exit list for the declared combo")
    raise Refused(f"declared combo {want} is not a factorial row of the "
                  "free-levels artifact")


def annotate(tl: pd.DataFrame, mod) -> pd.DataFrame:
    keys = [ax[1] for ax in mod.AXES]
    vals = []
    for raw in tl["signals_at_entry"]:
        d = mod.parse_signals(raw)
        if d is None or any(k not in d for k in keys):
            vals.append(None)
        else:
            vals.append({k: float(d[k]) for k in keys})
    out = tl.copy()
    out["_vals"] = vals
    out["entry_date"] = out["entry_date"].astype(str).str[:10]
    return out


def ids_for(tl: pd.DataFrame, mod, levels: dict) -> set:
    cov = tl[tl["_vals"].notna()]
    keep = cov[cov["_vals"].apply(lambda v: mod.passes(levels, v))]
    return set(zip(keep["ticker"].astype(str), keep["entry_date"]))


def rows_for(ted: pd.DataFrame, ids: set, exit_name: str) -> pd.DataFrame:
    sub = ted[ted["exit_method"].astype(str) == exit_name]
    mask = [(t, d) in ids for t, d in
            zip(sub["ticker"].astype(str), sub["entry_date"])]
    return sub[mask]


def read(cube_dir: Path, art_path: Path, level_args: list[str],
         exit_name: str, *, min_n: int = 10, disclosure: str = "") -> dict:
    art = json.loads(art_path.read_text(encoding="utf-8"))
    mod = load_adapter(art.get("grader", ""))
    strat = str(art.get("strategy"))
    levels = parse_levels(level_args, mod.AXES)
    expect = artifact_row(art, levels, exit_name)

    tl = pd.read_csv(cube_dir / "trade_log.csv", low_memory=False)
    tl = annotate(tl[tl["strategy"].astype(str) == strat], mod)
    if tl.empty:
        raise Refused(f"no {strat} rows in trade_log.csv")
    prod = {ax[1]: None for ax in mod.AXES}
    cov = tl[tl["_vals"].notna()]
    bad = cov[~cov["_vals"].apply(lambda v: mod.passes(prod, v))]
    windows = flw.split_windows(tl)
    repro = {"covered_rows": int(len(cov)),
             "unverifiable_rows": int(tl["_vals"].isna().sum()),
             "rows_by_window": windows,
             "failed_reproduction": int(len(bad))}
    if len(bad):
        raise Refused(f"signal reproduction: {len(bad)} of {len(cov)} covered "
                      "rows do not re-pass the production gate")

    ted = pd.read_csv(cube_dir / "trade_exit_detail.csv", low_memory=False)
    ted = ted[ted["strategy"].astype(str) == strat].copy()
    ted["pnl_pct"] = rc.net_pnl(ted["pnl_pct"].astype(float))
    ted["entry_date"] = ted["entry_date"].astype(str).str[:10]
    d = pd.to_datetime(ted["entry_date"]).dt.date
    is_mask = (d >= rc.IS_START) & (d < rc.IS_END)
    ho_mask = (d >= rc.HO_START) & (d < rc.HO_END)

    ids = ids_for(tl, mod, levels)
    is_rows = rows_for(ted[is_mask], ids, exit_name)
    is_res = rc.evaluate(is_rows["pnl_pct"], is_rows["hold_days"], min_n=min_n)
    got = {"n": int(len(is_rows)),
           "sharpe": None if is_res is None else is_res.get("sharpe"),
           "ci_lo": None if is_res is None else is_res.get("ci_lo")}

    def _r(x):
        return None if x is None else round(float(x), 3)
    score_ok = (got["n"] == expect.get("n")
                and _r(got["sharpe"]) == _r(expect.get("sharpe"))
                and _r(got["ci_lo"]) == _r(expect.get("ci_lo")))
    score = {"artifact": {k: expect.get(k) for k in ("n", "sharpe", "ci_lo")},
             "re_derived": {k: (_r(v) if k != "n" else v)
                            for k, v in got.items()},
             "equal": bool(score_ok)}
    if not score_ok:
        raise Refused(f"score reproduction: re-derived IS {score['re_derived']}"
                      f" != artifact {score['artifact']} at {exit_name}")

    ho_rows = rows_for(ted[ho_mask], ids, exit_name)
    fp_n = int(len(rows_for(ted, ids, exit_name)))
    res = rc.evaluate(ho_rows["pnl_pct"], ho_rows["hold_days"], min_n=min_n,
                      full_period_n=fp_n)
    out = {"ticket": "S6-B3140c", "strategy": strat,
           "cube": str(cube_dir).replace("\\", "/"),
           "free_levels_artifact": str(art_path).replace("\\", "/"),
           "adapter": art.get("grader"),
           "declared_levels": {k: ("production" if v is None else v)
                               for k, v in levels.items()},
           "declared_exit": exit_name, "min_n": min_n,
           "basis": "net (roster_core.net_pnl); windows roster_core IS/HO, "
                    "entry-dated",
           "reproduction": repro, "score_reproduction": score,
           "holdout_n": int(len(ho_rows)), "full_period_n": fp_n,
           "labels": ["GRID-SELECTED", "EXPLORATORY (B2085/F24)",
                      "OCCUPANCY: offline trade set, not a bound (S6-B3139r)"],
           "coverage_disclosure": disclosure or None,
           "rule": "PASS iff all six roster_core.LIVE_GATES clear on the "
                   "holdout at the declared exit; one read, no re-roll"}
    if res is None:
        out["verdict"] = "BELOW_POWER_FLOOR"
        return out
    gates = {k: bool(res["gates"][k]) for k in rc.LIVE_GATES}
    out.update({k: res.get(k) for k in
                ("sharpe", "sortino", "psr", "profit_factor", "payoff",
                 "expectancy", "win_rate", "p", "ci_lo")})
    out["gates"] = gates
    out["gates_passed"] = int(sum(gates.values()))
    out["verdict"] = "PASS" if all(gates.values()) else "FAIL"
    if out["verdict"] == "PASS":
        out["margin"] = rc.qualifier_margin(res.get("sharpe"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cube", required=True)
    ap.add_argument("--free-levels", required=True)
    ap.add_argument("--level", action="append", default=[],
                    help="axis_key=value (or axis_key=production); repeat")
    ap.add_argument("--exit", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-n", type=int, default=10)
    ap.add_argument("--disclosure", default="")
    # S6-B3395 Batch 7c: the fourth holdout-read door - the owner's own word,
    # checked against its ledger row (scripts/owner_word.py, S6-B3338), and the
    # holdout-read ledger (scripts/holdout_reads.py)
    ap.add_argument("--ruling", required=True,
                    help="the owner's words opening this read, verbatim as its row records them")
    ap.add_argument("--ruling-ticket", required=True,
                    help="the ticket whose row records --ruling")
    ap.add_argument("--rereads", default=None,
                    help="the read_id of the recorded holdout read this one repeats")
    a = ap.parse_args(argv)
    import owner_word
    import holdout_reads as hr
    word = {"ticket": a.ruling_ticket.strip(), "verbatim": owner_word.normalise(a.ruling)}
    werrs = owner_word.refusals(word, door="declared-row holdout read")
    if werrs:
        print(f"[REFUSED] {werrs[0]} - the holdout was NOT read")
        return 3
    out = Path(a.out)
    if out.exists():
        print(f"[REFUSED] {out} exists - the holdout read is spend-once")
        return 3
    # runbook 1.1 item 2 / F4: the declared row's artifact is COMMITTED before
    # any holdout code path runs (the check both offline readers make)
    why = hr.step1_uncommitted(a.free_levels)
    if why:
        print(f"[REFUSED] {why} - the holdout was NOT read")
        return 3
    try:
        strat = json.loads(Path(a.free_levels).read_text(encoding="utf-8")).get("strategy")
    except (OSError, ValueError) as exc:
        print(f"[REFUSED] the free-levels artifact is unreadable ({exc!r}) - the "
              "holdout was NOT read")
        return 2
    read_id = hr.repo_rel(out)
    why = (hr.reread_refusal(strat, None, declared=a.rereads,
                             door="declared_row_holdout_read")
           or hr.read_id_refusal(read_id, door="declared_row_holdout_read"))
    if why:
        print(f"[REFUSED] {why} - the holdout was NOT read")
        return 3
    prior = [e["read_id"] for e in hr.prior_reads(strat, None)]
    try:
        rec = read(Path(a.cube), Path(a.free_levels), a.level, a.exit,
                   min_n=a.min_n, disclosure=a.disclosure)
    except Refused as exc:
        print(f"[REFUSED] {exc} - the holdout was NOT read")
        return 2
    hr.record(read_id=read_id, strategy=strat, leg=None,
              door="declared_row_holdout_read", artifact=read_id,
              source=hr.repo_rel(a.cube), owner_word=word,
              rereads=[a.rereads] if a.rereads else [],
              declared=True if a.rereads else None)
    rec["owner_word"] = word
    rec["holdout_read_ledger"] = {"read_id": read_id, "prior_reads": prior,
                                  "rereads": [a.rereads] if a.rereads else []}
    out.write_text(json.dumps(rec, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: rec.get(k) for k in
                      ("verdict", "gates_passed", "gates", "sharpe", "ci_lo",
                       "sortino", "psr", "profit_factor", "holdout_n",
                       "full_period_n", "score_reproduction")},
                     indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
