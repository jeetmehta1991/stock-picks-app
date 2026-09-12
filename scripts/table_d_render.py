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
from producer_variant_table import SPECS_PHASE0  # noqa: E402


def load(paths: list) -> tuple[list, list, list]:
    arts = [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]
    rows, skips = [], []
    for a in arts:
        for r in a.get("rows", []):
            (skips if r.get("is_sharpe") is None else rows).append(r)
    return arts, rows, skips


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
    params = SPECS_PHASE0[strategy]["params"]
    ranked = sorted((r for r in rows if not r.get("npt_barred")),
                    key=lambda r: -r["is_sharpe"])

    tested_levels: dict[str, set] = {}
    for r in rows:
        if r.get("axis"):
            tested_levels.setdefault(r["axis"], set()).add(r["level"])

    resweeps = {a["axis"]: a for a in arts if a.get("axis")}
    fires = next((a.get("reproduction_fires") for a in arts
                  if a.get("reproduction_fires")), None)

    inv = []
    for p in params:
        if p["free_band"]:
            levs = tested_levels.get(p["param"])
            shown = (", ".join(str(x) for x in sorted(levs, key=str)) if levs
                     else ", ".join(str(x) for x in p["free_band"]))
            line = f"{p['id']} {p['param']}: TESTED at {{{shown}}}"
            rs = resweeps.get(p["param"])
            if rs and rs.get("coverage"):
                c = rs["coverage"]
                line += (f" under WIDENED COVERAGE {c['is_fire_coverage']:.3f}"
                         f" (owner option (b); {c['excluded_gap_pct']}% gap"
                         " excluded from both arms - verdict binds the covered"
                         " subpopulation only)")
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
            " production behavior; one-at-a-time design):",
            *["  - " + x for x in inv],
            *[u"NULL PRICE - " + x for x in nulls],
            *["DISPOSITION - " + x for x in skip_notes],
            f"Showing top {min(top, len(ranked))} of {len(ranked)} ranked cells.",
            "",
            "| rank | " + " | ".join(p["param"] for p in params)
            + " | exit | IS sharpe | IS ci_lo | IS n | full n |",
            "|" + "---|" * (len(params) + 6)]

    body = []
    for i, r in enumerate(ranked[:top], 1):
        c = _row_cells(r, params)
        ci = r.get("is_ci_lo")
        body.append("| " + str(i) + " | "
                    + " | ".join(c[p["param"]] for p in params)
                    + f" | {r['exit']} | {r['is_sharpe']:.3f} | "
                    + ("" if ci is None else str(round(ci, 3)))
                    + f" | {r['is_n']} | {r['full_n_count_only']} |")
    return "\n".join(head + body) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--artifacts", nargs="+", required=True)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    md = build_table(a.strategy, a.artifacts, a.top)
    Path(a.out).write_text(md, encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
