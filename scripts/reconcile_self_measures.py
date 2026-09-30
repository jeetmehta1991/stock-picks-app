#!/usr/bin/env python
"""S6-B2294 (B3139): cross-validate the repo's SELF-MEASURING tools against an
INDEPENDENT source, so a tool that grades this project's own compliance is
never the only witness to its own correctness.

WHY. The ticket (B2294) named the class: a reconciliation run by hand is a
cross-check nobody runs. The council deferred it until a third hand-run or a
reconciliation that FAILED; both happened - B3097 (the discipline hook
reported delivery while 2 KB of 367.5 KB reached context, L871) and B3102
(the turn gate's window was blind to mid-turn instructions, L795). And the
first run of this script failed on the ledger: 60 S6-LANDING-* rows the
landing supervisor writes are in NEITHER queue_state.tickets() NOR
queue_state.unparsed() (the id charset has no underscore), so every six-class
count reported from queue_state has silently excluded them (S6-B3139n).

EACH CHECK PAIRS A TOOL WITH A SOURCE IT DOES NOT SHARE CODE WITH:
  queue       queue_state.tickets() + unparsed()  vs  a cell-split parse of
              every row whose first cell is a bold S6 id (no regex shared)
  landings    postconfig_landing.undelivered()    vs  a raw json read of the
              landings record, last event per cube
  ledger      the landings record's cubes          vs  postconfig_ledger.json:
              every landed cube carries all nine battery steps (B2520)
  gate_reach  verify_turn_compliance's scan_ gates vs  the module's own call
              graph from main() - a gate no entry point reaches is defined,
              proven, reported live and never run (the B1751 class)

Read-only. Exit 0 = every check agrees; 1 = a disagreement (each named);
3 = an input unreadable (a check that cannot see says so - L642).
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "EXECUTION_QUEUE.md").is_file():          # L846 marker rule
    raise SystemExit(f"reconcile_self_measures: {ROOT} is not the repo root (L846)")
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

QUEUE = ROOT / "EXECUTION_QUEUE.md"
LEDGER = ROOT / "output_audit" / "postconfig_ledger.json"
VTC = ROOT / "scripts" / "verify_turn_compliance.py"


# ------------------------------------------------------------------ queue
def raw_queue_states(text: str) -> dict:
    """{id: state} by SPLITTING cells - no regex shared with queue_state.
    A row counts when its first cell is a bold S6 id and its second a bold
    word; the last row per id wins (the ledger is an append log)."""
    out = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) < 4:
            continue
        c1, c2 = cells[1].strip(), cells[2].strip()
        if not (c1.startswith("**S6-") and c1.endswith("**") and len(c1) > 7):
            continue
        if not (c2.startswith("**") and c2.endswith("**") and len(c2) > 4):
            continue
        out[c1[2:-2]] = c2[2:-2]
    return out


def check_queue(text: str, tickets: dict, unparsed: dict) -> dict:
    raw = raw_queue_states(text)
    qs = {k: (v if isinstance(v, str) else (v or {}).get("state")) for k, v in tickets.items()}
    invisible = sorted(i for i in raw if i not in qs and i not in unparsed)
    phantom = sorted(i for i in qs if i not in raw)
    mismatch = sorted(i for i in raw if i in qs and qs[i] != raw[i])
    ok = not (invisible or phantom or mismatch)
    return {"check": "queue", "ok": ok,
            "raw_ids": len(raw), "reducer_ids": len(qs), "reducer_unparsed": len(unparsed),
            "invisible_to_reducer": len(invisible), "invisible_sample": invisible[:5],
            "invisible_states": _count(raw[i] for i in invisible),
            "reducer_only": phantom[:5], "state_mismatch": mismatch[:5]}


def _count(it) -> dict:
    c: dict = {}
    for x in it:
        c[x] = c.get(x, 0) + 1
    return c


# ------------------------------------------------------------------ landings
def raw_undelivered(lines) -> set:
    """Cubes whose LAST event in the record says reported_to_owner falsy,
    read with json alone (no postconfig_landing code)."""
    last = {}
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if isinstance(ev, dict) and ev.get("cube"):
            last[ev["cube"]] = ev
    return {c for c, ev in last.items() if not ev.get("reported_to_owner")}


def check_landings(lines, reducer_undelivered) -> dict:
    raw = raw_undelivered(lines)
    red = {ev.get("cube") for ev in reducer_undelivered}
    return {"check": "landings", "ok": raw == red, "raw_undelivered": sorted(raw),
            "reducer_undelivered": sorted(red),
            "only_raw": sorted(raw - red), "only_reducer": sorted(red - raw)}


# ------------------------------------------------------------------ ledger
def check_ledger(lines, ledger: dict, steps: list) -> dict:
    cubes = set()
    for ln in lines:
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if isinstance(ev, dict) and ev.get("cube"):
            cubes.add(ev["cube"])
    missing = sorted(c for c in cubes if c not in ledger)
    short = sorted(c for c in cubes if c in ledger
                   and sorted(ledger[c]) != sorted(steps))
    return {"check": "ledger", "ok": not (missing or short), "landed_cubes": len(cubes),
            "missing_from_ledger": missing[:5], "not_nine_steps": short[:5]}


# ------------------------------------------------------------------ gate reach
def check_gate_reach(src: str) -> dict:
    t = ast.parse(src)
    funcs = {n.name: n for n in t.body if isinstance(n, ast.FunctionDef)}
    refs = {name: {x.id for x in ast.walk(node) if isinstance(x, ast.Name)} & set(funcs)
            for name, node in funcs.items()}
    seen, todo = set(), ["main"]
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.add(f)
        todo.extend(refs.get(f, ()))
    scans = sorted(n for n in funcs if n.startswith("scan_"))
    unreached = [s for s in scans if s not in seen]
    return {"check": "gate_reach", "ok": bool(scans) and "main" in funcs and not unreached,
            "scan_gates": len(scans), "unreached": unreached}


# ------------------------------------------------------------------ run
def run(root: Path = ROOT) -> list[dict]:
    """Every check on ONE snapshot per input: the queue text is read once and
    handed to both parsers (a row appended between two reads would otherwise
    read as a disagreement), and the landings lines once for both of theirs."""
    import tempfile

    import postconfig_landing as pl
    import queue_state as qs
    from verify_postconfig_complete import STEPS
    text = (root / "EXECUTION_QUEUE.md").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as d:
        snap = Path(d) / "EXECUTION_QUEUE.md"
        snap.write_text(text, encoding="utf-8")
        results = [check_queue(text, qs.tickets(snap), qs.unparsed(snap))]
    lines = pl.LANDINGS.read_text(encoding="utf-8").splitlines() if pl.LANDINGS.exists() else []
    results.append(check_landings(lines, pl.undelivered_events(
        [json.loads(x) for x in lines if x.strip() and _is_json(x)])))
    ledger = json.loads((root / "output_audit" / "postconfig_ledger.json").read_text(encoding="utf-8"))
    results.append(check_ledger(lines, ledger, list(STEPS)))
    results.append(check_gate_reach(
        (root / "scripts" / "verify_turn_compliance.py").read_text(encoding="utf-8")))
    return results


def _is_json(line: str) -> bool:
    try:
        json.loads(line)
    except ValueError:
        return False
    return True


def main(argv=None) -> int:
    try:
        results = run()
    except (OSError, ValueError) as exc:
        print(f"[reconcile] UNREADABLE: {exc!r}")
        return 3
    for r in results:
        detail = {k: v for k, v in r.items() if k not in ("check", "ok")}
        print(f"{'AGREE   ' if r['ok'] else 'DISAGREE'} {r['check']:11s} {json.dumps(detail, default=str)}")
    bad = [r["check"] for r in results if not r["ok"]]
    print("VERDICT:", "all self-measures agree with their independent sources"
          if not bad else f"{len(bad)} of {len(results)} checks DISAGREE: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
