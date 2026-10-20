"""S6-B3227: strategy docstrings that LIST a gate set, read against the gate.

WHY: docstrings and producer docs describe gates too, and they drift from
the code the way signals_used lists (S6-B3139c) and context bullets
(S6-B3221) did - morning_star's Gates section said its RSI band rejected
fires deep in oversold territory while rsi_14 < 45 admits them, and
52wh_break_retest's 'Post-B605 7-gate set' kept two legs the live gate no
longer reads. A docstring reaches no trade log and no agent, so this is a
reviewing aid with a ratchet, not a gate on behaviour.

WHAT IT MEASURES, per registered strategy: every docstring BLOCK that lists
a gate set - a line naming an 'N-gate set', a 'gate structure', 'gates per
direction', a 'Gates:' heading or 'Producer signals:', up to the next blank
line - and the signal keys that block names which the strategy's fire
decision does NOT read (the keys come from scripts/signals_used_lint.py's
side model; a token counts as a key when some registered strategy reads it,
or it starts vol_/above_/below_). History prose names dropped keys on
purpose, so a flag is a candidate, never a verdict (L823): the B3139q-r82
census hand-read all 30 blocks across 28 strategies, corrected every
drifted one with a 'CURRENT GATE (S6-B3227 census, ...)' note beside the
history, and recorded the flags that remain - history and mirror mentions -
in output_audit/b3227_docstring_census_reviewed.json with a reason each.

THE RATCHET (test_b3227_docstring_gate_listings_match_the_reviewed_register):
the live flags must EQUAL the register. A gate edit that drops a key a
listing still names adds a flag and fails until the docstring is corrected
and the register re-reviewed; a corrected docstring shrinks the register.
What it cannot see: a key the gate reads that a listing omits, and prose
that states a condition without naming a key.

    python scripts/docstring_gate_census.py             # report
    python scripts/docstring_gate_census.py --json PATH # per-strategy flags
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if not (ROOT / "backtest" / "signals" / "screener.py").is_file():
    raise SystemExit(f"{ROOT} is not the repository root - refusing")
for p in (ROOT, ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

REVIEWED = ROOT / "output_audit" / "b3227_docstring_census_reviewed.json"
HEAD = re.compile(r"(\d+-gate set|gate set|-gate structure|gates per direction|^\s*Gates[:( ]"
                  r"|Producer signals:)", re.I)
TOKEN = re.compile(r"[a-z][a-z0-9_]{3,}")
KEY_PREFIXES = ("vol_", "above_", "below_")


def census():
    """(flags, blocks): flags = {strategy: sorted keys a listing block names
    and the gate does not read}, only strategies with any; blocks = the
    number of listing blocks read."""
    import signals_used_lint as sul
    from backtest.signals import screener
    mod = sul.Module.of(screener)
    fns = [n for n in mod.tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("strat_")]
    reads, every_key = {}, set()
    for fn in fns:
        keys = {v for s in sul.analyse_function(mod, fn) for t, v in s.get("feeds", []) if t == "lit"}
        reads[fn.name] = keys
        every_key |= keys
    flags, blocks = {}, 0
    for fn in fns:
        lines = (ast.get_docstring(fn) or "").splitlines()
        named = set()
        for i, ln in enumerate(lines):
            if not HEAD.search(ln):
                continue
            blocks += 1
            block = [ln]
            for nxt in lines[i + 1:]:
                if not nxt.strip():
                    break
                block.append(nxt)
            named |= {t for t in TOKEN.findall(" ".join(block))
                      if t in every_key or t.startswith(KEY_PREFIXES)}
        stray = sorted(named - reads[fn.name] - {"borrow_ok"})
        if stray:
            flags[fn.name[len("strat_"):]] = stray
    return flags, blocks


def load_reviewed(path=REVIEWED):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    rev = d["reviewed"]
    for name, entry in rev.items():
        if not (entry.get("why") or "").strip():
            raise ValueError(f"{name}: a reviewed flag carries its reason")
    return {k: sorted(v["keys"]) for k, v in rev.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--json", help="write the per-strategy flags here")
    a = ap.parse_args(argv)
    flags, blocks = census()
    print(f"listing blocks {blocks}; strategies with a listed key the gate does not read "
          f"{len(flags)}")
    for k, v in sorted(flags.items()):
        print(f"  {k}: {', '.join(v)}")
    if a.json:
        Path(a.json).write_text(json.dumps(flags, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
