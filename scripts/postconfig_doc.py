#!/usr/bin/env python
"""B2211: ONE post-config analysis document, with each step's actual FINDINGS.

Source: output_audit/postconfig_ledger.json, output_audit/<cube>_grid_auto.json,
output_audit/<cube>_spot_check.json (all written by the battery via
scripts/run_postconfig.py); per CHECKLIST #77.

WHY THIS REPLACES THE PER-CONFIG CARDS (owner, 2026-08-26): "I want a single
document and not multiple. On looking at the reports its absolutely horrible
and inadequate. It just says done! I want to know the findings of each step!"

The B2198/B2208 card rendered step STATUS ("DONE") plus 150 truncated
characters. Every finding the battery actually produced - 14 named integrity
checks with measured values, an independent re-derivation of 50 sampled
trades, a 300-row combination funnel - sat on disk and never reached the
reader.

DESIGN (B2211 council, chairman synthesis):
- ONE document, regenerated WHOLE from the artifacts. Never appended: two
  configs landing together would interleave writes.
- Organised by HOW THE NUMBERS COULD BE WRONG, not by pipeline step order.
  Step names are the pipeline's internal structure; identity / leakage /
  reproduction / sample size is the reader's decision structure.
- Every check prints its MEASURED VALUE beside WHAT WOULD HAVE BEEN ALARMING.
  A row that can only ever say DONE carries no evidentiary weight.
- Never truncate; name the file holding the full detail.
- FALSIFIABILITY DISCLOSED at the top: how many named checks have EVER
  returned non-PASS across the whole ledger. If that number is zero, green is
  weak evidence and the document says so instead of implying confidence it
  has not earned.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "output_audit"
LEDGER = AUDIT / "postconfig_ledger.json"
DOC = AUDIT / "POSTCONFIG_REPORT.md"
# B2520: "closed" has ONE definition - the gate's (DONE with evidence, or N/A
# with a reason; SKIPPED closes nothing). Rendering a second definition here
# is how a report can say "9 of 9" while the gate says exit 2.
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_postconfig_complete import STEPS, is_closed  # noqa: E402
import postconfig_landing as _landing  # noqa: E402
# S6-B2409 (owner ruling 2026-08-30): the selection-noise floor is RETIRED IN
# ITS ENTIRETY - this renderer no longer frames any value against it, not even
# as a diagnostic. (Its L696 history: the constant kept re-entering Step-1
# reports as a verdict because a generator carried it; the generator now
# carries nothing to re-supply.) Step-1 admission remains min-trades >= 10
# plus a ranked list with NO gates (owner ruling 2026-08-17, B1608).

# What each named check MEANS and what would have been alarming. A measured
# value without its expectation is undecidable by the reader, so this mapping
# is the core of the document rather than decoration around it.
CHECK_MEANING = {
    "cube_exists": ("cube produced rows",
                    "zero rows = the config ran and emitted nothing"),
    "one_strategy": ("exactly one strategy in the cube",
                     "more than 1 = the strategy-subset filter leaked"),
    "M2_exits_per_entry_vs_registry": (
        "every entry carries one row per registered exit",
        "a shortfall = exits silently dropped from the cube"),
    "megacaps_present": ("mega-caps present in the universe",
                         "absent = the abandoned A-C chunk universe (L445)"),
    "M1_content_sha": ("cube content hash",
                       "a repeat across configs = two configs produced "
                       "identical cubes, so one knob did nothing"),
    "M3_fill_date": ("fills that preceded their own entry",
                     "any non-zero = look-ahead in execution"),
    "M4_window": ("entry-date span actually simulated",
                  "a short span = the run did not cover its window"),
    "M4_holdout_touch": (
        "entries at or after the LOCKED holdout start",
        "any non-zero = the holdout was contaminated and the run is void"),
    "M5_pnl_integrity": (
        "NaN/inf PnL, and values beyond the winsorize bound",
        "NaN/inf = arithmetic corruption; beyond-bound is disclosure only, "
        "clipped at grade time"),
    "M7_degraded_exits": (
        "exit methods that silently fell back to another",
        "each mapping = an exit you paid to test and did not actually test"),
    "M10_gate_receipt": ("pre-launch receipt matches the run manifest",
                         "mismatch = this run is not the run that was gated"),
    "step7_engine_implemented": ("engine-side implementation check exit code",
                                 "non-zero = the wiring is absent"),
    "M9_universe_artifact": ("universe artifact verified",
                             "FAIL = the ticker list is not what was intended"),
    "ledger_status_matches_evidence": (
        "rows claiming DONE whose evidence contradicts it",
        "any non-zero = the ledger is lying about itself"),
    "step2_grade_auto": ("grading ran at this config's own parameters",
                         "non-zero = the grid was never produced"),
    "step4_spot_check_auto": ("independent spot check ran",
                              "non-zero = no re-derivation happened"),
}

# Which risk question each check answers.
GROUPS = [
    ("Is this the right data?",
     ["cube_exists", "one_strategy", "megacaps_present", "M9_universe_artifact",
      "M1_content_sha", "M4_window", "M2_exits_per_entry_vs_registry"]),
    ("Did anything leak from the future?",
     ["M4_holdout_touch", "M3_fill_date", "M10_gate_receipt"]),
    ("Does the arithmetic reproduce?",
     ["M5_pnl_integrity", "M7_degraded_exits", "ledger_status_matches_evidence",
      "step2_grade_auto", "step4_spot_check_auto", "step7_engine_implemented"]),
]


def parse_checks(evidence: str) -> list[tuple[str, str, str]]:
    """Split the packed step-1 evidence string into (name, outcome, value).

    The truncation the owner saw came from 14 checks sharing one string. This
    fixes it at the READING end, so every historical ledger entry stays
    parseable without a schema migration.
    """
    out = []
    for m in re.finditer(r"(\w+)=(PASS|FAIL|WARN|SKIP)\(([^;]*)", evidence or ""):
        out.append((m.group(1), m.group(2), m.group(3).rstrip(") ")))
    return out


def falsifiability(ledger: dict) -> tuple[int, int]:
    """(non-PASS count, total named checks) across the WHOLE ledger."""
    total = bad = 0
    for entry in ledger.values():
        for row in entry.values():
            for _, outcome, _ in parse_checks(row.get("evidence", "")):
                total += 1
                if outcome != "PASS":
                    bad += 1
    return bad, total


def load_artifacts(cube: str) -> dict:
    d: dict = {"cube": cube}
    for key, path in (("grid", AUDIT / (cube + "_grid_auto.json")),
                      ("spot", AUDIT / (cube + "_spot_check.json")),
                      ("lenses", AUDIT / (cube + "_lenses.json"))):
        d[key] = (json.loads(path.read_text(encoding="utf-8"))
                  if path.exists() else None)
    return d


# The metric keys the graders copy INTO the admit dict beside the knobs; the
# knobs are whatever remains, so a new family renders without a new branch.
_ADMIT_METRIC_KEYS = frozenset({
    "fires", "exit", "holdout_n", "full_period_n", "is_ci_lo", "is_sharpe",
    "sharpe", "ci_lo", "verdict", "exits_effective", "exits_collapsed",
    "npt_excluded_identity_boundary", "rank", "class_size", "members"})
_SPOT_PARAM_KEYS = ("swing_length", "ema_span", "close_mitigation", "tail_n",
                    "min_committed_growth", "fallback_min_increased")


def combination_label(admit: dict) -> str:
    """Knob=value for every knob the admit dict carries (B2520: the smc-only
    cm/brk/age/tail template rendered None x4 for the institutional family)."""
    knobs = [(k, v) for k, v in admit.items() if k not in _ADMIT_METRIC_KEYS]
    return " ".join(f"{k}={v}" for k, v in knobs) or "(no knobs recorded)"


def spot_params(spot: dict) -> str:
    """The parameters the spot-checker actually ran with - only the keys the
    artifact carries with a value (institutional has no swing/tail)."""
    parts = [f"{k} {spot.get(k)}" for k in _SPOT_PARAM_KEYS
             if spot.get(k) is not None]
    return ", ".join(parts) or "parameters not recorded in the artifact"


def landings_section() -> list[str]:
    """B2520: what landed, when, by which path, and whether the owner has seen
    it. The record is output_audit/postconfig_landings.jsonl, appended by
    scripts/postconfig_landing.py the moment a cube lands (engine hook or
    run_wave); reported_to_owner flips when a LANDING REPORT for the cube
    reaches the final response (verify_turn_compliance.scan_undelivered_landing)."""
    try:
        events = _landing.read_landings()
    except Exception as exc:  # noqa: BLE001 - a report must render regardless
        return [f"_landing record unreadable: {type(exc).__name__}: {exc}_", ""]
    latest: dict[str, dict] = {}
    for ev in events:
        if ev.get("cube"):
            latest[ev["cube"]] = ev
    if not latest:
        return ["_no landings recorded yet (record starts at B2520; every cube "
                "landed before it was dispositioned by hand)_", ""]
    pending = [c for c, ev in latest.items() if not ev.get("reported_to_owner")]
    out = [f"{len(latest)} cube(s) landed through the supervisor; "
           f"**{len(pending)} not yet reported to the owner**"
           + (f" ({', '.join(pending)})" if pending else "") + ".", "",
           "| cube | landed | via | battery exit | blocking | WARN/FAIL findings "
           "| committed | pushed | reported |", "|---|---|---|---|---|---|---|---|---|"]
    for c, ev in sorted(latest.items(), key=lambda kv: kv[1].get("ts") or "",
                        reverse=True):
        finds = ev.get("findings") or []
        blocking = ev.get("blocking") or []
        out.append(
            f"| {c} | {ev.get('ts')} | {ev.get('source')} | "
            f"{ev.get('battery_exit')} | {', '.join(blocking) or 'none'} | "
            f"{len(finds)}{': ' + '; '.join(str(f).replace('|', '/') for f in finds) if finds else ''} | "
            f"{ev.get('committed')} | {ev.get('pushed')} | "
            f"{'yes ' + str(ev.get('reported_ts') or '') if ev.get('reported_to_owner') else '**NO**'} |")
    out.append("")
    return out


def config_section(cube: str, entry: dict, art: dict) -> list[str]:
    grid, spot = art.get("grid"), art.get("spot")
    checks = parse_checks((entry.get("1_cube_sanity") or {}).get("evidence", ""))
    by_name = {n: (o, v) for n, o, v in checks}

    cfg = (grid or {}).get("config") or {}
    ident = ", ".join(f"{k}={v}" for k, v in cfg.items()) or "parameters not recorded"
    lines = [f"### {cube}", "", f"**Configuration:** {ident}", ""]

    # STEP-1 RANKING FIRST. (Was 'VERDICT FIRST' until B2299: Step 1 has no
    # verdicts - it hands forward a ranked list with no gates applied.)
    rank = (grid or {}).get("step1_ranking") or []
    if rank:
        top = rank[0]
        cl = top.get("is_ci_lo")
        lines += [f"**STEP-1 RANKING (no gates applied - owner ruling B1608): "
                  f"best cell is_ci_lo {cl}** (is_sharpe "
                  f"{top.get('is_sharpe')}, {top.get('fires')} fires, exit "
                  f"{top.get('exit')}). Step-1 admission is min-trades >= 10 "
                  f"plus this ranked list; is_ci_lo is the RANKING KEY, not a "
                  f"gate. A ranked cell is a CANDIDATE for Step-2 validation, "
                  f"not a validated edge - its height is partly the search "
                  f"itself. (S6-B2409: the former selection-noise-floor "
                  f"framing is retired.)", ""]
    else:
        lines += ["**NO GRADED GRID** - step 2 produced no artifact.", ""]

    # B2520: completeness is the GATE's verdict, not a second tally. Before
    # B2520 this line counted DONE + SKIPPED as "steps ran" and called the
    # skipped ones "NOT automated ... by design" - a report that normalised the
    # very miss the owner asked about ("why are some steps skipped after each
    # config?"). Now: every one of the nine steps is either closed (DONE with
    # evidence / N/A with a reason) or NAMED as open, and an open step means
    # verify_postconfig_complete exits 2 for this cube.
    closed = [s for s in STEPS if is_closed(entry.get(s))]
    na = [s for s in closed if (entry.get(s) or {}).get("status") == "N/A"]
    open_steps = [s for s in STEPS if s not in closed]
    lines += [f"**Completeness: {len(closed)} of {len(STEPS)} steps closed** "
              f"({len(closed) - len(na)} DONE with evidence, {len(na)} N/A with "
              f"a reason{': ' + ', '.join(na) if na else ''}). "
              + ("Every step is dispositioned; nothing is outstanding on this "
                 "cube."
                 if not open_steps else
                 f"**{len(open_steps)} step(s) NOT closed "
                 f"({', '.join(open_steps)}) - this cube BLOCKS the turn gate "
                 "until each is DONE with evidence or N/A with a reason; "
                 "SKIPPED is not a disposition (B2520).**"), ""]
    lines += ["| step | status | evidence / reason (never truncated) |",
              "|---|---|---|"]
    for s in STEPS:
        row = entry.get(s) or {}
        st = row.get("status") or "MISSING"
        ev = str(row.get("evidence") or row.get("reason") or
                 row.get("note") or "").replace("|", "/").replace("\n", " ")
        if s == "1_cube_sanity":
            ev = "the named checks are tabulated below by risk question"
        mark = "" if is_closed(row) else " **<-- NOT CLOSED**"
        lines.append(f"| {s} | {st}{mark} | {ev or '-'} |")
    lines.append("")

    for title, names in GROUPS:
        rows = [(n, by_name[n]) for n in names if n in by_name]
        if not rows:
            continue
        lines += [f"**{title}**", "",
                  "| check | measured | outcome | what would have been alarming |",
                  "|---|---|---|---|"]
        for n, (outcome, val) in rows:
            meaning, alarm = CHECK_MEANING.get(n, (n, "-"))
            mark = "" if outcome == "PASS" else " **<-- NOT PASS**"
            clean = val.replace("|", "/")
            lines.append(f"| {meaning} | {clean} | {outcome}{mark} | {alarm} |")
        lines.append("")

    if spot:
        agree = spot.get("agree", 0)
        dis = spot.get("disagree", 0)
        tot = agree + dis + spot.get("skipped", 0)
        fails = len(spot.get("execution_failures") or [])
        lines += ["**Independent re-derivation of sampled trades (step 4)**", "",
                  f"- {agree} of {tot} sampled trades re-derived to the SAME "
                  f"fire/no-fire decision as the engine; {dis} disagreed; "
                  f"{fails} execution failures.",
                  f"- Sampled with seed {spot.get('seed')} at this config's own "
                  f"parameters ({spot_params(spot)})"
                  + (f" by {spot.get('checker')}" if spot.get("checker") else "")
                  + ".",
                  "- CAVEAT worth stating: the re-derivation uses the SAME "
                  "parameter set as the engine, so it catches wiring and data "
                  "faults, NOT a wrong parameter choice. Full per-trade rows: "
                  f"output_audit/{cube}_spot_check.json.", ""]
        if dis:
            lines += [f"- **{dis} DISAGREEMENTS - inspect before trusting "
                      "this cube.**", ""]
        if spot.get("empty_records") not in (None, 0):
            lines += [f"- {spot.get('empty_records')} sampled trades carried an "
                      "EMPTY signals_at_entry record (S6-B2512 class) - the "
                      "re-derivation could still decide them from the "
                      "precompute, but the engine's own record is missing.", ""]

    lenses = art.get("lenses")
    if lenses:
        rows_l = lenses.get("lenses") or []
        bad_l = [r for r in rows_l if r.get("level") in ("WARN", "FAIL")]
        lines += [f"**Adversarial lenses (step 5) - {len(rows_l)} lenses, "
                  f"{len(bad_l)} WARN/FAIL** (step basis: "
                  f"{lenses.get('step_basis')}; family {lenses.get('family')})",
                  "", "| lens | level | evidence |", "|---|---|---|"]
        for r in rows_l:
            mark = "" if r.get("level") == "INFO" else " **<-- NOT INFO**"
            lines.append(f"| {r.get('lens')} | {r.get('level')}{mark} | "
                         f"{str(r.get('evidence')).replace('|', '/')} |")
        lines.append("")

    if grid:
        res = grid.get("results") or []
        verd = Counter(r.get("verdict") for r in res)
        starved = verd.get("NO_EXIT_SELECTABLE", 0)
        pct = (100.0 * starved / len(res)) if res else 0.0
        lines += ["**Is the sample large enough to mean anything? "
                  "(step 2 funnel)**", "",
                  f"- {len(res)} parameter combinations enumerated.",
                  f"- **{starved} ({pct:.0f}%) STARVED in-sample** - no exit "
                  "cleared the minimum trade count, so they were never graded. "
                  "A sample-size fact, not a quality verdict.",
                  f"- {len(res) - starved} graded and ranked, collapsing to "
                  f"{grid.get('step1_distinct_outcomes')} distinct outcome "
                  "classes (step 6b: combinations differing only in a "
                  "saturated parameter are the SAME fire set, so counting rows "
                  "overstates the evidence - L473); the top "
                  f"{len(rank)} classes carry "
                  f"{grid.get('step1_combinations_carried')} combinations "
                  "forward to Step 2 (tighten_breaker_block.py:449-454).", ""]
        if rank:
            lines += ["| rank | is_ci_lo | is_sharpe | fires | exit | "
                      "class size | combination |",
                      "|---|---|---|---|---|---|---|"]
            for r in rank[:5]:
                combo = combination_label(r.get("admit") or {})
                lines.append(f"| {r.get('rank')} | {r.get('is_ci_lo')} | "
                             f"{r.get('is_sharpe')} | {r.get('fires')} | "
                             f"{r.get('exit')} | {r.get('class_size')} | "
                             f"{combo} |")
            lines += ["", "_Top 5 of the ranking; the full list is in "
                      f"output_audit/{cube}_grid_auto.json._", ""]
    return lines


def build(cubes: list[str] | None = None) -> str:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    bad, total = falsifiability(ledger)
    graded = [c for c in ledger if (AUDIT / (c + "_grid_auto.json")).exists()]
    if cubes:
        graded = [c for c in graded if any(w in c for w in cubes)]
    graded.sort(key=lambda c: (AUDIT / (c + "_grid_auto.json")).stat().st_mtime,
                reverse=True)

    # S6-B2330 (owner directive 2026-08-28): TABLE D, the Step-1 ranked list,
    # regenerated here because this function already runs at EVERY landing via
    # run_wave.py:289 - the auto-update the owner asked for needs no new watcher
    # and no cron. Rendered through producer_variant_table.table_d, which owns
    # the columns: Table C's docstring records that hand-retyping a locked table
    # dropped four columns three times, so the renderer is the only source.
    try:
        import sys as _sys
        _sys.path.insert(0, str(ROOT / "scripts"))
        from producer_variant_table import (table_d as _table_d,
                                            table_d_params as _table_dp)
        _grids = {}
        for _p in sorted(AUDIT.glob("output_*_grid_auto.json"),
                         key=lambda x: x.stat().st_mtime):
            _n = _p.name[len("output_"):-len("_grid_auto.json")]
            _grids[_n] = json.loads(_p.read_text(encoding="utf-8"))
        _td = (_table_d(_grids) + ["", "### TABLE D-2 - THE SIX SWEPT AXES", ""]
               + _table_dp(_grids)) if _grids else ["_no graded grids yet_"]
    except Exception as _e:  # never let the ranked list break the whole report
        _td = [f"_TABLE D unavailable: {type(_e).__name__}: {_e}_"]

    out = ["# POST-CONFIG ANALYSIS - all configs, all findings", "",
           "Source: output_audit/postconfig_ledger.json plus each config's "
           "_grid_auto.json, _spot_check.json and _lenses.json (written by "
           "scripts/run_postconfig.py) and output_audit/postconfig_landings.jsonl "
           "(written by scripts/postconfig_landing.py); rendered by "
           "scripts/postconfig_doc.py; per CHECKLIST #77.", "",
           "REGENERATED WHOLE at every config landing - by the landing "
           "supervisor the engine itself invokes (B2520), so a cube that lands "
           "by ANY launch path reaches this document. Replaces the per-config "
           "report cards (B2198/B2208), which reported step STATUS rather than "
           "step FINDINGS.", "",
           "## How much confidence these checks earn", "",
           f"**Across the entire ledger ({len(ledger)} entries), {total} named "
           f"checks have run and {bad} have ever returned non-PASS.**"]
    out += ["", "## Landings - what the supervisor recorded (B2520)", ""]
    out += landings_section()
    out += ["", "## TABLE D - STEP-1 RANKED LIST (top 20)", ""] + _td
    if bad == 0:
        out += ["", "**Read that as a caution, not a reassurance.** A check "
                "that has never failed has not been shown capable of failing, "
                "so an all-green battery is WEAK evidence. The checks that "
                "would carry real weight are ones with a demonstrated failure "
                "mode - a deliberately corrupted cube proving they trip. Until "
                "then, green means 'nothing obviously wrong was detected', "
                "never 'this cube is correct'."]
    out += ["", f"## Index - {len(graded)} graded config(s), newest first", "",
            "| config | best is_ci_lo | fires | starved | steps closed "
            "(DONE+N/A of 9; the gate's own is_closed) |",
            "|---|---|---|---|---|"]
    for c in graded:
        grid = json.loads((AUDIT / (c + "_grid_auto.json")).read_text(encoding="utf-8"))
        rank = grid.get("step1_ranking") or []
        top = rank[0] if rank else {}
        cl = top.get("is_ci_lo")
        res = grid.get("results") or []
        starved = sum(1 for r in res if r.get("verdict") == "NO_EXIT_SELECTABLE")
        entry = ledger.get(c, {})
        n_closed = sum(1 for s in STEPS if is_closed(entry.get(s)))
        open_names = [s for s in STEPS if not is_closed(entry.get(s))]
        out.append(f"| {c} | {cl if cl is not None else '-'} | "
                   f"{top.get('fires', '-')} | {starved}/{len(res)} | "
                   f"{n_closed}/{len(STEPS)}"
                   + (f" **OPEN: {', '.join(open_names)}**" if open_names else "")
                   + " |")
    out += ["", "## Per-config findings", ""]
    for c in graded:
        out += config_section(c, ledger.get(c, {}), load_artifacts(c))
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", default="",
                    help="comma-separated substrings to include "
                         "(default: every graded config)")
    ap.add_argument("--out", default=str(DOC))
    a = ap.parse_args()
    cubes = [c.strip() for c in a.configs.split(",") if c.strip()] or None
    text = build(cubes)
    Path(a.out).write_text(text, encoding="utf-8")
    print(f"[OK] wrote {a.out} ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
