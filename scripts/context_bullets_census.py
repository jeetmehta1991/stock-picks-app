"""S6-B3221: census of every strategy's context_bullets against the gate it
describes.

WHY: a strategy's context_bullets ride every fire into the trade log
(backtest/engine/backtest.py -> exit_manager.ClosedTrade) and the site's
technical bullets (backtest/results/site_generator.py). A bullet that states a
threshold or names a signal can drift from the gate exactly as the
signals_used lists did (S6-B3139c): strat_rsi_overbought_short's first bullet
said RSI-14 'above 68' while its gate has read rsi_14 > 65 since B1140.

WHAT IT MEASURES, per declaration side (a _strat3 has a long and a short side;
the side model and the gate-key closure are scripts/signals_used_lint.py's):

  numbers   every number in a bullet's static text (an f-string's literal
            parts only - a formatted value prints the live reading, so it
            cannot drift). Each is classed
              GATE     equal to a constant the side's gate compares against
                       (as written, x100 as a percentage, or /100; the shared
                       borrow helper's dtc > 5 is not counted);
              KEYNAME  part of a key the gate reads or the bullet displays, of
                       the strategy's own name, or a vol_spike_NNx multiplier
                       (vol_spike_15x is 1.5x - names are decimal-shifted);
              HISTORY  a prior value ('was 35', 'loosened from 40', 'from
                       62-79', 'dropped the 252d-low anchor');
              REF      a batch or ticket reference ('Batch 358', '#44');
              CITE     a four-digit year (a literature citation);
              FREE     none of these - a claim the census cannot settle.
  keys      every snake_case token in a bullet's static text that is a key the
            screener's strategies read, classed READ (the side's gate reads
            it), DISPLAY (only the bullet's own formatted values read it) or
            NOT-READ.

  A FREE number passes only as a member of the reviewed register,
  output_audit/b3221_bullet_census_reviewed.json (DATA, not code - CSV-first):
  a reader compared it against the gate and the producer and found it true.
  A producer-sourced group carries ANCHORS - the producer lines the number
  comes from, with their occurrence counts - so a producer edit that moves the
  constant moves the count and fails the check until the bullet is re-read.

  WHAT --check CATCHES: a gate constant changed under a bullet that states it
  (the number falls from GATE to FREE); a key swapped under a bullet that
  states the old multiplier ('Volume 1.5x' over vol_above_avg); a bullet naming
  a key its gate does not read; a new unreviewed number; a reviewed producer
  constant changed (its anchor count moves); a register member that no longer
  needs reviewing (stale - the register shrinks with the code); one of the 80
  corrected bullet texts coming back on its side (the register's 'retired'
  list). WHAT IT CANNOT
  SEE: the prose shape - a bullet asserting a condition its gate no longer
  tests, with no number and no key ('Bearish bar - rejection of stop-hunt
  extension' after B1145 dropped the bar gate). S6-B3221 read all 283 live
  sides for that shape; it stays a reading task (runbook §1.7).

    python scripts/context_bullets_census.py             # report
    python scripts/context_bullets_census.py --json PATH # per-side rows
    python scripts/context_bullets_census.py --check     # exit 1 on any of the above

Pinned by test_b3221_bullet_numbers_and_keys_match_the_gate.
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import signals_used_lint as L  # noqa: E402

# declaration helper -> bullet argument positions / keywords
BULLET_POS = {"_strat": (4,), "_strat3": (5, 6), "_strat_signal": (4,)}
BULLET_KW = {"_strat": ("context_bullets",), "_strat3": ("bullets_long", "bullets_short"),
             "_strat_signal": ("bullets",)}
NUM = re.compile(r"(?<![A-Za-z0-9_.])(\d+(?:\.\d+)?)([%x]?)")
SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
OPS = {ast.Gt: ">", ast.GtE: ">=", ast.Lt: "<", ast.LtE: "<=", ast.Eq: "==", ast.NotEq: "!="}

# The reviewed register (S6-B3221): FREE numbers a reader compared against the
# gate and the producer and found TRUE, grouped by reason, keyed (strategy,
# side, bullet index, token). --check passes only these.
REVIEWED_PATH = ROOT / "output_audit" / "b3221_bullet_census_reviewed.json"


def load_reviewed(path=None):
    p = Path(path) if path else REVIEWED_PATH
    return json.loads(p.read_text(encoding="utf-8"))["groups"]


def load_retired(path=None):
    """[strategy, side, text] for every bullet S6-B3221 corrected or removed -
    the census-rendered text (an f-string's values shown as {...})."""
    p = Path(path) if path else REVIEWED_PATH
    return json.loads(p.read_text(encoding="utf-8"))["retired"]


def retired_recurrences(rows, retired=None):
    """Retired texts present again in their side's bullets - a correction
    reverted, or a stale bullet copied back from an old version."""
    have = {(r["strategy"], r["side"]): {b["text"] for b in r.get("bullets", []) if "text" in b}
            for r in rows}
    return [t for t in (load_retired() if retired is None else retired)
            if t[2] in have.get((t[0], t[1]), set())]


def reviewed_members(groups):
    return {tuple(m) for g in groups for m in g["members"]}


def anchor_problems(groups, root=None):
    """Every anchor whose occurrence count in its file is not the recorded
    one: (why, file, snippet, recorded, found)."""
    base = Path(root) if root else ROOT
    out = []
    for g in groups:
        for a in g["anchors"]:
            p = base / a["file"]
            got = p.read_text(encoding="utf-8").count(a["snippet"]) if p.exists() else 0
            if got != a["count"]:
                out.append((g["why"], a["file"], a["snippet"], a["count"], got))
    return out


def _num(node):
    """The numeric value of a constant (or a negated one), else None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
            and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _num(node.operand)
        return -v if v is not None else None
    return None


def _is_get(n, sname):
    return (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get"
            and isinstance(n.func.value, ast.Name) and n.func.value.id == sname)


def _gate_exprs(expr, fn, mod, assigns, guards):
    """Every expression that decides the side's fire: the fires argument, the
    early-return guard tests, each assignment its names read (transitively, the
    control-dependence tests included - the lint's model), and the body of every
    module-level helper called with the signal dict."""
    sname = fn.args.args[0].arg
    out, todo, done, helpers = [], [expr] + guards, set(), set()
    while todo:
        e = todo.pop(0)
        out.append((e, sname))
        for n in ast.walk(e):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in assigns \
                    and n.id not in done:
                done.add(n.id)
                todo += assigns[n.id]
            # the borrow helper's dtc > 5 is the shared short-borrow gate, not
            # a threshold a bullet states; expanding it would let every short
            # bullet's 5, 0.05 or 500 pass as a gate match by coincidence
            if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in mod.funcs
                    and n.func.id not in helpers and not n.func.id.startswith("strat_")
                    and n.func.id != L.BORROW_HELPER
                    and any(isinstance(a, ast.Name) and a.id == sname for a in n.args)):
                helpers.add(n.func.id)
                h = mod.funcs[n.func.id]
                hs = h.args.args[0].arg if h.args.args else sname
                out += [(st, hs) for st in h.body]
    return out


def gate_profile(exprs, mod):
    """The side's comparisons (operand source, operator, constant) and the set
    of numeric constants it compares against; a .get default is not a
    threshold and is kept apart."""
    comps, consts, defaults = [], set(), set()
    for e, sname in exprs:
        for n in ast.walk(e):
            if _is_get(n, sname) and len(n.args) > 1 and _num(n.args[1]) is not None:
                defaults.add(_num(n.args[1]))
            if isinstance(n, ast.Compare):
                terms = [n.left] + list(n.comparators)
                for a, op, b in zip(terms, n.ops, terms[1:]):
                    for x, y in ((a, b), (b, a)):
                        v = _num(y)
                        if v is not None and _num(x) is None:
                            comps.append([mod.seg(x) or ast.unparse(x), OPS.get(type(op), "?"), v])
                            consts.add(v)
            elif isinstance(n, (ast.BinOp,)):
                for side in (n.left, n.right):
                    v = _num(side)
                    if v is not None:
                        consts.add(v)
    return comps, consts, defaults


def _spike(key):
    m = re.fullmatch(r"vol_spike_(\d+)x", key)
    if not m:
        return None
    d = m.group(1)
    return float(d[0] + "." + d[1:]) if len(d) == 2 else float(d)


def _bullet_parts(e, mod):
    """(static text with {..} for each formatted value, the keys the bullet's
    formatted values read)."""
    if isinstance(e, ast.Constant) and isinstance(e.value, str):
        return e.value, []
    if isinstance(e, ast.JoinedStr):
        txt, reads = [], []
        for v in e.values:
            if isinstance(v, ast.Constant):
                txt.append(str(v.value))
            else:
                txt.append("{" + (mod.seg(v.value) or ast.unparse(v.value)) + "}")
                for n in ast.walk(v.value):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                            and n.func.attr == "get" and n.args \
                            and isinstance(n.args[0], ast.Constant):
                        reads.append(n.args[0].value)
        return "".join(txt), reads
    return None, []


def _static_only(text):
    return re.sub(r"\{[^{}]*\}", " ", text)


# a prior value: 'was 35', 'loosened from 40', 'loosened 2% -> 3%', 'dropped
# the 252d-low anchor', 'pre-B2076 used ~90-bar'
HISTORY_BEFORE = re.compile(
    r"(?:\bwas|\bfrom|\bloosened|\bdropped the|\bused)\s*[~<>=+-]*\s*$")
# a range or pair continuing a prior value ('from 62-79', 'was <5 / <35'); an
# arrow ('2% -> 3%') introduces the CURRENT value, so it never chains
CHAIN_BEFORE = re.compile(r"^\s*(?:-(?!>)|/|or)\s*[<>=+]*\s*$")
REF_BEFORE = re.compile(r"(?:\bBatch\s+|#|\bDEC-|\bCouncil\s+)$")


def classify_number(n, suffix, consts, key_tokens, before="", prev=None):
    """GATE / KEYNAME / HISTORY / REF / CITE / FREE for one number.
    `before` is the static text just before it; `prev` is the previous
    number in the same bullet as (end offset, class) - a number chained to
    a HISTORY number ('was <5 / <35', 'from 62-79') is HISTORY too."""
    v = float(n)
    for c in consts:
        a = abs(c)
        if any(abs(v - t) < 1e-9 for t in (a, a * 100, a / 100)):
            return "GATE"
    if n in key_tokens or (suffix == "x" and v in key_tokens.get("__spike__", set())):
        return "KEYNAME"
    if v in key_tokens.get("__spike__", set()):
        return "KEYNAME"
    if HISTORY_BEFORE.search(before[-16:]):
        return "HISTORY"
    if prev is not None and prev[1] == "HISTORY" and CHAIN_BEFORE.match(before[prev[0]:]):
        return "HISTORY"
    if REF_BEFORE.search(before[-12:]):
        return "REF"
    if suffix == "" and "." not in n and len(n) == 4 and 1900 <= int(n) <= 2035:
        return "CITE"
    return "FREE"


def _stage(name, mod, fn, every_key, staged):
    """Stage the declaration sides of one strategy function (the gate side
    of the census); every_key collects the keys any strategy reads."""
    assigns = L._assignments(fn)
    guards = []
    for n in ast.walk(fn):
        if isinstance(n, ast.If) and any(
                isinstance(b, ast.Return) and L._is_decl(b.value)
                and isinstance(b.value.args[0], ast.Constant) for b in n.body):
            guards.append(n.test)
    for c in [c for c in ast.walk(fn) if L._is_decl(c)]:
        fire_ix = L.DECL[c.func.id][0]
        bl = [c.args[i] if i < len(c.args) else None for i in BULLET_POS[c.func.id]]
        for kw in c.keywords:
            if kw.arg in BULLET_KW[c.func.id]:
                bl[BULLET_KW[c.func.id].index(kw.arg)] = kw.value
        for si, (fx, b) in enumerate(zip([c.args[i] for i in fire_ix], bl)):
            side = ("long", "short")[si] if c.func.id == "_strat3" else "single"
            rec = {"strategy": name, "side": side, "function": fn.name,
                   "module": mod.path.name, "line": c.lineno}
            if isinstance(fx, ast.Constant):
                rec["status"] = "CONSTANT_FIRES"
                staged.append((rec, None, None, None, None))
                continue
            exprs = _gate_exprs(fx, fn, mod, assigns, guards)
            allk = list(L._closure(fx, fn, mod, assigns))
            for g in guards:
                allk += L._closure(g, fn, mod, assigns)
            feeds = list(dict.fromkeys(v for t, v in allk if t == "lit"))
            # a key built at runtime (an f-string over a span knob) is kept as
            # its source text - the census cannot class a bullet against it,
            # and says so in the row
            rec["gate_keys_built"] = list(dict.fromkeys(v for t, v in allk if t == "dyn"))
            every_key.update(feeds)
            staged.append((rec, exprs, feeds, b, mod))


def census():
    """One row per live declaration side with a literal bullet list."""
    from backtest.signals import index_rebalance, screener
    from backtest.signals.screener import ALL_STRATEGIES
    mods = {"backtest.signals.screener": L.Module.of(screener),
            "backtest.signals.index_rebalance": L.Module.of(index_rebalance)}
    every_key = set()
    staged = []
    for name, f in ALL_STRATEGIES.items():
        mod = mods[f.__module__]
        fn = mod.funcs[f.__name__]
        body = [b for b in fn.body
                if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))]
        if (len(body) == 1 and isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.Call)
                and isinstance(body[0].value.func, ast.Name)):
            tgt = getattr(screener, body[0].value.func.id, None)
            if getattr(tgt, "__module__", None) in mods and tgt.__module__ != f.__module__:
                mod = mods[tgt.__module__]
                fn = mod.funcs[tgt.__name__]
        _stage(name, mod, fn, every_key, staged)
    return _classify(staged, every_key)


def census_source(src, extra_keys=()):
    """The census over a toy module source - every function named strat_X
    is a strategy named X (the seam the pin's must-fire cases use).
    extra_keys stands in for keys OTHER strategies read."""
    mod = L.Module(src)
    every_key = set(extra_keys)
    staged = []
    for fname, fn in mod.funcs.items():
        if fname.startswith("strat_"):
            _stage(fname[len("strat_"):], mod, fn, every_key, staged)
    return _classify(staged, every_key)


def _classify(staged, every_key):
    rows = []
    for rec, exprs, feeds, b, mod in staged:
        if exprs is None:
            rows.append(rec)
            continue
        comps, consts, defaults = gate_profile(exprs, mod)
        rec.update(gate_keys=feeds, comparisons=comps, defaults=sorted(defaults))
        if not isinstance(b, (ast.List, ast.Tuple)):
            rec["status"] = "NONLITERAL_BULLETS"
            rec["bullets_source"] = mod.seg(b) if b is not None else None
            rows.append(rec)
            continue
        rec["status"] = "OK"
        bullets = []
        for i, e in enumerate(b.elts):
            text, reads = _bullet_parts(e, mod)
            if text is None:
                bullets.append({"i": i, "kind": "other", "source": mod.seg(e)})
                continue
            kt = {}
            for k in list(feeds) + reads + [rec["strategy"]]:
                for tok in re.findall(r"\d+(?:\.\d+)?", k):
                    kt[tok] = True
                sp = _spike(k)
                if sp is not None:
                    kt.setdefault("__spike__", set()).add(sp)
            static = _static_only(text)
            nums, prev = [], None
            for m in NUM.finditer(static):
                cls = classify_number(m.group(1), m.group(2), consts, kt,
                                      static[:m.start()], prev)
                nums.append({"n": m.group(1), "suffix": m.group(2), "class": cls})
                prev = (m.end(), cls)
            keys = []
            for tok in dict.fromkeys(SNAKE.findall(static)):
                if tok in feeds:
                    keys.append({"key": tok, "class": "READ"})
                elif tok in reads:
                    keys.append({"key": tok, "class": "DISPLAY"})
                elif tok in every_key:
                    keys.append({"key": tok, "class": "NOT-READ"})
            bullets.append({"i": i, "kind": "fstring" if reads or "{" in text else "static",
                            "text": text, "display_reads": reads, "numbers": nums, "keys": keys})
        rec["bullets"] = bullets
        rows.append(rec)
    return rows


def unsettled(rows):
    """(strategy, side, bullet index, token, class) for every FREE number and
    NOT-READ key, reviewed or not."""
    out = []
    for r in rows:
        for bl in r.get("bullets", []):
            for x in bl.get("numbers", []):
                if x["class"] == "FREE":
                    out.append((r["strategy"], r["side"], bl["i"], x["n"] + x["suffix"], "FREE"))
            for x in bl.get("keys", []):
                if x["class"] == "NOT-READ":
                    out.append((r["strategy"], r["side"], bl["i"], x["key"], "NOT-READ"))
    return list(dict.fromkeys(out))


def candidates(rows, groups=None):
    """The unsettled tokens the reviewed register does not cover. A NOT-READ
    key is never reviewable: a bullet naming a key its gate does not read is
    corrected, not excused."""
    members = reviewed_members(load_reviewed() if groups is None else groups)
    return [c for c in unsettled(rows) if c[4] == "NOT-READ" or c[:4] not in members]


def stale_reviewed(rows, groups=None):
    """Register members that are no longer unsettled - the bullet changed,
    or its number now matches the gate. The register shrinks with the code
    (#279: an exclusion register is checked in both directions)."""
    live = {c[:4] for c in unsettled(rows) if c[4] == "FREE"}
    members = reviewed_members(load_reviewed() if groups is None else groups)
    return sorted(members - live)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 on an unreviewed FREE number, a NOT-READ key, a stale "
                         "register member or a moved producer anchor")
    ap.add_argument("--json", help="write the per-side rows here")
    a = ap.parse_args(argv)
    rows = census()
    groups = load_reviewed()
    live = [r for r in rows if r.get("status") == "OK"]
    nb = sum(len(r["bullets"]) for r in live)
    cls = {}
    for r in live:
        for bl in r["bullets"]:
            for x in bl.get("numbers", []):
                cls[x["class"]] = cls.get(x["class"], 0) + 1
            for x in bl.get("keys", []):
                cls["key " + x["class"]] = cls.get("key " + x["class"], 0) + 1
    cand = candidates(rows, groups)
    stale = stale_reviewed(rows, groups)
    moved = anchor_problems(groups)
    back = retired_recurrences(rows)
    print(f"sides {len(rows)} (live with literal bullets {len(live)}); bullets {nb}; "
          f"classes {dict(sorted(cls.items()))}; register {len(reviewed_members(groups))} "
          f"members in {len(groups)} groups; unreviewed {len(cand)}; stale {len(stale)}; "
          f"moved anchors {len(moved)}; retired texts back {len(back)}")
    for c in cand:
        print("  UNREVIEWED", c)
    for m in stale:
        print("  STALE REGISTER MEMBER", m)
    for p in moved:
        print("  MOVED ANCHOR", p[1], repr(p[2]), "recorded", p[3], "found", p[4], "-", p[0])
    for t in back:
        print("  RETIRED TEXT BACK", t)
    for r in rows:
        if r.get("status") not in ("OK",):
            print("  STATUS", r["strategy"], r["side"], r["status"])
    if a.json:
        Path(a.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return 1 if (a.check and (cand or stale or moved or back)) else 0


if __name__ == "__main__":
    sys.exit(main())
