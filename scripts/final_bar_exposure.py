#!/usr/bin/env python
"""S6-B3155a: how much FROZEN graded output was priced on a partial final bar
(read-only; nothing here re-grades anything - re-grading admitted lines is the
owner's option (c), not taken).

THE SET is read from the evidence written by
scripts/final_bar_third_source_check.py classify, never typed:
  - repair rows of shape PARTIAL_SESSION (prices differed from the confirmed
    full session; VOLUME_ONLY rows priced every exit correctly),
  - unconfirmed_partial_bars (prices differ from the prefetch, no third-source
    record),
  - no_prefetch_differs (no prefetch file; the third source does not
    reproduce the engine bar).
CVNA is in none of them: its engine bar is the full session in a 5.0x price
scale (379.09 = 5 x 75.818), so its exits were priced consistently.

REPORTS
  cubes     - per roster cube (build_phase_1b_roster.CUBES), rows exiting on
              the evidence date, and those on a partial-priced ticker.
  admitted  - EXACT per admitted line: its graded trade set reproduced by the
              fail-closed #290 functions in scripts/rescore_admissions_net.py
              (recorded metrics and both trade counts must reproduce; a
              net-basis breadth read is reproduced the same way on its own
              cube), joined to the cube's exit_date on (ticker, entry_date,
              direction, exit_method). A line whose window ends before the
              evidence date is NOT-EXPOSED.

usage: python scripts/final_bar_exposure.py [--evidence ...] [--out ...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "EXECUTION_QUEUE.md").is_file():          # L846 marker rule
    raise SystemExit(f"final_bar_exposure: {ROOT} is not the repo root (L846)")
for _p in (ROOT, ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

EVIDENCE = "output_audit/b3155a_final_bar_third_source.json"
OUT = "output_audit/b3155a_final_bar_exposure.json"


def partial_priced(evidence: dict) -> set:
    return ({r["ticker"] for r in evidence["repair"] if r["shape"] == "PARTIAL_SESSION"}
            | set(evidence["unconfirmed_partial_bars"])
            | set(evidence["no_prefetch_differs"]))


def cube_exposure(cube_dir: Path, date: str, tickers: set) -> dict:
    import pandas as pd
    p = cube_dir / "trade_exit_detail.csv"
    if not p.is_file():
        return {"missing": str(p)}
    n = on_final = on_set = 0
    reasons, strats = Counter(), Counter()
    for ch in pd.read_csv(p, usecols=["ticker", "strategy", "exit_date", "exit_reason"],
                          dtype=str, chunksize=1_000_000):
        n += len(ch)
        f = ch[ch["exit_date"] == date]
        on_final += len(f)
        g = f[f["ticker"].isin(tickers)]
        on_set += len(g)
        reasons.update(g["exit_reason"].fillna("NA"))
        strats.update(g["strategy"].fillna("NA"))
    return {"rows": n, "exit_on_date": on_final, "exit_on_date_partial_priced": on_set,
            "exit_reasons_top8": dict(reasons.most_common(8)),
            "strategies_distinct": len(strats)}


def _breadth_line(ran, adm: dict, art: dict):
    """A net-basis breadth read reproduced like reproduce_tws_line: both trade
    counts exact and the recorded holdout Sharpe on the read's own basis."""
    combo = adm["combination"]
    row = next((r for r in art.get("rows", [])
                if r.get("axis") == combo["axis"] and r.get("op") == combo["op"]
                and abs(float(r.get("level")) - float(combo["level"])) < 1e-9
                and r.get("exit") == adm["exit"]), None)
    if row is None:
        return {"status": "UNAVAILABLE", "reason": "admitted cell not found"}, None, None
    cdir = Path(art["cube_dir"])
    cdir = cdir if cdir.is_absolute() else ROOT / cdir
    frame = ran.cube_frame(cdir, adm["strategy"], [combo["axis"]])
    sub = ran.apply_ops(frame[frame["exit_method"] == adm["exit"]],
                        [(combo["axis"], combo["op"], float(combo["level"]))])
    sc = ran.score_both(sub)
    ok = (sc["holdout_n"] == row["holdout_n"] and sc["full_period_n"] == row["full_n"]
          and abs(float(sc["net"]["sharpe"]) - float(row["holdout_sharpe"])) <= 1e-3)
    if not ok:
        return {"status": "UNAVAILABLE", "reason": "reproduction failed (fail closed)"}, None, None
    return {"status": "RESCORED"}, sub, cdir


def admitted_exposure(date: str, tickers: set) -> dict:
    import pandas as pd
    import rescore_admissions_net as ran
    adms = json.loads((ROOT / "output_audit" / "phase_1b_step2_admissions.json")
                      .read_text(encoding="utf-8"))["admissions"]
    exits_cache: dict = {}
    lines = []
    for adm in adms:
        strat = adm["strategy"]
        rec = {"strategy": strat, "exit": adm["exit"], "window": adm.get("window")}
        ends = re.findall(r"\d{4}-\d{2}-\d{2}", str(adm.get("window") or ""))
        if len(ends) >= 2 and ends[1] < date:
            rec["status"] = "NOT-EXPOSED"
            rec["reason"] = f"window ends {ends[1]}, before {date}"
            lines.append(rec)
            continue
        art = json.loads((ROOT / adm["grid_artifact"]).read_text(encoding="utf-8"))
        if strat == "three_white_soldiers":
            res, sub = ran.reproduce_tws_line(adm)
            cdir = ROOT / art["cube_dir"]
        elif str(art.get("basis")) == "net":
            res, sub, cdir = _breadth_line(ran, adm, art)
        else:
            res, sub = ran.reproduce_r5_line(adm, art)
            cdir = ROOT / "output_r5_merged_1_7"
        rec["reproduction"] = res.get("status")
        if sub is None:
            rec["status"] = "UNAVAILABLE"
            rec["reason"] = res.get("reason")
            lines.append(rec)
            continue
        key = str(cdir)
        if key not in exits_cache:
            exits_cache[key] = pd.read_csv(
                cdir / "trade_exit_detail.csv", low_memory=False,
                usecols=["ticker", "strategy", "entry_date", "direction", "exit_method",
                         "exit_date"])
        e = exits_cache[key]
        e = e[e.strategy == strat].copy()
        e["entry_date"] = pd.to_datetime(e["entry_date"], errors="coerce").dt.date
        k = ["ticker", "entry_date", "direction", "exit_method"]
        m = sub[k].merge(e[k + ["exit_date"]], on=k, how="left")
        on = m[m["exit_date"] == date]
        hit = on[on["ticker"].isin(tickers)]
        rec.update({"status": "COUNTED", "cube": str(cdir.relative_to(ROOT)).replace("\\", "/"),
                    "rows": int(len(sub)), "join_unmatched": int(m["exit_date"].isna().sum()),
                    "exit_on_date": int(len(on)), "exit_on_date_partial_priced": int(len(hit)),
                    "tickers": sorted(set(hit["ticker"]))})
        lines.append(rec)
    counted = [r for r in lines if r["status"] == "COUNTED"]
    touched = [r for r in counted if r["exit_on_date_partial_priced"]]
    return {"lines": len(lines), "counted": len(counted),
            "not_exposed": [r["strategy"] for r in lines if r["status"] == "NOT-EXPOSED"],
            "unavailable": [r["strategy"] for r in lines if r["status"] == "UNAVAILABLE"],
            "touched": len(touched),
            "rows_touched_total": sum(r["exit_on_date_partial_priced"] for r in counted),
            "max_rows_one_line": max((r["exit_on_date_partial_priced"] for r in counted), default=0),
            "per_line": lines}


def main(argv=None) -> int:
    from build_phase_1b_roster import CUBES
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--evidence", default=EVIDENCE)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv)
    ev = json.loads((ROOT / a.evidence).read_text(encoding="utf-8"))
    date = ev["date"]
    tickers = partial_priced(ev)
    step2 = set((ROOT / ev["step2_universe"]["tickers_file"]).read_text().split())
    doc = {"ticket": "S6-B3155a", "date": date, "evidence": a.evidence,
           "generator": "scripts/final_bar_exposure.py",
           "partial_priced": {"n": len(tickers), "in_step2_universe": len(tickers & step2),
                              "definition": "PARTIAL_SESSION repair rows + unconfirmed_partial_bars "
                                            "+ no_prefetch_differs (CVNA excluded: full session "
                                            "in a 5.0x scale)"},
           "cubes": {label: cube_exposure(ROOT / d, date, tickers) for label, d in CUBES},
           "admitted": admitted_exposure(date, tickers),
           "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (ROOT / a.out).write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("partial-priced:", json.dumps(doc["partial_priced"]))
    for label, c in doc["cubes"].items():
        print(label, {k: c.get(k) for k in ("rows", "exit_on_date", "exit_on_date_partial_priced",
                                            "strategies_distinct")})
    ad = doc["admitted"]
    print("admitted:", {k: ad[k] for k in ("lines", "counted", "touched", "rows_touched_total",
                                           "max_rows_one_line", "not_exposed", "unavailable")})
    return 0 if not ad["unavailable"] else 3


if __name__ == "__main__":
    sys.exit(main())
