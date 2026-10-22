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
  changed_since_r5  the strategy's FIRE LOGIC differs from the R5-era code -
                    its body and every function, module constant and config
                    value it reaches, with docstrings and the _strat payload
                    removed (S6-B3235: CodeSide / fire_logic_changes)
  survives_pct      share of R5 fires on which the LIVE strategy function
                    fires with the recorded direction (S6-B2814)
  survives_pct_by_side  the same share per recorded direction, {'long': x,
                    'short': y} for each side with R5 fires: a two-sided
                    strategy's sides can survive their current gates very
                    differently (S6-B3232 correction, B3139q-r80 - MEASURED
                    12 of 56 duals in the long shortlist), so a per-side
                    consumer must not scale by survives_pct; r5_fires_by_side
                    carries each side's denominator
  stream            TIGHTEN / LOOSEN / BOTH / NONE - see classify_stream
  ticket            the campaign's tickets from the OWNER-OPENED register,
                    output_audit/owner_campaign_opens.json (S6-B3194);
                    mention_tickets keeps every ledger row naming it
  admitted          present in phase_1b_step2_admissions.json
  status            one of eleven, mutually exclusive (B2825/B2833/
                    S6-B3135/S6-B3135a), decided by status_for():
                    DONE-ADMITTED / IN-ROSTER-FUNNEL / DONE-OWNER-CLOSED /
                    DISABLED / PRUNED-DUPLICATE / CLOSED-NEGATIVE /
                    CONTAINED-IN-REPRESENTATIVE (terminal)
                    IN-ROSTER-MIRROR / IN-CAMPAIGN / STALLED-CAMPAIGN /
                    NOT-STARTED (in lanes)

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
import copy
import hashlib
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

    A LOWER BOUND by construction: a threshold reached through a helper is
    invisible to a source pattern; one read inline from config as _cfg.<NAME>
    is matched since S6-B3171 (resolved to production by build_table_a).
    Stated in the artifact so the count is never read as total.
    """
    out = {}
    for n in ast.walk(ast.parse(src)):
        if not (isinstance(n, ast.FunctionDef) and n.name.startswith("strat_")):
            continue
        # S6-B3272 (r92 audit): strip the DOCSTRING before the regex - a
        # history note quoting a removed comparison is prose, not a gate
        # (ultimate_oscillator's 'uo' came from its B631 note and drove
        # its stream BOTH and shortlist lane for 40+ days). Pinned by
        # test_b3272.
        stmts = n.body
        if stmts and isinstance(stmts[0], ast.Expr) \
                and isinstance(stmts[0].value, ast.Constant):
            stmts = stmts[1:]
        body = "\n".join(ast.unparse(x) for x in stmts)
        keys = set(re.findall(
            r"s\.get\(f?['\"]([a-z0-9_{}]+)['\"][^)]*\)\s*[<>]=?\s*"
            r"(?:-?[0-9.]+|_cfg\.[A-Z0-9_]+)", body))  # S6-B3171: config-read RHS
        if keys:
            out[n.name[len("strat_"):]] = sorted(keys)
    return out


# S6-B3235 (B3139q-r84): THE FLAG MEANS THE FIRE LOGIC CHANGED. Until r84 it
# compared ast.unparse of each strat_ body with the R5-era screener, and that
# was wrong in BOTH directions - MEASURED at fd2c815be: 124 of its 160 flags
# were text edits (docstrings, and the signals_used lists and context bullets
# that _strat / _strat3 only pass through into the returned dict), while the
# 4 index-rebalance strategies, whose screener body is one delegation to
# backtest/signals/index_rebalance.py, read unchanged after S6-B3226 changed
# their fire logic there. Now a strategy's fire logic is a SET OF MEMBERS -
# its own body, every function it reaches (screener helpers, other strategies,
# a function imported from a signals module), the module constants and config
# values those read - each with docstrings, bare strings and the _strat
# payload removed; the flag fires when any member differs from its R5-era form
# or exists on one side only. Still an UPPER bound on behaviour (a span swap
# identical at its default counts), and blind to the producers that compute
# the signals - survives_pct, which replays the live function on R5's
# persisted signals, is the behavioural measure.
_PAYLOAD_ARGS = {"_strat": (3, 4), "_strat3": (3, 4, 5, 6),
                 "_strat_signal": (3, 4)}  # index_rebalance's _strat mirror
_PAYLOAD_KW = ("signals_used", "context_bullets", "signals_used_long",
               "signals_used_short", "bullets_long", "bullets_short")
_SIGNALS_PKG = "backtest.signals."
_SCREENER = "backtest.signals.screener"
_CONFIG = "backtest.config"

# A member whose change was REVIEWED as unable to move a fire decision, pinned
# to its stripped form at review (sha256, 16 hex). A later edit of the member
# voids its entry - its readers flag again - and test_b3235 fails on a stale
# or redundant entry, both directions (L587). MEASURED r84: the only member
# outside a strategy's own body that changed since R5 for a stripped-unchanged
# strategy is this pair, reached by 81 strategies through the borrow gate.
FIRE_NEUTRAL_CHANGES = {
    "fn:backtest.signals.screener:_short_borrow_trap_active": (
        "c736fa330e944493",
        "S6-B2118b instrumentation: counters added at the definition; the "
        "value returned, days_to_cover > 5.0, is the R5-era expression"),
    "value:backtest.signals.screener:_BORROW_TRAP_COUNTER": (
        "974950244a3ca6ad",
        "S6-B2118b: the counter dict that helper increments, read by "
        "borrow_trap_rate and by no fire decision"),
}


def member_digest(text) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()[:16]


def strip_fire_logic(node) -> str:
    """ast.unparse of a function with what no fire decision reads removed:
    docstrings and bare string statements in every block, and the PAYLOAD
    arguments of _strat / _strat3 (signals_used, context bullets). An AST
    carries no comments. The direction and category arguments stay - they
    ride the dict a trade is built from."""
    node = copy.deepcopy(node)
    for n in ast.walk(node):
        for block in ("body", "orelse", "finalbody"):
            stmts = getattr(n, block, None)
            if isinstance(stmts, list) and stmts:
                kept = [b for b in stmts if not (
                    isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant)
                    and isinstance(b.value.value, str))]
                setattr(n, block, kept or [ast.Pass()])
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id in _PAYLOAD_ARGS):
            for i in _PAYLOAD_ARGS[n.func.id]:
                if i < len(n.args):
                    n.args[i] = ast.Constant(None)
            n.keywords = [k for k in n.keywords if k.arg not in _PAYLOAD_KW]
    return ast.unparse(node)


class CodeSide:
    """One revision of the repo's strategy code - R5's or the working tree's
    - read module by module on demand. `sources` injects {module: text} (the
    test seam); anything absent is read at `rev` (git show) or, with rev None,
    from disk. A module missing at that revision reads as empty."""

    def __init__(self, rev=None, sources=None, root=None):
        self.rev, self.root = rev, Path(root or ROOT)
        self._src = dict(sources or {})
        self._idx = {}

    def source(self, module: str) -> str:
        if module not in self._src:
            rel = module.replace(".", "/") + ".py"
            if self.rev is None:
                p = self.root / rel
                self._src[module] = p.read_text(encoding="utf-8") if p.is_file() else ""
            else:
                self._src[module] = subprocess.run(
                    ["git", "show", f"{self.rev}:{rel}"], cwd=self.root,
                    capture_output=True, text=True, encoding="utf-8",
                    errors="replace", timeout=60).stdout
        return self._src[module]

    def index(self, module: str) -> dict:
        """Module-level functions, assigned values, and the names that alias
        the config module, a config value, or a signals-module function."""
        if module not in self._idx:
            src = self.source(module)
            tree = ast.parse(src) if src.strip() else ast.Module(body=[], type_ignores=[])
            ix = {"funcs": {}, "values": {}, "cfg_alias": set(), "cfg_name": {},
                  "imported": {}, "strategies": {}}
            for n in tree.body:
                if isinstance(n, ast.FunctionDef):
                    ix["funcs"][n.name] = n
                elif isinstance(n, ast.Assign):
                    for t in n.targets:
                        if isinstance(t, ast.Name):
                            ix["values"][t.id] = n.value
                elif (isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
                      and n.value is not None):
                    ix["values"][n.target.id] = n.value
                elif isinstance(n, ast.ImportFrom):
                    mod = n.module or ""
                    for a in n.names:
                        local = a.asname or a.name
                        if mod == "backtest" and a.name == "config":
                            ix["cfg_alias"].add(local)
                        elif mod == _CONFIG:
                            ix["cfg_name"][local] = a.name
                        elif mod.startswith(_SIGNALS_PKG):
                            ix["imported"][local] = (mod, a.name)
            for n in ast.walk(tree):
                if isinstance(n, ast.FunctionDef) and n.name.startswith("strat_"):
                    ix["strategies"].setdefault(n.name, n)
            self._idx[module] = ix
        return self._idx[module]

    def member_text(self, key: str):
        """The stripped text of one member id - 'fn:<module>:<name>' or
        'value:<module>:<name>' - on this side; None when it is absent."""
        kind, mod, name = key.split(":")
        ix = self.index(mod)
        node = (ix["funcs"] if kind == "fn" else ix["values"]).get(name)
        if node is None:
            return None
        return strip_fire_logic(node) if kind == "fn" else ast.unparse(node)

    def members(self, fn_node, module: str = _SCREENER) -> dict:
        """{member id: stripped text} - everything the function's fire
        decision can reach in the repo's own code."""
        out = {}

        def value(mod, name):
            key = f"value:{mod}:{name}"
            if key in out:
                return
            node = self.index(mod)["values"].get(name)
            out[key] = None if node is None else ast.unparse(node)
            if node is not None:
                walk(node, mod)

        def func(mod, name, node=None):
            key = f"fn:{mod}:{name}"
            if key in out:
                return
            node = node if node is not None else self.index(mod)["funcs"].get(name)
            out[key] = None if node is None else strip_fire_logic(node)
            if node is not None:
                walk(node, mod)

        def walk(node, mod):
            ix = self.index(mod)
            # a function-level import binds names too: the index-rebalance
            # shorts import _short_borrow_trap_active inside their bodies
            local = {}
            for n in ast.walk(node):
                if isinstance(n, ast.ImportFrom):
                    m2 = n.module or ""
                    for a in n.names:
                        if m2.startswith(_SIGNALS_PKG):
                            local[a.asname or a.name] = ("fn", (m2, a.name))
                        elif m2 == _CONFIG:
                            local[a.asname or a.name] = ("value", (_CONFIG, a.name))
            for n in ast.walk(node):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    if n.id in local:
                        kind, target = local[n.id]
                        (func if kind == "fn" else value)(*target)
                    elif n.id in ix["funcs"]:
                        func(mod, n.id)
                    elif n.id in ix["imported"]:
                        func(*ix["imported"][n.id])
                    elif n.id in ix["cfg_name"]:
                        value(_CONFIG, ix["cfg_name"][n.id])
                    elif n.id in ix["values"]:
                        value(mod, n.id)
                elif (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                      and n.value.id in ix["cfg_alias"]):
                    value(_CONFIG, n.attr)

        func(module, fn_node.name, fn_node)
        return out


def fire_logic_changes(old: "CodeSide", new: "CodeSide", names=None,
                       neutral=None) -> set:
    """Strategies (names without the strat_ prefix) whose fire-logic members
    differ between two code sides. A strategy absent on either side is not
    'changed since R5' - it has no R5 fires to compare. A member listed in
    `neutral` (default FIRE_NEUTRAL_CHANGES) is skipped while its current
    stripped form still hashes to the reviewed digest."""
    neutral = FIRE_NEUTRAL_CHANGES if neutral is None else neutral
    a, b = old.index(_SCREENER)["strategies"], new.index(_SCREENER)["strategies"]
    pick = set(a) & set(b) if names is None else {"strat_" + n for n in names} & set(a) & set(b)
    out = set()
    for k in sorted(pick):
        ma, mb = old.members(a[k]), new.members(b[k])
        for m in set(ma) | set(mb):
            if ma.get(m) == mb.get(m):
                continue
            reg = neutral.get(m)
            if reg and mb.get(m) is not None and member_digest(mb[m]) == reg[0]:
                continue
            out.add(k[len("strat_"):])
            break
    return out


def neutral_register_problems(old: "CodeSide", new: "CodeSide",
                              register=None) -> list:
    """S6-B3235: every FIRE_NEUTRAL_CHANGES entry must still differ from its
    R5-era form - else it is redundant and goes - and must still hash to its
    reviewed digest - else the member changed after review and is re-read
    before it is re-pinned. Both directions (L587)."""
    register = FIRE_NEUTRAL_CHANGES if register is None else register
    out = []
    for key, (dig, why) in sorted(register.items()):
        a, b = old.member_text(key), new.member_text(key)
        if not str(why).strip():
            out.append(f"{key}: no review reason")
        if a == b:
            out.append(f"{key}: REDUNDANT - the member is back to its R5-era form")
        if b is None or member_digest(b) != dig:
            got = member_digest(b) if b is not None else None
            out.append(f"{key}: STALE - the member changed after review "
                       f"(digest now {got})")
    return out


def changed_since_r5(src_now: str, root=None) -> set:
    """Strategies whose FIRE LOGIC differs from the R5-era code (S6-B3235):
    the members fire_logic_changes compares, at R5_SCREENER_COMMIT against
    the working tree, with `src_now` as the current screener. UPPER bound on
    behavioural change - a configurable-span swap identical at its default
    counts (runbook §2.5). An unreadable R5 screener RAISES: the old rule
    returned an empty set there, so every row read unchanged (L642)."""
    old = CodeSide(R5_SCREENER_COMMIT, root=root)
    if not old.source(_SCREENER).strip():
        raise RuntimeError(f"the R5-era screener ({R5_SCREENER_COMMIT}) is "
                           "unreadable - an empty read would mark every "
                           "strategy unchanged (S6-B3235, L642)")
    new = CodeSide(None, sources={_SCREENER: src_now}, root=root)
    return fire_logic_changes(old, new)


# S6-B2810c: a MENTION is not a campaign. The first build flagged IN-CAMPAIGN
# when any ticket id preceded the strategy name anywhere in a queue cell - and
# all four news-family flags traced to S6-B1428a, an exit-reassignment ticket
# that campaigns nothing (L748: an identifier matched in prose). S6-B2810c then
# required campaign vocabulary in the row; S6-B3194 (2026-10-19) retired that
# for the lanes - IN-CAMPAIGN and STALLED-CAMPAIGN read the owner-opened
# register (load_campaign_opens, register_tickets), and campaign_tickets keeps
# its vocabulary split only beside the mention list it produces.
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

    S6-B3194: NO LANE READS campaign_ids. The campaign lanes read the
    owner-opened register through register_tickets(); this vocabulary
    split labelled 44 strategies as campaigns and 4 were, so it survives
    only as the producer of the mention list.
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
    return sorted(camp), sorted(ment)


LIVE_TICKET_STATES = ("OPEN", "BLOCKED", "DEFERRED", "RUNNING")


def live_campaign_tickets(tickets, ticket_states) -> list:
    """The naming campaign tickets whose CURRENT ledger state is
    non-terminal, judged over EVERY naming ticket. S6-B3179: live-ness was
    once judged on a list already cut to three ids for display, so a live
    ticket sorting fourth or later read STALLED-CAMPAIGN (3 of 225 flipped)."""
    return [t for t in tickets if ticket_states.get(t) in LIVE_TICKET_STATES]


def register_tickets(name: str, campaign_opens: dict, ticket_states: dict) -> tuple:
    """S6-B3194 (owner "A approved" + table "ok", 2026-10-19): (tickets,
    live_tickets) for `name` from the OWNER-OPENED register - never from a
    vocabulary match. An unlisted strategy has no campaign tickets whatever
    the ledger says about it, so status_for reads it NOT-STARTED; a listed
    one is IN-CAMPAIGN while any of its tickets is live (B2829, judged over
    the whole list - S6-B3179) and STALLED-CAMPAIGN once every one is
    terminal (B2833)."""
    r = campaign_opens.get(name)
    tickets = list(r["tickets"]) if r else []
    return tickets, live_campaign_tickets(tickets, ticket_states)


# S6-B3239 (a) (owner ruled 2026-10-21, 'Approve all recs execute'): A SIDE
# WHOSE GATE READS A KEY ABSENT FROM EVERY ONE OF ITS R5 FIRES IS UNMEASURED.
# The survival replay hands the live function each fire's persisted signals;
# a key the cube never persisted is in none of them, .get returns its default,
# and the side read 0.0 - MEASURED B3139q-r80, reproduced r85: 9 sides carry
# such a key and 8 read 0.0 that way. A missing measurement is not a measured
# zero (L580): such a side's survival is None, its RAW share stands in the
# current-gate projection, and unmeasured_gate_keys names the keys. A side that
# still survives 1.0 is measured - its absent key was an OR leg that never
# decided (shooting_star_short).
def _resolve_key(kind: str, v: str, cfg):
    """A lint feed as a signal key: a literal as is; a key built at runtime -
    an f-string over a _cfg knob - resolved against backtest.config; anything
    else None (not resolvable, so not checked)."""
    if kind == "lit":
        return v
    try:
        node = ast.parse(v, mode="eval").body
    except SyntaxError:
        return None
    if not isinstance(node, ast.JoinedStr):
        return None
    parts = []
    for p in node.values:
        if isinstance(p, ast.Constant):
            parts.append(str(p.value))
        elif (isinstance(p, ast.FormattedValue) and isinstance(p.value, ast.Attribute)
              and isinstance(p.value.value, ast.Name) and p.value.value.id == "_cfg"
              and hasattr(cfg, p.value.attr)):
            parts.append(str(getattr(cfg, p.value.attr)))
        else:
            return None
    return "".join(parts)


def gate_keys_by_direction(rows=None) -> dict:
    """{strategy: {direction: set of signal keys its fire decision reads}},
    from scripts/signals_used_lint.py - the repo's one side model (guards,
    assignments and helpers followed). A side whose direction is not a
    constant feeds both directions; the lint's borrow_ok marker is not a
    signal key and is dropped. `rows` is the test seam (the lint's rows)."""
    if rows is None:
        if str(ROOT / "scripts") not in sys.path:
            sys.path.insert(0, str(ROOT / "scripts"))
        import signals_used_lint as _sul
        rows = _sul.analyse()
        borrow = _sul.BORROW
    else:
        borrow = "borrow_ok"
    from backtest import config as _c
    out = {}
    for r in rows:
        per = out.setdefault(r["strategy"], {})
        for sd in r["sides"]:
            if sd.get("status") not in ("OK", "NONLITERAL_LIST"):
                continue
            keys = {k for k in (_resolve_key(t, v, _c) for t, v in sd.get("feeds", ()))
                    if k and k != borrow}
            d = sd.get("direction")
            for dd in ((d,) if d in ("long", "short") else ("long", "short")):
                per.setdefault(dd, set()).update(keys)
    return out


def unmeasured_sides(sigs, dirs, side_survives: dict, keys_by_dir: dict) -> dict:
    """{direction: sorted gate keys absent from EVERY R5 fire of that side} for
    each side whose measured survival is below 1.0 (S6-B3239). A key counts as
    present on a fire when the persisted dict holds a non-None value for it."""
    out = {}
    for d, sv in side_survives.items():
        if sv is None or sv >= 1.0 or not keys_by_dir.get(d):
            continue
        have = set()
        for s_, d_ in zip(sigs, dirs):
            if d_ == d:
                have.update(k for k, v in s_.items() if v is not None)
        absent = sorted(k for k in keys_by_dir[d] if k not in have)
        if absent:
            out[d] = absent
    return out


def measured_survival(ok_side: dict, n_side: dict, side_survives: dict):
    """S6-B3239: the strategy's survives_pct over its MEASURED sides only -
    None when every side is UNMEASURED (or the strategy has no fires)."""
    meas = [d for d in n_side if side_survives.get(d) is not None]
    n = sum(n_side[d] for d in meas)
    return round(sum(ok_side.get(d, 0) for d in meas) / n, 4) if n else None


def current_gate_projection(projected: float, fires: int, n_side: dict,
                            side_survives: dict, survives) -> float:
    """B2822 + S6-B3239: the Step-1 projection under the CURRENT gate. With
    no UNMEASURED side it is the raw projection x survives_pct (the raw one
    where survival is None - a zero-fire row). With one, each MEASURED side
    scales by its own survival and an UNMEASURED side (survival None) keeps
    its RAW share - never the 0.0 default the replay would have read."""
    if fires and any(side_survives.get(d) is None for d in n_side):
        return projected * sum(
            n / fires * (1.0 if side_survives.get(d) is None else side_survives[d])
            for d, n in n_side.items())
    return projected if survives is None else projected * survives


def extras_tightenable(name: str, side: str = None) -> bool:
    """S6-B3272 composition (r94): a STRATEGY_EXTRAS axis carrying an
    offline-tighter level (free_band beyond production) is a REAL
    tightenable axis the s.get regex cannot see - a LOCAL compare like
    ultimate_oscillator's rsi_2 (table_a_bands evidence field). Without
    this, stripping the docstring would re-lane a genuinely tightenable
    strategy to LOOSEN. side=None asks any axis; side='long'/'short'
    asks axes labelled for that side. Pinned by test_b3272."""
    try:
        from table_a_bands import STRATEGY_EXTRAS as _extras
    except Exception:
        return False
    for k in _extras.get(name, []):
        for ax in k.get("axis_levels", []):
            if side and not str(ax.get("side", "")).startswith(side):
                continue
            if [v for v in (ax.get("free_band") or [])
                    if v != ax.get("production")]:
                return True
    return False


def classify_stream(tightenable: bool, projected: float) -> str:
    starved = projected < MIN_FIRES_FOR_GRID
    if tightenable and starved:
        return "BOTH"
    if tightenable:
        return "TIGHTEN"
    if starved:
        return "LOOSEN"
    return "NONE"


# S6-B3135 / S6-B3135a (owner rulings 2026-09-29): the status vocabulary.
# TERMINAL rows leave every work lane; NEVER_REOPEN rows are owner decisions,
# not gate verdicts, so the reopen flag (a changed entry condition) never
# applies to them.
# S6-B2420 DROPPED (owner ruling 2026-10-20, 'Approve all recs fable mode be
# extremely thorough'): the short-leg Step 2 that kept IN-ROSTER-MIRROR open
# is withdrawn, so the mirror lane is terminal too - on the roster by the
# mirror policy, closed to re-testing like every member ('2 yes. No more
# retesting', 2026-09-29), with no work scheduled - and, being an owner
# decision rather than a gate verdict, never flagged for reopening.
TERMINAL_STATUSES = ("DONE-ADMITTED", "IN-ROSTER-FUNNEL", "DONE-OWNER-CLOSED",
                     "IN-ROSTER-MIRROR", "DISABLED", "PRUNED-DUPLICATE",
                     "CLOSED-NEGATIVE", "CONTAINED-IN-REPRESENTATIVE")
NEVER_REOPEN = ("DONE-ADMITTED", "IN-ROSTER-FUNNEL", "DONE-OWNER-CLOSED",
                "IN-ROSTER-MIRROR")
OWNER_CLOSURES = Path("output_audit") / "owner_campaign_closures.json"


def _required(path, doc, key: str, typ: type):
    """S6-B3217 (L936): a committed record's REQUIRED field. An absent key,
    a null or the wrong type RAISES - the 'or []' / 'or {}' defaults this
    replaces read a malformed record as an empty population, the silent
    fallback #232 names (L642). An explicit empty list or dict is a DECLARED
    empty and reads empty."""
    v = doc.get(key) if isinstance(doc, dict) else None
    if not isinstance(v, typ):
        raise ValueError(f"{path}: needs '{key}' as a {typ.__name__} - got "
                         f"{type(v).__name__} (S6-B3217)")
    return v


def load_owner_closures(root=ROOT) -> dict:
    """{strategy: record} for campaigns the OWNER closed outright (S6-B3135a).
    Every record carries the owner's words (verbatim, or in substance with the
    rows that record them) and the date ruled. An unreadable or malformed
    register RAISES - a closure list that silently read empty would reopen
    closed campaigns (L642)."""
    p = Path(root) / OWNER_CLOSURES
    d = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    for r in _required(p, d, "closures", list):
        s = r.get("strategy")
        words = r.get("ruling_verbatim") or r.get("ruling_in_substance")
        if not s or not words or not r.get("ruled"):
            raise ValueError(f"{p}: a closure needs strategy, ruled and the "
                             f"owner's words - got {r!r}")
        if s in out:
            raise ValueError(f"{p}: {s} is closed twice")
        out[s] = r
    return out


# S6-B3194 (owner "A approved" + table "ok", 2026-10-19): "campaigned" is a
# RECORDED fact. The 12-word vocabulary heuristic below labelled 44
# strategies as campaigns and 4 were campaign subjects when read one by one
# (output_audit/b3194_campaign_classification.json) - the ledger could not
# store "campaign subject", so a guess stood in for it (#247 / L932).
CAMPAIGN_OPENS = Path("output_audit") / "owner_campaign_opens.json"


def load_campaign_opens(root=ROOT) -> dict:
    """{strategy: record} for campaigns the OWNER opened (S6-B3194). Every
    record carries the owner's words, the date opened and the campaign's
    tickets - the tickets alone decide live versus stalled. An unreadable or
    malformed register RAISES: a register that silently read empty would
    turn every campaign NOT-STARTED (L642)."""
    p = Path(root) / CAMPAIGN_OPENS
    d = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    for r in _required(p, d, "opens", list):
        s = r.get("strategy")
        words = r.get("ruling_verbatim") or r.get("ruling_in_substance")
        tickets = r.get("tickets")
        if (not s or not words or not r.get("opened")
                or not isinstance(tickets, list) or not tickets):
            raise ValueError(f"{p}: an open needs strategy, opened, the "
                             f"owner's words and a ticket list - got {r!r}")
        if s in out:
            raise ValueError(f"{p}: {s} is opened twice")
        out[s] = r
    return out


def closed_populations(root=ROOT) -> dict:
    """B2825 (owner-directed 2026-09-16, "groups must be mutually exclusive;
    closed strategies must not count toward future work unless genuinely
    reopened"): the ADMITTED and CLOSED populations, each from its committed
    record - nothing here is a judgement. A pure function of `root` so the
    precedence pin reads the very sets main() reads (L593)."""
    root = Path(root)
    # S6-B3217 (L936): every record here is REQUIRED. An absent file raises
    # (read_text) and an absent field raises (_required); the exists()
    # guards and 'or []' defaults this replaces read a missing record as an
    # empty population, which would silently return admitted and closed
    # strategies to the work lanes (#232, L642).
    adm = root / ADMISSIONS.relative_to(ROOT)
    d = json.loads(adm.read_text(encoding="utf-8"))
    admitted = {r.get("strategy") for r in _required(adm, d, "admissions", list)
                if isinstance(r, dict) and r.get("strategy")}
    # B2825: the Jaccard-0.70 pruned duplicates (B2666) are EVALUATED AND
    # DISCARDED, not future work
    pruned = {r.get("strategy")
              for r in _required(adm, d, "pruned_collinear_b2666", list)
              if isinstance(r, dict) and r.get("strategy")}
    # family-pass FAIL, never re-admitted (b2628)
    p28 = root / "output_audit" / "b2628_institutional_family_grades.json"
    sib = _required(p28, json.loads(p28.read_text(encoding="utf-8")), "siblings", dict)
    closed_neg = {k for k, v in sib.items() if isinstance(v, dict)} - admitted - pruned
    # contained in an admitted representative (b2647)
    contained = set()
    p47 = root / "output_audit" / "b2647_pead_sibling_pass.json"
    for r in _required(p47, json.loads(p47.read_text(encoding="utf-8")), "graded", list):
        if isinstance(r, dict) and "CONTAINED" in str(r.get("disposition", "")):
            if r.get("strategy") not in admitted:
                contained.add(r["strategy"])
    from backtest.config import (STRATEGIES_DISABLED_MISSING_PRODUCER,
                                 STRATEGIES_DISABLED_DATA_SCARCITY,
                                 STRATEGIES_DISABLED_DUPLICATE)
    disabled = (set(STRATEGIES_DISABLED_MISSING_PRODUCER)
                | set(STRATEGIES_DISABLED_DATA_SCARCITY)
                | set(STRATEGIES_DISABLED_DUPLICATE))
    return {"admitted": admitted, "pruned": pruned, "closed_neg": closed_neg,
            "contained": contained, "disabled": disabled}


def ticket_fields(tickets_all: list, mentions_all: list) -> tuple[list, list]:
    """S6-B3186: the campaign and mention ticket lists a status record
    stores - COMPLETE, in queue order.

    The record kept the first three ids while its own methodology note said
    mention_tickets keeps the unfiltered list, so a reader could not tell a
    capped record from a complete one (L558) - 24 of 225 strategies carry
    more than three (B3139q-r70t). Nothing renders these lists (the MD view
    shows status counts only), so the cap bought nothing.

    S6-B3194: the record's `tickets` field now comes from
    register_tickets(); the first list returned here is the vocabulary
    split, which no lane reads."""
    return list(tickets_all), list(mentions_all)


def status_for(name: str, *, admitted, roster_status, owner_closed, disabled,
               pruned, closed_neg, contained, live_tickets, tickets) -> str:
    """B2825 precedence - ONE status per strategy, mutually exclusive by
    construction; a terminal disposition beats a campaign mention.
    S6-B3135a: an owner-closed campaign (DONE-OWNER-CLOSED) outranks every
    lane, the roster-mirror lane included - a closed mirror reads
    DONE-OWNER-CLOSED, any other mirror IN-ROSTER-MIRROR; both are terminal
    since the owner dropped the mirrors' Step 2 (S6-B2420, 2026-10-20).
    An admission or a graded funnel cell outranks a closure: both are already
    terminal, and the admission is the stronger fact."""
    if name in admitted:
        return "DONE-ADMITTED"
    if roster_status == "IN-ROSTER-FUNNEL":
        return "IN-ROSTER-FUNNEL"
    if name in owner_closed:
        return "DONE-OWNER-CLOSED"
    if name in disabled:
        return "DISABLED"
    if name in pruned:
        return "PRUNED-DUPLICATE"
    if name in closed_neg:
        return "CLOSED-NEGATIVE"
    if name in contained:
        return "CONTAINED-IN-REPRESENTATIVE"
    if roster_status == "IN-ROSTER-MIRROR":
        return "IN-ROSTER-MIRROR"
    # B2833 (owner word "STALLED-CAMPAIGN approved", 2026-09-15): a row whose
    # campaign tickets exist but are ALL terminal is distinguished from a
    # never-campaigned row - Step-1 may be done with no Step-2 word, and
    # NOT-STARTED erased that history. NON-terminal: it keeps its lane.
    return ("IN-CAMPAIGN" if live_tickets
            else "STALLED-CAMPAIGN" if tickets else "NOT-STARTED")


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
    gate_keys = gate_keys_by_direction()  # S6-B3239

    tl = pd.read_csv(R5_DIR / "trade_log.csv", low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "direction",
                              "signals_at_entry"])
    tl = tl.drop_duplicates(["strategy", "ticker", "entry_date"])
    by_strat = {k: v for k, v in tl.groupby("strategy")}

    # B2825: the admitted and CLOSED populations, from committed records
    _pop = closed_populations(ROOT)
    admitted, pruned = _pop["admitted"], _pop["pruned"]
    closed_neg, contained = _pop["closed_neg"], _pop["contained"]
    disabled = _pop["disabled"]

    # S6-B3217: the ledger is REQUIRED - an absent queue read as empty text
    # would have dropped every mention silently
    qtext = QUEUE.read_text(encoding="utf-8", errors="replace")
    # B2829: the canonical last-row-wins reducer - never a hand parser (L695)
    sys.path.insert(0, str(ROOT / "scripts"))
    import queue_state as _qs
    # S6-B3135 (B3135): the Phase 1B roster is 31 strategies (7 funnel
    # cells + 15 Step-2 admissions + 9 mirrors), not the admissions file's
    # 15 - one reader, raising on an unreadable input (L642)
    import phase1b_membership as _pm
    _mem = _pm.members(ROOT)
    _mem_sum = _pm.summary(_mem)
    # S6-B3135a (owner 2026-09-29): campaigns the owner closed outright
    owner_closed = load_owner_closures(ROOT)
    # S6-B3194: the owner-opened campaigns - the ONLY source of the
    # campaign lanes (IN-CAMPAIGN / STALLED-CAMPAIGN)
    campaign_opens = load_campaign_opens(ROOT)
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
        if not tightenable and extras_tightenable(name):
            tightenable = True   # S6-B3272: a local-compare extras axis

        # S6-B2814: survival = the LIVE strategy function fires on the
        # persisted signals with the recorded direction. An erroring row is
        # a non-survival counted in the denominator, never dropped.
        survives = None
        side_survives, n_side = {}, {}
        fn = ALL_STRATEGIES.get(name)
        if callable(fn) and sigs:
            ok = 0
            # S6-B3232 correction: the same count per recorded direction, in
            # the same pass - an erroring row stays in its side's denominator
            ok_side = {}
            for s_, d_ in zip(sigs, dirs):
                n_side[d_] = n_side.get(d_, 0) + 1
                try:
                    r_ = fn(s_)
                except Exception:
                    continue
                if r_ and r_.get("fires") and r_.get("direction") == d_:
                    ok += 1
                    ok_side[d_] = ok_side.get(d_, 0) + 1
            survives = round(ok / fires, 4)
            side_survives = {d: round(ok_side.get(d, 0) / n, 4)
                             for d, n in sorted(n_side.items())}
        # S6-B3239: a side whose gate reads a key no R5 fire of it persisted
        # is UNMEASURED - its survival is None; the strategy's survives_pct
        # is the share over its MEASURED sides (None when there is none)
        unmeasured = unmeasured_sides(sigs, dirs, side_survives,
                                      gate_keys.get(name, {}))
        if unmeasured:
            for d in unmeasured:
                side_survives[d] = None
            survives = measured_survival(ok_side, n_side, side_survives)

        tickets_all, mentions_all = campaign_tickets(qtext, name)
        # S6-B3186: the record keeps the FULL lists (ticket_fields)
        _vocab, mentions = ticket_fields(tickets_all, mentions_all)
        # S6-B3194: the campaign tickets come from the owner-opened register,
        # never from a vocabulary match - the heuristic survives only as
        # the mention list (who talks about this strategy). B2829 (owner-
        # directed "statuses latest, no misses" 2026-09-16): a campaign is
        # LIVE only while one of its tickets' CURRENT ledger state is
        # non-terminal - a concluded campaign does not own a strategy forever.
        tickets, live_tickets = register_tickets(name, campaign_opens,
                                                 ticket_states)
        # B2825 status precedence - one status per strategy, MUTUALLY
        # EXCLUSIVE by construction; a terminal disposition beats a campaign
        # mention, and the stream lane below is voided for terminal rows.
        status = status_for(
            name, admitted=admitted, roster_status=_pm.roster_status(name, _mem),
            owner_closed=owner_closed, disabled=disabled, pruned=pruned,
            closed_neg=closed_neg, contained=contained,
            live_tickets=live_tickets, tickets=tickets)
        terminal = status in TERMINAL_STATUSES
        # REOPEN RULE (owner 2026-09-16, "unless reopened for a genuine
        # reason"): a terminal verdict was computed on the CLOSURE-TIME gate;
        # if the entry condition changed since R5 AND the old fires no longer
        # all satisfy it, the verdict's evidence base has moved - FLAGGED for
        # the owner, never auto-reopened.
        reopen = bool(terminal and status not in NEVER_REOPEN
                      and name in changed
                      and (survives is None or survives < 1.0))
        # B2822 (owner-caught: "the counts are all over the place"): the LANE
        # is classified on CURRENT-GATE fires, not raw R5 fires. hub-1 sat at
        # stream NONE off 2,933 raw fires while only 5.15% survive its current
        # gate - its honest projection is ~14, which is LOOSEN. Where survival
        # is unmeasured (zero-fire rows) the raw projection stands.
        eff = current_gate_projection(projected, fires, n_side,
                                      side_survives, survives)
        recs.append({"strategy": name, "family": fam, "r5_fires": fires,
                     "changed_since_r5": name in changed,
                     "survives_pct": survives,
                     "survives_pct_by_side": side_survives,
                     "unmeasured_gate_keys": unmeasured,
                     "r5_fires_by_side": dict(sorted(n_side.items())),
                     "projected_step1_fires": round(projected, 1),
                     "projected_current_gate": round(eff, 1),
                     "reopen_candidate": reopen,
                     "stream": "-" if terminal
                     else classify_stream(tightenable, eff),
                     "tightenable_keys": covered, "tickets": tickets,
                     "live_campaign_tickets": live_tickets,
                     "mention_tickets": mentions,
                     "admitted": name in admitted,
                     "roster_roles": list((_mem.get(name) or {}).get("roles", [])),
                     "status": status})

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
             "changed_since_r5 compares FIRE LOGIC (S6-B3235): the strategy's "
             "body and every function, module constant and config value it "
             "reaches - a delegation to another signals module included - with "
             "docstrings and the signals_used / context-bullet payload removed, "
             "against the R5-era code; a reviewed fire-neutral change "
             "(FIRE_NEUTRAL_CHANGES) counts only once its digest goes stale. An "
             "UPPER BOUND on behaviour (a configurable-span swap identical at its "
             "default counts) and blind to the producers that compute the signals",
             "stream TIGHTEN rests on a source pattern for numeric comparisons, "
             "a LOWER BOUND - thresholds via a helper or a config constant are invisible",
             "survives_pct calls the LIVE strategy function on each fire's persisted "
             "signals (S6-B2814; validated: reproduces 151/2933 and 1880/1880 exactly). "
             "A LOWER BOUND where a gate leg reads a key some fires did not persist; "
             "an erroring row counts as non-survival. S6-B3239: a SIDE whose gate "
             "reads a key absent from EVERY one of its R5 fires is UNMEASURED - its "
             "survival is None, unmeasured_gate_keys names the keys, the strategy's "
             "survives_pct covers its measured sides only (None when it has none), "
             "and the current-gate projection keeps that side's RAW share; None "
             "otherwise only for zero-fire strategies",
             "the campaign lanes read the OWNER-OPENED register "
             "(output_audit/owner_campaign_opens.json, S6-B3194): a listed "
             "strategy is IN-CAMPAIGN while one of its register tickets is "
             "non-terminal (B2829) and STALLED-CAMPAIGN once every one is "
             "terminal (B2833, owner-approved 2026-09-15); an unlisted "
             "strategy is NOT-STARTED whatever tickets mention it - a mention "
             "is not a campaign (the vocabulary heuristic this replaces "
             "labelled 44 strategies and 4 were campaign subjects); "
             "mention_tickets keeps the full mention list",
             "stream and the proj column use the CURRENT-GATE projection "
             "(raw projection x survives_pct, B2822); projected_step1_fires "
             "in this JSON keeps the raw figure",
             "terminal statuses (ADMITTED / DISABLED / PRUNED-DUPLICATE / "
             "CLOSED-NEGATIVE / CONTAINED) are MUTUALLY EXCLUSIVE with the "
             "stream lanes and excluded from every work bucket (B2825); "
             "reopen_candidate flags a terminal row whose entry condition "
             "changed since its closure evidence (survives < 1.0) - flagged "
             "for the owner, never auto-reopened",
             "IN-ROSTER-FUNNEL / IN-ROSTER-MIRROR (S6-B3135) come from "
             "scripts/phase1b_membership.py: a graded 3-cube funnel cell is on "
             "the Phase 1B roster, terminal like an admission and CLOSED to "
             "re-testing like one (owner 2026-09-29, '2 yes. No more "
             "retesting'); a short mirror retained by the owner's mirror "
             "policy is on the roster, UNGRADED beyond R5, and terminal "
             "since the owner dropped its Step 2 (S6-B2420, 2026-10-20)",
             "DONE-OWNER-CLOSED (S6-B3135a) is a campaign the owner closed "
             "outright, read from output_audit/owner_campaign_closures.json "
             "with the owner's words; it outranks the mirror lane, so "
             "IN-ROSTER-MIRROR is exactly the mirrors the owner has not closed. "
             "A closed mirror stays ON the Phase 1B roster - the closure "
             "ends its campaign, not its membership"],
         "phase1b_roster": _mem_sum,
         "owner_closures": sorted(owner_closed),
         "campaign_opens": sorted(campaign_opens),
         "rows": recs}, indent=2), encoding="utf-8")

    # ---- the markdown view -------------------------------------------------
    import collections
    bystream = collections.Counter(r["stream"] for r in recs)
    bystatus = collections.Counter(r["status"] for r in recs)
    _TERMINAL = TERMINAL_STATUSES
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
         f"**Phase 1B roster: {_mem_sum['total']} distinct = "
         f"{_mem_sum['funnel_cells']} graded funnel cells + "
         f"{_mem_sum['step2_admissions']} Step-2 admissions + "
         f"{_mem_sum['mirrors']} short mirrors ({_mem_sum['long']} long / "
         f"{_mem_sum['short']} short)** - read from scripts/phase1b_membership.py "
         "(S6-B3135). 'DONE - admitted' below counts the Step-2 admissions "
         "only; the funnel cells and mirrors carry their own rows.", "",
         "## Totals", "",
         "| | count |", "|---|---|",
         f"| registered strategies | {len(recs)} |",
         f"| DONE - admitted to Phase 1B | {bystatus.get('DONE-ADMITTED', 0)} |",
         f"| IN-ROSTER-FUNNEL - a graded 3-cube funnel cell on the Phase 1B roster, terminal (S6-B3135) | {bystatus.get('IN-ROSTER-FUNNEL', 0)} |",
         f"| IN-ROSTER-MIRROR - a short mirror on the roster by the mirror policy, ungraded beyond R5, terminal (its Step 2 dropped 2026-10-20, S6-B2420) | {bystatus.get('IN-ROSTER-MIRROR', 0)} |",
         f"| DONE-OWNER-CLOSED - a campaign the owner closed outright, terminal; stays on the roster (S6-B3135a) | {bystatus.get('DONE-OWNER-CLOSED', 0)} |",
         f"| IN-CAMPAIGN - an owner-opened campaign (register), a ticket LIVE | {bystatus.get('IN-CAMPAIGN', 0)} |",
         f"| STALLED-CAMPAIGN - an owner-opened campaign (register), every ticket terminal (B2833) | {bystatus.get('STALLED-CAMPAIGN', 0)} |",
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
          "- `changed_since_r5` compares **fire logic** (S6-B3235): the strategy's body "
          "and every function, module constant and config value it reaches - a "
          "delegation to index_rebalance.py included - with docstrings and the "
          "signals_used / context-bullet payload removed. A reviewed fire-neutral "
          "change (the borrow gate's S6-B2118b counters) is skipped while its digest "
          "holds. An **upper bound** on behaviour - a configurable-span swap identical "
          "at its default counts - and blind to the producers that compute the signals.",
          "- `stream = TIGHTEN` rests on a source pattern for numeric comparisons and is "
          "a **lower bound** - a threshold reached through a helper or compared to a "
          "config constant is invisible to it.",
          "- `survives_pct` calls the **live strategy function** on each fire's persisted "
          "signals (S6-B2814). A **lower bound** where a gate leg reads a key some fires did "
          "not persist; an erroring row counts as non-survival; `-` only for zero-fire "
          "strategies. **UNMEASURED** (S6-B3239): a side whose gate reads a key absent from "
          "EVERY one of its R5 fires has no survival - the replay would read the key's "
          "default, not a measurement - so its raw share stands in the projection and the "
          "cell names the side; `unmeasured_gate_keys` in the JSON names the keys.",
          "- `IN-CAMPAIGN` / `STALLED-CAMPAIGN` read the **owner-opened register** "
          "(`output_audit/owner_campaign_opens.json`, S6-B3194): a listed strategy is "
          "IN-CAMPAIGN while one of its register tickets is non-terminal (B2829), and "
          "STALLED-CAMPAIGN (B2833, owner-approved 2026-09-15) once every one is "
          "terminal - campaigned, concluded mid-path, still in its stream lane. **A "
          "mention is not a campaign**: an unlisted strategy is NOT-STARTED whatever "
          "tickets name it. The vocabulary heuristic this replaces labelled 44 "
          "strategies and 4 were campaign subjects when read one by one; "
          "`mention_tickets` in the JSON keeps the full mention list.",
          "- `IN-ROSTER-FUNNEL` / `IN-ROSTER-MIRROR` (S6-B3135): read from "
          "scripts/phase1b_membership.py, the one reader of the Phase 1B roster. "
          "A funnel cell is terminal like an admission and closed to re-testing "
          "like one (owner 2026-09-29); a mirror is ungraded beyond R5 and "
          "terminal too - the owner dropped its Step 2 (S6-B2420, 2026-10-20).",
          "- `DONE-OWNER-CLOSED` (S6-B3135a, owner 2026-09-29): a campaign the "
          "owner closed outright (output_audit/owner_campaign_closures.json, "
          "each with the owner's words). Terminal; never auto-reopened. A "
          "closed mirror stays ON the Phase 1B roster - the closure ends its "
          "campaign, not its membership.",
          "",
          "## Per strategy", "",
          "| strategy | family | R5 fires | proj. Step-1 (current-gate) | chg | survives | stream | status |",
          "|---|---|---|---|---|---|---|---|"]
    for r in sorted(recs, key=lambda x: (-x["r5_fires"], x["strategy"])):
        sv = "-" if r["survives_pct"] is None else f"{r['survives_pct']:.1%}"
        if r["unmeasured_gate_keys"]:
            # S6-B3239: a missing measurement is never printed as a number
            um = "/".join(sorted(r["unmeasured_gate_keys"]))
            sv = ("UNMEASURED" if r["survives_pct"] is None
                  else f"{sv} ({um} UNMEASURED)")
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
