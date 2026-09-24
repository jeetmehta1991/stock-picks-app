#!/usr/bin/env python
"""B2699 (owner-caught 2026-09-12, L784): THE Table D renderer - the single
program that emits a campaign's offline Step-1 Table D.

Owner, verbatim: "table D should be a unified table that contains the
thresholds for each producer tested. no separate table ds are logical. alot
of producers depth and breadth are still missing."

FORM (the standard, derived from the INVENTORY rather than from any one
sweep's slice):
  - ONE unified table per campaign. A late-landing axis (e.g. a re-swept
    coverage-skipped axis) RE-RENDERS this table; addendum tables are barred.
  - One column per Table A inventory row (every P<n> and B<n> in
    SPECS_PHASE0[strategy]["params"]): tested axes carry their thresholds
    per row; untested axes appear at PRODUCTION value, and the preamble
    marks them resim-only / UNTESTED-OFFLINE - missing from the view is the
    defect this renderer exists to prevent (#182 applied to the view).
  - Bands, null prices, coverage disclosures and SKIP dispositions come
    from the ARTIFACTS' own fields, never retyped (L695/#201).

Pinned by test_b2699_table_d_is_one_unified_table_with_every_inventory_column.
Pattern lineage: scripts/show_table_c.py (L652 "print it, quote the output").
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from producer_variant_table import (  # noqa: E402
    SPECS, SPECS_PHASE0)


def _spec(strategy: str) -> dict:
    """S6-B2874 (scoped): resolve from EITHER registry.

    This module read SPECS_PHASE0[strategy] as a bare subscript. MEASURED
    at B2874: that raises KeyError for 6 of 8 registered families -
    including the most-run family in the repo and the candle pair
    registered this session - because a promoted entry MOVES from
    SPECS_PHASE0 into SPECS and nothing here followed it.

    The council cut the full registry MERGE from this fix: reconciling
    three precedence orders across four consumers is a refactor no
    measured caller demands, and every order flattened is an undocumented
    behavioural decision. The crash is the bug; the merge stays ticketed.

    PHASE0 FIRST, DELIBERATELY - this PRESERVES existing behaviour rather
    than improving it. MEASURED: flipping to SPECS-first changed what the 2
    both-registry names render (smc_liquidity_sweep_reversal lost its
    confirmation_arm column) and test_b2699 caught it. Every precedence
    order flattened here would be an undocumented behavioural decision, so
    this fix adds a FALLBACK and changes no existing resolution: names that
    resolved before resolve identically, and the 6 that CRASHED now work.
    Reconciling the orders across all four consumers is the merge, and the
    merge stays ticketed (S6-B2874).
    """
    spec = SPECS_PHASE0.get(strategy) or SPECS.get(strategy)
    if spec is None:
        raise SystemExit(
            f"no Table A spec for {strategy!r} in EITHER registry - "
            f"SPECS has {len(SPECS)} entries, SPECS_PHASE0 has "
            f"{len(SPECS_PHASE0)} (S6-B2874)")
    return spec


# B3082: the campaign's parameter points can arrive in either of two
# shapes, and the renderer owes the same unified table for both.
#   SWEEP      - one cube, one-at-a-time axis sweeps graded offline; the
#                artifact carries "rows" as a LIST of graded rows.
#   FACTORIAL  - one ENGINE RUN per corner (the candle campaign: 18 configs
#                over P3 x P4 x P5); each artifact carries "rows" as an INT
#                row-count, its corner in "config", and its graded cells in
#                "per_exit".
# Detected on the TYPE of "rows" rather than on a filename, because a
# filename is a claim by its author (L445).
_CONFIG_TO_PARAM = {
    "P2_n_bars": "n_bars (pattern length)",
    "P3_min_body_pct": "min_body_pct_of_range",
    "P4_min_step_pct": "min_step_up_pct",
    "P5_max_wick_pct": "max_upper_wick_pct",
}


def _factorial_rows(a: dict) -> list:
    """One row per graded exit of a factorial corner.

    The corner's levels come from the artifact's own config block, so the
    table reports what the run actually used rather than what a filename
    suggests. A cell with no is_sharpe is a non-observation and is routed to
    the SKIP list by the caller exactly as a sweep row would be.
    """
    cfg = a.get("config") or {}
    levels = {_CONFIG_TO_PARAM[k]: v for k, v in cfg.items()
              if k in _CONFIG_TO_PARAM}
    out = []
    for pe in a.get("per_exit") or []:
        out.append({
            "exit": pe.get("exit"),
            "is_sharpe": pe.get("is_sharpe"),
            "is_ci_lo": pe.get("is_ci_lo"),
            "fires": pe.get("fires"),
            "rank": pe.get("rank"),
            "admit": pe.get("admit"),
            "levels": levels,
            "cube": a.get("cube"),
            # B3088 RETRACTION of B3082b. That comment said per_exit carries
            # no per-cell trade counts and rendered '-'. IT DOES CARRY THEM,
            # under a misleading name. grade_candle_config.py:268 builds
            # full_n as cube.groupby("exit_method").size() and line 279 sets
            # "fires" to len(g) over is_rows grouped the same way - BOTH are
            # counts of CUBE ROWS, i.e. trades. VERIFIED across 18 of 18
            # configs: rows / results_n_exits == fires == full_period_n
            # exactly. The value is identical across exits BY CONSTRUCTION
            # (every entry is replayed through all 24 exits) and varies
            # 69..560 across configs. full_period_n matches fires only
            # because holdout_n is 0 - Step 1 does not read the holdout.
            "is_n": pe.get("fires"),
            "full_n_count_only": (pe.get("admit") or {}).get("full_period_n"),
        })
    return out


def load(paths: list) -> tuple[list, list, list]:
    arts = [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]
    rows, skips = [], []
    for a in arts:
        raw = a.get("rows")
        src = raw if isinstance(raw, list) else _factorial_rows(a)
        for r in src:
            (skips if r.get("is_sharpe") is None else rows).append(r)
    return arts, rows, skips


# B3088: buckets COPIED from producer_variant_table.DEPTH_TIERS rather than
# re-invented, so the two renderers cannot drift (L799). Runbook 6.4b: tier =
# DEEP n>=100 / MID 30-99 / THIN 10-29. It exists because rank improves
# monotonically as evidence thins - RANK IS NOT TRUSTWORTHINESS - so the depth
# band has to sit beside the ranking key.
DEPTH_TIERS = ((100, None, "DEEP"), (30, 100, "MID"), (0, 30, "THIN"))


def _tier(n) -> str:
    """The depth band for a cell, or '-' when the count is not recorded.

    An absent count yields an absent tier - never THIN, which would read as a
    measured shallow sample (L580).
    """
    if n is None:
        return "-"
    for lo, hi, name in DEPTH_TIERS:
        if n >= lo and (hi is None or n < hi):
            return name
    return "-"


def _rank_key(r: dict) -> tuple:
    """The LOCKED Table D order: is_ci_lo DESC, then n DESC.

    B3085. This renderer ranked on -is_sharpe, which the runbook's 6.4b
    names as the REJECTED key: "Sorting on Sharpe was rejected: L455 records
    that the higher Sharpe can carry a NEGATIVE lower bound." MEASURED on the
    432-row three_white_soldiers set - 15 of the 25 top rows under the Sharpe
    sort carried a negative lower bound, and only 2 of 25 positions agreed
    with the specified order.

    A row whose lower bound or trade count is NOT RECORDED sorts LAST on that
    key rather than being read as 0 - an absent measurement must never rank as
    a measured one (L580). Python's sort is stable, so rows tied on every
    available key keep the order their artifacts were read in.
    """
    ci = r.get("is_ci_lo")
    n = r.get("is_n")
    return (0 if ci is not None else 1, -(ci if ci is not None else 0),
            0 if n is not None else 1, -(n if n is not None else 0))


def _design(rows: list) -> str:
    """B3082e: name the design the ROWS have, not an assumed one.

    This header said "one-at-a-time design" unconditionally. On the
    factorial candle campaign that is false - each corner moves three
    axes together - and a header asserting a design the rows do not
    have is the same defect as a label asserting a test that never
    ran. Derived from the rows, so it cannot drift from them.
    """
    if any(r.get("levels") for r in rows):
        return "FACTORIAL design - a row is one corner, several axes at once"
    return "one-at-a-time design"


def _n(v) -> str:
    """A count the artifact does not carry renders '-', never 0 or None."""
    return "-" if v is None else str(v)


def _level_cell(param: dict, level) -> str:
    t = param.get("type", "")
    if t.startswith("float>="):
        return f">={level}"
    if t.startswith("float<="):
        return f"<={level}"
    return str(level)


def _row_cells(r: dict, params: list) -> dict:
    """Every inventory column gets a value: production for what the cell did
    not vary, the threshold for what it did, '-' for a breadth axis not
    applied (production behavior)."""
    vals = {}
    for p in params:
        vals[p["param"]] = "-" if p["id"].startswith("B") else str(p["production"])
    # B3082: a FACTORIAL row varies several axes at once. Without this the
    # loop below would set at most ONE of them and the other tested axes
    # would render at production value - a view that cannot be told apart
    # from one where they were never tested (#182 applied to the view).
    if r.get("levels"):
        by_name = {p["param"]: p for p in params}
        for name, level in r["levels"].items():
            p = by_name.get(name)
            if p is not None:
                vals[name] = _level_cell(p, level)
        return vals
    tag = r.get("cell", "")
    if tag.startswith("depth:"):
        leg, arm = tag.split(":", 1)[1].split("/")
        vals["leg"] = leg
        vals["confirmation_arm"] = arm
    elif r.get("axis"):
        p = next(x for x in params if x["param"] == r["axis"])
        vals[r["axis"]] = _level_cell(p, r["level"])
    return vals


def build_table(strategy: str, artifact_paths: list, top: int = 25) -> str:
    arts, rows, skips = load(artifact_paths)
    params = _spec(strategy)["params"]
    # B2708: Table D renders the LIVE Table A inventory - artifact rows for
    # axes an owner ruling has since pruned from the band drop out of the
    # view (their tested history stays in the committed artifacts).
    known = {p["param"] for p in params}
    rows = [r for r in rows if not r.get("axis") or r["axis"] in known]
    skips = [s for s in skips if s.get("axis") in known]
    ranked = sorted((r for r in rows if not r.get("npt_barred")),
                    key=_rank_key)

    # B3082c: evidence of testing comes in two shapes and BOTH count.
    #   sweep     - r["axis"]/r["level"], one axis per row
    #   factorial - r["levels"], every axis the corner varied
    # Reading only the first labelled a factorial campaign's tested axes
    # UNTESTED while the body showed their thresholds.
    tested_levels: dict[str, set] = {}
    resim_tested: set = set()
    for r in rows:
        if r.get("axis"):
            tested_levels.setdefault(r["axis"], set()).add(r["level"])
        for name, lev in (r.get("levels") or {}).items():
            tested_levels.setdefault(name, set()).add(lev)
            resim_tested.add(name)

    resweeps = {a["axis"]: a for a in arts if a.get("axis")}
    fires = next((a.get("reproduction_fires") for a in arts
                  if a.get("reproduction_fires")), None)

    inv = []
    for p in params:
        # S6-B2874: `.get`, not a subscript. MEASURED at B2874: 29 of 70
        # params across both registries carry NO free_band, and this line
        # only ever met the 41 that do because the resolver above it
        # KeyErrored before reaching them. Fixing the first crash unmasked
        # the second - the defect was hiding behind the defect (L814).
        levs = tested_levels.get(p["param"])
        if levs:
            shown = ", ".join(str(x) for x in sorted(levs, key=str))
            # B3082c: name the MECHANISM. Re-simulation is stronger evidence
            # than offline grading, and calling it "untested offline" reads
            # as untested.
            how = ("TESTED BY RE-SIMULATION" if p["param"] in resim_tested
                   else "TESTED")
            # B3082d: ONE level equal to production is the axis being HELD,
            # not tested - calling it tested overstates the campaign's
            # coverage. And a multi-level axis owes its DENOMINATOR: how
            # many of its band levels were actually run (#182 applied to
            # the view, the defect this renderer exists to prevent).
            band = p.get("band") or []
            if len(levs) == 1 and next(iter(levs)) == p.get("production"):
                line = (f"{p['id']} {p['param']}: HELD AT PRODUCTION"
                        f" {p['production']} - band {band} was not varied")
            else:
                cov = (f" ({len(levs)} of {len(band)} band levels)"
                       if band else "")
                line = f"{p['id']} {p['param']}: {how} at {{{shown}}}{cov}"
            rs = resweeps.get(p["param"])
            if rs and rs.get("coverage"):
                c = rs["coverage"]
                line += (f" under WIDENED COVERAGE {c['is_fire_coverage']:.3f}"
                         f" (owner option (b); {c['excluded_gap_pct']}% gap"
                         " excluded from both arms - verdict binds the covered"
                         " subpopulation only)")
        elif p.get("free_band"):
            # B3082c: previously this printed the BAND under a "TESTED at"
            # heading whenever nothing had tested it - announcing a test
            # that never ran (L580). It is offline-gradable and UNTESTED.
            line = (f"{p['id']} {p['param']}: production {p['production']},"
                    f" free band {p['free_band']} - NOT TESTED in this"
                    " campaign (offline-gradable; no rows varied it)")
        else:
            line = (f"{p['id']} {p['param']}: production {p['production']},"
                    f" band {p['band']} - resim-only, UNTESTED-OFFLINE"
                    " (no env knob; engine re-simulation required)")
        inv.append(line)

    nulls = []
    for a, path in zip(arts, artifact_paths):
        pn = a.get("permutation_null") or {}
        if not pn:
            continue
        name = Path(path).name
        if a.get("axis"):
            label = f"single-axis null ({a['axis']}, {name})"
            best = pn.get("observed_best_is_sharpe")
        else:
            label = f"numeric-breadth null (3-of-4 axes swept in {name})"
            best = pn.get("observed_breadth_best_is_sharpe")
        nulls.append(f"{label}: best {best} vs q95 "
                     f"{pn.get('null_max_quantiles', {}).get('0.95')}, "
                     f"p {pn.get('p_value_best')} ({pn.get('n_perms')} perms, SYNTHETIC)")

    skip_notes = []
    for s in skips:
        ax = s.get("axis")
        if ax in resweeps:
            skip_notes.append(f"{ax} was coverage-SKIPPED ({s.get('level')}) and is"
                              " SUPERSEDED by its re-sweep - rows integrated in this table")
        else:
            skip_notes.append(f"{ax} SKIP ({s.get('level')}) - UNTESTED, not refuted")

    head = ["# TABLE D (OFFLINE FORM, unified) - " + strategy + " Step-1",
            "",
            f"{len(rows)} graded cells across {len(arts)} artifact(s)"
            + (f"; reproduction {fires} fires" if fires else "")
            + "; holdout NOT read; no gates (B1608); npt excluded from ranking.",
            "INVENTORY (one column per Table A row; '-' = breadth axis not applied,"
            " production behavior; " + _design(rows) + "):",
            *["  - " + x for x in inv],
            *[u"NULL PRICE - " + x for x in nulls],
            *["DISPOSITION - " + x for x in skip_notes],
            *(["COUNTS - IS n is the in-sample trade count for the cell and "
               "full n the full-period count. On a FACTORIAL artifact the "
               "grader stores the first under the name 'fires', which counts "
               "CUBE ROWS and not signal fires; n is identical across exits "
               "BY CONSTRUCTION, because every entry is replayed through all "
               "24 exit methods, and it varies across configs. full n equals "
               "IS n wherever holdout_n is 0 - Step 1 does not read the "
               "holdout."]
              if any(r.get("levels") for r in ranked) else []),
            *(["COUNTS - %d of %d ranked rows carry no IS n, so their tier "
               "reads '-'. An absent count is never rendered as 0 or as THIN "
               "(L580)." % (sum(1 for r in ranked if r.get("is_n") is None),
                            len(ranked))]
              if any(r.get("is_n") is None for r in ranked) else []),
            "TIER - DEEP n>=100, MID 30-99, THIN 10-29. Rank improves "
            "monotonically as evidence thins, so RANK IS NOT TRUSTWORTHINESS "
            "and the depth band sits beside the ranking key deliberately.",
            "SORT - is_ci_lo DESCENDING, then IS n descending, nothing filtered (runbook 6.4b). Ranking on Sharpe is the REJECTED order: a higher Sharpe can carry a NEGATIVE lower bound (L455)."
            + ("" if any(r.get("is_n") is not None for r in ranked)
               else " No row carries IS n, so the secondary key cannot discriminate and rows tied on is_ci_lo keep artifact order - never a substituted count."),
            "EXITS - Step 1 picks each cell's exit by SHARPE alone (B1605) while this table RANKS by is_ci_lo. Two objectives, so a leading row can carry the exit that won on Sharpe.",
            f"Showing top {min(top, len(ranked))} of {len(ranked)} ranked cells.",
            "",
            "| rank | " + " | ".join(p["param"] for p in params)
            + " | exit | IS sharpe | IS ci_lo | IS n | full n | tier |",
            "|" + "---|" * (len(params) + 7)]

    body = []
    for i, r in enumerate(ranked[:top], 1):
        c = _row_cells(r, params)
        ci = r.get("is_ci_lo")
        body.append("| " + str(i) + " | "
                    + " | ".join(c[p["param"]] for p in params)
                    + f" | {r['exit']} | {r['is_sharpe']:.3f} | "
                    + ("" if ci is None else str(round(ci, 3)))
                    # B3082b: '-' for a count the artifact does not carry.
                    # An unmeasured value must never render as 0 or None
                    # (L580); .get keeps a sweep row's behaviour unchanged.
                    + " | " + _n(r.get("is_n"))
                    + " | " + _n(r.get("full_n_count_only"))
                    + " | " + _tier(r.get("is_n")) + " |")
    return "\n".join(head + body) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--artifacts", nargs="+", required=True)
    ap.add_argument("--top", type=int, default=10**9,
                    help="rows to show (default: ALL - S6-B2700 deferred half closed at B2702)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    md = build_table(a.strategy, a.artifacts, a.top)
    Path(a.out).write_text(md, encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
