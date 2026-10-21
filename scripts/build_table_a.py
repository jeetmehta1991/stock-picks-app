#!/usr/bin/env python
"""B2836 (owner-directed 2026-09-16): generate the per-strategy Table A pair -
DEPTH (own-gate persisted magnitudes) and BREADTH (companion producers on the
strategy's own fires) - for every strategy in a named lane of the stamped
status view, into the strategy_optimisation/ directory.

The owner's charter: Fable defines the bands for ALL producers per strategy,
each level marked OFFLINE (a subset of recorded fires - free) or RESIM (an
engine leg). The 12 TIGHTEN-lane strategies first (Fable end-to-end), the 29
BOTH-lane next (tables by Fable, execution by Opus).

MEASURED, NEVER INVENTED (#165/#201): every band level is a quantile of the
key's values on the strategy's SURVIVING fires (the T1 filter - the live
strategy function replayed on each fire's persisted signals, exactly the
builder's survival path); every coverage and retention figure is counted from
those same rows. Single-definition rule (L593): QUANTS and MIN_COVERAGE are
IMPORTED from breadth_step1_grid, the instrument that will consume the bands;
fire loading and signal parsing are the builder's own.

WHAT THIS CANNOT SEE (stated in every file): a producer whose values are not
persisted in signals_at_entry does not exist to the cube - such axes are
engine-only by construction (runbook §4.3) and no offline table can enumerate
them. The depth extraction is the builder's source pattern - a LOWER BOUND
(thresholds via helpers or config constants are invisible).

Module attribution names a module that WRITES the key (S6-B3251; an f-string
template counts) under backtest/signals, data and engine - a static AST read.
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import build_strategy_status as bss                      # noqa: E402
from breadth_step1_grid import MIN_COVERAGE, QUANTS      # noqa: E402
from table_a_bands import (KEY_SELECTOR_KNOBS, LEG_DEFN, PRODUCER_BANDS,  # noqa: E402
                           STRATEGY_EXTRAS, band_axes, band_level_classes)


_CODE_NOW = None


def fire_logic_config_reads(name: str):
    """S6-B3253: the config values strategy `name`'s fire logic reads - the
    S6-B3235 fire-logic members (its body and all it reaches, a delegation
    followed) - or None when the strategy's function is not found."""
    global _CODE_NOW
    if _CODE_NOW is None:
        _CODE_NOW = bss.CodeSide(None)
    fn = _CODE_NOW.index("backtest.signals.screener")["strategies"].get("strat_" + name)
    if fn is None:
        return None
    return {m.split(":", 2)[2] for m in _CODE_NOW.members(fn)
            if m.startswith("value:backtest.config:")}

# B2841: one numeric-compare pattern for BOTH extractors. The first cut used
# [^)]* for the s.get(...) argument span, which cannot cross the ')' of a
# nested call - so a default like float('-inf') broke the match and TWO LIVE
# production gates were missing from Table A depth (cmf_flip's
# po3_accum_range_pct >= 0.0458, pairs_short's ppo_signal >= -0.858). One
# nested-paren level is now allowed.
# S6-B3171 extends the RHS: a gate that reads its threshold from config
# (s.get(key) < _cfg.NAME) is matched and resolved to the production value
# by _resolve_rhs - the S6-B3120h precedent one token to the right.
_NUM_CMP = (r"s\.get\(f?['\"]([a-zA-Z0-9_{}.]+)['\"]"
            r"(?:[^()]|\([^()]*\))*\)\s*([<>]=?)\s*"
            r"(-?[0-9.]+|_cfg\.[A-Z0-9_]+)")

# S6-B3120h: a SPAN-KEYED gate reads its signal through an f-string whose
# placeholder is a config constant - s.get(f"price_above_ema_{_cfg.
# STRAT_EMA_SPAN}") since B3119. The old key pattern ([a-z0-9_{}]+) could not
# cross the '.', so the leg was DROPPED SILENTLY and every regeneration lost
# the bollinger P3/P4 ema rows that had to be hand-restored (the L875 class
# reaching the generator). Known config placeholders resolve to their
# production value so the leg lands under its persisted production key (and
# its PRODUCER_BANDS entry); an UNKNOWN braced key passes through unchanged -
# visible in the render, never silently dropped.
def _resolve_fstring_key(key: str) -> str:
    from backtest import config as _bt_cfg
    return key.replace("{_cfg.STRAT_EMA_SPAN}", str(_bt_cfg.STRAT_EMA_SPAN))


def _resolve_rhs(v: str) -> float:
    """S6-B3171 (the S6-B3120h precedent, comparison side): a threshold the
    gate reads from config resolves to its production value, so an
    env-actuated ceiling stays visible to Table A and the stream detector
    instead of silently dropping (the L875 class)."""
    if v.startswith("_cfg."):
        from backtest import config as _bt_cfg
        return float(getattr(_bt_cfg, v[len("_cfg."):]))
    return float(v)

OUT_DIR = ROOT / "strategy_optimisation"
STATUS_JSON = ROOT / "output_audit" / "strategy_optimisation_status.json"

# modules scanned for the (heuristic) key -> emitting-module attribution
_ATTR_DIRS = ("backtest/signals", "backtest/data", "backtest/engine")


def depth_comparisons(src: str) -> dict:
    """(strategy) -> [(key, op, literal), ...] for every s.get(key) <op> NUMBER.

    The builder's numeric_thresholds() keeps only the KEYS; Table A needs the
    operator and the production literal too, so this walks the same AST with
    a grouped pattern. Same lower-bound caveat as the builder's.
    """
    out = {}
    for n in ast.walk(ast.parse(src)):
        if not (isinstance(n, ast.FunctionDef) and n.name.startswith("strat_")):
            continue
        body = ast.unparse(n)
        rows = re.findall(_NUM_CMP, body)
        if rows:
            out[n.name[len("strat_"):]] = [
                (_resolve_fstring_key(k), op, _resolve_rhs(v)) for k, op, v in rows]
    return out


def gate_legs(src: str) -> dict:
    """(strategy) -> (boolean_legs, helper_gates): the NON-numeric members of
    the entry condition. B2838, owner-caught: the first render's depth table
    held only numeric-literal gates, so a strategy like three_black_crows_short
    showed ONE row while its gate reads a candle-pattern PRODUCER boolean and a
    borrow-trap helper - and an axis left out of Table A is invisible at close
    (L785). Boolean legs carry their tunables in the PRODUCER layer; those
    knobs are inventoried at R1 (the SPECS entry), so the pre-R1 row marks
    them with their bands to define rather than omitting them. Helper-gate detection
    is a source pattern - a lower bound, like every extraction here.
    """
    out = {}
    for n in ast.walk(ast.parse(src)):
        if not (isinstance(n, ast.FunctionDef) and n.name.startswith("strat_")):
            continue
        body = ast.unparse(n)
        all_keys = [_resolve_fstring_key(k) for k in re.findall(
            r"s\.get\(f?['\"]([a-zA-Z0-9_{}.]+)['\"]", body)]
        numeric = {_resolve_fstring_key(k)
                   for k, _, _ in re.findall(_NUM_CMP, body)}
        legs = sorted({k for k in all_keys if k not in numeric})
        # left boundary required: without it the DEF SIGNATURE's own name
        # matched ("...crows_short(s)" yielded a phantom helper _crows_short)
        helpers = sorted(set(re.findall(
            r"(?<![a-z0-9_])(_[a-z0-9_]+)\(s[,)]", body)) - {"_strat", "_strat3"})
        out[n.name[len("strat_"):]] = (legs, helpers)
    return out


def gate_bodies(src: str) -> dict:
    """B2844 (owner: 'Table A format does not show formula'): the SS6/#183
    locked artifact is FORMULA + Table A + Table B, and 'Section 1 and Table A
    are two views of one' (plan:637) - the generated files carried no Section 1.
    This returns each strategy's executable gate body VERBATIM from the AST
    (docstring and the return statement dropped; the fires expression is the
    formula's strategy layer, unparaphrased)."""
    out = {}
    for n in ast.walk(ast.parse(src)):
        if not (isinstance(n, ast.FunctionDef) and n.name.startswith("strat_")):
            continue
        stmts = n.body
        if stmts and isinstance(stmts[0], ast.Expr) \
                and isinstance(stmts[0].value, ast.Constant):
            stmts = stmts[1:]
        stmts = [s for s in stmts if not isinstance(s, ast.Return)]
        out[n.name[len("strat_"):]] = "\n".join(ast.unparse(s) for s in stmts)
    return out


def _written_keys(text: str):
    """S6-B3251: the keys a module WRITES, as (literal keys, templates). A
    write is a subscript-assignment target (X["k"] = ..., augmented and tuple
    targets too), a key of a dict literal or dict comprehension that is
    returned, assigned or passed to .update(), an .update(k=...) keyword, or
    a .setdefault("k", ...) key. An f-string key is a TEMPLATE - each {...}
    matches [A-Za-z0-9_.]+ - kept with its count of literal characters, the
    measure of how specific it is. A key that is only READ (s.get, a
    membership test, a name quoted in prose) is not a write."""
    lits, tmpls = set(), []

    def key_of(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lits.add(node.value)
        elif isinstance(node, ast.JoinedStr):
            parts, nlit = [], 0
            for v in node.values:
                if isinstance(v, ast.Constant):
                    parts.append(re.escape(str(v.value)))
                    nlit += len(str(v.value))
                else:
                    parts.append(r"[A-Za-z0-9_.]+")
            if nlit:
                tmpls.append((re.compile("^" + "".join(parts) + "$"), nlit))

    def dict_keys(node):
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if k is not None:
                    key_of(k)
        elif isinstance(node, ast.DictComp):
            key_of(node.key)

    for n in ast.walk(ast.parse(text)):
        if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in targets:
                for tt in (t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t]):
                    if isinstance(tt, ast.Subscript):
                        key_of(tt.slice)
            if n.value is not None:
                dict_keys(n.value)
        elif isinstance(n, ast.Return) and n.value is not None:
            dict_keys(n.value)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr == "update":
                for a in n.args:
                    dict_keys(a)
                lits.update(kw.arg for kw in n.keywords if kw.arg)
            elif n.func.attr == "setdefault" and n.args:
                key_of(n.args[0])
    return lits, tmpls


def _module_index() -> list[tuple[str, str, tuple]]:
    """(module path, text, written keys) per scanned module (S6-B3251)."""
    idx = []
    for d in _ATTR_DIRS:
        for p in sorted((ROOT / d).glob("*.py")):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            try:
                written = _written_keys(text)
            except SyntaxError:
                written = (set(), [])
            idx.append((f"{d}/{p.name}", text, written))
    return idx


def attribute(key: str, idx) -> str:
    """S6-B3251: the module that WRITES `key` - a literal writer first (in
    path order), else the most specific f-string template that renders it,
    else none. The old rule named the first file QUOTING the key, often a
    consumer: MEASURED B3139q-r86, williams_r_oversold's price_above_ema_200
    named backtest/signals/index_rebalance.py (a strategy reading it) and
    cmf_flip's cmf_cross_up named screener.py, while technical.py writes
    both (one through an f-string, which a literal grep never matches)."""
    lit = [name for name, _text, (lits, _tm) in idx if key in lits]
    if lit:
        return lit[0] + (f" +{len(lit) - 1}" if len(lit) > 1 else "")
    tm = sorted((-max(n for rx, n in tms if rx.match(key)), name)
                for name, _text, (_l, tms) in idx
                if any(rx.match(key) for rx, _n in tms))
    if tm:
        return (f"{tm[0][1]} (f-string template)"
                + (f" +{len(tm) - 1}" if len(tm) > 1 else ""))
    return "(no module found writing the key)"


def surviving_fires(name: str, frame: pd.DataFrame, survives_pct,
                    unmeasured=None):
    """The T1 filter, reproduced from the builder's survival path: keep a fire
    iff the LIVE strategy function fires with the recorded direction on its
    persisted signals. Identity (skipped) when the view says survives == 1.0.
    S6-B3239: an UNMEASURED side's fires (its gate reads a key no R5 fire of
    it persisted) are dropped first - the replay would read the key's default,
    so none of them can be confirmed a survivor; survives_pct then covers the
    measured sides only, and None means no measured side remains."""
    sigs = [bss._parse_signals(x) for x in frame["signals_at_entry"]]
    dropped = False
    if unmeasured:
        keep_side = [str(d) not in unmeasured for d in frame["direction"]]
        dropped = not all(keep_side)
        frame = frame[pd.Series(keep_side, index=frame.index)]
        sigs = [s for s, k in zip(sigs, keep_side) if k]
        if survives_pct is None:
            return frame, sigs, dropped
    if survives_pct is None or survives_pct >= 1.0:
        return frame, sigs, dropped
    from backtest.signals.screener import ALL_STRATEGIES
    fn = ALL_STRATEGIES.get(name)
    if fn is None:
        raise SystemExit(f"REFUSED: {name} not in ALL_STRATEGIES")
    keep = []
    for s_, d_ in zip(sigs, frame["direction"]):
        try:
            r_ = fn(s_)
        except Exception:
            keep.append(False)
            continue
        keep.append(bool(r_ and r_.get("fires")
                         and r_.get("direction") == str(d_)))
    kept = frame[pd.Series(keep, index=frame.index)]
    ksigs = [s for s, k in zip(sigs, keep) if k]
    return kept, ksigs, True


def key_series(sigs: list[dict]) -> dict:
    """key -> (kind, pd.Series of values over fires). kind: numeric | binary."""
    allk = set().union(*(s.keys() for s in sigs)) if sigs else set()
    out = {}
    for k in sorted(allk):
        vals = [s.get(k) for s in sigs]
        nn = [v for v in vals if v is not None]
        if not nn:
            continue
        if all(isinstance(v, bool) for v in nn):
            out[k] = ("binary", pd.Series([None if v is None else bool(v)
                                           for v in vals], dtype="object"))
            continue
        ser = pd.to_numeric(pd.Series(vals), errors="coerce")
        if ser.notna().sum() == 0:
            continue
        out[k] = ("numeric", ser)
    return out


def _fmt(x) -> str:
    return f"{x:.4f}".rstrip("0").rstrip(".") if isinstance(x, float) else str(x)


# B2836b: a companion must be SCALE-FREE. A cross-sectional threshold on an
# absolute price-denominated key (a band level, a pivot, a moving average)
# selects by SHARE PRICE, not by signal state - its fire-quantiles are just
# the universe's price distribution, and ~60 such keys buried the real axes
# in the first render. Mechanical discriminator, stated per file: |Spearman|
# against a persisted price proxy >= 0.95 => price-denominated, excluded
# from banding BY NAME (with the measured correlation - nothing silent).
_PRICE_PROXIES = ("bb_20_20_mid", "dema", "hull_ma")
_PRICE_RHO = 0.95


def price_denominated(series: dict) -> tuple[dict, str]:
    proxy = next((p for p in _PRICE_PROXIES
                  if p in series and series[p][0] == "numeric"
                  and series[p][1].notna().mean() >= 0.9), None)
    if proxy is None:
        return {}, "(no persisted price proxy - split not applied)"
    ps = series[proxy][1]
    out = {}
    for k, (kind, ser) in series.items():
        if kind != "numeric" or k == proxy:
            continue
        try:
            rho = ser.corr(ps, method="spearman")
        except Exception:
            continue
        if pd.notna(rho) and abs(rho) >= _PRICE_RHO:
            out[k] = round(float(rho), 3)
    out[proxy] = 1.0
    return out, proxy



def _axis(aid, prm, n, sub, act, env, split) -> tuple:
    """S6-B3189: one footer axis - (id, param, n, subset_safe, actuated, env,
    engine, offline, pending). The last three are LEVEL counts that partition
    n: engine = levels the engine runs (production plus any actuated
    non-production level), offline = levels graded from a run's cube,
    pending = levels needing an env knob that does not exist. Every caller
    passes its split; the band rule lives in table_a_bands.band_level_classes."""
    eng, off, pend = split
    assert eng >= 1 and off >= 0 and pend >= 0 and eng + off + pend == n, (
        aid, n, split)
    return (aid, prm, n, sub, act, env, eng, off, pend)


def _axis_sub(cls, prose_sub: bool) -> bool:
    """S6-B3196: an axis's subset-safe flag follows its OWN level classes - a
    multi-axis row can hold a pure-offline axis beside a pure-pending one
    (insider_cluster_active's N and window), and one prose prefix cannot
    describe both. An axis with no non-production level keeps the row's
    prose reading: it has no level to class."""
    n, eng, off, pend = cls
    if n <= 1:
        return prose_sub
    return off > 0 and eng == 1 and pend == 0


def _offline_cell(split, prose, note: str = "") -> str:
    """S6-B3224: an OFFLINE cell leads with its row's COUNTED class - the
    levels the footer grades offline, per axis - so the registry's prose can
    no longer claim an offline grading the count does not hold (6 band rows
    did, MEASURED B3139q-r72w). split is the (n, engine, offline, pending)
    list the footer counts; an empty list is a mirror, counted on the leg it
    mirrors; note says why a count is what it is."""
    if not split:
        return f"counted on the mirrored leg - {prose}"
    parts = ", ".join(f"{off} of {n}" for n, _eng, off, _pend in split)
    return f"offline {parts} levels{note} - {prose}"


def _band_rows(pid: int, subject: str, knobs, axes: list | None = None,
               reads=None) -> list:
    """B2841: the R1 band definitions (table_a_bands.py) as sub-rows under a
    P-row. env None on a resim-bearing knob renders DEFINED-NO-ACTUATOR - the
    band exists, the engine plumbing is follow-up (validate_spec refuses an
    actuatorless resim level, S6-B2569a)."""
    out = []
    for j, k in enumerate(knobs, 1):
        env = k.get("env")
        # S6-B3253: a KEY-SELECTOR knob reaches only a gate that reads it;
        # `reads` is the strategy's fire-logic config set (None = unknown,
        # the old reading). The env name stays on the axis so a twin row
        # still counts as ONE knob; its levels go PENDING, never ENGINE.
        cut = (bool(env) and env in KEY_SELECTOR_KNOBS and reads is not None
               and env not in reads)
        if cut:
            k = dict(k, env=None)
        resim = k.get("resim", "-")
        needs_act = resim not in ("-", "", None) and "none" not in str(resim).lower()[:4]
        act = ("" if not needs_act else
               (f"; env {env} does not reach this gate - it reads the literal "
                f"key - DEFINED-NO-ACTUATOR here (S6-B3253)" if cut else
                f"; env {env}" if env else "; DEFINED-NO-ACTUATOR"))
        vals = k.get("band")
        vals_s = (", ".join(_fmt(v) if isinstance(v, float) else str(v)
                            for v in vals) if isinstance(vals, list)
                  else str(vals))
        # S6-B2862: RENDER AND COUNT FROM ONE SITE. The caller used to append
        # axes in a separate loop, and the STRATEGY-row call site simply did
        # not have one - so 35 axes went unrendered in the footer across 21 of
        # 41 files. Emitting both here makes that omission unexpressible.
        # band_axes is a hand-authored decomposition, never a parse of the
        # band text: a multi-axis band contributes several axes, and a mirror
        # ("as morning_star, mirrored") contributes none, because its axes are
        # already counted on the leg it mirrors.
        _cls = band_level_classes(k)
        if axes is not None:
            # S6-B3189: each axis's levels are classed ONE BY ONE (engine /
            # offline / pending) by the registry's band_level_classes, so the
            # footer and the import-time validator cannot disagree. The
            # TIGHTER prefix used to class EVERY level offline - stochrsi
            # oversold's looser k < 25 then read as a free grading.
            _sub = str(k.get("offline", "")).startswith("TIGHTER")
            # S6-B2862: the ACTUATOR flag must be carried, not inferred. The
            # footer used to read n == 1 as "DEFINED-NO-ACTUATOR", which was
            # only ever true because a prose band silently scored 1. Counting
            # bands correctly breaks that proxy, and an unactuated axis would
            # start inflating ENGINE RUNS - the exact class B2866 refuses.
            _act = bool(env) and not cut
            if len(_cls) == 1:
                axes.append(_axis(f"P{pid}.{j}", k["param"][:40], _cls[0][0],
                                  _axis_sub(_cls[0], _sub), _act, env,
                                  _cls[0][1:]))
            else:
                for _ai, _c in enumerate(_cls, 1):
                    axes.append(_axis(f"P{pid}.{j}.{_ai}", k["param"][:40],
                                      _c[0], _axis_sub(_c, _sub), _act, env,
                                      _c[1:]))
        out.append(
            f"| P{pid}.{j} | BAND | {k['param']} - {k['evidence']} | "
            f"{k['basis']} | "
            f"{k['production']} | {vals_s} | "
            f"{_offline_cell(_cls, k.get('offline', '-'))} | "
            f"{resim}{act} | T3 review before any grid |")
    return out

def render(name: str, row: dict, frame, sigs, filtered: bool,
           comparisons, legs_helpers, idx, specs_names, stamp: str,
           body: str = "") -> str:
    n_all = len(frame)
    # B2845 zero-survivor guard: smc_order_block_bounce survives 0.0 - the T1
    # filter keeps NOTHING, so no offline level is measurable and every
    # retention division below would be 0/0. Emit the honest short form: the
    # formula and inventory stand; the measured sections are replaced by the
    # workflow's own verdict (W-T T1: surviving fires below the floor
    # re-lanes the campaign to W-L - the engine, not the cube, must speak).
    _reads = fire_logic_config_reads(name)   # S6-B3253
    um = row.get("unmeasured_gate_keys") or {}
    um_txt = "; ".join(f"{d} side reads {', '.join(ks)}" for d, ks in sorted(um.items()))
    if n_all == 0:
        verdict = (
            "**T1 VERDICT: 0 of the R5 fires survive the CURRENT gate - no "
            "offline band level is measurable from this cube. Per the "
            "workflow's T1 gate the campaign RE-LANES TO W-L (engine): the "
            "producer bands below are the resim inventory it prices.**")
        if um:
            # S6-B3239: not a measured zero - the gate reads a key the cube
            # never persisted, so survival cannot be measured from it at all
            verdict = (
                f"**T1 VERDICT: UNMEASURED (S6-B3239) - the CURRENT gate's {um_txt}, "
                "absent from every R5 fire of that side, so the replay would "
                "read a default and no survival, and no offline band level, is "
                "measurable from this cube. Per the workflow's T1 gate the "
                "campaign RE-LANES TO W-L (engine): a run at the current gate "
                "produces fires carrying the key, and the producer bands below "
                "are the resim inventory it prices.**")
        return "\n".join([
            f"# Table A - {name}", "", stamp, "",
            f"**Lane:** {row['stream']} | **family:** {row['family']} | "
            f"**status:** {row['status']} | **R5 fires:** {row['r5_fires']} | "
            f"**surviving fires (T1): 0** (survives_pct "
            f"{'UNMEASURED' if row['survives_pct'] is None and um else row['survives_pct']})",
            "",
            verdict, "",
            "## Formula (Section 1 of the SS6/#183 locked artifact)", "",
            "```python", body or "(no body extracted)", "```", "",
            "## Producer bands (resim inventory for the W-L campaign)", "",
            "The gate's parameters and their defined bands are those of the "
            "shared producers - see the smc SPECS family "
            "(producer_variant_table) and table_a_bands.py entries for: "
            + ", ".join(sorted(set(legs_helpers[0]))) + ".", ""])
    series = key_series(sigs)
    depth_keys = sorted({k for k, _, _ in comparisons})
    legs, helpers = legs_helpers
    in_specs = name in specs_names
    L = [f"# Table A - {name}", "",
         stamp, "",
         f"**Lane:** {row['stream']} | **family:** {row['family']} | "
         f"**status:** {row['status']} | **R5 fires:** {row['r5_fires']} | "
         f"**surviving fires (T1):** {n_all}"
         + (f" (the {um_txt}, absent from every R5 fire of that side - its fires "
            "are UNMEASURED and dropped, S6-B3239)" if um else "")
         + (f" (survives_pct {row['survives_pct']})" if filtered else
            (" (code changed since R5; the status build's survival filter"
             f" measured survives_pct {row['survives_pct']} - every fire kept)"
             if row.get("changed_since_r5") else
             " (unchanged since R5 - filter is identity)")),
         "",
         f"**SPECS entry:** {'registered in producer_variant_table' if in_specs else 'NONE - build at R1 before any engine leg (W-T T0)'}",
         "",
         # B2844 (owner-caught): the SS6/#183 locked artifact is FORMULA +
         # Table A + Table B - Section 1 and Table A are two views of one
         # (plan:637). Same id sequence as the inventory below, so the two
         # views cannot drift (pinned: identical P-id sets).
         "## Formula (Section 1 of the SS6/#183 locked artifact)", ""]
    _p = 0
    L.append("=============================== PRODUCER LAYER ===============================")
    L.append("")
    for leg in legs:
        _p += 1
        kn = PRODUCER_BANDS.get(leg, [])
        note = (f"knobs P{_p}.1-P{_p}.{len(kn)} (band rows in Table A)"
                if kn else "knobs bands to define")
        L.append(f"P{_p}  {leg}  <- {attribute(leg, idx)}")
        # B2851 (owner-caught): the boolean's defining condition belongs IN
        # the Formula, not behind an evidence pointer.
        L.append(f"       DEFN: {LEG_DEFN.get(leg, 'read the producer source (evidence column)')}")
        L.append(f"       {note}")
    L += ["", "============================== STRATEGY LAYER ==============================", ""]
    for key, op, prod in sorted(set(comparisons)):
        _p += 1
        L.append(f"P{_p}  {key} {op} {_fmt(prod)}   [EXISTING-THRESHOLD]")
    for h in helpers:
        _p += 1
        L.append(f"P{_p}  {h}(s)   [helper gate]")
    for k in STRATEGY_EXTRAS.get(name, []):
        _p += 1
        L.append(f"P{_p}  {k['param']}   [local-variable gate]")
    L += ["", "Gate body, VERBATIM from backtest/signals/screener.py "
          f"strat_{name} (docstring and return dropped):", "",
          "```python", body or "(no body extracted)", "```", "",
         "## Table A - parameter inventory (canonical shape - READY FOR OWNER BAND REVIEW)",
         "",
         "One row per parameter the entry condition touches, BOTH layers, nothing",
         "omitted (L785: an axis left out of Table A is invisible at close).",
         "Every producer row carries its DEFINED BANDS in the P<n>.x rows beneath",
         "it (B2845, owner-corrected: a ready and FINAL Table A per strategy);",
         "the engine-spec (SPECS) entry is built from these before any engine",
         "leg runs.", "",
         "| id | layer | producer / parameter | what it does | production | band VALUES | free_band (OFFLINE) | resim_band (RESIM) | status |",
         "|---|---|---|---|---|---|---|---|---|"]
    axes = []   # (id, param, n_levels, subset_safe, actuated) - footer
    pid = 0
    for leg in legs:
        pid += 1
        # B2840: a boolean's UNDERLYING condition is bandable (owner point).
        # OFFLINE only where its input magnitudes are persisted on the fires;
        # a variant needing unpersisted bars is RESIM by construction.
        L.append(f"| P{pid} | PRODUCER | {leg} - emitted by {attribute(leg, idx)}; "
                 f"the boolean's UNDERLYING condition is bandable through its "
                 f"producer's internals | {LEG_DEFN.get(leg, 'see evidence')} "
                 f"| leg required True | - (knobs below) | only where the "
                 f"condition's input magnitudes are persisted on the fires - "
                 f"else none | variants over unpersisted bars/inputs - RESIM; "
                 f"a shared producer's resim runs the FULL OPEN consumer set "
                 f"and its one cube is graded per consumer (runbook section 4.3 - results "
                 f"reused by construction); "
                 f"knobs {'in the SPECS entry' if in_specs else ('DEFINED below (P' + str(pid) + '.x)' if PRODUCER_BANDS.get(leg) else 'to define')} | "
                 f"{'SPECS-REGISTERED' if in_specs else ('BANDS-DEFINED' if PRODUCER_BANDS.get(leg) else 'BANDS-TO-DEFINE')} |")
        L += _band_rows(pid, leg, PRODUCER_BANDS.get(leg, []), axes, reads=_reads)
    for key, op, prod in sorted(set(comparisons)):
        pid += 1
        _kind, _ser = series.get(key, ("missing", None))
        _nfree = 0
        if _kind == "numeric":
            _qs = sorted(set(round(float(q), 4) for q in _ser.quantile(QUANTS)))
            _hi = op in (">", ">=")
            _nfree = sum(1 for lv in _qs if (lv > prod if _hi else lv < prod))
        axes.append(_axis(f"P{pid}", f"{key} {op} {_fmt(prod)}", _nfree + 1,
                          True, True, None, (1, _nfree, 0)))
        L.append(f"| P{pid} | STRATEGY | {key} `{op} {_fmt(prod)}` "
                 f"[EXISTING-THRESHOLD] | {LEG_DEFN.get(key, 'gate threshold on the persisted magnitude')} "
                 f"| `{op} {_fmt(prod)}` | production + {_nfree} tighter measured levels | "
                 f"{_offline_cell([(_nfree + 1, 1, _nfree, 0)], 'measured tighter QUANTS levels - see the free-band section below')}"
                 f" | looser side "
                 f"- band at R1 | MEASURED-PRE-R1 |")
        L += _band_rows(pid, key, PRODUCER_BANDS.get(key, []), axes, reads=_reads)
    for h in helpers:
        pid += 1
        if h == "_short_borrow_trap_active":
            # B2840 (owner question): a boolean's UNDERLYING condition is
            # bandable, and this shared helper's is days_to_cover > 5.0
            # (screener.py) with days_to_cover PERSISTED - so the tighter
            # side is offline TODAY. The 5.0 is an owner-ruled risk guard
            # (B718a, GME pre-squeeze calibration) shared across the
            # strategies that call it: any band is per-strategy-override
            # scope, on the owner's word only. L941 (B3139q-r75): the cell
            # names no caller count and no universal - a population claim
            # typed into a cell is not derived (test_b3224b), and two
            # delegating shorts never call the helper (S6-B3226).
            axes.append(_axis(f"P{pid}", "days_to_cover cap 5.0", 1, False,
                              False, None, (1, 0, 0)))
            L.append(f"| P{pid} | STRATEGY-HELPER | {h}(s) - underlying "
                     f"condition: days_to_cover > 5.0 (blocks the fire) | "
                     f"blocks SHORT fires when days_to_cover > 5.0 (B718a) | "
                     f"cap 5.0 (B718a owner-ruled risk guard) | "
                     f"- (no band ruled) | "
                     f"{_offline_cell([(1, 1, 0, 0)], 'tighter = LOWER cap on persisted days_to_cover - OFFLINE subset', ' (no band ruled)')} "
                     f"| raising the cap admits engine-blocked fires - RESIM; "
                     f"shared helper (the short-side borrow gate the B744 "
                     f"lint checks for) so any band is a "
                     f"per-strategy override on the owner's word | "
                     f"BANDABLE-OWNER-GATED |")
            continue
        L.append(f"| P{pid} | STRATEGY-HELPER | {h}(s) - a helper gate; its "
                 f"internals are outside the source pattern (lower bound) | "
                 f"see the helper's own source | required | - | - | "
                 f"inspect before any engine leg | BANDS-TO-DEFINE |")
    for k in STRATEGY_EXTRAS.get(name, []):
        pid += 1
        # S6-B3228: an extras row is classed LEVEL BY LEVEL like every band
        # row (_band_rows) - its per-side list bands reach the footer, where
        # a prose band used to score n = 1 (production only)
        _cls = band_level_classes(k)
        _sub = str(k.get("offline", "")).startswith("TIGHTER")
        _env = k.get("env")
        if len(_cls) == 1:
            axes.append(_axis(f"P{pid}", k["param"][:40], _cls[0][0],
                              _axis_sub(_cls[0], _sub), bool(_env), _env,
                              _cls[0][1:]))
        else:
            for _ai, _c in enumerate(_cls, 1):
                axes.append(_axis(f"P{pid}.{_ai}", k["param"][:40], _c[0],
                                  _axis_sub(_c, _sub), bool(_env), _env,
                                  _c[1:]))
        L.append(f"| P{pid} | STRATEGY | {k['param']} - {k['evidence']} | "
                 f"{k['basis']} | {k['production']} | {k.get('band', '-')} | "
                 f"{_offline_cell(_cls, k.get('offline', '-'))} | "
                 f"{k.get('resim', '-')} | T3 review |")
    L += ["| B-rows | BREADTH | every companion in the B-row candidate census "
          "below is Table A inventory once REGISTERED at the T3 band review "
          "(runbook section 3.6; B-rows are Table A members by owner ruling) | AND-leg "
          "companions on persisted keys | - | census levels below | census "
          "levels below | sub-floor / unpersisted producers | CANDIDATE |",
          "",
          "### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]",
          "",
          "Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine",
          "hours). Looser side = RESIM (engine) by construction - a looser level admits",
          "bars the cube never recorded. Levels are QUANTS quantiles "
          f"{list(QUANTS)} of the key's values on the surviving fires; only levels",
          "STRICTLY tighter than production enter the free band.", "",
         "| key | source (module writing the key) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |",
         "|---|---|---|---|---|---|"]
    for key, op, prod in sorted(set(comparisons)):
        kind, ser = series.get(key, ("missing", pd.Series(dtype=float)))
        if kind != "numeric":
            L.append(f"| {key} | {attribute(key, idx)} | `{op} {_fmt(prod)}` | "
                     f"NOT NUMERIC ON FIRES ({kind}) | - | engine-only |")
            continue
        cov = ser.notna().mean()
        qs = sorted(set(round(float(q), 4) for q in ser.quantile(QUANTS)))
        tighter_hi = op in (">", ">=")          # tighter = RAISE the floor
        cells = []
        for lv in qs:
            tighter = lv > prod if tighter_hi else lv < prod
            if not tighter:
                continue
            kept = int((ser >= lv).sum() if tighter_hi else (ser <= lv).sum())
            cells.append(f"{_fmt(lv)} -> {kept} ({kept / n_all:.0%})")
        # B2843 (owner question "are we raising the threshold or making it
        # tighter?"): say the direction in words, per row, both sides.
        tdir = ("TIGHTER = RAISE the floor: " if tighter_hi
                else "TIGHTER = LOWER the ceiling: ")
        free = tdir + ("; ".join(cells) if cells else
                       "(no QUANTS level sits tighter than production - band at T3)")
        loose = ("LOOSER = " + ("LOWER" if tighter_hi else "RAISE") +
                 " the threshold: RESIM - band from the SPECS entry"
                 + ("" if name in specs_names else " (to be built)"))
        L.append(f"| {key} | {attribute(key, idx)} | `{op} {_fmt(prod)}` | "
                 f"{cov:.1%} | {free} | {loose} |")

    # ---- breadth ----------------------------------------------------------
    L += ["",
          "### B-row candidate census - companion producers persisted on the fires [NEW-GATE]",
          "",
          "**Every row here is a NEW-GATE** (standing owner rule 2026-08-10): adding a",
          "companion threshold is an AND-leg the strategy does not currently have -",
          "**no grid runs before the T3 owner band review words the band**. All",
          f"companion levels are OFFLINE (subset selection). Coverage floor {MIN_COVERAGE}",
          "(breadth_step1_grid.MIN_COVERAGE); keys below it are listed at the bottom as",
          "RESIM-ONLY - offline grading would silently drop their absent rows.", "",
          "| key | source (module writing the key) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |",
          "|---|---|---|---|---|---|---|"]
    priced, proxy = price_denominated(series)
    low_cov, binaries = [], []
    census_n = 0   # B-row candidate axes counted for the factorial footer
    for key, (kind, ser) in series.items():
        if key in depth_keys or key in priced:
            continue
        if kind == "binary":
            rate = pd.Series([v for v in ser if v is not None]).mean()
            if 0.0 < rate < 1.0:
                binaries.append((key, rate))
            continue
        cov = ser.notna().mean()
        if ser.nunique(dropna=True) <= 1:
            continue
        if cov < MIN_COVERAGE:
            low_cov.append((key, cov))
            continue
        qs = sorted(set(round(float(q), 4) for q in ser.quantile(QUANTS)))
        hi = "; ".join(f"{_fmt(lv)}: {int((ser >= lv).sum())} "
                       f"({int((ser >= lv).sum()) / n_all:.0%})" for lv in qs)
        lo = "; ".join(f"{_fmt(lv)}: {int((ser <= lv).sum())} "
                       f"({int((ser <= lv).sum()) / n_all:.0%})" for lv in qs)
        L.append(f"| {key} | {attribute(key, idx)} | {cov:.1%} | "
                 f"{', '.join(_fmt(q) for q in qs)} | {hi} | {lo} | OFFLINE |")
        census_n += 1
    L += ["", "### Binary companions (offline AND-able; no band - a boolean has no threshold)", ""]
    if binaries:
        L += ["| key | fire-rate on surviving fires |", "|---|---|"] + [
            f"| {k} | {r:.1%} |" for k, r in sorted(binaries)]
    else:
        L.append("(none with a non-degenerate rate)")
    census_n += len(binaries)
    L += ["", f"### Below the {MIN_COVERAGE} coverage floor - RESIM-ONLY", ""]
    if low_cov:
        L += ["| key | coverage |", "|---|---|"] + [
            f"| {k} | {c:.1%} |" for k, c in sorted(low_cov)]
    else:
        L.append("(none)")
    L += ["",
          f"### Price-denominated keys - EXCLUDED from banding (|Spearman| >= {_PRICE_RHO} vs proxy `{proxy}`)",
          "",
          "A cross-sectional threshold on an absolute price level selects by SHARE",
          "PRICE, not by signal state. Usable only as a RATIO to price - which is",
          "producer work, i.e. RESIM, never an offline band.", ""]
    if priced:
        L.append(", ".join(f"`{k}` ({r})" for k, r in sorted(priced.items())))
    else:
        L.append("(none)")
    L += ["",
          "**Boundary (runbook section 4.3):** a producer with NO key in signals_at_entry is",
          "invisible to this table and to every offline instrument - genuinely new",
          "breadth producers are an engine-side design act, never an offline sweep.", ""]

    # B2851 (owner-caught): the locked standard's FACTORIAL, computed from
    # THIS table's axes (plan:1211 - computed, never hand-counted), paired
    # with the Formula section above (B1523: never shown apart).
    import math
    # S6-B3120h: ONE physical knob can back SEVERAL P-rows - STRAT_EMA_SPAN
    # drives BOTH the below_ema_200 (short leg) and price_above_ema_200 (long
    # leg) rows, per the SPECS bollinger_lower tools block ("ONE engine axis").
    # Counting each row as its own factor squared the span axis (8 -> 64) for
    # one env value. An env-actuated axis therefore counts ONCE per env name;
    # every duplicate row still renders, marked as sharing its knob.
    _seen_env: dict[str, str] = {}
    eff, shared = [], {}
    for t in axes:
        aid, envn = t[0], t[5]
        if envn and envn in _seen_env:
            shared[aid] = (envn, _seen_env[envn])
            continue
        if envn:
            _seen_env[envn] = aid
        eff.append(t)
    fact = math.prod(t[2] for t in eff) if eff else 0
    # S6-B3189: the footer's figures are COUNTS of level-combinations that
    # partition FULL FACTORIAL additively - engine runs + offline gradings +
    # pending = full. They used to be multiplication FACTORS printed under
    # count labels: PENDING printed 1 with nothing pending (the empty product)
    # in 3 of 38 files, and with more than one engine run the offline figure
    # was per run (16 of 38). An axis holding offline AND pending levels
    # cannot be a product of bucket factors at all, so the partition is a sum.
    runs = math.prod(t[6] for t in eff) if eff else 0
    grad = math.prod(t[6] + t[7] for t in eff) if eff else 0
    # pending is counted from n MINUS each axis's pending levels, never as
    # fact - grad: that way the identity asserted below can fail, exactly when
    # some axis's three classes do not add up to its n.
    pend = fact - (math.prod(t[2] - t[8] for t in eff) if eff else 0)
    offl = grad - runs
    # THREE buckets, not two (S6-B2862). A fire-adding axis whose env actuator
    # does not exist cannot be run, so counting it in ENGINE RUNS would promise
    # engine hours for a band that is DEFINED but not IMPLEMENTED - state 1 of
    # the four-state workflow in runbook section 2.3. The old code got this right only
    # by accident: a prose band scored n=1, and n==1 was read as "no actuator".
    # S6-B2862: the rendered line here used to read "check {runs} x {free} =
    # {runs*free}". Every axis is in exactly ONE of the two buckets, so that
    # product equals FULL FACTORIAL identically - MEASURED, the "check" line
    # matched its own factorial on 40 of 40 files. A check that cannot fail is
    # decoration, and it reads to a non-author as "someone verified this".
    # The invariant it gestured at is real, so it becomes an ASSERT (which can
    # stop the build), and the rendered line becomes a cost the owner can act
    # on. Per-run and cap figures: plan:861 and the B2107 owner ruling.
    _STEP1_H = 3.66
    _CAP_H = 5
    assert fact == runs + offl + pend, (
        "axis partition broken: engine, offline and pending levels must "
        "partition every axis (S6-B3189) "
        f"(fact={fact} runs={runs} offline={offl} pending={pend})")
    L += ["## Factorial - configs this table implies (computed from the "
          "rows above; pairs with the Formula in Section 1)", "",
          "| axis | parameter | n levels | class | own engine run? "
          "| engine | offline | pending |",
          "|---|---|---|---|---|---|---|---|"]
    for t in axes:
        aid, prm, n, sub, act = t[:5]
        eng, off, pnd = t[6], t[7], t[8]
        # S6-B3189: an axis whose levels fall in more than one class is MIXED
        # and says which classes; a pure axis keeps its old words.
        _kinds = [w for w, x in (("offline", off), ("engine", eng - 1),
                                 ("pending", pnd)) if x > 0]
        if len(_kinds) > 1:
            cls = "MIXED - " + " AND ".join(_kinds) + " levels"
        else:
            cls = "subset-safe" if sub else "**FIRE-ADDING**"
        if aid in shared:
            _e, _first = shared[aid]
            need = f"shares env {_e} with {_first} - ONE knob, counted once"
            cols = "- | - | -"
        else:
            if len(_kinds) > 1:
                need = (("**YES**" if eng > 1 else "no - production only")
                        + (f"; {off} offline" if off else "")
                        + (f"; {pnd} pending (DEFINED-NO-ACTUATOR)" if pnd
                           else ""))
            else:
                need = "no - derives offline" if sub else \
                    ("no - production only (DEFINED-NO-ACTUATOR)" if not act
                     else "**YES**")
            cols = f"{eng} | {off} | {pnd}"
        L.append(f"| {aid} | {prm} | {n} | {cls} | {need} | {cols} |")
    expr = " x ".join(str(t[2]) for t in eff) or "0"
    L += ["", "```",
          f"FULL FACTORIAL     {expr} = {fact}",
          f"offline gradings   {offl} level-combinations x 24 exits = "
          f"{offl * 24} (graded from the engine runs' cubes, never run "
          "themselves)",
          f"ENGINE RUNS        {runs} (per axis: the production level plus "
          "any actuated non-production level)",
          f"PENDING ACTUATION  {pend} level-combinations need an env knob "
          "that does not exist - a FEATURE REQUEST, not a runnable band "
          "(runbook section 2.3 state 1; B2866)",
          f"TILING             {runs} + {offl} + {pend} = {fact} (engine + "
          "offline + pending: every level of every axis sits in exactly one "
          "class - the three count columns above; S6-B3189)",
          f"STEP-1 SERIAL COST {runs} x {_STEP1_H} h = {runs * _STEP1_H:,.0f} h "
          f"at the ruled 1y x 200-ticker shape",
          f"                   per-run {_STEP1_H} h is within the {_CAP_H} h "
          "local cap (B2107); the TOTAL is not a plan until the owner rules a "
          "budget on it",
          "```", "",
          f"B-row candidates NOT in this factorial: {census_n} census axes "
          "join it only when REGISTERED at the T3 band review.", ""]
    return "\n".join(L)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default="TIGHTEN", choices=("TIGHTEN", "BOTH"))
    ap.add_argument("--subdir", default=None,
                    help="output folder under strategy_optimisation/ (default: the lane name; owner-directed tighten/both for the BOTH wave)")
    # C15 (B2852, owner-approved): the preflight regenerate-and-diff gate
    # rebuilds into a temp root so a pre-commit check never writes the tree.
    ap.add_argument("--out-root", default=None,
                    help="write under this root instead of strategy_optimisation/ (C15 regeneration)")
    # S6-B3232 (B3139q-r86): ONE named strategy to ONE named file, for a
    # campaign outside the TIGHTEN/BOTH charter (a NONE-lane breadth
    # candidate); never writes the charter folders
    ap.add_argument("--strategy", default=None,
                    help="render one strategy whatever its lane; needs --out")
    ap.add_argument("--out", default=None,
                    help="with --strategy: the file to write")
    a = ap.parse_args()

    view = json.loads(STATUS_JSON.read_text(encoding="utf-8"))
    if bool(a.strategy) != bool(a.out):
        raise SystemExit("REFUSED: --strategy and --out go together (S6-B3232)")
    if a.strategy:
        rows = [r for r in view["rows"] if r["strategy"] == a.strategy]
        if not rows:
            raise SystemExit(f"REFUSED: {a.strategy} is not in the status view")
        if rows[0]["stream"] in ("TIGHTEN", "BOTH"):
            raise SystemExit(f"REFUSED: {a.strategy} is a {rows[0]['stream']} row - its "
                             "Table A is the lane charter's; regenerate that lane")
    else:
        rows = [r for r in view["rows"] if r["stream"] == a.lane]
    if not rows:
        raise SystemExit(f"REFUSED: no {a.lane} rows in the status view")
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                             capture_output=True, text=True,
                             timeout=15).stdout.strip() or "unknown"
    except Exception:
        sha = "unknown"
    stamp = (f"**Build (L803/#309):** generator scripts/build_table_a.py | cube "
             f"{bss.R5_DIR.name} | status build {view['build']['source_commit']} | "
             f"commit {sha} at {time.strftime('%Y-%m-%d %H:%M:%S')} - a copy "
             f"without this line, or with a stale stamp, is NOT the current band set")

    src = (ROOT / "backtest" / "signals" / "screener.py").read_text(
        encoding="utf-8", errors="replace")
    comps = depth_comparisons(src)
    legs = gate_legs(src)
    bodies = gate_bodies(src)
    idx = _module_index()
    try:
        # B2850: PHASE0 entries are validated inventories awaiting their
        # first engine campaign (battery adapters come with it, L754) -
        # REGISTERED for Table A purposes, same as full SPECS families.
        from producer_variant_table import SPECS, SPECS_PHASE0
        specs_names = set(SPECS) | set(SPECS_PHASE0)
    except Exception:
        specs_names = set()

    tl = pd.read_csv(bss.R5_DIR / "trade_log.csv", low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "direction",
                              "signals_at_entry"])
    tl = tl.drop_duplicates(["strategy", "ticker", "entry_date"])

    out_base = Path(a.out_root) if a.out_root else OUT_DIR
    sub = (Path(a.out).parent if a.strategy
           else out_base / (a.subdir if a.subdir else a.lane.lower()))
    sub.mkdir(parents=True, exist_ok=True)
    written = []
    for r in sorted(rows, key=lambda x: -x["projected_current_gate"]):
        name = r["strategy"]
        frame = tl[tl["strategy"] == name]
        if frame.empty:
            raise SystemExit(f"REFUSED: no R5 fires for {name} (fail closed)")
        kept, sigs, filtered = surviving_fires(name, frame, r["survives_pct"],
                                               r.get("unmeasured_gate_keys"))
        md = render(name, r, kept, sigs, filtered, comps.get(name, []),
                    legs.get(name, ([], [])), idx, specs_names, stamp,
                    body=bodies.get(name, ""))
        p = Path(a.out) if a.strategy else sub / f"{name}.md"
        p.write_text(md, encoding="utf-8", newline="\n")
        written.append(p)
        _rel = p.relative_to(ROOT) if p.is_relative_to(ROOT) else p
        print(f"  wrote {_rel}  (fires {len(frame)} -> {len(kept)})")
    _srel = sub.relative_to(ROOT) if sub.is_relative_to(ROOT) else sub
    print(f"{len(written)} Table A file(s) under {_srel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
