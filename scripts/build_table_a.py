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
engine-only by construction (plan 11.2s) and no offline table can enumerate
them. The depth extraction is the builder's source pattern - a LOWER BOUND
(thresholds via helpers or config constants are invisible).

Module attribution is a literal grep of the key name across backtest/signals,
backtest/data and backtest/engine - a heuristic, labelled as such per file.
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
from table_a_bands import PRODUCER_BANDS, STRATEGY_EXTRAS  # noqa: E402

# B2841: one numeric-compare pattern for BOTH extractors. The first cut used
# [^)]* for the s.get(...) argument span, which cannot cross the ')' of a
# nested call - so a default like float('-inf') broke the match and TWO LIVE
# production gates were missing from Table A depth (cmf_flip's
# po3_accum_range_pct >= 0.0458, pairs_short's ppo_signal >= -0.858). One
# nested-paren level is now allowed.
_NUM_CMP = (r"s\.get\(f?['\"]([a-z0-9_{}]+)['\"]"
            r"(?:[^()]|\([^()]*\))*\)\s*([<>]=?)\s*(-?[0-9.]+)")

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
            out[n.name[len("strat_"):]] = [(k, op, float(v)) for k, op, v in rows]
    return out


def gate_legs(src: str) -> dict:
    """(strategy) -> (boolean_legs, helper_gates): the NON-numeric members of
    the entry condition. B2838, owner-caught: the first render's depth table
    held only numeric-literal gates, so a strategy like three_black_crows_short
    showed ONE row while its gate reads a candle-pattern PRODUCER boolean and a
    borrow-trap helper - and an axis left out of Table A is invisible at close
    (L785). Boolean legs carry their tunables in the PRODUCER layer; those
    knobs are inventoried at R1 (the SPECS entry), so the pre-R1 row marks
    them INVENTORY-PENDING-R1 rather than omitting them. Helper-gate detection
    is a source pattern - a lower bound, like every extraction here.
    """
    out = {}
    for n in ast.walk(ast.parse(src)):
        if not (isinstance(n, ast.FunctionDef) and n.name.startswith("strat_")):
            continue
        body = ast.unparse(n)
        all_keys = re.findall(r"s\.get\(f?['\"]([a-z0-9_{}]+)['\"]", body)
        numeric = {k for k, _, _ in re.findall(_NUM_CMP, body)}
        legs = sorted({k for k in all_keys if k not in numeric})
        # left boundary required: without it the DEF SIGNATURE's own name
        # matched ("...crows_short(s)" yielded a phantom helper _crows_short)
        helpers = sorted(set(re.findall(
            r"(?<![a-z0-9_])(_[a-z0-9_]+)\(s[,)]", body)) - {"_strat", "_strat3"})
        out[n.name[len("strat_"):]] = (legs, helpers)
    return out


def _module_index() -> list[tuple[str, str]]:
    idx = []
    for d in _ATTR_DIRS:
        for p in sorted((ROOT / d).glob("*.py")):
            try:
                idx.append((f"{d}/{p.name}",
                            p.read_text(encoding="utf-8", errors="replace")))
            except OSError:
                continue
    return idx


def attribute(key: str, idx) -> str:
    hits = [name for name, text in idx
            if f'"{key}"' in text or f"'{key}'" in text]
    if not hits:
        return "(not found by literal grep)"
    extra = f" +{len(hits) - 1}" if len(hits) > 1 else ""
    return hits[0] + extra


def surviving_fires(name: str, frame: pd.DataFrame, survives_pct):
    """The T1 filter, reproduced from the builder's survival path: keep a fire
    iff the LIVE strategy function fires with the recorded direction on its
    persisted signals. Identity (skipped) when the view says survives == 1.0."""
    sigs = [bss._parse_signals(x) for x in frame["signals_at_entry"]]
    if survives_pct is None or survives_pct >= 1.0:
        return frame, sigs, False
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



def _band_rows(pid: int, subject: str, knobs) -> list:
    """B2841: the R1 band definitions (table_a_bands.py) as sub-rows under a
    P-row. env None on a resim-bearing knob renders DEFINED-NO-ACTUATOR - the
    band exists, the engine plumbing is follow-up (validate_spec refuses an
    actuatorless resim level, S6-B2569a)."""
    out = []
    for j, k in enumerate(knobs, 1):
        env = k.get("env")
        resim = k.get("resim", "-")
        needs_act = resim not in ("-", "", None) and "none" not in str(resim).lower()[:4]
        act = ("" if not needs_act else
               (f"; env {env}" if env else "; DEFINED-NO-ACTUATOR"))
        out.append(
            f"| P{pid}.{j} | BAND | {k['param']} - {k['evidence']} | "
            f"{k['production']} | {k.get('offline', '-')} | {resim}{act} | "
            f"{k['basis']}; T3 review before any grid |")
    return out

def render(name: str, row: dict, frame, sigs, filtered: bool,
           comparisons, legs_helpers, idx, specs_names, stamp: str) -> str:
    n_all = len(frame)
    series = key_series(sigs)
    depth_keys = sorted({k for k, _, _ in comparisons})
    legs, helpers = legs_helpers
    in_specs = name in specs_names
    L = [f"# Table A - {name}", "",
         stamp, "",
         f"**Lane:** {row['stream']} | **family:** {row['family']} | "
         f"**status:** {row['status']} | **R5 fires:** {row['r5_fires']} | "
         f"**surviving fires (T1):** {n_all}"
         + (f" (survives_pct {row['survives_pct']})" if filtered else
            " (unchanged since R5 - filter is identity)"),
         "",
         f"**SPECS entry:** {'registered in producer_variant_table' if in_specs else 'NONE - build at R1 before any engine leg (W-T T0)'}",
         "",
         "## Table A - parameter inventory (the SS6 canonical shape, pre-R1)",
         "",
         "One row per parameter the entry condition touches, BOTH layers, nothing",
         "omitted (L785: an axis left out of Table A is invisible at close). The",
         "R1 SPECS entry absorbs and supersedes this pre-R1 inventory - producer",
         "knob rows below are placeholders it must fill.", "",
         "| id | layer | producer / parameter | production | free_band (OFFLINE) | resim_band (RESIM) | status |",
         "|---|---|---|---|---|---|---|"]
    pid = 0
    for leg in legs:
        pid += 1
        # B2840: a boolean's UNDERLYING condition is bandable (owner point).
        # OFFLINE only where its input magnitudes are persisted on the fires;
        # a variant needing unpersisted bars is RESIM by construction.
        L.append(f"| P{pid} | PRODUCER | {leg} - emitted by {attribute(leg, idx)}; "
                 f"the boolean's UNDERLYING condition is bandable through its "
                 f"producer's internals | leg required True | only where the "
                 f"condition's input magnitudes are persisted on the fires - "
                 f"else none | variants over unpersisted bars/inputs - RESIM; "
                 f"a shared producer's resim runs the FULL OPEN consumer set "
                 f"and its one cube is graded per consumer (11.2s - results "
                 f"reused by construction); "
                 f"knobs {'in the SPECS entry' if in_specs else 'INVENTORY-PENDING-R1 (SPECS)'} | "
                 f"{'SPECS-REGISTERED' if in_specs else 'INVENTORY-PENDING-R1'} |")
        L += _band_rows(pid, leg, PRODUCER_BANDS.get(leg, []))
    for key, op, prod in sorted(set(comparisons)):
        pid += 1
        L.append(f"| P{pid} | STRATEGY | {key} `{op} {_fmt(prod)}` "
                 f"[EXISTING-THRESHOLD] | `{op} {_fmt(prod)}` | measured tighter "
                 f"QUANTS levels - see the free-band section below | looser side "
                 f"- band at R1 | MEASURED-PRE-R1 |")
        L += _band_rows(pid, key, PRODUCER_BANDS.get(key, []))
    for h in helpers:
        pid += 1
        if h == "_short_borrow_trap_active":
            # B2840 (owner question): a boolean's UNDERLYING condition is
            # bandable, and this shared helper's is days_to_cover > 5.0
            # (screener.py) with days_to_cover PERSISTED - so the tighter
            # side is offline TODAY. The 5.0 is an owner-ruled risk guard
            # (B718a, GME pre-squeeze calibration) shared by every short
            # strategy: any band is per-strategy-override scope, on the
            # owner's word only.
            L.append(f"| P{pid} | STRATEGY-HELPER | {h}(s) - underlying "
                     f"condition: days_to_cover > 5.0 (blocks the fire) | "
                     f"cap 5.0 (B718a owner-ruled risk guard) | tighter = "
                     f"LOWER cap on persisted days_to_cover - OFFLINE subset "
                     f"| raising the cap admits engine-blocked fires - RESIM; "
                     f"shared helper (6 consumers) so any band is a "
                     f"per-strategy override on the owner's word | "
                     f"BANDABLE-OWNER-GATED |")
            continue
        L.append(f"| P{pid} | STRATEGY-HELPER | {h}(s) - a helper gate; its "
                 f"internals are outside the source pattern (lower bound) | "
                 f"required | - | inspect at R1 | INVENTORY-PENDING-R1 |")
    for k in STRATEGY_EXTRAS.get(name, []):
        pid += 1
        L.append(f"| P{pid} | STRATEGY | {k['param']} - {k['evidence']} | "
                 f"{k['production']} | {k.get('offline', '-')} | "
                 f"{k.get('resim', '-')} | {k['basis']}; T3 review |")
    L += ["| B-rows | BREADTH | every companion in the B-row candidate census "
          "below is Table A inventory once REGISTERED at the T3 band review "
          "(11.2b3; B-rows are Table A members by owner ruling) | - | census "
          "levels below | sub-floor / unpersisted producers | CANDIDATE |",
          "",
          "### Measured free-band levels - the STRATEGY-layer inputs [EXISTING-THRESHOLD]",
          "",
          "Tighter side = OFFLINE free_band (a SUBSET of the recorded fires, zero engine",
          "hours). Looser side = RESIM (engine) by construction - a looser level admits",
          "bars the cube never recorded. Levels are QUANTS quantiles "
          f"{list(QUANTS)} of the key's values on the surviving fires; only levels",
          "STRICTLY tighter than production enter the free band.", "",
         "| key | source (literal grep) | gate | coverage | OFFLINE free_band: level -> retained (n, %) | RESIM side |",
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
          "| key | source (literal grep) | coverage | levels (QUANTS on fires) | keep >= level (n, %) | keep <= level (n, %) | mark |",
          "|---|---|---|---|---|---|---|"]
    priced, proxy = price_denominated(series)
    low_cov, binaries = [], []
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
    L += ["", "### Binary companions (offline AND-able; no band - a boolean has no threshold)", ""]
    if binaries:
        L += ["| key | fire-rate on surviving fires |", "|---|---|"] + [
            f"| {k} | {r:.1%} |" for k, r in sorted(binaries)]
    else:
        L.append("(none with a non-degenerate rate)")
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
          "**Boundary (plan 11.2s):** a producer with NO key in signals_at_entry is",
          "invisible to this table and to every offline instrument - genuinely new",
          "breadth producers are an engine-side design act, never an offline sweep.", ""]
    return "\n".join(L)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default="TIGHTEN", choices=("TIGHTEN", "BOTH"))
    a = ap.parse_args()

    view = json.loads(STATUS_JSON.read_text(encoding="utf-8"))
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
    idx = _module_index()
    try:
        from producer_variant_table import SPECS
        specs_names = set(SPECS)
    except Exception:
        specs_names = set()

    tl = pd.read_csv(bss.R5_DIR / "trade_log.csv", low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "direction",
                              "signals_at_entry"])
    tl = tl.drop_duplicates(["strategy", "ticker", "entry_date"])

    sub = OUT_DIR / a.lane.lower()
    sub.mkdir(parents=True, exist_ok=True)
    written = []
    for r in sorted(rows, key=lambda x: -x["projected_current_gate"]):
        name = r["strategy"]
        frame = tl[tl["strategy"] == name]
        if frame.empty:
            raise SystemExit(f"REFUSED: no R5 fires for {name} (fail closed)")
        kept, sigs, filtered = surviving_fires(name, frame, r["survives_pct"])
        md = render(name, r, kept, sigs, filtered, comps.get(name, []),
                    legs.get(name, ([], [])), idx, specs_names, stamp)
        p = sub / f"{name}.md"
        p.write_text(md, encoding="utf-8", newline="\n")
        written.append(p)
        print(f"  wrote {p.relative_to(ROOT)}  (fires {len(frame)} -> {len(kept)})")
    print(f"{len(written)} Table A file(s) under {sub.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
