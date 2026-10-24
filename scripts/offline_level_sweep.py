#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2638 (S6-B2633): Step-1 for an OFFLINE-FREE strategy - no engine hours.

THE CLASS THIS SERVES. A producer parameter is *offline-free* when the
MAGNITUDE it thresholds was persisted in `signals_at_entry` at fire time. Then
a TIGHTER level is not a new simulation - it is a SUBSET of the landed fire
set, and Step-1 costs seconds instead of the 16-40 engine hours a config
carries. This module is the generic instrument (the owner's run-producers-once
directive); `pead_long_high_yoy_growth_only` is its first caller, and the axis
map is data, not code, so the next strategy is a new --axes argument.

FOUR REFUSALS, all fail-closed (L642: the absent input is the case the guard
exists for):

  1. REPRODUCTION. Re-applying the PRODUCTION levels must return the landed
     fire set exactly. Anything below 1.0 means the persisted magnitude is not
     the quantity the engine thresholded, and every derived level would be
     measuring a different gate than the one that ran. Refuses below --repro-min.
  2. COVERAGE. Rows whose signals_at_entry is empty cannot be levelled. An
     empty dict is NOT a zero (S6-B2512 / B2574): it means the engine's live
     signals were never persisted for that row. Refuses below --coverage-min.
  3. JOIN. Every cube row must find its magnitudes. An unmatched row would be
     silently dropped from the subset and quietly shrink the denominator.
  4. TRUNCATION. Subsetting is exact only if the engine recorded EVERY
     candidate that fired. `backtest.BacktestEngine._process_day` bypasses max_candidates_per_day
     under cube isolation, so an isolation cube is safe; a NON-isolation cube
     truncates at the cap, and the trades a tighter level would have freed were
     never simulated. MEASURED for pead: max 48 fires on one day against a cap
     of 30, which is the positive evidence that no truncation occurred.

IN-SAMPLE ONLY, BY CONSTRUCTION. This module never slices the holdout - it
imports roster_core.in_sample and has no holdout code path at all. Step-1 is a
ranked list with NO gates (owner ruling B1608); the single pre-registered
holdout read is a SEPARATE, owner-fired action against the cell named here.

WHAT THE ARTIFACT IS FOR. The written JSON is the pre-registration record: it
names the trials count, the selected cell and the axis map BEFORE any holdout
code runs. A ranked list produced after a holdout read is not evidence.

Usage:
  python scripts/offline_level_sweep.py --strategy pead_long_high_yoy_growth_only \
      --axes "days_since_last_earnings:le:20,40,60" \
             "earnings_eps_yoy_growth:ge:0.05,0.10,0.20,0.35,0.50" \
      --production 60,0.05 --out output_audit/b2638_pead_step1_is_surface.json
"""
from __future__ import annotations

import argparse
import ast
import itertools
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import roster_core as rc  # noqa: E402

CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"
CANDIDATE_CAP = 30          # backtest.BacktestEngine.__init__ default; bypassed under isolation


# S6-B3290: the four comparison ops. le/ge are the original pair; lt/gt are
# their STRICT forms for gates written with < and > (williams_r_oversold reads
# williams_r < -80 and rsi_2 < 5) - a level on a strict gate keeps one fewer
# boundary fire, and a non-strict read would reproduce a different fire set.
AXIS_OPS = ("le", "ge", "lt", "gt")
TIGHTEN_DOWN = ("le", "lt")      # a LOWER level is tighter
TIGHTEN_UP = ("ge", "gt")        # a HIGHER level is tighter


def parse_axis(spec: str) -> dict:
    """'key:op:v1,v2[@group]' -> {'key','op','levels','group'}. op is le/lt
    (tighten downward) or ge/gt (tighten upward) - the direction the
    THRESHOLD is applied, which is a property of the gate, never inferable
    from the numbers. S6-B3290: an optional '@group' suffix names an OR arm -
    axes sharing a group are OR-ed inside keep() (a fire passes the group when
    ANY member passes), and every group is AND-ed with the plain axes, which
    is the shape of an `(a OR b) AND c` gate. No group = a plain AND leg."""
    group = None
    if "@" in spec:
        spec, group = spec.rsplit("@", 1)
        if not group:
            raise ValueError(f"axis {spec}: empty OR-group name after '@'")
    key, op, levels = spec.split(":", 2)
    if op not in AXIS_OPS:
        raise ValueError(f"axis {key}: op must be one of {AXIS_OPS}, got {op!r}")
    return {"key": key, "op": op, "levels": [float(v) for v in levels.split(",")],
            "group": group}


def _cmp(col: pd.Series, op: str, level: float) -> pd.Series:
    if op == "le":
        return col <= level
    if op == "ge":
        return col >= level
    if op == "lt":
        return col < level
    return col > level


def _parse_sig(s):
    if not isinstance(s, str) or not s.strip():
        return {}
    try:
        return json.loads(s)
    except Exception:
        try:
            return ast.literal_eval(s)
        except Exception:
            return {}


def looser_levels(axes: list[dict], production) -> list[str]:
    """S6-B3195: each axis level on the LOOSER side of its production level.

    keep() applies col <= level for an le axis (col >= level for ge), so a
    level above production on an le axis keeps EVERY production fire and the
    cell grades identically to production while labelled with the looser
    setting - a wrong grade with every other refusal green. A looser level
    admits bars the cube never simulated: it is engine work (runbook 0.7),
    never an offline grade. MEASURED when added: 0 of 9 existing sweep
    artifacts carried one, so no recorded grade was wrong."""
    out = []
    for ax, pv in zip(axes, production):
        bad = [lv for lv in ax["levels"]
               if (lv > pv if ax["op"] in TIGHTEN_DOWN else lv < pv)]
        if bad:
            out.append(f"{ax['key']} {ax['op']}: levels {bad} are looser "
                       f"than production {pv}")
    return out


def keep(frame: pd.DataFrame, axes: list[dict], combo: tuple) -> pd.DataFrame:
    """AND over plain axes; within an OR group (S6-B3290) a fire passes when
    ANY member passes, and the group result is AND-ed with the rest. A null
    magnitude fails its own comparison, so an OR member whose key the fire did
    not persist contributes False and the other members decide."""
    m = pd.Series(True, index=frame.index)
    groups: dict = {}
    for ax, level in zip(axes, combo):
        test = _cmp(frame[ax["key"]], ax["op"], level)
        g = ax.get("group")
        if g is None:
            m &= test
        else:
            groups[g] = (groups[g] | test) if g in groups else test
    for test in groups.values():
        m &= test
    return frame[m]


def _read_filtered(path: Path, usecols: list[str], strategy: str,
                   direction: str | None, chunksize: int = 250_000) -> pd.DataFrame:
    """S6-B3290: the merged R5 files are 4.6 GB (trade log) and 1.6 GB (cube);
    a whole-file read beside a running chain is what the owner's memory
    budget cannot carry. Stream in chunks and keep one strategy's rows (and
    one direction's when --direction is set) - the same rows the whole-file
    read then filtered, pinned by test_b3290."""
    parts = []
    for ch in pd.read_csv(path, low_memory=False, usecols=usecols, chunksize=chunksize):
        sel = ch[ch["strategy"] == strategy]
        if direction is not None:
            sel = sel[sel["direction"] == direction]
        if len(sel):
            parts.append(sel)
    if not parts:
        return pd.DataFrame(columns=usecols)
    return pd.concat(parts, ignore_index=True)


def _survival_inputs(strategy: str) -> tuple:
    """(survives_pct, unmeasured_gate_keys) for the strategy from the status
    view - the T1 filter's inputs, the same fields build_table_a reads. Fails
    closed on an absent row or stamp (L642)."""
    from step1_gates import STATUS_JSON
    view = json.loads(Path(STATUS_JSON).read_text(encoding="utf-8"))
    rows = [r for r in view["rows"] if r.get("strategy") == strategy]
    if len(rows) != 1:
        raise SystemExit(f"REFUSED: {strategy} has {len(rows)} status rows - the "
                         "T1 survival filter needs exactly one (S6-B3290)")
    r = rows[0]
    if "survives_pct" not in r:
        raise SystemExit(f"REFUSED: the status row for {strategy} carries no "
                         "survives_pct - regenerate the view (S6-B3290)")
    return r["survives_pct"], r.get("unmeasured_gate_keys")


def load_derive(path) -> tuple:
    """S6-B3290b: (derive_fn, {path, sha256}) from a module file exposing
    derive(sig: dict) -> dict. Fails closed on an absent file or function."""
    import hashlib
    import importlib.util as ilu
    p = Path(path)
    if not p.is_file():
        raise SystemExit(f"REFUSED: --derive {path} is not a file")
    spec = ilu.spec_from_file_location("ols_derive_" + p.stem, p)
    mod = ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = getattr(mod, "derive", None)
    if not callable(fn):
        raise SystemExit(f"REFUSED: --derive {path} exposes no derive(sig) function")
    return fn, {"path": str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}


def load(strategy: str, axes: list[dict], direction: str | None = None,
         survival: bool = False, derive=None) -> tuple[pd.DataFrame, dict]:
    """Merged cube + magnitudes, plus the refusal evidence. Raises on refusal.

    S6-B3290: `direction` keeps one leg of a dual strategy (the per-side
    bands of S6-B3270 grade one side's fires); `survival` applies the T1
    filter (build_table_a.surviving_fires on the status view's survives_pct)
    BEFORE anything is graded, so reproduction is measured against the
    SURVIVING subset as runbook T4 requires. Both read the files in chunks."""
    keys = [ax["key"] for ax in axes]
    if len(set(keys)) != len(keys):
        raise SystemExit(f"REFUSED: an axis key repeats ({keys}) - one column per "
                         "key, so two axes on one key cannot be joined (S6-B3290)")
    t = _read_filtered(TRADE_LOG, ["ticker", "strategy", "entry_date", "direction",
                                   "signals_at_entry"], strategy, direction)
    if t.empty:
        raise SystemExit(f"REFUSED: {strategy} has no rows in {TRADE_LOG.name}"
                         + (f" with direction {direction}" if direction else ""))
    landed = int(len(t))
    survival_dropped = 0
    if survival:
        import build_table_a as _bta
        pct, unmeasured = _survival_inputs(strategy)
        t = t.drop_duplicates(["strategy", "ticker", "entry_date"])
        kept, _sigs, _filtered = _bta.surviving_fires(strategy, t, pct, unmeasured)
        survival_dropped = int(len(t) - len(kept))
        t = kept.copy()
        if t.empty:
            raise SystemExit(f"REFUSED: no surviving fires for {strategy} after the "
                             "T1 filter (S6-B3290)")
    sig = t["signals_at_entry"].map(_parse_sig)
    if derive is not None:
        # S6-B3290b: derived keys ride the persisted dict; an empty dict stays
        # empty so the coverage refusal still sees the gap
        sig = sig.map(lambda d: derive(d) if isinstance(d, dict) and d else d)
    covered = sig.map(lambda d: isinstance(d, dict) and len(d) > 0)
    coverage = float(covered.mean())
    for ax in axes:
        t[ax["key"]] = sig.map(lambda d, k=ax["key"]: d.get(k))

    g = _read_filtered(CUBE, rc.CUBE_COLUMNS, strategy, direction)
    if survival:
        # the cube rows of a dropped fire would read as a join gap; restrict
        # the cube to the surviving fires and keep the join refusal for the
        # fires that survived and still found no row
        g = g.merge(t[["ticker", "entry_date"]].drop_duplicates(),
                    on=["ticker", "entry_date"], how="inner")
    cols = ["ticker", "entry_date"] + keys
    m = g.merge(t[cols].drop_duplicates(["ticker", "entry_date"]),
                on=["ticker", "entry_date"], how="left")
    # a fire whose dict never persisted the FIRST key is a join gap only when
    # the WHOLE row is missing; test the indicator column, not a magnitude
    probe = g[["ticker", "entry_date"]].drop_duplicates().merge(
        t[["ticker", "entry_date"]].drop_duplicates().assign(_hit=1),
        on=["ticker", "entry_date"], how="left")
    unmatched = int(probe["_hit"].isna().sum())

    per_day = t.groupby("entry_date").size()
    ev = {"landed_fires": landed, "coverage": coverage,
          "cube_rows": int(len(g)), "unmatched_join_rows": unmatched,
          "max_fires_per_day": int(per_day.max()),
          "candidate_cap": CANDIDATE_CAP,
          "cap_bypassed_evidence": bool(per_day.max() > CANDIDATE_CAP),
          "direction": direction,
          "survival_filter": {"applied": bool(survival), "fires_after": int(len(t)),
                              "fires_dropped": survival_dropped}}
    m["entry_date"] = pd.to_datetime(m["entry_date"], errors="coerce").dt.date
    return m, ev


def permutation_null(IS, axes, min_n, n_perms, seed):
    """B2676 (S6-B2638a): the grid-stage multiplicity instrument.

    Under NO signal->outcome link, what does the BEST IS sharpe over this
    exact grid look like? Each permutation shuffles the MAGNITUDE block
    jointly across unique fires (preserving the magnitudes' joint
    distribution and the per-exit pnl structure) and re-grades the identical
    cells x exits grid. The returned maxima are SYNTHETIC (rng) by
    construction - they price the search, they are never performance.
    B2376 measured that NO multiplicity correction existed at the grid
    stage; this is that correction, inherited by every campaign that runs
    this module with --null-perms.
    """
    import numpy as np
    rng = np.random.default_rng(seed)
    keys = [ax["key"] for ax in axes]
    fires = (IS.drop_duplicates(["ticker", "entry_date"])
               [["ticker", "entry_date"] + keys].reset_index(drop=True))
    base = IS.drop(columns=keys)
    maxima = []
    for _ in range(n_perms):
        idx = rng.permutation(len(fires))
        shuf = fires[["ticker", "entry_date"]].join(
            fires.loc[idx, keys].reset_index(drop=True))
        mm = base.merge(shuf, on=["ticker", "entry_date"], how="left")
        best = None
        for combo in itertools.product(*[ax["levels"] for ax in axes]):
            k = keep(mm, axes, combo)
            for _ex, sub in k.groupby("exit_method"):
                r = rc.evaluate(sub["pnl_pct"], sub["hold_days"], min_n=min_n)
                if r and r.get("sharpe") is not None and (best is None or r["sharpe"] > best):
                    best = r["sharpe"]
        maxima.append(best)
    return maxima


def cell_family_rows(cells) -> list:
    """S6-B3096f (B3101): the multiplicity family of a level sweep is EVERY
    cell searched - the record keeps only the graded ones. A graded cell is
    scored; a cell with trades and no exit at min_n could not be priced
    (BELOW_POWER_FLOOR); a zero-trade cell produced no candidate (ZERO_FIRES)."""
    return [({"levels": c["levels"], "is_sharpe": c["is_sharpe"]}
             if c.get("is_sharpe") is not None else
             {"levels": c["levels"],
              "verdict": "BELOW_POWER_FLOOR" if c.get("is_trades") else "ZERO_FIRES"})
            for c in cells]


def sweep(strategy: str, axes: list[dict], production: tuple,
          coverage_min: float, repro_min: float, min_n: int,
          direction: str | None = None, survival: bool = False,
          derive=None) -> dict:
    m, ev = load(strategy, axes, direction=direction, survival=survival,
                 derive=derive)
    if ev["coverage"] < coverage_min:
        raise SystemExit(f"REFUSED: signal coverage {ev['coverage']:.4f} < "
                         f"{coverage_min} - un-levellable rows would be dropped silently")
    if ev["unmatched_join_rows"]:
        raise SystemExit(f"REFUSED: {ev['unmatched_join_rows']} cube rows found no "
                         "magnitudes - the subset denominator would be wrong")

    fires = m.drop_duplicates(["ticker", "entry_date"])
    repro = len(keep(fires, axes, production)) / max(len(fires), 1)
    if repro < repro_min:
        raise SystemExit(f"REFUSED: production levels reproduce {repro:.4f} of the "
                         f"landed fire set (< {repro_min}) - the persisted magnitude "
                         "is not the quantity the engine thresholded")
    # S6-B3195: AFTER the reproduction refusal - a level is looser only
    # relative to production, so production must reproduce first (a wrong
    # production is a reproduction failure, not a looser level) - and
    # BEFORE any cell is graded.
    _loose = looser_levels(axes, production)
    if _loose:
        raise SystemExit("REFUSED (S6-B3195): " + "; ".join(_loose) + " - a "
                         "looser level keeps every production fire, so its "
                         "offline grade would be production's grade under "
                         "another label")
    if not ev["cap_bypassed_evidence"]:
        ev["truncation_note"] = (
            f"max fires/day {ev['max_fires_per_day']} <= cap {CANDIDATE_CAP}: no "
            "positive evidence the cap was bypassed. Subsetting is exact only if "
            "the cube ran under isolation (backtest.py:2417).")

    IS = rc.in_sample(m)          # the only window this module ever reads
    cells = []
    for combo in itertools.product(*[ax["levels"] for ax in axes]):
        k = keep(IS, axes, combo)
        best_sh, best_ex = None, None
        for ex, sub in k.groupby("exit_method"):
            r = rc.evaluate(sub["pnl_pct"], sub["hold_days"], min_n=min_n)
            if r and r.get("sharpe") is not None and (best_sh is None or r["sharpe"] > best_sh):
                best_sh, best_ex = r["sharpe"], ex
        # owner directive: report TRADES, never cube rows - a cell's row count
        # is trades x exits and overstates the evidence ~26x.
        cells.append({"levels": list(combo),
                      "is_trades": int(len(k.drop_duplicates(["ticker", "entry_date"]))),
                      "is_cube_rows": int(len(k)),
                      "best_exit": best_ex, "is_sharpe": best_sh,
                      "exits_evaluated": int(k["exit_method"].nunique())})
    graded = [c for c in cells if c["is_sharpe"] is not None]
    _family_rows = cell_family_rows(cells)   # S6-B3096f (B3101)
    graded.sort(key=lambda c: c["is_sharpe"], reverse=True)
    trials = sum(c["exits_evaluated"] for c in cells)
    return {"strategy": strategy,
            "axes": [{"key": a["key"], "op": a["op"], "levels": a["levels"],
                      "group": a.get("group")} for a in axes],
            "direction": direction,
            "production_levels": list(production),
            "evidence": ev, "reproduction": repro,
            "cells_total": len(cells), "cells_graded": len(graded),
            "trials_searched": trials,
            "window": {"is": [str(rc.IS_START), str(rc.IS_END)]},
            "ranked": graded,
            "_family_rows": _family_rows,
            "preregistration_candidate": graded[0] if graded else None,
            "holdout_read": "NOT FIRED - owner-gated, one shot, against the "
                            "preregistration_candidate named above"}


def attach_null(rec, strategy, axes, min_n, null_perms, null_seed,
                direction=None, survival=False, derive=None):
    """Compute the permutation null for a completed sweep record, in place.
    Reloads the frame (sweep does not retain it) - the same refusals apply
    upstream, so a record that graded is a record the null can price."""
    import numpy as np
    m, _ = load(strategy, axes, direction=direction, survival=survival,
                derive=derive)
    IS = rc.in_sample(m)
    maxima = permutation_null(IS, axes, min_n, null_perms, null_seed)
    valid = [x for x in maxima if x is not None]
    obs = (rec.get("preregistration_candidate") or {}).get("is_sharpe")
    p = ((1 + sum(1 for x in valid if x >= obs)) / (len(valid) + 1)
         if (obs is not None and valid) else None)
    qs = ({str(q): round(float(np.quantile(valid, q)), 3)
           for q in (0.5, 0.9, 0.95, 0.99)} if valid else {})
    rec["permutation_null"] = {
        "provenance": "SYNTHETIC - rng permutations of the magnitude block "
                      "across fires; prices the search, never performance",
        "n_perms": null_perms, "seed": null_seed,
        "null_none_count": null_perms - len(valid),
        "null_max_is_sharpe_quantiles": qs,
        "observed_best_is_sharpe": obs,
        "p_value_best": round(p, 4) if p is not None else None}



def preregistration_refusal(rec: dict) -> str:
    """S6-B3293: the reason this artifact names NO preregistration candidate,
    or '' when its best cell is one. A candidate is a cell worth spending the
    one-shot holdout read on: its IS sharpe must be positive, and when a
    permutation null ran, the search's own null must not price it above the
    S6-B3206 noise bar (producer_variant_table.DEPTH_NULL_P_MAX). MEASURED
    before this rule: the williams_r_oversold short sweep named a best cell
    with IS sharpe -0.198 at p 1.0 as its candidate."""
    best = rec.get("preregistration_candidate")
    if not best:
        return "no graded cell"
    sh = best.get("is_sharpe")
    if sh is None or float(sh) <= 0:
        return (f"best cell IS sharpe {sh} is not positive - no level in the band "
                "beats zero in-sample, nothing to read on the holdout")
    p = (rec.get("permutation_null") or {}).get("p_value_best")
    if p is not None:
        from producer_variant_table import DEPTH_NULL_P_MAX
        if float(p) > DEPTH_NULL_P_MAX:
            return (f"the search's own permutation null prices the best cell at p {p} "
                    f"> {DEPTH_NULL_P_MAX} (the S6-B3206 noise bar) - the surface is "
                    "noise, nothing to read on the holdout")
    return ""


def apply_preregistration_refusal(rec: dict) -> str:
    """S6-B3293: record the refusal on the artifact and VOID the candidate
    when there is one; returns the refusal ('' keeps the candidate). main()
    routes through this before the multiplicity report - pinned by
    test_b3293's wiring arm, because main() itself runs the whole sweep."""
    rec["preregistration_refusal"] = preregistration_refusal(rec)
    if rec["preregistration_refusal"]:
        rec["preregistration_candidate"] = None
    return rec["preregistration_refusal"]


def render_table(rec: dict) -> str:
    """B2643 (owner directive 2026-09-08): TABLE D, OFFLINE FORM.

    The ranked producer-combination view must NOT wait for an engine run - for
    an offline campaign the Step-1 artifact IS the run, so its ranking renders
    to markdown beside the JSON, automatically, every sweep (L651: delivery
    cannot depend on the reporter remembering; the runner invokes the renderer).
    """
    axes = rec["axes"]
    head = (f"# TABLE D (OFFLINE FORM) - {rec['strategy']}\n\n"
            f"Ranked producer combinations from the IN-SAMPLE sweep: "
            f"{rec['cells_graded']} of {rec['cells_total']} cells, "
            f"{rec['trials_searched']} trials (cells x exits); window "
            f"{rec['window']['is'][0]} .. {rec['window']['is'][1]}; "
            f"holdout NOT read by this artifact.\n\n")
    if rec.get("preregistration_refusal"):
        head += (f"**NO PREREGISTRATION CANDIDATE (S6-B3293): "
                 f"{rec['preregistration_refusal']}**\n\n")
    cols = " | ".join(f"{a['key']} ({a['op']}"
                      + (f", or:{a['group']}" if a.get("group") else "") + ")"
                      for a in axes)
    lines = [f"| rank | {cols} | IS trades | best exit | IS sharpe |",
             "|" + "---|" * (len(axes) + 4)]
    prod = list(rec.get("production_levels", ()))
    for i, c in enumerate(rec["ranked"], 1):
        vals = " | ".join(str(v) for v in c["levels"])
        mark = " (production)" if list(c["levels"]) == prod else ""
        lines.append(f"| {i} | {vals}{mark} | {c['is_trades']} | "
                     f"{c['best_exit']} | {c['is_sharpe']:.3f} |")
    return head + "\n".join(lines) + "\n"


from step1_gates import require_band_ruling, require_fresh_status  # noqa: E402  (B2848)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--axes", nargs="+", required=True,
                    help="key:op:v1,v2,...[@group] with op in {le,ge,lt,gt}; "
                         "axes sharing @group are OR-ed (S6-B3290)")
    ap.add_argument("--direction", choices=["long", "short"], default=None,
                    help="S6-B3290: grade ONE leg of a dual strategy")
    ap.add_argument("--derive", default=None,
                    help="S6-B3290b: a module file exposing derive(sig) -> dict "
                         "that adds DERIVED keys to each fire's persisted dict "
                         "before the axes read them")
    ap.add_argument("--survival", action="store_true",
                    help="S6-B3290: apply the T1 survival filter (status view "
                         "survives_pct) before grading; reproduction is then "
                         "measured on the surviving subset (runbook T4)")
    ap.add_argument("--production", required=True,
                    help="comma-separated production level per axis, in order")
    ap.add_argument("--out", required=True)
    ap.add_argument("--band-ruling", required=True,
                    help="the owner's T3 band words, verbatim (S6-B2848a; "
                         "refused empty; recorded into the artifact)")
    ap.add_argument("--coverage-min", type=float, default=0.99)
    ap.add_argument("--repro-min", type=float, default=0.999)
    ap.add_argument("--min-n", type=int, default=30)
    ap.add_argument("--null-perms", type=int, default=0,
                    help="B2676: permutation-null size for the best-of-grid "
                         "multiplicity price; 0 = off")
    ap.add_argument("--null-seed", type=int, default=13)
    a = ap.parse_args()
    _ruling = require_band_ruling(a.band_ruling, a.strategy)   # S6-B2848a + B2855
    _stamp = require_fresh_status()                # S6-B2848b

    axes = [parse_axis(s) for s in a.axes]
    production = tuple(float(v) for v in a.production.split(","))
    if len(production) != len(axes):
        raise SystemExit(f"REFUSED: --production has {len(production)} values for "
                         f"{len(axes)} axes")
    derive_fn, derive_rec = (load_derive(a.derive) if a.derive else (None, None))
    rec = sweep(a.strategy, axes, production, a.coverage_min, a.repro_min, a.min_n,
                direction=a.direction, survival=a.survival, derive=derive_fn)
    rec["derive"] = derive_rec
    if a.null_perms > 0:
        attach_null(rec, a.strategy, axes, a.min_n, a.null_perms, a.null_seed,
                    direction=a.direction, survival=a.survival, derive=derive_fn)
        pn = rec["permutation_null"]
        print(f"permutation null ({pn['n_perms']} perms): observed best "
              f"{pn['observed_best_is_sharpe']} | null q95 "
              f"{pn['null_max_is_sharpe_quantiles'].get('0.95')} | p {pn['p_value_best']}")
    # S6-B3096f (B3101): the multiplicity block is written EVERY sweep - with
    # the permutation null when one ran, 'none_available' when not (was: only
    # under --null-perms > 0, default 0, so a default T4 grid carried none and
    # breadth_step2_read refused it, fail-closed). trials_searched rides beside
    # it: the partition counts CELLS, the search spanned cells x exits.
    # S6-B3293: a best cell is a CANDIDATE only when it is worth the one-shot
    # read; the refusal is recorded and the candidate voided, so the holdout
    # read tool refuses instead of spending the door on nothing.
    if apply_preregistration_refusal(rec):
        print(f"NO PREREGISTRATION CANDIDATE: {rec['preregistration_refusal']}")
    rec["multiplicity"] = rc.bh_fdr_report(
        rec.pop("_family_rows"), permutation_null=rec.get("permutation_null"))
    rec["multiplicity"]["trials_searched"] = rec.get("trials_searched")
    rec["band_ruling_verbatim"] = _ruling
    rec["status_stamp_at_run"] = _stamp
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    # B2643: the offline Table D ships WITH the artifact, unconditionally.
    table_path = Path(a.out).with_suffix(".md")
    table_path.write_text(render_table(rec), encoding="utf-8")

    print(f"{rec['strategy']}: reproduction {rec['reproduction']:.4f} | coverage "
          f"{rec['evidence']['coverage']:.4f} | {rec['cells_graded']} of "
          f"{rec['cells_total']} cells graded | {rec['trials_searched']} trials")
    for c in rec["ranked"][:5]:
        print(f"   {c['levels']}  IS sharpe {c['is_sharpe']:.3f}  "
              f"exit {c['best_exit']}  n={c['is_trades']}")
    print(f"wrote {a.out}  (holdout NOT read)")
    print(f"wrote {table_path}  (TABLE D, offline form)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
