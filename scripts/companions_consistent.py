#!/usr/bin/env python
# Source: two institutional_companion_screen.py artifacts per CHECKLIST #77.
"""scripts/companions_consistent.py - runbook 3.6 steps 1-2, the generic form
(S6-B3291b, B3139q-r107): the consistent-sign intersection of two companion
screens (the same strategy at the two runbook exits, time_stop_10d and
breakeven_plus_trail), clustered by the producer MODULE that writes each key
(build_table_a's module index, the one inventory the Table A renderer uses),
with ONE representative per cluster chosen by the stated criterion (#165):
the largest joint effect, min(|effect_ts10|, |effect_bept|), where a boolean's
effect is pnl_lift and a numeric's is q5_minus_q1.

The b3117 bollinger_lower artifact was built by a one-off script that was
never committed (its _doc line names the rule); this module is that rule as
a tool, so the next family runs it instead of re-deriving it.

A SCREEN, never a gate - B-row registration happens at the T3 owner band
review (runbook 3.6 item 4).

    python scripts/companions_consistent.py --a <ts10.json> --b <bept.json> \
        --strategy squeeze_breakout --out output_audit/<batch>_<strategy>_companions_consistent.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def _effect(r: dict) -> float:
    return float(r["pnl_lift"] if r["kind"] == "bool" else r["q5_minus_q1"])


def consistent(a: dict, b: dict) -> list[dict]:
    """FDR survivors in BOTH screens whose effect sign agrees."""
    ra = {r["key"]: r for r in a["results"] if r.get("fdr_survivor")}
    rb = {r["key"]: r for r in b["results"] if r.get("fdr_survivor")}
    out = []
    for k in sorted(set(ra) & set(rb)):
        ea, eb = _effect(ra[k]), _effect(rb[k])
        if ea == 0 or eb == 0 or (ea > 0) != (eb > 0):
            continue
        out.append({"key": k, "kind": ra[k]["kind"], "effect_a": ea, "effect_b": eb,
                    "joint": min(abs(ea), abs(eb)), "p_a": ra[k]["p"], "p_b": rb[k]["p"],
                    "sign": "+" if ea > 0 else "-"})
    return out


def cluster(rows: list[dict], module_of) -> dict:
    """key -> producer module (build_table_a._module_index); unknown keys go
    to their own 'unindexed' cluster so nothing is silently dropped."""
    clusters: dict[str, list] = {}
    for r in rows:
        mod = module_of(r["key"]) or "unindexed"
        r["module"] = mod
        clusters.setdefault(mod, []).append(r)
    out = {}
    for mod, members in clusters.items():
        members.sort(key=lambda r: -r["joint"])
        out[mod] = {"representative": members[0]["key"],
                    "criterion": "max joint effect min(|a|, |b|) (#165)",
                    "members": [m["key"] for m in members], "rows": members}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="screen artifact at exit A (time_stop_10d)")
    ap.add_argument("--b", required=True, help="screen artifact at exit B (breakeven_plus_trail)")
    ap.add_argument("--strategy", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    a = json.loads(Path(args.a).read_text(encoding="utf-8"))
    b = json.loads(Path(args.b).read_text(encoding="utf-8"))
    for name, art in (("a", a), ("b", b)):
        if art.get("peeked"):
            raise SystemExit(f"REFUSED: screen {name} read the holdout (peeked) - the consistent "
                             "set is an in-sample screen")
        want = [args.strategy]
        if art.get("selection") == "exact" and sorted(art.get("strategies") or []) != want:
            raise SystemExit(f"REFUSED: screen {name} selected {art.get('strategies')}, not {want}")
    rows = consistent(a, b)
    import build_table_a as bta
    idx = bta._module_index()      # [(module path, text, (written keys, ...))]

    def module_of(k):
        for mod, _text, written in idx:
            keys = written[0] if isinstance(written, tuple) else written
            if k in keys:
                return mod
        return None
    cl = cluster(rows, module_of)
    rec = {"_doc": "runbook 3.6 steps 1-2: consistent-sign BH-FDR survivors under BOTH exits, "
                   "clustered by the producer module that writes the key (build_table_a module "
                   "index); representative = max joint effect min(|a|, |b|) (#165). A SCREEN, "
                   "never a gate - B-row registration happens at the T3 owner band review.",
           "strategy": args.strategy, "exit_a": a["exit"], "exit_b": b["exit"],
           "screens": {"a": str(args.a), "b": str(args.b)},
           "survivors_a": a.get("survivors"), "survivors_b": b.get("survivors"),
           "n_consistent": len(rows), "clusters": cl}
    Path(args.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"{args.strategy}: {a.get('survivors')} + {b.get('survivors')} survivors -> "
          f"{len(rows)} consistent in {len(cl)} clusters -> {args.out}")
    for mod, c in sorted(cl.items(), key=lambda kv: -kv[1]["rows"][0]["joint"]):
        r = c["rows"][0]
        print(f"  {mod}: {c['representative']} ({r['kind']}, {r['sign']}, joint {r['joint']:.3f}; "
              f"{len(c['members'])} member(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
