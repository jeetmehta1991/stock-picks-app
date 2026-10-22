#!/usr/bin/env python
"""S6-B3232 (owner ruling 2026-10-20, recommendation (a) approved): a ranked
shortlist of NOT-STARTED and STALLED long strategies, built from evidence
already on disk, for the owner to pick the next long campaigns toward the
Phase 1B target of at least 30 long strategies (S6-B3220). No engine run.

WHAT IT READS - and what it never reads:
  * output_audit/strategy_optimisation_status.json - each strategy's status,
    family, persisted-threshold coverage and projected current-gate Step-1
    fires; the population is the rows still NOT-STARTED or STALLED-CAMPAIGN
    (L802: the completion record is read before anything is named as work).
  * output_audit/b1453_phase_1b_roster.json all_rows - only the IN-SAMPLE
    fields of each strategy's R5 long row: the exit the in-sample selector
    chose (roster_core.select_exit slices the in-sample window itself), its
    in-sample Sharpe and the count of in-sample-evaluable admission gates it
    clears. The holdout-derived fields of those rows are never read; a
    holdout is read only on the owner's word, per campaign (runbook 0.6).
  * the R5 cube's backtest_results.csv direction_mix ('<n>L/<m>S'): the LONG
    share of a strategy's R5 trades. A two-sided strategy's projected fires
    count both sides, so the long side's projection is the status view's
    projection times this share, and the long side's lane is re-derived with
    the status builder's own rule (classify_stream) - MEASURED at build time:
    hull_rsi trades 463 long / 807 short, so its long side projects under the
    Step-1 floor although the strategy as a whole clears it.
  * the status view's survives_pct_by_side['long']: the share of the R5
    LONG fires the live strategy still fires long on. The long projection
    is the raw projection x the long share x the LONG side's survival.
    B3139q-r80 CORRECTION: the r79 build scaled by the strategy-level
    survival, assuming both sides survive their current gates alike -
    MEASURED false for 12 of the 56 two-sided rows (morning_star long
    0.9753 against 0.4618 overall; avwap_50_reclaim long 0.0 against
    0.8608), so their long projections and lanes were misstated.
  * the registry: a strategy is long-capable when it is a pure long or a
    two-sided strategy (its empty-signal call returns direction long or None);
    EXPLORATORY_STRATEGIES; and each docstring, for an owner re-scope that
    bars deployment (L905).

THE ORDER, stated (#165): (1) COST CLASS of the long side's lane, cheapest
first - TIGHTEN (offline, zero engine hours), NONE (a breadth candidate, the
offline companion grid), BOTH (offline first, engine after), LOOSEN (engine
resim) - the runbook's own lane costs (0.7 stream table, 3.6). The lane
already carries the Step-1 floor: the status builder's classify_stream puts
a projection under the floor in BOTH or LOOSEN and one at or over it in
TIGHTEN or NONE, so no separate floor key exists (a first draft had one, and
reversing it changed nothing - B3139q-r79 mutation S3); (2) in-sample gates
cleared, most first; (3) in-sample Sharpe, highest first. Steps (2) and (3)
are a SELECTION order on in-sample evidence,
not a prediction: whether in-sample strength predicts holdout survival is not
measured here (ARBITRARY-PENDING-JUSTIFICATION for any predictive reading;
L904/L906: an in-sample figure is never sized against the holdout gate).
Nothing is dropped: a row with no R5 long row is listed unranked.

    python scripts/build_long_campaign_shortlist.py            # print
    python scripts/build_long_campaign_shortlist.py --write    # write the artifact
"""
from __future__ import annotations

import argparse
import csv
import inspect
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# L846: a script resolving repo facts from its own location refuses a tree the
# marker does not confirm, rather than reading a path that is not the repo
if not (ROOT / "backtest" / "signals" / "screener.py").is_file():
    raise SystemExit(f"{ROOT} is not the repository root - refusing")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

STATUS = Path("output_audit") / "strategy_optimisation_status.json"
ROSTER = Path("output_audit") / "b1453_phase_1b_roster.json"
OUT = Path("output_audit") / "b3232_long_campaign_shortlist.json"
OPEN_STATUSES = ("NOT-STARTED", "STALLED-CAMPAIGN")
IN_SAMPLE_FIELDS = ("cube", "n_tickers", "strategy", "direction", "exit",
                    "is_sharpe", "is_n_gates")
COST_ORDER = ("TIGHTEN", "NONE", "BOTH", "LOOSEN")
COST_MEANING = {
    "TIGHTEN": "offline - zero engine hours",
    "NONE": "breadth - offline companion grid",
    "BOTH": "offline first, engine after",
    "LOOSEN": "engine resim",
}
DEPLOY_BARS = ("do not deploy", "no deployment", "no production deployment")
CANONICAL_CUBE = "R5"


def in_sample_rows(roster: dict) -> dict:
    """{strategy: in-sample fields of its canonical-cube LONG row}. Only the
    IN_SAMPLE_FIELDS are copied out of each row - nothing else is touched."""
    out = {}
    for r in roster["all_rows"]:
        if r.get("cube") != CANONICAL_CUBE or str(r.get("direction")) != "long":
            continue
        out[r["strategy"]] = {k: r.get(k) for k in IN_SAMPLE_FIELDS}
    return out


def long_share(results_csv: Path) -> dict:
    """{strategy: long trades / all trades} from direction_mix '<n>L/<m>S'."""
    out = {}
    with results_csv.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            mix = (r.get("direction_mix") or "").strip()
            try:
                lo, sh = mix.split("/")
                n_l, n_s = int(lo.rstrip("L")), int(sh.rstrip("S"))
            except ValueError:
                continue
            if n_l + n_s > 0:
                out[r["strategy"]] = n_l / (n_l + n_s)
    return out


def long_capable() -> dict:
    """{strategy: 'long' | 'dual'} from each registered strategy's own
    empty-signal call (a two-sided strategy returns direction None)."""
    from backtest.signals.screener import ALL_STRATEGIES
    out = {}
    for name, fn in ALL_STRATEGIES.items():
        d = fn({}).get("direction")
        if d == "long":
            out[name] = "long"
        elif d is None:
            out[name] = "dual"
    return out


def deploy_bar(name: str):
    """The owner re-scope phrase in the strategy's docstring that bars
    deployment, or None (L905: the subject's source is opened)."""
    from backtest.signals.screener import ALL_STRATEGIES
    doc = (inspect.getdoc(ALL_STRATEGIES[name]) or "").lower()
    return next((p for p in DEPLOY_BARS if p in doc), None)


def side_tightenable(tightenable_keys, side_keys) -> bool:
    """S6-B3271 (r92 audit): a SIDE's lane counts only covered numeric
    keys that side's own gate reads - a key only the other leg thresholds
    cannot tighten this side (williams_stoch_dual's williams_r is
    short-only, yet its long lane read BOTH). The side model is the
    lint's (gate_keys_by_direction, S6-B3239). Pinned by test_b3271."""
    import build_strategy_status as _bss
    return any(v >= _bss.COVERAGE_FLOOR
               for k, v in (tightenable_keys or {}).items()
               if k in side_keys)


def build(root: Path = ROOT) -> dict:
    view = json.loads((root / STATUS).read_text(encoding="utf-8"))
    roster = json.loads((root / ROSTER).read_text(encoding="utf-8"))
    from backtest.engine.multiple_testing_correction import EXPLORATORY_STRATEGIES
    import build_strategy_status as bss
    floor = bss.MIN_FIRES_FOR_GRID
    caps = long_capable()
    isr = in_sample_rows(roster)
    share = long_share(root / bss.R5_DIR.name / "backtest_results.csv")
    pop = [r for r in view["rows"] if r["status"] in OPEN_STATUSES
           and r["strategy"] in caps]
    _long_keys = {s_: d_.get("long", set())
                  for s_, d_ in bss.gate_keys_by_direction().items()}  # S6-B3271
    ranked, unranked = [], []
    for r in pop:
        name = r["strategy"]
        sh = share.get(name)
        proj = r["projected_current_gate"]
        long_surv = (r.get("survives_pct_by_side") or {}).get("long")
        # S6-B3239: a long side the view marks UNMEASURED (its gate reads a
        # key absent from every R5 long fire) keeps its RAW share, labelled
        um_long = (r.get("unmeasured_gate_keys") or {}).get("long")
        if sh and long_surv is None and not um_long:
            # a strategy with R5 long fires must carry a long survival - an
            # absent one is a stale or partial status view, never a 1.0 (L642)
            raise ValueError(f"{name}: R5 long share {sh} but no long-side "
                             "survival in the status view - rebuild it")
        if sh is None:
            long_proj = None
        elif sh == 1.0:
            long_proj = proj  # every R5 fire is long: the strategy's survival IS the long side's
        else:
            long_proj = round(r["projected_step1_fires"] * sh
                              * (1.0 if um_long else (long_surv or 0.0)), 1)
        tightenable = (side_tightenable(r.get("tightenable_keys"),
                                        _long_keys.get(name, set()))
                       or bss.extras_tightenable(name, "long"))  # S6-B3271/72
        lane = r["stream"] if long_proj is None else bss.classify_stream(tightenable, long_proj)
        row = {"strategy": name, "kind": caps[name], "family": r["family"],
               "status": r["status"], "strategy_lane": r["stream"],
               "long_lane": lane, "cost": COST_MEANING.get(lane, "?"),
               "long_share_r5": None if sh is None else round(sh, 4),
               "long_survival_r5": long_surv,
               "long_survival_unmeasured_keys": um_long or None,
               "projected_step1_fires_strategy": proj,
               "projected_step1_fires_long": long_proj,
               "step1_floor_met": (long_proj if long_proj is not None else proj) >= floor,
               "exploratory": name in EXPLORATORY_STRATEGIES,
               "deploy_bar": deploy_bar(name)}
        x = isr.get(name)
        if x is None:
            row["note"] = "no R5 long row in the in-sample roster - listed unranked"
            unranked.append(row)
            continue
        row.update({"is_exit": x["exit"], "is_sharpe": x["is_sharpe"],
                    "is_gates_cleared": x["is_n_gates"]})
        ranked.append(row)
    ranked.sort(key=lambda r: (COST_ORDER.index(r["long_lane"]) if r["long_lane"] in COST_ORDER else 9,
                               -(r["is_gates_cleared"] or 0),
                               -(r["is_sharpe"] if r["is_sharpe"] is not None else -1e9),
                               r["strategy"]))
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
    unranked.sort(key=lambda r: r["strategy"])
    try:
        commit = subprocess.run(["git", "rev-parse", "--short=9", "HEAD"], cwd=root,
                                capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        commit = "unknown"
    return {
        "generator": "scripts/build_long_campaign_shortlist.py (S6-B3232)",
        "build": {"source_commit": commit,
                  "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                  "status_view_build": (view.get("build") or {}).get("source_commit")},
        "population": {"open_long_capable": len(pop), "ranked": len(ranked),
                       "unranked": len(unranked), "step1_floor": floor},
        "order": ("long-side lane cost (TIGHTEN, NONE, BOTH, LOOSEN - the lane "
                  "carries the Step-1 floor), then in-sample gates cleared, then "
                  "in-sample Sharpe - a selection order on in-sample evidence, "
                  "not a holdout prediction"),
        "ranked": ranked, "unranked": unranked}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--write", action="store_true", help=f"write {OUT}")
    ap.add_argument("--top", type=int, default=20)
    a = ap.parse_args(argv)
    d = build()
    p = d["population"]
    print(f"open long-capable {p['open_long_capable']} | ranked {p['ranked']} | "
          f"unranked {p['unranked']} | Step-1 floor {p['step1_floor']} fires")
    for r in d["ranked"][:a.top]:
        flags = ",".join(f for f in ("EXPLORATORY" if r["exploratory"] else "",
                                     f"BAR:{r['deploy_bar']}" if r["deploy_bar"] else "") if f)
        print(f"{r['rank']:>3} {r['strategy']:42s} {r['kind']:4s} {r['long_lane']:7s} "
              f"floor={'Y' if r['step1_floor_met'] else 'n'} gates={r['is_gates_cleared']} "
              f"is_sharpe={r['is_sharpe']} long_proj={r['projected_step1_fires_long']} {flags}")
    if a.write:
        (ROOT / OUT).write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
        print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
