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
  survives_pct      share of R5 fires on which the LIVE strategy function
                    fires with the recorded direction (S6-B2814)
  stream            TIGHTEN / LOOSEN / BOTH / NONE - see classify_stream
  ticket            campaign tickets naming this strategy in EXECUTION_QUEUE.md
  admitted          present in phase_1b_step2_admissions.json
  status            one of eight, mutually exclusive (B2825/B2833):
                    DONE-ADMITTED / DISABLED / PRUNED-DUPLICATE /
                    CLOSED-NEGATIVE / CONTAINED-IN-REPRESENTATIVE (terminal)
                    IN-CAMPAIGN / STALLED-CAMPAIGN / NOT-STARTED (in lanes)

STREAM IS THE HONEST PART, so its rule is stated rather than implied:
  TIGHTEN  the entry condition compares a signal to a NUMBER and that magnitude
           is persisted in signals_at_entry -> a tighter level is a SUBSET of
           the recorded fires and costs ZERO engine hours (runbook §3).
  LOOSEN   no tightenable persisted magnitude, OR the strategy is fire-starved
           under its current condition (< MIN_FIRES_FOR_GRID projected at the
           Step-1 shape) so the productive direction is a looser producer band -
           an ENGINE resim, since a looser level admits bars the cube never
           recorded (runbook §0.3, DEPTH is Priority 1).
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
# S6-B2810b: the R5 window is 4 YEARS (2022-05-06 .. 2026-05-04, plan 11.0 /
# PROJECT_PLAN spec). The first build shipped 5 - a calendar-year max-min+1
# over entry dates - which deflated every projection x0.8 AND biased
# classify_stream toward starved: 11 rows sat in the [80,100) band and
# carried the wrong stream. A span is a WINDOW LENGTH, not a count of
# calendar years touched.
R5_SPAN_YEARS = 4.0
MIN_FIRES_FOR_GRID = 100       # below this a Step-1 grid cannot be populated

# S6-B2814 (B2802 successor): survival is measured by calling the LIVE
# strategy function on each fire's persisted signals - the real gate IS the
# rule, so there is no hand-written re-expression to drift (the retired
# CURRENT_RULES map held 2 of 223 and every other row read "-"). VALIDATED
# before adoption: the live-function path reproduces both measured baselines
# exactly - smc_liquidity_sweep_reversal 151 of 2933 and turtle_soup_short
# 1880 of 1880, zero erroring rows. LOWER-BOUND caveat: a gate leg reading a
# key the cube never persisted defaults False, and an erroring row counts as
# a non-survival in the denominator.


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
    counts as changed (runbook §2.5).
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


# S6-B2810c: a MENTION is not a campaign. The first build flagged IN-CAMPAIGN
# when any ticket id preceded the strategy name anywhere in a queue cell - and
# all four news-family flags traced to S6-B1428a, an exit-reassignment ticket
# that campaigns nothing (L748: an identifier matched in prose). A row now
# counts as a CAMPAIGN only when it also carries campaign vocabulary. The
# vocabulary is a HEURISTIC and is caveated as such (caveat 4): a borderline
# row is settled by reading the ticket, never by this list.
CAMPAIGN_VOCAB = ("campaign", "step 1", "step-1", "step 2", "step-2",
                  "depth", "breadth", "band", "register", "specs",
                  "grader", "admission")


def campaign_tickets(qtext: str, name: str) -> tuple:
    """(campaign_ids, mention_ids) for `name`, ROW-scoped.

    A ledger row opens with its ticket id (table `| **id**` or legacy
    `- **id**` form) - the structural anchor L748 requires - and the name
    must appear in THAT row. campaign_ids additionally require a
    CAMPAIGN_VOCAB token in the row; mention_ids do not, and are kept so a
    reader can still ask "who talks about this strategy".
    """
    camp, ment = set(), set()
    for line in qtext.splitlines():
        m = re.match(r"[|-]\s*\*\*(S6-B\d+[a-z]?(?:\.[a-z0-9]+)?)\*\*", line)
        # B2830: WORD-BOUNDED name match. Bare `name in line` flagged
        # 52w_low_breakdown off a ticket naming only
        # 52w_low_breakdown_pullback_short - a strategy whose name is a
        # substring of a sibling's inherits the sibling's campaigns
        # (L748, substring variant; found by the #270 whole-row re-read).
        if not m or not re.search(
                r"(?<![a-z0-9_])" + re.escape(name) + r"(?![a-z0-9_])", line):
            continue
        ment.add(m.group(1))
        low = line.lower()
        if any(v in low for v in CAMPAIGN_VOCAB):
            camp.add(m.group(1))
    return sorted(camp)[:3], sorted(ment)[:3]


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
    pruned = set()
    if ADMISSIONS.exists():
        d = json.loads(ADMISSIONS.read_text(encoding="utf-8"))
        rows = d if isinstance(d, list) else d.get("admissions") or d.get("rows") or []
        admitted = {r.get("strategy") for r in rows
                    if isinstance(r, dict) and r.get("strategy")}
        # B2825: the Jaccard-0.70 pruned duplicates (B2666) are EVALUATED AND
        # DISCARDED, not future work
        pruned = {r.get("strategy")
                  for r in (d.get("pruned_collinear_b2666") or [])
                  if isinstance(r, dict) and r.get("strategy")}

    # B2825 (owner-directed 2026-09-16, "groups must be mutually exclusive;
    # closed strategies must not count toward future work unless genuinely
    # reopened"): CLOSED populations, each from its committed record -
    # nothing here is a judgement.
    closed_neg = set()      # family-pass FAIL, never re-admitted (b2628)
    contained = set()       # contained in an admitted representative (b2647)
    p28 = ROOT / "output_audit" / "b2628_institutional_family_grades.json"
    if p28.exists():
        sib = json.loads(p28.read_text(encoding="utf-8")).get("siblings") or {}
        closed_neg = {k for k, v in sib.items()
                      if isinstance(v, dict)} - admitted - pruned
    p47 = ROOT / "output_audit" / "b2647_pead_sibling_pass.json"
    if p47.exists():
        for r in json.loads(p47.read_text(encoding="utf-8")).get("graded") or []:
            if isinstance(r, dict) and "CONTAINED" in str(r.get("disposition", "")):
                if r.get("strategy") not in admitted:
                    contained.add(r["strategy"])
    from backtest.config import (STRATEGIES_DISABLED_MISSING_PRODUCER,
                                 STRATEGIES_DISABLED_DATA_SCARCITY,
                                 STRATEGIES_DISABLED_DUPLICATE)
    disabled = (set(STRATEGIES_DISABLED_MISSING_PRODUCER)
                | set(STRATEGIES_DISABLED_DATA_SCARCITY)
                | set(STRATEGIES_DISABLED_DUPLICATE))

    qtext = QUEUE.read_text(encoding="utf-8", errors="replace") if QUEUE.exists() else ""
    # B2829: the canonical last-row-wins reducer - never a hand parser (L695)
    sys.path.insert(0, str(ROOT / "scripts"))
    import queue_state as _qs
    ticket_states = {k: (v.get("state") if isinstance(v, dict) else v)
                     for k, v in _qs.tickets().items()}

    recs = []
    for name in sorted(ALL_STRATEGIES):
        fam = fams.get(name, "-")
        frame = by_strat.get(name)
        fires = 0 if frame is None else len(frame)
        rate = fires / R5_UNIVERSE / R5_SPAN_YEARS if fires else 0.0
        projected = rate * STEP1_TICKERS * STEP1_YEARS

        sigs, dirs = [], []
        if frame is not None and fires:
            sigs = [_parse_signals(x) for x in frame["signals_at_entry"]]
            dirs = list(frame["direction"].values)

        # is any declared numeric threshold backed by a PERSISTED magnitude?
        keys = thresholds.get(name, [])
        tightenable, covered = False, {}
        if keys and sigs:
            for k in keys:
                c = sum(1 for s in sigs
                        if isinstance(s.get(k), (int, float))
                        and not isinstance(s.get(k), bool)) / len(sigs)
                covered[k] = round(c, 4)
                if c >= COVERAGE_FLOOR:
                    tightenable = True

        # S6-B2814: survival = the LIVE strategy function fires on the
        # persisted signals with the recorded direction. An erroring row is
        # a non-survival counted in the denominator, never dropped.
        survives = None
        fn = ALL_STRATEGIES.get(name)
        if callable(fn) and sigs:
            ok = 0
            for s_, d_ in zip(sigs, dirs):
                try:
                    r_ = fn(s_)
                except Exception:
                    continue
                if r_ and r_.get("fires") and r_.get("direction") == d_:
                    ok += 1
            survives = round(ok / fires, 4)

        tickets, mentions = campaign_tickets(qtext, name)
        # B2829 (owner-directed "statuses latest, no misses" 2026-09-16): a
        # campaign is LIVE only while a naming ticket's CURRENT ledger state
        # is non-terminal. Before this, a ticket EXECUTED long ago flagged
        # IN-CAMPAIGN forever - the ticket-state half of L804's class.
        live_tickets = [t for t in tickets
                        if ticket_states.get(t) in ("OPEN", "BLOCKED",
                                                    "DEFERRED", "RUNNING")]
        # B2825 status precedence - one status per strategy, MUTUALLY
        # EXCLUSIVE by construction; a terminal disposition beats a campaign
        # mention, and the stream lane below is voided for terminal rows.
        if name in admitted:
            status = "DONE-ADMITTED"
        elif name in disabled:
            status = "DISABLED"
        elif name in pruned:
            status = "PRUNED-DUPLICATE"
        elif name in closed_neg:
            status = "CLOSED-NEGATIVE"
        elif name in contained:
            status = "CONTAINED-IN-REPRESENTATIVE"
        else:
            # B2833 (owner word "STALLED-CAMPAIGN approved", 2026-09-15): a
            # row whose campaign tickets exist but are ALL terminal is
            # distinguished from a never-campaigned row - Step-1 may be done
            # with no Step-2 word, and NOT-STARTED erased that history
            # (flagged at B2829, ruled now). NON-terminal: it keeps its lane.
            status = ("IN-CAMPAIGN" if live_tickets
                      else "STALLED-CAMPAIGN" if tickets else "NOT-STARTED")
        terminal = status in ("DONE-ADMITTED", "DISABLED", "PRUNED-DUPLICATE",
                              "CLOSED-NEGATIVE", "CONTAINED-IN-REPRESENTATIVE")
        # REOPEN RULE (owner 2026-09-16, "unless reopened for a genuine
        # reason"): a terminal verdict was computed on the CLOSURE-TIME gate;
        # if the entry condition changed since R5 AND the old fires no longer
        # all satisfy it, the verdict's evidence base has moved - FLAGGED for
        # the owner, never auto-reopened.
        reopen = bool(terminal and status != "DONE-ADMITTED"
                      and name in changed
                      and (survives is None or survives < 1.0))
        # B2822 (owner-caught: "the counts are all over the place"): the LANE
        # is classified on CURRENT-GATE fires, not raw R5 fires. hub-1 sat at
        # stream NONE off 2,933 raw fires while only 5.15% survive its current
        # gate - its honest projection is ~14, which is LOOSEN. Where survival
        # is unmeasured (zero-fire rows) the raw projection stands.
        eff = projected if survives is None else projected * survives
        recs.append({"strategy": name, "family": fam, "r5_fires": fires,
                     "changed_since_r5": name in changed,
                     "survives_pct": survives,
                     "projected_step1_fires": round(projected, 1),
                     "projected_current_gate": round(eff, 1),
                     "reopen_candidate": reopen,
                     "stream": "-" if terminal
                     else classify_stream(tightenable, eff),
                     "tightenable_keys": covered, "tickets": tickets,
                     "live_campaign_tickets": live_tickets,
                     "mention_tickets": mentions,
                     "admitted": name in admitted, "status": status})

    # L803 (B2822): the BUILD STAMP. A regenerated artifact without one
    # leaves its stale copies indistinguishable from HEAD - the owner quoted
    # a superseded build's stream counts and nothing on any copy said which
    # build it was. Batch + source commit + timestamp ride BOTH outputs.
    import time as _time
    try:
        _sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              cwd=ROOT, capture_output=True, text=True,
                              timeout=15).stdout.strip() or "unknown"
    except Exception:
        _sha = "unknown"
    build = {"source_commit": _sha,
             "generated_at": _time.strftime("%Y-%m-%d %H:%M:%S")}

    Path(a.json).write_text(json.dumps(
        {"generator": "scripts/build_strategy_status.py",
         "build": build,
         "cube": str(R5_DIR), "r5_screener_commit": R5_SCREENER_COMMIT,
         "rules": {"coverage_floor": COVERAGE_FLOOR,
                   "min_fires_for_grid": MIN_FIRES_FOR_GRID,
                   "step1_shape": f"{STEP1_TICKERS} tickers x {STEP1_YEARS}y"},
         "caveats": [
             "changed_since_r5 is an UPPER BOUND - any code difference counts",
             "stream TIGHTEN rests on a source pattern for numeric comparisons, "
             "a LOWER BOUND - thresholds via a helper or a config constant are invisible",
             "survives_pct calls the LIVE strategy function on each fire's persisted "
             "signals (S6-B2814; validated: reproduces 151/2933 and 1880/1880 exactly). "
             "A LOWER BOUND where a gate leg reads an unpersisted key (defaults False); "
             "an erroring row counts as non-survival; None only for zero-fire strategies",
             "IN-CAMPAIGN requires a CAMPAIGN_VOCAB token in the row naming the "
             "strategy (S6-B2810c; a bare mention is not a campaign) - the "
             "vocabulary is a heuristic, so borderline rows are settled by "
             "reading the ticket; mention_tickets keeps the unfiltered list; "
             "IN-CAMPAIGN additionally requires a naming ticket whose CURRENT "
             "ledger state is non-terminal (B2829) - a concluded campaign does "
             "not own a strategy forever; a row whose campaign tickets exist "
             "but are ALL terminal is STALLED-CAMPAIGN (B2833, owner-approved "
             "2026-09-15): campaigned, concluded mid-path, still in its lane. "
             "STALLED inherits the vocabulary heuristic WITHOUT the liveness "
             "mask, so a builder-audit ticket that names a strategy as an "
             "EXAMPLE (the S6-B2810b/c and S6-B2830 rows) can stall it "
             "falsely - settle a surprising row by reading its tickets",
             "stream and the proj column use the CURRENT-GATE projection "
             "(raw projection x survives_pct, B2822); projected_step1_fires "
             "in this JSON keeps the raw figure",
             "terminal statuses (ADMITTED / DISABLED / PRUNED-DUPLICATE / "
             "CLOSED-NEGATIVE / CONTAINED) are MUTUALLY EXCLUSIVE with the "
             "stream lanes and excluded from every work bucket (B2825); "
             "reopen_candidate flags a terminal row whose entry condition "
             "changed since its closure evidence (survives < 1.0) - flagged "
             "for the owner, never auto-reopened"],
         "rows": recs}, indent=2), encoding="utf-8")

    # ---- the markdown view -------------------------------------------------
    import collections
    bystream = collections.Counter(r["stream"] for r in recs)
    bystatus = collections.Counter(r["status"] for r in recs)
    _TERMINAL = ("DONE-ADMITTED", "DISABLED", "PRUNED-DUPLICATE",
                 "CLOSED-NEGATIVE", "CONTAINED-IN-REPRESENTATIVE")
    todo = [r for r in recs if r["status"] not in _TERMINAL]
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
         f"**Build:** commit {build['source_commit']} at {build['generated_at']} "
         "(L803: a copy without this line is a STALE VERSION - trust only the "
         "build at HEAD)", "",
         f"**Cube:** R5 ({R5_DIR.name}) | **R5-era screener:** {R5_SCREENER_COMMIT} | "
         f"**Step-1 shape:** {STEP1_TICKERS} tickers x {STEP1_YEARS}y | "
         f"**grid floor:** {MIN_FIRES_FOR_GRID} fires", "",
         "## Totals", "",
         "| | count |", "|---|---|",
         f"| registered strategies | {len(recs)} |",
         f"| DONE - admitted to Phase 1B | {bystatus.get('DONE-ADMITTED', 0)} |",
         f"| IN-CAMPAIGN - a campaign-marked ticket names it, LIVE | {bystatus.get('IN-CAMPAIGN', 0)} |",
         f"| STALLED-CAMPAIGN - campaigned, every naming ticket terminal (B2833) | {bystatus.get('STALLED-CAMPAIGN', 0)} |",
         f"| NOT-STARTED | {bystatus.get('NOT-STARTED', 0)} |",
         f"| CLOSED-NEGATIVE - family-pass FAIL, never re-admitted (b2628) | {bystatus.get('CLOSED-NEGATIVE', 0)} |",
         f"| PRUNED-DUPLICATE - Jaccard >= 0.70 of an admitted canonical (B2666) | {bystatus.get('PRUNED-DUPLICATE', 0)} |",
         f"| CONTAINED-IN-REPRESENTATIVE (b2647) | {bystatus.get('CONTAINED-IN-REPRESENTATIVE', 0)} |",
         f"| DISABLED (backtest.config sets) | {bystatus.get('DISABLED', 0)} |",
         f"| REOPEN-CANDIDATE flags among the terminal rows | {sum(1 for r in recs if r['reopen_candidate'])} |", "",
         "## Stream - of the OPEN population only (terminal rows excluded, B2825)", "",
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
          "- `survives_pct` calls the **live strategy function** on each fire's persisted "
          "signals (S6-B2814). A **lower bound** where a gate leg reads an unpersisted key; "
          "an erroring row counts as non-survival; `-` only for zero-fire strategies.",
          "- `IN-CAMPAIGN` requires a campaign-vocabulary token in the row naming the "
          "strategy (S6-B2810c) - **a bare mention is not a campaign** - AND a naming "
          "ticket whose CURRENT ledger state is non-terminal (B2829). The vocabulary "
          "is a heuristic; a borderline row is settled by reading the ticket, and "
          "`mention_tickets` in the JSON keeps the unfiltered list.",
          "- `STALLED-CAMPAIGN` (B2833, owner-approved 2026-09-15): campaign tickets "
          "exist but every one is terminal - campaigned, concluded mid-path (e.g. "
          "Step-1 done, no Step-2 word). **Not terminal**: the row keeps its stream "
          "lane; the history is preserved rather than erased into NOT-STARTED. It "
          "inherits the vocabulary heuristic WITHOUT the liveness mask, so a "
          "builder-audit ticket naming a strategy as an EXAMPLE (S6-B2810b/c, "
          "S6-B2830) can stall it falsely - settle a surprising row by reading "
          "its tickets.", "",
          "## Per strategy", "",
          "| strategy | family | R5 fires | proj. Step-1 (current-gate) | chg | survives | stream | status |",
          "|---|---|---|---|---|---|---|---|"]
    for r in sorted(recs, key=lambda x: (-x["r5_fires"], x["strategy"])):
        sv = "-" if r["survives_pct"] is None else f"{r['survives_pct']:.1%}"
        L.append(f"| {r['strategy']} | {r['family']} | {r['r5_fires']} | "
                 f"{r['projected_current_gate']} | {'YES' if r['changed_since_r5'] else ''} | "
                 f"{sv} | {r['stream']} | {r['status']} |")
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"wrote {a.out} and {a.json}")
    print(f"  registered {len(recs)} | admitted {bystatus.get('DONE-ADMITTED',0)} | "
          f"in-campaign {bystatus.get('IN-CAMPAIGN',0)} | "
          f"stalled-campaign {bystatus.get('STALLED-CAMPAIGN',0)} | "
          f"not-started {bystatus.get('NOT-STARTED',0)}")
    print("  NOT-ADMITTED by stream: " + ", ".join(
        f"{k}={tstream.get(k,0)}" for k in ("TIGHTEN", "BOTH", "LOOSEN", "NONE")))
    print("  tighten candidates, top families: " + ", ".join(
        f"{f}={c}" for f, c in famcount.most_common(6)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
