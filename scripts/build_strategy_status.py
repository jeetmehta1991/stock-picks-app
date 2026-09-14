#!/usr/bin/env python
"""S6-B2808 (owner-approved 2026-09-13): the per-strategy optimisation STATUS
view - the file that answers "has strategy X been optimised, and which stream
does it belong to" without a four-way hand-join.

WHY IT EXISTS. L802: I ranked six strategies as "do these first" and two were
already ADMITTED, because my screen tested three properties of the STRATEGY and
zero properties of the LEDGER. The filter was not forgotten - it was
unavailable. Answering that question needed joining STRATEGY_ROSTER.md (no
per-strategy status), PHASE_1B_ROSTER.md (only what PASSED), the admissions JSON
(14 rows) and EXECUTION_QUEUE.md (keyed by TICKET, so it cannot be asked about a
STRATEGY). This joins them once, mechanically, and regenerates.

THE COLUMNS, and what each is derived FROM - every one is a read, none is a
judgement:
  strategy          screener.ALL_STRATEGIES
  family            the category argument declared in the strategy's own
                    _strat/_strat3 call; strategies whose call does not carry
                    one are reported as "-" rather than guessed
  r5_fires          distinct (ticker, entry_date) rows in the R5 trade log
  changed_since_r5  AST diff of the strat_ function against the R5-era screener
  survives_pct      share of R5 fires still satisfying the CURRENT condition -
                    only computable where a rule is registered (see CURRENT_RULES)
  stream            TIGHTEN / LOOSEN / BOTH / NONE - see classify_stream
  ticket            campaign tickets naming this strategy in EXECUTION_QUEUE.md
  admitted          present in phase_1b_step2_admissions.json
  status            DONE-ADMITTED / IN-CAMPAIGN / NOT-STARTED

STREAM IS THE HONEST PART, so its rule is stated rather than implied:
  TIGHTEN  the entry condition compares a signal to a NUMBER and that magnitude
           is persisted in signals_at_entry -> a tighter level is a SUBSET of
           the recorded fires and costs ZERO engine hours (plan 11.2b).
  LOOSEN   no tightenable persisted magnitude, OR the strategy is fire-starved
           under its current condition (< MIN_FIRES_FOR_GRID projected at the
           Step-1 shape) so the productive direction is a looser producer band -
           an ENGINE resim, since a looser level admits bars the cube never
           recorded (plan 11.2b2b, DEPTH is Priority 1).
  BOTH     tightenable AND fire-starved.
  NONE     neither - no numeric knob and not fire-starved; a candidate for
           BREADTH (companion axes) rather than depth.

A strategy is never marked TIGHTEN on an unpersisted magnitude: the coverage is
measured per key, and a key below COVERAGE_FLOOR is not counted.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

R5_DIR = ROOT / "output_r5_merged_1_7"
ADMISSIONS = ROOT / "output_audit" / "phase_1b_step2_admissions.json"
QUEUE = ROOT / "EXECUTION_QUEUE.md"
# the screener as it stood when the R5 cube was produced (trade_log 2026-07-24)
R5_SCREENER_COMMIT = "fee970996"

COVERAGE_FLOOR = 0.98          # a magnitude present on fewer rows is not usable
STEP1_TICKERS = 200            # the plan's Step-1 shape
STEP1_YEARS = 1
R5_UNIVERSE = 544
R5_SPAN_YEARS = 5
MIN_FIRES_FOR_GRID = 100       # below this a Step-1 grid cannot be populated

# Entry conditions re-expressed for the survival check. Only families whose rule
# has been READ go here - an unregistered strategy reports survives_pct as None
# rather than a guess (a wrong survival number is worse than no number, L802).
CURRENT_RULES = {
    "smc_liquidity_sweep_reversal": (
        ["smc_liquidity_swept_dn", "smc_liquidity_swept_up"],
        lambda s, d: _t(s, "smc_liquidity_swept_dn" if d == "long"
                        else "smc_liquidity_swept_up")
        and (_t(s, "smc_choch_bullish") or _t(s, "smc_bos_bullish")) if d == "long"
        else _t(s, "smc_liquidity_swept_up")
        and (_t(s, "smc_choch_bearish") or _t(s, "smc_bos_bearish"))),
    "turtle_soup_short": (
        ["smc_liquidity_swept_up", "smc_bos_bearish", "below_prev_high",
         "close_below_open"],
        lambda s, d: (_t(s, "smc_liquidity_swept_up") or _t(s, "smc_bos_bearish"))
        and _t(s, "below_prev_high") and _t(s, "close_below_open")),
}


def _t(sig: dict, key: str) -> bool:
    return sig.get(key) is True


def _parse_signals(raw):
    if not isinstance(raw, str) or not raw.strip():
        return {}
    for reader in (json.loads, ast.literal_eval):
        try:
            v = reader(raw)
        except (ValueError, SyntaxError, TypeError):
            continue
        if isinstance(v, dict):
            return v
    return {}


def declared_families(src: str) -> dict:
    """The category each strategy declares in its own _strat/_strat3 call.

    Direction literals ('long'/'short') are NOT categories - a signature that
    yields one means the pattern did not find the category argument, so the
    strategy is reported as '-' rather than mislabelled.
    """
    out = {}
    for n in ast.walk(ast.parse(src)):
        if not (isinstance(n, ast.FunctionDef) and n.name.startswith("strat_")):
            continue
        body = ast.unparse(n)
        m = re.search(r"_strat3?\((?:[^,]+,){1,2}\s*['\"]([a-z_]+)['\"]", body)
        fam = m.group(1) if m else None
        if fam in (None, "long", "short"):
            fam = "-"
        out[n.name[len("strat_"):]] = fam
    return out


def numeric_thresholds(src: str) -> dict:
    """Signal keys the entry condition compares to a NUMBER, per strategy.

    A LOWER BOUND by construction: a threshold reached through a helper, or
    compared against a config constant rather than a literal, is invisible to a
    source pattern. Stated in the artifact so the count is never read as total.
    """
    out = {}
    for n in ast.walk(ast.parse(src)):
        if not (isinstance(n, ast.FunctionDef) and n.name.startswith("strat_")):
            continue
        body = ast.unparse(n)
        keys = set(re.findall(
            r"s\.get\(f?['\"]([a-z0-9_{}]+)['\"][^)]*\)\s*[<>]=?\s*-?[0-9.]+", body))
        if keys:
            out[n.name[len("strat_"):]] = sorted(keys)
    return out


def changed_since_r5(src_now: str) -> set:
    """Strategies whose function body differs from the R5-era screener.

    UPPER BOUND on behavioural change - a rename or a configurable-span swap
    counts as changed (plan 11.2b4).
    """
    try:
        old = subprocess.run(
            ["git", "show", f"{R5_SCREENER_COMMIT}:backtest/signals/screener.py"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=60).stdout
    except Exception:
        return set()
    if not old.strip():
        return set()

    def funcs(s):
        return {n.name: ast.unparse(n) for n in ast.walk(ast.parse(s))
                if isinstance(n, ast.FunctionDef) and n.name.startswith("strat_")}
    a, b = funcs(old), funcs(src_now)
    return {k[len("strat_"):] for k in set(a) & set(b) if a[k] != b[k]}


def classify_stream(tightenable: bool, projected: float) -> str:
    starved = projected < MIN_FIRES_FOR_GRID
    if tightenable and starved:
        return "BOTH"
    if tightenable:
        return "TIGHTEN"
    if starved:
        return "LOOSEN"
    return "NONE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "STRATEGY_OPTIMISATION_STATUS.md"))
    ap.add_argument("--json", default=str(ROOT / "output_audit"
                                          / "strategy_optimisation_status.json"))
    a = ap.parse_args()

    from backtest.signals.screener import ALL_STRATEGIES
    src = (ROOT / "backtest" / "signals" / "screener.py").read_text(
        encoding="utf-8", errors="replace")
    fams = declared_families(src)
    thresholds = numeric_thresholds(src)
    changed = changed_since_r5(src)

    tl = pd.read_csv(R5_DIR / "trade_log.csv", low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "direction",
                              "signals_at_entry"])
    tl = tl.drop_duplicates(["strategy", "ticker", "entry_date"])
    by_strat = {k: v for k, v in tl.groupby("strategy")}

    admitted = set()
    if ADMISSIONS.exists():
        d = json.loads(ADMISSIONS.read_text(encoding="utf-8"))
        rows = d if isinstance(d, list) else d.get("admissions") or d.get("rows") or []
        admitted = {r.get("strategy") for r in rows
                    if isinstance(r, dict) and r.get("strategy")}

    qtext = QUEUE.read_text(encoding="utf-8", errors="replace") if QUEUE.exists() else ""

    recs = []
    for name in sorted(ALL_STRATEGIES):
        fam = fams.get(name, "-")
        frame = by_strat.get(name)
        fires = 0 if frame is None else len(frame)
        rate = fires / R5_UNIVERSE / R5_SPAN_YEARS if fires else 0.0
        projected = rate * STEP1_TICKERS * STEP1_YEARS

        # is any declared numeric threshold backed by a PERSISTED magnitude?
        keys = thresholds.get(name, [])
        tightenable, covered = False, {}
        if keys and frame is not None and fires:
            sigs = [_parse_signals(x) for x in frame["signals_at_entry"]]
            for k in keys:
                c = sum(1 for s in sigs
                        if isinstance(s.get(k), (int, float))
                        and not isinstance(s.get(k), bool)) / len(sigs)
                covered[k] = round(c, 4)
                if c >= COVERAGE_FLOOR:
                    tightenable = True

        survives = None
        rule = CURRENT_RULES.get(name)
        if rule and frame is not None and fires:
            _, fn = rule
            sigs = [_parse_signals(x) for x in frame["signals_at_entry"]]
            dirs = list(frame["direction"].values)
            survives = round(sum(1 for s, d in zip(sigs, dirs) if fn(s, d)) / fires, 4)

        tickets = sorted(set(re.findall(r"\*\*(S6-B\d+[a-z]?)\*\*[^|]*" + re.escape(name),
                                        qtext)))[:3]
        status = ("DONE-ADMITTED" if name in admitted
                  else "IN-CAMPAIGN" if tickets else "NOT-STARTED")
        recs.append({"strategy": name, "family": fam, "r5_fires": fires,
                     "changed_since_r5": name in changed,
                     "survives_pct": survives,
                     "projected_step1_fires": round(projected, 1),
                     "stream": classify_stream(tightenable, projected),
                     "tightenable_keys": covered, "tickets": tickets,
                     "admitted": name in admitted, "status": status})

    Path(a.json).write_text(json.dumps(
        {"generator": "scripts/build_strategy_status.py",
         "cube": str(R5_DIR), "r5_screener_commit": R5_SCREENER_COMMIT,
         "rules": {"coverage_floor": COVERAGE_FLOOR,
                   "min_fires_for_grid": MIN_FIRES_FOR_GRID,
                   "step1_shape": f"{STEP1_TICKERS} tickers x {STEP1_YEARS}y"},
         "caveats": [
             "changed_since_r5 is an UPPER BOUND - any code difference counts",
             "stream TIGHTEN rests on a source pattern for numeric comparisons, "
             "a LOWER BOUND - thresholds via a helper or a config constant are invisible",
             "survives_pct is populated only for strategies whose current rule is "
             "registered in CURRENT_RULES; None means UNMEASURED, never 100pct"],
         "rows": recs}, indent=2), encoding="utf-8")

    # ---- the markdown view -------------------------------------------------
    import collections
    bystream = collections.Counter(r["stream"] for r in recs)
    bystatus = collections.Counter(r["status"] for r in recs)
    todo = [r for r in recs if r["status"] != "DONE-ADMITTED"]
    famcount = collections.Counter(r["family"] for r in todo
                                   if r["stream"] in ("TIGHTEN", "BOTH"))

    L = ["<!-- AUTO-GENERATED by scripts/build_strategy_status.py (S6-B2808).",
         "     Do NOT hand-edit; regenerate. -->", "",
         "# STRATEGY OPTIMISATION STATUS - the per-strategy view", "",
         "**Why this file exists (L802).** Answering *has strategy X been optimised, and "
         "what stream is it in* previously required joining four sources by hand - the "
         "strategy roster (no per-strategy status), the Phase-1B roster (only what "
         "PASSED), the admissions JSON, and the queue (keyed by TICKET, so it cannot be "
         "asked about a STRATEGY). A ranking built without that join recommended a family "
         "that was already finished.", "",
         f"**Cube:** R5 ({R5_DIR.name}) | **R5-era screener:** {R5_SCREENER_COMMIT} | "
         f"**Step-1 shape:** {STEP1_TICKERS} tickers x {STEP1_YEARS}y | "
         f"**grid floor:** {MIN_FIRES_FOR_GRID} fires", "",
         "## Totals", "",
         "| | count |", "|---|---|",
         f"| registered strategies | {len(recs)} |",
         f"| DONE - admitted to Phase 1B | {bystatus.get('DONE-ADMITTED', 0)} |",
         f"| IN-CAMPAIGN - a ticket names it | {bystatus.get('IN-CAMPAIGN', 0)} |",
         f"| NOT-STARTED | {bystatus.get('NOT-STARTED', 0)} |", "",
         "## Stream - of the strategies NOT yet admitted", "",
         "| stream | meaning | count |", "|---|---|---|"]
    meanings = {
        "TIGHTEN": "a persisted magnitude can be tightened - OFFLINE, zero engine hours",
        "LOOSEN": "fire-starved at the current condition - needs a looser producer band, ENGINE",
        "BOTH": "tightenable AND fire-starved",
        "NONE": "no numeric knob and not starved - a BREADTH candidate"}
    tstream = collections.Counter(r["stream"] for r in todo)
    for k in ("TIGHTEN", "BOTH", "LOOSEN", "NONE"):
        L.append(f"| {k} | {meanings[k]} | {tstream.get(k, 0)} |")
    L += ["", "## Tightening candidates by family - largest families first", "",
          "| family | strategies to tighten |", "|---|---|"]
    for fam, c in famcount.most_common():
        L.append(f"| {fam} | {c} |")
    L += ["", "## Caveats that bound every number above", "",
          "- `changed_since_r5` is an **upper bound**: any code difference counts, "
          "including a rename or a configurable-span swap.",
          "- `stream = TIGHTEN` rests on a source pattern for numeric comparisons and is "
          "a **lower bound** - a threshold reached through a helper or compared to a "
          "config constant is invisible to it.",
          "- `survives_pct` is populated only where the current rule is registered in "
          "`CURRENT_RULES`. **`-` means UNMEASURED, never 100%.**", "",
          "## Per strategy", "",
          "| strategy | family | R5 fires | proj. Step-1 | chg | survives | stream | status |",
          "|---|---|---|---|---|---|---|---|"]
    for r in sorted(recs, key=lambda x: (-x["r5_fires"], x["strategy"])):
        sv = "-" if r["survives_pct"] is None else f"{r['survives_pct']:.1%}"
        L.append(f"| {r['strategy']} | {r['family']} | {r['r5_fires']} | "
                 f"{r['projected_step1_fires']} | {'YES' if r['changed_since_r5'] else ''} | "
                 f"{sv} | {r['stream']} | {r['status']} |")
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"wrote {a.out} and {a.json}")
    print(f"  registered {len(recs)} | admitted {bystatus.get('DONE-ADMITTED',0)} | "
          f"in-campaign {bystatus.get('IN-CAMPAIGN',0)} | "
          f"not-started {bystatus.get('NOT-STARTED',0)}")
    print("  NOT-ADMITTED by stream: " + ", ".join(
        f"{k}={tstream.get(k,0)}" for k in ("TIGHTEN", "BOTH", "LOOSEN", "NONE")))
    print("  tighten candidates, top families: " + ", ".join(
        f"{f}={c}" for f, c in famcount.most_common(6)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
