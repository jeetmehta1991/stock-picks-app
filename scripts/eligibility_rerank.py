#!/usr/bin/env python
"""S6-B3134a lens C RE-RANK (B3139): the bollinger_lower span cubes re-graded
with every entry the daily_subtract_v1 screen would have refused REMOVED - the
question the S6-B3119f waterfall order turns on, and the council's
'config 1 reported both as run and daily-emulated'.

WHY. The span cubes were built by the pre-B3135 engine (no eligibility stamp
= jan1_legacy), which let through entries the fixed engine refuses: carry-only
tickers (M2) and not-screenable-today days (M1). The lens
(eligibility_leak --cube) LABELS them; this re-GRADES without them, through
the family's OWN grader (grade_bollinger_config.grade - the code the landing
ran, L593), so the as-run and clean figures differ only by the removal.

METHOD, per cube:
  1. REPRODUCE the landed figures from the cube with the same grader - the
     Step-1 ranking rows (exit, fires, is_ci_lo) or, under --step2, the
     Step-2 block (verdict, selected exit, holdout n, full-period n, sharpe) -
     against the committed grid artifact; a cube that does not reproduce
     publishes NOTHING (#290).
  2. CLASSIFY every (ticker, entry_date) with eligibility_leak.Classifier.
  3. REMOVE rows classified carry:* or daily:*; unknown:* rows are KEPT and
     counted (a guard that cannot see says so - neither clean nor leaked).
  4. RE-GRADE the remainder with the same grader, config and min_n.
Step-1 order is by the top ranked exit's is_ci_lo (the ranking key, runbook
6.4b), ties by fires. Read-only over the cubes; writes one JSON.
Exit 0 = every cube reproduced; 3 = at least one did not.

Usage:
  python scripts/eligibility_rerank.py --cubes output_bl_span009_span009 \\
      output_bl_span250_span250 output_bl_span100_span100 \\
      --slice-verdict APPROXIMATE --out <json>
  python scripts/eligibility_rerank.py --step2 --cubes output_bl_step2_p4_9_p4_9 \\
      --slice-verdict APPROXIMATE --out <json>

--slice-verdict is REQUIRED: the output's exactness is the slice's claim-(2)
result, stated by the caller from compare.json, never defaulted.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "EXECUTION_QUEUE.md").is_file():          # L846 marker rule
    raise SystemExit(f"eligibility_rerank: {ROOT} is not the repo root (L846)")
for _p in (ROOT, ROOT / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import pandas as pd                                       # noqa: E402

import eligibility_leak as el                             # noqa: E402
import grade_bollinger_config as gb                       # noqa: E402

STEP1_KEY = ("exit", "fires", "is_ci_lo")
STEP2_KEY = ("verdict", "selected_exit", "holdout_n", "full_period_n", "sharpe")


def span_of(cube_dir: Path) -> int:
    """The span the engine READ, from the landed arm's env - never the name."""
    man = json.loads((cube_dir / "run_manifest.json").read_text(encoding="utf-8"))
    env = ((man.get("arms") or [{}])[0] or {}).get("env") or {}
    if "STRAT_EMA_SPAN" not in env:
        raise SystemExit(f"[FAIL] {cube_dir.name}: no STRAT_EMA_SPAN in the landed arm")
    return int(float(str(env["STRAT_EMA_SPAN"])))


def _figures(doc: dict, step2: bool):
    if step2:
        s2 = doc.get("step2") or {}
        return tuple(s2.get(k) for k in STEP2_KEY)
    return [tuple(r.get(k) for k in STEP1_KEY) for r in doc.get("step1_ranking") or []]


def _grade_frame(frame: pd.DataFrame, cube_dir: Path, span: int, tmp: Path,
                 step2: bool) -> dict:
    """Grade `frame` through the family grader: written as a cube beside a
    copy of the landed manifest, so the grader resolves the SAME graded
    strategy (graded_and_riders reads the manifest) and verifies the span."""
    d = tmp / cube_dir.name
    d.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(cube_dir / "run_manifest.json", d / "run_manifest.json")
    frame.to_csv(d / "trade_exit_detail.csv", index=False)
    refusal, disc = gb.verify_manifest(d, {"ema_span": span})
    if refusal:
        raise SystemExit(refusal)
    return gb.grade(d / "trade_exit_detail.csv", {"P4_ema_span": span},
                    disclosure=disc, step2=step2)


def rerank_cube(cube_dir: Path, grid: Path | None, tmp: Path, step2: bool = False) -> dict:
    span = span_of(cube_dir)
    full = pd.read_csv(cube_dir / "trade_exit_detail.csv", low_memory=False)
    landed = _grade_frame(full, cube_dir, span, tmp / "landed", step2)
    row = {"cube": cube_dir.name, "span": span, "step2": step2, "rows": int(len(full))}
    if grid is not None and grid.is_file():
        want = _figures(json.loads(grid.read_text(encoding="utf-8")), step2)
        got = _figures(landed, step2)
        row["reproduction"] = {"grid": str(grid.relative_to(ROOT)).replace("\\", "/")
                               if grid.is_relative_to(ROOT) else str(grid),
                               "equal": got == want}
        if got != want:
            row["verdict"] = "NOT-REPRODUCED"
            row["mismatch"] = {"want": want if step2 else want[:5],
                               "got": got if step2 else got[:5]}
            return row
    else:
        row["reproduction"] = {"grid": None, "equal": None,
                               "note": "no committed grid artifact - NOT checked"}
    strat = landed["strategy"]
    sub = full[full["strategy"].astype(str) == strat]
    end = max(el._as_date(x) for x in sub["entry_date"])
    clf = el.Classifier(sub["ticker"].astype(str).unique(), end)
    reasons = el.classify_entries(sub, clf)
    cls = reasons.map(el.reason_class)
    leak = cls.isin(["carry", "daily"])
    clean = _grade_frame(full.drop(index=sub.index[leak]), cube_dir, span,
                         tmp / "clean", step2)
    entries = sub.drop_duplicates(["ticker", "entry_date"])
    ent_cls = cls.loc[entries.index]
    row.update({
        "strategy": strat,
        "strategy_rows": int(len(sub)),
        "leaked_rows": int(leak.sum()),
        "unknown_rows_kept": int((cls == "unknown").sum()),
        "entries": int(len(entries)),
        "leaked_entries": int(ent_cls.isin(["carry", "daily"]).sum()),
        "by_reason": {k: int(v) for k, v in reasons[leak].value_counts().items()},
        "kept_rows": int(len(sub) - int(leak.sum())),
        "as_run": _summary(landed, step2),
        "clean": _summary(clean, step2),
        "verdict": "RERANKED",
    })
    return row


def _summary(doc: dict, step2: bool) -> dict:
    out = {"is_rows": doc["is_rows"], "holdout_rows": doc["holdout_rows"],
           "top": (doc["step1_ranking"] or [None])[0],
           "ranking": doc["step1_ranking"][:5]}
    if step2:
        s2 = doc.get("step2") or {}
        out["step2"] = {k: s2.get(k) for k in
                        ("verdict", "selected_exit", "holdout_n", "full_period_n",
                         "sharpe", "sortino", "profit_factor", "psr", "gates_passed",
                         "gates")}
    return out


def _key(top):
    if not top:
        return (float("inf"), 0)
    ci = top.get("is_ci_lo")
    return (-(ci if ci is not None else -9e9), -(top.get("fires") or 0))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cubes", nargs="+", required=True)
    ap.add_argument("--step2", action="store_true",
                    help="grade and reproduce the Step-2 block (the ONE holdout "
                         "read of the IS-selected exit) instead of the Step-1 ranking")
    ap.add_argument("--out", required=True)
    ap.add_argument("--slice-verdict", required=True,
                    choices=("EXACT", "APPROXIMATE"),
                    help="the S6-B3134a slice's claim-(2) result: EXACT only if "
                         "every legacy-only entry was a classified leak and every "
                         "daily-only entry sat on a clean ticker-day")
    a = ap.parse_args(argv)
    tmp = Path(tempfile.mkdtemp(prefix="elig_rerank_"))
    rows = []
    try:
        for c in a.cubes:
            cube_dir = (ROOT / c) if not Path(c).is_absolute() else Path(c)
            grid = ROOT / "output_audit" / f"{cube_dir.name}_grid_auto.json"
            rows.append(rerank_cube(cube_dir, grid, tmp, step2=a.step2))
            r = rows[-1]
            print(f"{r['cube']}: span {r['span']} {r['verdict']}"
                  + (f" - leaked rows {r['leaked_rows']} of {r['strategy_rows']}"
                     if r["verdict"] == "RERANKED" else ""))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    ok = [r for r in rows if r["verdict"] == "RERANKED"]
    doc = {"ticket": "S6-B3134a lens C (B3139)",
           "mode": "step2" if a.step2 else "step1",
           "method": ("grade_bollinger_config.grade on the landed cube (reproduced "
                      "against its committed grid) and on the cube with every "
                      "carry:* / daily:* row removed; unknown:* rows kept and counted"),
           "cubes": rows,
           "not_reproduced": [r["cube"] for r in rows if r["verdict"] != "RERANKED"],
           "exactness": a.slice_verdict,
           "exactness_note": (
               "EXACT: the S6-B3134a slice showed the daily screen removes classified "
               "leaks and nothing else" if a.slice_verdict == "EXACT" else
               "APPROXIMATE: the S6-B3134a slice FAILED its claim (2) - removing a "
               "leaked ticker also moves every surviving ticker's cross-sectional "
               "deciles, and the cube-isolation occupancy block skips a WHOLE "
               "candidate behind one holder, so a clean ticker-day's entry can "
               "differ too (S6-B3139q, S6-B3139r). The clean figures are the "
               "leak rows removed, not a re-run of the daily screen.")}
    if not a.step2:
        doc["ranking_key"] = "top ranked exit's is_ci_lo (runbook 6.4b), ties by fires"
        doc["order_as_run"] = [r["span"] for r in sorted(ok, key=lambda r: _key(r["as_run"]["top"]))]
        doc["order_clean"] = [r["span"] for r in sorted(ok, key=lambda r: _key(r["clean"]["top"]))]
        doc["order_changed"] = doc["order_as_run"] != doc["order_clean"]
        print("order as run:", doc["order_as_run"], "| clean:", doc["order_clean"],
              "| changed:", doc["order_changed"])
    else:
        for r in ok:
            print(f"{r['cube']} step2 as run {r['as_run']['step2']} | clean {r['clean']['step2']}")
    Path(a.out).write_text(json.dumps(doc, indent=1, default=float), encoding="utf-8")
    print("wrote", a.out)
    return 3 if doc["not_reproduced"] else 0


if __name__ == "__main__":
    sys.exit(main())
