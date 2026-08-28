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
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "output_audit"
LEDGER = AUDIT / "postconfig_ledger.json"
DOC = AUDIT / "POSTCONFIG_REPORT.md"
NOISE_FLOOR = 0.333          # B2009 PHASE-1B per-cell selection-noise floor.
# S6-B2299 / L696: this is a DIFFERENT GRAIN from Step-1 admission, which is
# min-trades >= 10 plus a ranked list with NO gates (owner ruling 2026-08-17,
# B1608; tighten_breaker_block.py:383). Printing it as a Step-1 VERDICT made
# four separate reports state a threshold the grader does not apply. Report it
# as a DIAGNOSTIC and always name its grain.

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
                      ("spot", AUDIT / (cube + "_spot_check.json"))):
        d[key] = (json.loads(path.read_text(encoding="utf-8"))
                  if path.exists() else None)
    return d


def config_section(cube: str, entry: dict, art: dict) -> list[str]:
    grid, spot = art.get("grid"), art.get("spot")
    checks = parse_checks((entry.get("1_cube_sanity") or {}).get("evidence", ""))
    by_name = {n: (o, v) for n, o, v in checks}

    cfg = (grid or {}).get("config") or {}
    ident = ", ".join(f"{k}={v}" for k, v in cfg.items()) or "parameters not recorded"
    lines = [f"### {cube}", "", f"**Configuration:** {ident}", ""]

    # VERDICT FIRST - measured against the run's own bar.
    rank = (grid or {}).get("step1_ranking") or []
    if rank:
        top = rank[0]
        cl = top.get("is_ci_lo")
        above = cl is not None and cl > NOISE_FLOOR
        tail = ("A cell above the yardstick is a CANDIDATE for Step-2 "
                "validation, not a validated edge."
                if above else
                "Its height is explainable by the search itself.")
        lines += [f"**STEP-1 RANKING (no gates applied - owner ruling B1608): "
                  f"best cell is_ci_lo {cl}** (is_sharpe "
                  f"{top.get('is_sharpe')}, {top.get('fires')} fires, exit "
                  f"{top.get('exit')}). Step-1 admission is min-trades >= 10 "
                  f"plus this ranked list; is_ci_lo is the RANKING KEY, not a "
                  f"gate. DIAGNOSTIC ONLY: that value is "
                  f"{'above' if above else 'below'} the {NOISE_FLOOR} "
                  f"PHASE-1B per-cell selection-noise floor (B2009), a "
                  f"DIFFERENT GRAIN. {tail}", ""]
    else:
        lines += ["**NO GRADED GRID** - step 2 produced no artifact.", ""]

    skipped = sorted(k for k, v in entry.items() if v.get("status") == "SKIPPED")
    done = [k for k, v in entry.items() if v.get("status") == "DONE"]
    lines += [f"**Completeness: {len(done)} of {len(done) + len(skipped)} "
              f"steps ran.** The {len(skipped)} judgment steps "
              f"({', '.join(skipped)}) are NOT automated and remain "
              "outstanding - this evidence package is incomplete by design, "
              "which is different from clean.", ""]

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
                  f"parameters (swing {spot.get('swing_length')}, span "
                  f"{spot.get('ema_span')}, close_mitigation "
                  f"{spot.get('close_mitigation')}, tail_n "
                  f"{spot.get('tail_n')}).",
                  "- CAVEAT worth stating: the re-derivation uses the SAME "
                  "parameter set as the engine, so it catches wiring and data "
                  "faults, NOT a wrong parameter choice. Full per-trade rows: "
                  f"output_audit/{cube}_spot_check.json.", ""]
        if dis:
            lines += [f"- **{dis} DISAGREEMENTS - inspect before trusting "
                      "this cube.**", ""]

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
                  f"- {verd.get('BELOW_POWER_FLOOR', 0)} graded and ranked; "
                  f"{grid.get('step1_combinations_carried')} carried across "
                  f"{grid.get('step1_distinct_outcomes')} distinct outcome "
                  "classes after equivalence collapse (combinations differing "
                  "only in a saturated parameter are the SAME fire set, so "
                  "counting rows overstates the evidence - L473).", ""]
        if rank:
            lines += ["| rank | is_ci_lo | is_sharpe | fires | exit | "
                      "class size | combination |",
                      "|---|---|---|---|---|---|---|"]
            for r in rank[:5]:
                a = r.get("admit") or {}
                combo = (f"cm={a.get('close_mitigation')} "
                         f"brk={a.get('break_pct_max')} "
                         f"age={a.get('age_bars_max')} tail={a.get('tail_n')}")
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

    out = ["# POST-CONFIG ANALYSIS - all configs, all findings", "",
           "Source: output_audit/postconfig_ledger.json plus each config's "
           "_grid_auto.json and _spot_check.json (written by "
           "scripts/run_postconfig.py); rendered by scripts/postconfig_doc.py; "
           "per CHECKLIST #77.", "",
           "REGENERATED WHOLE at every config landing. Replaces the per-config "
           "report cards (B2198/B2208), which reported step STATUS rather than "
           "step FINDINGS.", "",
           "## How much confidence these checks earn", "",
           f"**Across the entire ledger ({len(ledger)} entries), {total} named "
           f"checks have run and {bad} have ever returned non-PASS.**"]
    if bad == 0:
        out += ["", "**Read that as a caution, not a reassurance.** A check "
                "that has never failed has not been shown capable of failing, "
                "so an all-green battery is WEAK evidence. The checks that "
                "would carry real weight are ones with a demonstrated failure "
                "mode - a deliberately corrupted cube proving they trip. Until "
                "then, green means 'nothing obviously wrong was detected', "
                "never 'this cube is correct'."]
    out += ["", f"## Index - {len(graded)} graded config(s), newest first", "",
            "| config | best is_ci_lo | vs floor | fires | starved | steps run |",
            "|---|---|---|---|---|---|"]
    for c in graded:
        grid = json.loads((AUDIT / (c + "_grid_auto.json")).read_text(encoding="utf-8"))
        rank = grid.get("step1_ranking") or []
        top = rank[0] if rank else {}
        cl = top.get("is_ci_lo")
        res = grid.get("results") or []
        starved = sum(1 for r in res if r.get("verdict") == "NO_EXIT_SELECTABLE")
        entry = ledger.get(c, {})
        done = sum(1 for v in entry.values() if v.get("status") == "DONE")
        steps = sum(1 for v in entry.values()
                    if v.get("status") in ("DONE", "SKIPPED"))
        out.append(f"| {c} | {cl if cl is not None else '-'} | "
                   f"{'ABOVE' if (cl is not None and cl > NOISE_FLOOR) else 'below'} | "
                   f"{top.get('fires', '-')} | {starved}/{len(res)} | "
                   f"{done}/{steps} |")
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
