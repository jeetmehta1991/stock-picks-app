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
    SPECS, SPECS_PHASE0, resolved_spec)


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

    S6-B3139z (B3139q-r20): the precedence is now RULED, not preserved -
    owner ruling S6-B3139o (2026-09-30) "SPECS wins", applied PER PARAM by
    producer_variant_table.resolved_spec, the one definition this renderer
    and band_coverage_gate share. The B2874 hazard is why it is per param:
    a whole-entry SPECS-first flip dropped smc_liquidity_sweep_reversal's
    confirmation_arm column (test_b2699); the per-param merge keeps every
    id either registry holds, so no column is lost. PHASE0-first had left
    this view showing bollinger_lower's P3/P4 band as 1 level while the
    coverage gate counted the ruled 8.
    """
    spec = resolved_spec(strategy)
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
            # under a misleading name. grade_candle_config.grade builds
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


def _cube_dir(cube) -> Path | None:
    """The run directory an artifact's `cube` field names.

    S6-B3139w. Artifacts record `cube` in four shapes - MEASURED over one
    Step-2 config's four artifacts: an absolute path to the cube CSV, an
    absolute directory, a repo-relative directory, and a Windows backslash
    path. A CSV path resolves to its directory; a relative one to ROOT.
    """
    if not cube:
        return None
    p = Path(str(cube).replace("\\", "/"))
    if not p.is_absolute():
        p = ROOT / p
    if p.suffix:
        p = p.parent
    return p


def _run_levels(a: dict, params: list) -> dict:
    """{param: value} for every env-actuated parameter, read from the cube's
    OWN run manifest - the value the engine actually ran at.

    S6-B3139w (council 2026-10-01, 5 of 5). A resim-swept axis runs ONE
    CUBE PER LEVEL, so no row varies it and the row-derived labels below
    printed the registry PRODUCTION value with NOT TESTED - span 200 for a
    cube that ran span 9. The source of truth is run_manifest.json ->
    arms[].env, joined to each param's `env` actuator (two params may share
    one actuator: P3 and P4 both read STRAT_EMA_SPAN).

    THE FAIL-CLOSED HALF (peer-review guard): when the manifest is absent,
    unreadable, or records no arm env, every env-actuated param reads
    UNKNOWN - never the registry production value, which would rebuild the
    same defect one layer down. When the manifest records an arm env that
    omits a param's actuator, the engine inherited its default
    (run_wave.py builds env as {**os.environ, **arm.env}), so the value is
    production and is labelled as such.
    """
    actuated = [p for p in params if p.get("env")]
    if not actuated:
        return {}
    d = _cube_dir(a.get("cube"))
    env = None
    if d is not None and (d / "run_manifest.json").is_file():
        try:
            m = json.loads((d / "run_manifest.json").read_text(encoding="utf-8"))
            arms = m.get("arms") or []
            if arms and isinstance(arms[0].get("env"), dict):
                env = arms[0]["env"]
        except (OSError, ValueError):
            env = None
    out = {}
    for p in actuated:
        if env is None:
            out[p["param"]] = UNKNOWN
        elif p["env"] in env:
            raw = env[p["env"]]
            # S6-B3139ax: a BLANK value is the engine's unset path - config
            # parses e.g. CANDLE_MAX_WICK_PCT as `float(raw) if raw else None`
            # (backtest/config._candle_wick_raw) - so the cube ran at production
            # and "" is not a level. A knob whose parser cannot take a blank
            # never produced a completed cube, so this cannot mislabel a run.
            if isinstance(raw, str) and not raw.strip():
                out[p["param"]] = p.get("production")
                continue
            try:
                out[p["param"]] = json.loads(raw)
            except (TypeError, ValueError):
                out[p["param"]] = raw
        else:
            out[p["param"]] = p.get("production")
    return out


UNKNOWN = "UNKNOWN"


def load(paths: list, params: list | None = None) -> tuple[list, list, list]:
    arts = [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]
    rows, skips = [], []
    for a in arts:
        raw = a.get("rows")
        src = raw if isinstance(raw, list) else _factorial_rows(a)
        run = _run_levels(a, params or [])
        a["_run_levels"] = run
        for r in src:
            if run:
                r = {**r, "run_levels": run}
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
    # S6-B3139w: the value the cube's engine actually ran at, from its own
    # run manifest - overrides the registry production default above.
    for name, level in (r.get("run_levels") or {}).items():
        p = next((x for x in params if x["param"] == name), None)
        if p is not None:
            vals[name] = (UNKNOWN if level == UNKNOWN
                          else _level_cell(p, level))
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
        p = next((x for x in params if x["param"] == r["axis"]), None)
        if p is not None:
            vals[r["axis"]] = _level_cell(p, r["level"])
        else:
            # S6-B3139an: a row keyed by a declared signal key lands in its
            # param's column, naming the key and its condition.
            p = next(x for x in params
                     if r["axis"] in (x.get("signal_keys") or []))
            vals[p["param"]] = _key_cond(r["axis"], r.get("op"), r["level"])
    return vals


def _key_cond(axis: str, op, level) -> str:
    """S6-B3139an: the cell for a row keyed by a param's signal key."""
    sym = {"le": "<=", "ge": ">="}.get(op)
    if sym:
        return f"{axis} {sym} {level}"
    if op in ("eq_true", "eq_false"):
        return f"{axis} = {'true' if op == 'eq_true' else 'false'}"
    if op == "pos":  # S6-B3139az: a COUNT kept at > 0
        return f"{axis} > 0"
    return f"{axis} {op} {level}"


def _manifest_step(a: dict):
    """(step or None, unreadable-reason or None) from the artifact's cube's own
    run manifest - the ONE reader _step and _holdout_clause share."""
    d = _cube_dir(a.get("cube"))
    if d is None or not (d / "run_manifest.json").is_file():
        return None, None
    try:
        m = json.loads((d / "run_manifest.json").read_text(encoding="utf-8"))
        return (int(m["step"]) if m.get("step") is not None else None), None
    except (OSError, ValueError, TypeError) as exc:
        return None, f"{d.name}: {type(exc).__name__}"


def _holdout_clause(arts: list) -> str:
    """S6-B3139af: what the rendered artifacts did with the holdout, derived
    PER ARTIFACT - its own `window` field first (breadth grids record "IS only
    ..."), else its cube's run-manifest step (1 = in-sample only; 2 = the
    config read the holdout once and was judged on the six live gates).
    Nothing recorded reads UNRECORDED, never a default: the preamble
    hard-coded "holdout NOT read; no gates (B1608)", false on Step-2 renders."""
    is_only, read, unknown, other = 0, 0, 0, {}
    for a in arts:
        w = a.get("window")
        if isinstance(w, str) and w.strip().upper().startswith("IS ONLY"):
            is_only += 1
            continue
        step, _bad = _manifest_step(a)
        if step == 1:
            is_only += 1
        elif step == 2:
            read += 1
        elif step is None:
            unknown += 1
        else:
            other[step] = other.get(step, 0) + 1
    parts = []
    if is_only:
        parts.append(f"{is_only} in-sample-only artifact(s): holdout NOT read,"
                     " no gates (B1608)")
    if read:
        parts.append(f"{read} Step-2 artifact(s): the holdout was read ONCE per"
                     " config and judged on the six live gates - see each"
                     " config's step2 verdict")
    for s, n in sorted(other.items()):
        parts.append(f"{n} Step-{s} artifact(s): holdout use not classified by"
                     " this renderer")
    if unknown:
        parts.append(f"{unknown} artifact(s) record no window and no run-manifest"
                     " step: holdout use UNRECORDED")
    return "; ".join(parts)


def _step(arts: list) -> str:
    """The step the cubes ran at, from their own manifests (S6-B3139w: the
    header said Step-1 unconditionally, on Step-2 cubes too). Several steps
    in one render are named together; none recorded reads 'step UNKNOWN'."""
    steps = set()
    unreadable = []
    for a in arts:
        step, bad = _manifest_step(a)
        if bad:
            # #122: a manifest that cannot be read is REPORTED in the
            # header, never skipped silently.
            unreadable.append(bad)
        elif step is not None:
            steps.add(step)
    note = f"; unreadable manifest(s): {', '.join(unreadable)}" if unreadable else ""
    if not steps:
        return f"step UNKNOWN (no readable run manifest recorded{note})"
    return " + ".join(f"Step-{s}" for s in sorted(steps)) + (
        f" ({note[2:]})" if note else "")


def build_table(strategy: str, artifact_paths: list, top: int = 25) -> str:
    params = _spec(strategy)["params"]
    arts, rows, skips = load(artifact_paths, params)
    # S6-B3139z: the spec above is the per-param merge with SPECS
    # authoritative (S6-B3139o). The pre-registration record (SPECS_PHASE0)
    # is disclosed beside any band it disagrees with - never chosen.
    _pre = SPECS_PHASE0.get(strategy) if SPECS.get(strategy) else None
    pre_band = {p["id"]: p.get("band")
                for p in ((_pre or {}).get("params") or [])}
    # B2708: Table D renders the LIVE Table A inventory - artifact rows for
    # axes an owner ruling has since pruned from the band drop out of the
    # view (their tested history stays in the committed artifacts).
    # S6-B3139an: a row's axis is a param's display LABEL or one of its
    # declared signal_keys - breadth grids key rows by signal name (adx,
    # below_ema_N), and matching labels alone hid 208 of 806 rows. A row
    # matching neither is dropped from the view AND COUNTED in the header.
    known = ({p["param"] for p in params}
             | {k for p in params for k in (p.get("signal_keys") or [])})
    dropped: dict[str, int] = {}
    for r in rows:
        if r.get("axis") and r["axis"] not in known:
            dropped[r["axis"]] = dropped.get(r["axis"], 0) + 1
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
    # S6-B3139w: a resim-swept axis is one cube per level, so its evidence is
    # the cube's run manifest, not row variance. A value equal to production
    # is the axis HELD (the existing branch below says so); UNKNOWN is
    # carried to its own inventory line, never counted as tested.
    # Only a NON-production run level is resim evidence: a manifest holding
    # an actuated param at its default says nothing about whether OFFLINE
    # rows varied it, so it must not relabel an offline axis as resim.
    unknown_run: set = set()
    run_seen: dict[str, set] = {}
    for a in arts:
        for name, lev in (a.get("_run_levels") or {}).items():
            if lev == UNKNOWN:
                unknown_run.add(name)
            else:
                run_seen.setdefault(name, set()).add(lev)
    prod = {p["param"]: p.get("production") for p in params}
    for name, levs in run_seen.items():
        if any(lev != prod.get(name) for lev in levs):
            tested_levels.setdefault(name, set()).update(levs)
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
        # S6-B3139an: rows keyed by this param's signal keys (breadth AND-
        # conditions on the production base). Their levels are the subject's
        # own quantiles or flags, not this param's band, so they are NAMED
        # here and never counted toward the band denominator below.
        comp = [r for r in rows if r.get("axis") in (p.get("signal_keys") or [])]
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
                    " campaign (offline-gradable; "
                    + ("no row ran a band level)" if comp
                       else "no rows varied it)"))
        else:
            # S6-B3139z: the knob clause reads the row - a resim-only param
            # with an env knob is not "no env knob".
            knob = (f"resim via {p['env']}" if p.get("env")
                    else "no env knob")
            line = (f"{p['id']} {p['param']}: production {p['production']},"
                    f" band {p['band']} - resim-only, UNTESTED-OFFLINE"
                    f" ({knob}; engine re-simulation required)")
        # S6-B3139w/z: where the pre-registration record (SPECS_PHASE0)
        # disagrees with the authoritative band it is disclosed, never chosen.
        pre = pre_band.get(p["id"])
        if pre is not None and pre != (p.get("band") or []):
            line += (f"; band {p.get('band')} per SPECS (pre-registration"
                     f" SPECS_PHASE0 band {pre}; SPECS wins per owner ruling"
                     " S6-B3139o)")
        if comp:
            by_k: dict[str, list] = {}
            for r in comp:
                by_k.setdefault(r["axis"], []).append(r)
            num = lambda x: ((0, float(x)) if isinstance(x, (int, float))
                             else (1, str(x)))
            parts = []
            for k in sorted(by_k):
                for o in sorted({r.get("op") for r in by_k[k]}, key=str):
                    if o in ("eq_true", "eq_false", "pos"):
                        parts.append(_key_cond(k, o, None))
                        continue
                    lv = sorted({r["level"] for r in by_k[k]
                                 if r.get("op") == o}, key=num)
                    sym = {"le": "<=", "ge": ">="}.get(o, o)
                    parts.append(f"{k} {sym} {{{', '.join(map(str, lv))}}}")
            line += (f"; OFFLINE COMPANION ROWS ({len(comp)}, in this column):"
                     f" {'; '.join(parts)} - AND-conditions on the production"
                     " base, not counted toward the band levels")
        # S6-B3139w fail-closed half: an actuated axis whose cube left no
        # readable run manifest. The tested-status above still holds; the
        # VALUE the cube ran at is unknown, so production is never assumed
        # (the row cells read UNKNOWN for the same reason).
        if not levs and p["param"] in unknown_run:
            line += ("; run value UNKNOWN - no readable run_manifest.json"
                     " arm env for this cube, production NOT assumed")
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

    head = ["# TABLE D (OFFLINE FORM, unified) - " + strategy + " " + _step(arts),
            "",
            f"{len(rows)} graded cells across {len(arts)} artifact(s)"
            + (f"; reproduction {fires} fires" if fires else "")
            + "; " + _holdout_clause(arts) + "; npt excluded from ranking.",
            # S6-B3139an: a dropped row is COUNTED, never silent.
            *([f"ROWS NOT RENDERED - {sum(dropped.values())} artifact row(s)"
               " whose axis is neither a Table A label nor a declared signal"
               " key (B2708 prunes them from this view; their history stays"
               " in the artifacts): "
               + ", ".join(f"{k} ({v})" for k, v in sorted(dropped.items()))]
              if dropped else []),
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
            "SORT - is_ci_lo DESCENDING, then IS n descending, nothing filtered (runbook section 7.5). Ranking on Sharpe is the REJECTED order: a higher Sharpe can carry a NEGATIVE lower bound (L455)."
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
