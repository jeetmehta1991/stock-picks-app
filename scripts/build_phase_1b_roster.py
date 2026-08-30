"""scripts/build_phase_1b_roster.py (B1453) -- THE Phase 1B roster, consolidated.

OWNER DIRECTIVE 2026-08-04: "I need the updated strategy list with all strategies that pass the
updated argmax criteria on gates from r5, r6 and gate 1 runs along with symmetrical short mirrors.
This is the source of truth."

WHY A NEW GENERATOR RATHER THAN EDITING build_passed_strategy_exit_list.py
That script is bound to the R5 cube's auxiliary artifacts (walk_forward_r5_all_cells_annualized
.json, best_exit_per_strategy_by_regime.json, passed_strategy_exit_holdout_graded.json), none of
which exist for the R6b or Group-1 cubes. Making it multi-cube would be a large refactor of a
working script mid-decision. This generator reuses its METHOD -- the IS-select / holdout-grade
window discipline, the same metrics.py implementations, the same BH-FDR and Jaccard -- and reads
all three cubes. S6-B1452a tracks consolidating the two.

METHOD (the corrected one; B1452 retracted a holdout-selected variant)
  1 SELECT   each (strategy x direction) cell's exit on IS folds F1-F3 (2022-05-05 -> 2025-05-05)
             by argmax GATES-CLEARED, tie-break IS Sharpe. The holdout is never read here.
  2 GRADE    the single chosen exit once on the holdout F4 (2025-05-05 -> 2026-05-05).
  3 GATE 1   BH-FDR (q<0.05) across the holdout family, so the roster survives multiple testing.
  4 DE-DUP   Jaccard >= 0.70 on the (ticker, entry_date) holdout trade set drops near-identical
             cells. Canonical member chosen by holdout Sharpe -- selection-justified: Sharpe is
             the promotion statistic, not a proxy for it (CHECKLIST #165; supersedes the B1444
             largest-trade-set heuristic flagged as arbitrary in S6-B1445b).
  5 MIRRORS  every survivor gets its symmetric short mirror resolved: REGISTERED (exists),
             LONG-ONLY-DATA (excused per feedback_asymmetric_data_sources_break_mechanical_inverse
             + the B611 reversal), or NEEDS-CREATION.

CROSS-CUBE CAVEAT, stated in the output because it bounds every comparison:
R5 ran 544 tickers; R6b and Group-1 ran ~140 (a seeded 150-ticker sample). Per-trade statistics
(Sharpe, PF, expectancy) are comparable across cubes because they are per-trade ratios. TRADE
COUNTS are NOT -- so `min_trades` is materially harder to clear on the small-sample cubes and a
cell can be UNEVAL there purely from universe size. Flagged per cell rather than silently pooled.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backtest.config import PASSING_CRITERIA as PC          # noqa: E402
from backtest.results.metrics import _sortino_ratio, _deflated_sharpe  # noqa: E402
from walk_forward_r5_cells import _sharpe, bh_fdr            # noqa: E402
from backtest.signals.screener import ALL_STRATEGIES         # noqa: E402
from backtest.config import (STRATEGIES_DISABLED_DATA_SCARCITY,  # noqa: E402
                             STRATEGIES_DISABLED_MISSING_PRODUCER, DEPRECATED_STRATEGIES)

# S6-B1452a (B1463): the window discipline, the conditioning and the gate evaluation now
# live in ONE place. Two files independently defining IS_END is how the B1452 lookahead
# would recur unnoticed, and S6-OPT-196 regrades the 196-strategy backlog repeatedly.
# S6-B1467c/B2009 HISTORY: a selection-noise floor (the mean holdout-Sharpe
# gap between near-identical twins whose exits were chosen independently,
# from output_audit/b1467_exit_selection_noise.json) once split gate-clearing
# cells into ROBUST/PROVISIONAL. S6-B2409 (owner ruling 2026-08-30): that
# floor and the split are RETIRED IN THEIR ENTIRETY - clearing the six
# LIVE_GATES is qualification, full stop. The per-cell margin over the live
# gate remains a reported number (roster_core.qualifier_margin).

from roster_core import (                                    # noqa: E402
    IS_START, IS_END, HO_START, HO_END, WINSORIZE, COST_BPS, MIN_N, FDR_Q, JACCARD,
    LIVE_GATES, DEMOTED, evaluate, npt_spanning_exclusion, rank_key,
    select_exit, truthful_exit_name,
)

CUBES = [("R5", "output_r5_merged_1_7"),
         ("R6b", "output_r6b_cube_14"),
         ("Group1", "output_r6c_group1_3")]

# 13F / insider / congressional / buyback data is LONG-ONLY by SEC rule, so a mechanical short
# mirror is economically false, not merely untested (B611 reversal).
ASYM_MARKERS = ("institutional_", "insider", "smart_money", "congress", "13f", "13d",
                "activist", "lobbying", "buyback")



def uses_long_only_data(name: str) -> tuple[bool, list[str]]:
    """Decide data-asymmetry from the SIGNALS THE FUNCTION ACTUALLY CONSUMES, never the name.

    B1453 fix, self-caught on the first generated roster: `xs_momentum_with_smart_money_long`
    was classified LONG-ONLY-DATA purely because its NAME contains "smart_money" - but B1194
    (2026-07-06, Council 278) REMOVED the smart_money gate, so it now fires on
    `xs_momentum_top_decile AND price_above_ema_200`, both direction-symmetric, and its exact
    mirror `xs_momentum_bottom_decile_short` already exists (annotated B1452). Name-based
    inference over a stale name wrongly excused a mirror the owner had just directed be paired.
    Class: a strategy's DATA DEPENDENCIES are a property of its consumed signal keys; the name
    is documentation and can go stale (the same class as S6-B1419's misdiagnosis).
    """
    import inspect
    import re as _re
    try:
        src = inspect.getsource(ALL_STRATEGIES[name])
    except Exception:
        return False, []
    keys = set(_re.findall(r"s\.get\(\"([a-z0-9_]+)\"", src))
    hits = sorted(k for k in keys if any(a in k for a in ASYM_MARKERS))
    return bool(hits), hits


def _declared_mirrors() -> dict[str, str]:
    """Pairs DECLARED in a docstring as `EXACT MIRROR of <parent>` -- the authoritative source.

    B1453: stem/token matching cannot bridge `xs_momentum_with_smart_money_long` ->
    `xs_momentum_bottom_decile_short` (2 shared tokens, threshold 3), so it reported
    NEEDS-CREATION for a pair the owner had just directed be recognised and which was annotated
    at B1452. Rather than special-casing that one strategy, this reads the annotation convention
    itself: any strategy whose docstring says "EXACT MIRROR of X" declares the X <-> self pair.
    Curated intent beats string similarity, and the annotation is where intent already lives.
    """
    import inspect
    import re as _re
    out: dict[str, str] = {}
    for nm, fn in ALL_STRATEGIES.items():
        try:
            doc = inspect.getdoc(fn) or ""
        except Exception:
            continue
        m = _re.search(r"EXACT MIRROR of\s+(?:strat_)?([a-z0-9_]+)", doc)
        if m:
            parent = m.group(1)
            if parent in ALL_STRATEGIES:
                out[parent] = nm      # parent -> its declared mirror
                out[nm] = parent      # and the reverse
    return out


_DECLARED = None


def is_dual(name: str) -> bool:
    """A DUAL strategy's own short branch IS its mirror - nothing needs creating.

    B1454 fix, self-caught: the first roster flagged `avwap_252_breakout` and
    `force_index_breakout` as NEEDS-CREATION. Both are dual (`reclaim_252_long`/
    `loss_252_short`, and `fl`/`fs`) and the R5 cube carries BOTH directions for each.
    Wiring a separate `_short` strategy would have created a redundant duplicate of a
    branch that already trades. Detected from the SOURCE (a short branch exists), which is
    the same logic-over-name principle as L279.
    """
    import inspect
    import re as _re
    try:
        src = inspect.getsource(ALL_STRATEGIES[name])
    except Exception:
        return False
    if _re.search(r"^\s*fs\s*=", src, _re.M):
        return True
    return bool(_re.search(r"_short\b\s*=", src)) and bool(_re.search(r"_long\b\s*=", src))


def mirror_status(name: str) -> tuple[str, str | None]:
    global _DECLARED
    if _DECLARED is None:
        _DECLARED = _declared_mirrors()
    reg = set(ALL_STRATEGIES)
    # A DECLARED pairing outranks both the asymmetry heuristic and string matching: it is an
    # explicit statement of intent about this specific pair.
    if name in _DECLARED:
        return "REGISTERED", _DECLARED[name]
    if is_dual(name):
        return "DUAL-SELF", name          # its own short branch is the mirror
    asym, _hits = uses_long_only_data(name)
    if asym:
        return "LONG-ONLY-DATA", None
    stem = name[:-5] if name.endswith("_long") else (name[:-6] if name.endswith("_short") else name)
    want_short = not name.endswith("_short")
    for cand in ([stem + "_short", stem] if want_short else [stem + "_long", stem]):
        if cand in reg and cand != name:
            return "REGISTERED", cand
    STOP = {"long", "short", "with", "the", "of", "and"}
    toks = {t for t in name.split("_") if t not in STOP}
    best, bn = 0, None
    for r in reg:
        if r == name or (want_short and not r.endswith("_short")):
            continue
        ov = len({t for t in r.split("_") if t not in STOP} & toks)
        if ov > best:
            best, bn = ov, r
    if bn and best >= max(2, len(toks) - 1):
        return "REGISTERED", bn
    return "NEEDS-CREATION", None


def step2_admissions_section(A, admissions_path=None) -> None:
    """S6-B2413 (owner instruction 2026-08-30): render owner-ruled Step-2
    admissions into the roster document.

    The admissions file carries IDENTITY only (which combination, which
    ruling); every metric is re-derived here from the named grid artifact by
    EXACT match on the swept combination fields plus the exit - a hand-copied
    number in a record decays while staying quotable (L577/#256). A listed
    admission whose row cannot be located, or whose verdict is not PASS,
    REFUSES loudly (a guard fails closed on the absent input, L642): an
    admission is a bound, not a feature. An absent admissions FILE is the
    feature being absent - nothing ruled yet - and skips silently.
    """
    def _fmt(v, w=6, d=2):
        return f"{v:>{w}.{d}f}" if isinstance(v, (int, float)) else f"{'-':>{w}}"

    p = Path(admissions_path) if admissions_path else (
        REPO / "output_audit" / "phase_1b_step2_admissions.json")
    if not p.exists():
        return
    doc = json.loads(p.read_text(encoding="utf-8"))
    adms = doc.get("admissions") or []
    if not adms:
        return
    A("## Step-2 admissions (owner-ruled)")
    A("")
    A("Cells admitted by explicit owner ruling from the STRATEGY_OPTIMISATION_PLAN Step-2 "
      "waterfall - a DIFFERENT pipeline from the 3-cube funnel above (per-strategy "
      "producer-parameter search, six-gate grading, first-qualifier-stops). They are NOT rows "
      "of the funnel table and are not counted in it. Metrics are re-derived at render time "
      "from each admission's own grading artifact; the admissions file carries identity only.")
    A("")
    A("| Strategy | Dir | Producer combination | Exit | IS Shrp | IS ci_lo | HO Shrp | HO ci_lo | margin | psr | PF | Sortino | WR | Exp | HO n | Full n | Mirror |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for adm in adms:
        art = REPO / adm["grid_artifact"]
        grid = json.loads(art.read_text(encoding="utf-8"))
        rows = (grid.get("qualifiers") or grid.get("provisional_qualifiers")
                or grid.get("results") or [])
        want = adm["combination"]
        hit = [r for r in rows
               if all(r.get(k) == v for k, v in want.items())
               and r.get("exit") == adm["exit"]]
        if len(hit) != 1:
            raise ValueError(
                f"admission {adm['ticket']}: expected exactly 1 row matching "
                f"{want} + exit {adm['exit']!r} in {art.name}, found {len(hit)} "
                "- refusing to render an admission whose evidence cannot be located")
        r = hit[0]
        if r.get("verdict") != "PASS":
            raise ValueError(
                f"admission {adm['ticket']}: matched row verdict is "
                f"{r.get('verdict')!r}, not PASS - an admitted combination must "
                "have cleared all six gates")
        mstat, mname = mirror_status(adm["strategy"])
        mir = f"`{mname}`" if (mstat == "REGISTERED" and mname) else mstat
        combo = ", ".join(f"{k}={v}" for k, v in want.items())
        cfg = ", ".join(f"{k}={v}" for k, v in (adm.get("config") or {}).items())
        A(f"| `{adm['strategy']}` | {adm['direction']} | {cfg}; {combo} | `{adm['exit']}` | "
          f"{_fmt(r.get('is_sharpe'))} | {_fmt(r.get('is_ci_lo'))} | {_fmt(r.get('sharpe'))} | "
          f"{_fmt(r.get('ci_lo'))} | {r.get('margin'):+.3f} | {_fmt(r.get('psr'))} | "
          f"{_fmt(r.get('profit_factor'))} | {_fmt(r.get('sortino'))} | "
          f"{_fmt(r.get('win_rate'), 5, 3)} | {_fmt(r.get('expectancy'))} | "
          f"{r.get('holdout_n')} | {r.get('full_period_n')} | {mir} |")
    A("")
    for adm in adms:
        A(f"**{adm['ticket']} ({adm['ruled']})** - owner verbatim: "
          f"*\"{adm['ruling_verbatim']}\"* - strategy `{adm['strategy']}`, "
          f"{adm.get('universe', 'universe not recorded')}, "
          f"{adm.get('window', 'window not recorded')}; artifact `{adm['grid_artifact']}`.")
    A("")
    A("**Read the evidence shape honestly (L636).** These cells come from a parameter SEARCH "
      "(300 combinations per config; no multiplicity correction at the grid stage per owner "
      "ruling D2, psr being the remaining significance-style control), and the gates are "
      "computed on the 1-year holdout except the full-period trade count. Where a holdout "
      "Sharpe far exceeds its in-sample value on a small holdout n, the margin is fragile - "
      "the IS and holdout confidence lower bounds are rendered beside the point estimates so "
      "the interval width is never hidden. Engine wiring of an admitted combination is "
      "tracked separately (S6-B2411); admission to this document is not deployment.")
    A("")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="PHASE_1B_ROSTER.md")
    ap.add_argument("--json", default="output_audit/b1453_phase_1b_roster.json")
    args = ap.parse_args()

    rows = []
    for label, cube in CUBES:
        p = REPO / cube / "trade_exit_detail.csv"
        if not p.exists():
            print(f"[WARN] {label}: {cube} missing - SKIPPED (recorded in the doc)")
            continue
        # B1455b: the four label columns are low-cardinality over millions of rows, so reading
        # them as `category` and the numerics as float32/int32 cuts peak RSS by ~4x. Without
        # this the read OOMs whenever another job holds memory - regenerating the source-of-truth
        # doc must not depend on the machine being otherwise idle.
        df = pd.read_csv(p, usecols=["strategy", "direction", "exit_method", "entry_date",
                                     "ticker", "pnl_pct", "hold_days"], low_memory=False,
                         dtype={"strategy": "category", "direction": "category",
                                "exit_method": "category", "ticker": "category",
                                "pnl_pct": "float32", "hold_days": "float32"})
        df["entry_date"] = pd.to_datetime(df["entry_date"]).dt.date
        df["pnl_pct"] = df["pnl_pct"].clip(-WINSORIZE, WINSORIZE) - COST_BPS / 100.0
        ntick = df.ticker.nunique()
        print(f"[INFO] {label:<7} {cube:<24} rows={len(df):>8} tickers={ntick:>4}")
        for (strat, direction), g in df.groupby(["strategy", "direction"]):
            # B2078 (S6-B2014a, owner-approved 2026-08-23): selection routes
            # through roster_core.select_exit - the ONE selector. The inline
            # loop it replaces carried the D7 npt refusal but NEVER the B1593
            # duplicate collapse, so its "best of 26" argmax ran over
            # byte-identical fallback columns the canonical selector
            # collapses; the two paths could disagree exactly where the
            # n_gates tie-break fell between duplicates. Control-before-edit
            # diff recorded in the S6-B2014a closing row (L607 method).
            ex_pick, pick = select_exit(g, objective="gates")
            if pick is None:
                continue
            hog = g[(g.entry_date >= HO_START) & (g.entry_date < HO_END)
                    & (g.exit_method == ex_pick)]
            graded = evaluate(hog["pnl_pct"], hog["hold_days"],
                         # B1492: the full-period leg. `g` is the WHOLE cell across all
                         # four years at the chosen exit, so len(g) is the period total
                         # the new gate needs. Without this the 4y leg silently no-ops.
                         full_period_n=len(g[g.exit_method == ex_pick]))
            rows.append({"cube": label, "n_tickers": ntick, "strategy": strat,
                         "direction": direction, "exit": truthful_exit_name(ex_pick)[0],
                         "is_sharpe": pick["sharpe"], "is_n_gates": pick["n_gates"],
                         "holdout": graded,
                         "trades": set(map(tuple, hog[["ticker", "entry_date"]].values))})

    ev = [r for r in rows if r["holdout"] and r["holdout"]["p"] is not None]
    if ev:
        rej, thr = bh_fdr([r["holdout"]["p"] for r in ev], q=FDR_Q)
        for r, ok in zip(ev, rej):
            r["bh"] = bool(ok)
    else:
        thr = 0.0
    for r in rows:
        r.setdefault("bh", False)
        h = r["holdout"]
        r["verdict"] = ("UNEVAL" if h is None else
                        "PASS" if (h["all_live_gates"] and r["bh"]) else
                        "PASS-noFDR" if h["all_live_gates"] else "DROP")

    passed = [r for r in rows if r["verdict"] == "PASS"]
    # DE-DUP. selection-justified: canonical = highest **IS** Sharpe. B1454 correction - the
    # previous version ranked on HOLDOUT Sharpe, which is a selection decision made on the
    # graded window and biases the reported roster upward. Milder than the 26-exit lookahead
    # retracted at B1452 (2 near-identical candidates, not 26) but the same class, so it is
    # fixed rather than excused. IS Sharpe keeps every selection decision inside the
    # selection window (CHECKLIST #165 + the B1452 window discipline).
    # B1974: same class - a break-even cell must not lose canonical status
    # to a losing twin because 0.0 is falsy.
    passed.sort(key=lambda r: -rank_key(r["is_sharpe"]))
    dup_of, kept = {}, []
    for r in passed:
        red = None
        for k in kept:
            A, B = r["trades"], k["trades"]
            if A and B and len(A & B) / len(A | B) >= JACCARD:
                red = k["strategy"]
                break
        if red:
            dup_of[r["strategy"]] = red
        else:
            kept.append(r)

    for r in kept:
        st, nm = mirror_status(r["strategy"])
        r["mirror_status"], r["mirror"] = st, nm
        _asym, _hits = uses_long_only_data(r["strategy"])
        r["asym_signals"] = _hits
        r["mirror_registered"] = nm in set(ALL_STRATEGIES) if nm else False

    blocked = STRATEGIES_DISABLED_DATA_SCARCITY | STRATEGIES_DISABLED_MISSING_PRODUCER | DEPRECATED_STRATEGIES
    mirrors_reg = sorted({r["mirror"] for r in kept if r["mirror_status"] == "REGISTERED" and r["mirror"]})
    mirrors_new = sorted({r["strategy"] for r in kept if r["mirror_status"] == "NEEDS-CREATION"})
    mirrors_dual = sorted({r["strategy"] for r in kept if r["mirror_status"] == "DUAL-SELF"})
    mirrors_asym = sorted({r["strategy"] for r in kept if r["mirror_status"] == "LONG-ONLY-DATA"})

    def fmt(v, w=6, d=2):
        return f"{v:>{w}.{d}f}" if isinstance(v, (int, float)) else f"{'-':>{w}}"

    L = []
    A = L.append
    A("<!-- AUTO-GENERATED by scripts/build_phase_1b_roster.py (B1453). Do NOT hand-edit; regenerate. -->")
    A("")
    A("# PHASE 1B ROSTER - THE SOURCE OF TRUTH")
    A("")
    A(f"**Generated:** B1453 | **Cubes:** " + ", ".join(f"{l} (`{c}`)" for l, c in CUBES))
    A("")
    A("> Owner directive 2026-08-04: *\"I need the updated strategy list with all strategies that "
      "pass the updated argmax criteria on gates from r5, r6 and gate 1 runs along with symmetrical "
      "short mirrors. This is the source of truth.\"*")
    A("")
    A("**This supersedes `PASSED_STRATEGY_EXIT_LIST.md`**, which is R5-only, pre-dates the "
      "B1436/B1437 gate demotions, and selects exits by argmax IS-Sharpe rather than argmax "
      "gates-cleared.")
    A("")
    A("## Method - and the one thing that makes it honest")
    A("")
    A("| Step | What | Window |")
    A("|---|---|---|")
    A("| 1 SELECT | each cell's exit by **argmax GATES-CLEARED** (tie-break IS Sharpe) | IS F1-F3 `2022-05-05 -> 2025-05-05` |")
    A("| 2 GRADE | the **single chosen** exit, once | HOLDOUT F4 `2025-05-05 -> 2026-05-05` |")
    A(f"| 3 GATE 1 | BH-FDR q<{FDR_Q} across the holdout family | holdout |")
    A(f"| 4 DE-DUP | Jaccard >= {JACCARD} on (ticker, entry_date); canonical = highest holdout Sharpe | holdout |")
    A("| 5 MIRRORS | symmetric short mirror resolved for every survivor | registry |")
    A("")
    A("**The holdout is never read during selection.** B1452 retracted an earlier variant that "
      "chose among 26 exits ON the holdout and then graded there - with 26 candidates that almost "
      "always \"passes\" and reported 35 instead of the honest count. One test per cell.")
    A("")
    A(f"**Gates (only {len(LIVE_GATES)} of 8 bind).** Live: " +
      ", ".join(f"`{g}`" for g in LIVE_GATES) + f". Demoted to diagnostics: " +
      ", ".join(f"`{g}`" for g in DEMOTED) + " (B1387 win rate; B1436 max_drawdown + "
      "deflated_sharpe; B1437 calmar - calmar divides by the demoted drawdown).")
    A("")
    A("**`sharpe_per_regime` IS A MISNOMER - it is POOLED, not per-regime (B1455c).** The gate "
      "computes ONE Sharpe over the whole holdout for the cell and compares it to the config key "
      "`min_sharpe_per_regime` (0.5); there is no regime split anywhere in the computation. The "
      "name records the THRESHOLD borrowed, not the method. This matters two ways: (a) the "
      "pipeline is already using overall Sharpe, so switching to \"overall\" means adopting "
      "`min_sharpe_overall` = **1.0**, which is far STRICTER - it cuts the 23 passers to 1; "
      "(b) canonical criterion #11 (per-regime verdict, PASS in >=1 regime) is NOT implemented "
      "here. A true per-regime verdict would be MORE permissive than pooled, since a cell would "
      "need only its best regime. Measured feasibility on the holdout - cells reaching n>=100 "
      "within a regime: **bull 3,042 | neutral 52 | bear 0**. So a per-regime verdict is "
      "computable in bull, marginal in neutral, and impossible in bear on this fold. Ticketed "
      "S6-B1455e; no threshold changes without owner approval.")
    A("")
    A("**CROSS-CUBE CAVEAT.** R5 ran 544 tickers; R6b and Group-1 ran ~140. Per-trade ratios "
      "(Sharpe, PF, expectancy) ARE comparable. **Trade counts are NOT** - `min_trades >= 100` is "
      "materially harder on the small-sample cubes, so a cell may be UNEVAL there purely from "
      "universe size. The `Cube` and `Tickers` columns are shown on every row so this is never "
      "hidden.")
    A("")
    A("## Funnel")
    A("")
    A("| # | Stage | Rows |")
    A("|---|---|---|")
    A(f"| 0 | (strategy x direction) cells with a selectable IS exit | {len(rows)} |")
    A(f"| 1 | Holdout-evaluable (n >= {MIN_N} at the chosen exit) | {sum(1 for r in rows if r['holdout'])} |")
    A(f"| 2 | Clear all {len(LIVE_GATES)} live gates on the holdout | {sum(1 for r in rows if r['holdout'] and r['holdout']['all_live_gates'])} |")
    A(f"| 3 | Survive BH-FDR (q<{FDR_Q}, threshold p<={thr:.5f}) | {len(passed)} |")
    A(f"| 4 | De-duplicated (Jaccard < {JACCARD}) | **{len(kept)}** |")
    A("")

    # S6-B1458a: a pass count alone cannot show whether a screen has independent
    # constraints or one binding gate. Leave-one-out makes that visible, and here it
    # shows profit_factor and sortino uniquely rejecting ZERO cells - the five-gate
    # screen is a three-gate screen (L294).
    A("### Gate contribution (leave-one-out)")
    A("")
    A("A pass count hides whether a screen has five independent constraints or one binding gate.")
    A("")
    A("| gate | cells passing if this gate is DROPPED | uniquely rejects |")
    A("|---|---|---|")
    _ev = [r for r in rows if r.get("holdout")]
    _base = sum(1 for r in _ev if all(r["holdout"]["gates"].values()))
    for _g in LIVE_GATES:
        _n = sum(1 for r in _ev
                 if all(v for k, v in r["holdout"]["gates"].items() if k != _g))
        _u = _n - _base
        _mark = " **(rejects nothing)**" if _u == 0 else ""
        A(f"| `{_g}` | {_n} | {_u}{_mark} |")
    A("")

    # S6-B1461b: a roster used for portfolio construction must never show only its
    # nominal count. N_eff is read from the breadth artifact rather than recomputed,
    # so there is ONE implementation of it (same principle as S6-B1452a).
    A("### Effective breadth - READ THIS BEFORE SIZING")
    A("")
    _bp = REPO / "output_audit" / "b1462_breadth_alpha.json"
    if _bp.exists():
        try:
            _b = json.loads(_bp.read_text(encoding="utf-8"))["breadth"]
            A(f"| book | legs | mean pairwise corr | **N_eff** |")
            A("|---|---|---|---|")
            for _k, _lab in (("long_only", "LONG ONLY (the graded cells)"),
                             ("deployable", "DEPLOYABLE BOOK (all legs)")):
                _r = _b.get(_k)
                if _r:
                    A(f"| {_lab} | {_r['n']} | {_r['rho_bar']:.3f} | **{_r['n_eff']:.1f}** |")
            A("")
            A("The cell count is NOT the number of independent bets. De-dup compares (ticker, "
              "entry_date) SIGNAL overlap; two cells sharing few entries can still move together "
              "through shared ticker selection, signal family or entry timing. Beta-residualising "
              "against SPY moves N_eff by ~0.0 (mean R^2 0.010), so this is NOT market beta and "
              "beta-neutralising would not restore breadth (S6-B1461a, L301).")
            A("")
            A("**The deployable figure is carried by the short legs, which have NO holdout "
              "evidence of positive edge** - they are retained by the owner's symmetry directive, "
              "0 of 82 shorts cleared all five gates in bear (B1455), and several carry negative "
              "alpha. Evidenced breadth is the LONG ONLY row.")
        except Exception as _e:                        # preflight-allow: bare-report
            A(f"_breadth artifact unreadable ({_e}); run scripts/measure_roster_breadth_and_alpha.py_")
    else:
        A("_N_eff NOT MEASURED - run `scripts/measure_roster_breadth_and_alpha.py` before sizing._")
    A("")
    A(f"## THE ROSTER - {len(kept)} cells")
    A("")
    A("| # | Strategy | Dir | Cube | Tkrs | Exit | IS Shrp | HO Shrp | margin | HO n | Exp | WR | PF | Payoff | Mirror |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    # B1974: display sort - same class, no decision rides on it, fixed
    # anyway so the file has ONE definition of the ranking key (#226).
    for i, r in enumerate(sorted(kept,
                                 key=lambda x: -rank_key(x["holdout"]["sharpe"])), 1):
        h = r["holdout"]
        # B1455b: render every status the classifier can emit. This previously fell through
        # to "**NEEDS CREATION**" for anything that was not REGISTERED or LONG-ONLY-DATA, so
        # DUAL-SELF rows rendered as needing creation while the summary block below correctly
        # reported zero - the table and its own summary contradicted each other in a shipped doc.
        mir = {"REGISTERED": f"`{r['mirror']}`",
               "LONG-ONLY-DATA": "LONG-ONLY DATA",
               "DUAL-SELF": "DUAL (own short leg)",
               "NEEDS-CREATION": "**NEEDS CREATION**"}.get(
                   r["mirror_status"], f"**UNCLASSIFIED: {r['mirror_status']}**")
        # B2009: margin against the bar the cell actually had to clear - the
        # LIVE pooled gate (min_sharpe_overall, B1493-armed), not the
        # per-regime 0.5. The crossed-bar class, inside the roster builder.
        # B2048 (S6-B1972b): a kept cell passed the Sharpe gate, so an absent
        # holdout Sharpe here is a broken contract - it must FAIL LOUD, not
        # coalesce to 0 and silently print margin -1.0.
        if h["sharpe"] is None:
            raise ValueError(
                f"gate-passing cell {r['strategy']}|{r['direction']} carries "
                "no holdout sharpe - the kept-population contract broke")
        # S6-B2379/S6-B2409: one definition, in roster_core; margin is a
        # reported number only - the ROBUST/PROVISIONAL split is retired
        # (owner ruling 2026-08-30).
        from roster_core import qualifier_margin as _qualifier_margin
        margin = _qualifier_margin(h["sharpe"])
        r["margin"] = margin
        A(f"| {i} | `{r['strategy']}` | {r['direction']} | {r['cube']} | {r['n_tickers']} | "
          f"`{r['exit']}` | {fmt(r['is_sharpe'])} | {fmt(h['sharpe'])} | {margin:+.3f} | {h['n']} | "
          f"{fmt(h['expectancy'])} | {fmt(h['win_rate'],5,3)} | {fmt(h['profit_factor'])} | "
          f"{fmt(h['payoff'])} | {mir} |")
    A("")
    A("**Qualification (S6-B2409, owner ruling 2026-08-30).** A cell on this roster cleared "
      "all six live gates - that IS qualification. The former ROBUST/PROVISIONAL split "
      "against a selection-noise floor is retired in its entirety; `margin` reports how far "
      "the holdout Sharpe cleared the live pooled gate, as a number, gating nothing.")
    A("")
    # S6-B2413: owner-ruled Step-2 admissions render here, between the funnel
    # roster and the mirrors - identity from the admissions file, metrics
    # re-derived from each admission's own grading artifact.
    step2_admissions_section(A)
    A("## Symmetric short mirrors")
    A("")
    A("Owner standing directive: *promoted longs carry short mirrors by default* - the mirror is "
      "retained irrespective of its own cube result. The single excuse is a **long-only DATA "
      "SOURCE** (13F / insider / congressional / buyback), where a mechanical inverse is "
      "economically false rather than merely untested (B611 reversal).")
    A("")
    A(f"- **REGISTERED and retained ({len(mirrors_reg)}):** " +
      (", ".join(f"`{m}`" for m in mirrors_reg) if mirrors_reg else "none"))
    A(f"- **LONG-ONLY DATA, mirror excused ({len(mirrors_asym)}):**")
    if mirrors_asym:
        _ev = {r["strategy"]: r.get("asym_signals") or [] for r in kept}
        for m in mirrors_asym:
            A(f"    - `{m}` - consumes " + ", ".join(f"`{k}`" for k in _ev.get(m, [])))
        A("")
        A("    Excusal is decided from the signals each function ACTUALLY consumes, never from its "
          "name. B1453 caught `xs_momentum_with_smart_money_long` being excused on its name alone "
          "while B1194 had already removed its smart_money gate - it is NOT excused and its exact "
          "mirror `xs_momentum_bottom_decile_short` is retained.")
    else:
        A("    - none")
    A(f"- **DUAL - own short branch is the mirror, nothing to create ({len(mirrors_dual)}):** " +
      (", ".join(f"`{m}`" for m in mirrors_dual) if mirrors_dual else "none"))
    A(f"- **NEEDS CREATION ({len(mirrors_new)}):** " +
      (", ".join(f"`{m}`" for m in mirrors_new) if mirrors_new else "none"))
    A("")
    A(f"**Deployable total: {len(kept)} graded cells + {len(mirrors_reg)} registered mirrors "
      f"+ {len(mirrors_dual)} dual self-mirrors = {len(kept) + len(mirrors_reg)}** "
      f"(dual mirrors are already counted in their parent cell), plus "
      f"{len(mirrors_new)} mirrors to create.")
    A("")
    A("## What this roster does NOT establish")
    A("")
    A("1. **Shorts ARE now tested in bear - and they fail there too (B1455).** The earlier wording "
      "here (\"untested, not refuted\") was itself a data-partition artifact and is retracted. The "
      "holdout is 88% bull and holds only 33,644 bear-regime short trades spread across 93 "
      "strategies, so **0 cells reach n>=100** - that, not weak short edge, is why B1385's "
      "regime-conditional gate returned 77 UNEVAL. But the locked window *does* contain **567,814 "
      "bear-regime short trades**; they sit in the 2022-23 fold. Repartitioning (select "
      "2023-05->2026-05, grade on bear entries 2022-05->2023-05; `scripts/bear_regime_stress_test.py`) "
      "makes 1,560 short cells gradable with no new run:")
    A("")
    A("   | direction | gradable in bear | clear all 5 live gates | positive expectancy |")
    A("   |---|---|---|---|")
    A("   | SHORT | 82 | **0** | 18/82 (22%) |")
    A("   | LONG | 110 | 4 | 58/110 (53%) |")
    A("")
    A("   Shorts clear nothing in the bear market they exist for, and are outperformed by longs "
      "*inside that same bear*. **This is a stress test, not a promotion verdict** - it selects on "
      "later data and grades on earlier data, so it is temporally backwards and not walk-forward "
      "valid; the chosen exit is fitted to post-bear conditions. Per owner directive the mirrors "
      "are **retained irrespective**. This sizes the exposure taken on structural-symmetry "
      "grounds; it does not validate it.")
    A("2. **Levels are conditioned on the incumbent exit's trade set (S6-B1434c).** The cube "
      "replays all 26 exits over trades the ASSIGNED exit generated; ranking transfers, absolute "
      "magnitudes do not.")
    A("3. **`min_trades` will tighten in deployment.** Longer-hold exits plus same-strategy dedup "
      "reduce live fire counts below these cube figures.")
    A(f"4. **Blocked strategies excluded upstream:** {len(blocked)} "
      f"({len(STRATEGIES_DISABLED_DATA_SCARCITY)} data-scarcity, "
      f"{len(STRATEGIES_DISABLED_MISSING_PRODUCER)} missing-producer, "
      f"{len(DEPRECATED_STRATEGIES)} deprecated).")
    A("")
    A("## Reproduce")
    A("")
    A("```\npython scripts/build_phase_1b_roster.py\n```")
    A("")

    (REPO / args.output).write_text("\n".join(L), encoding="utf-8")
    for r in rows:
        r.pop("trades", None)
    (REPO / args.json).write_text(json.dumps(
        {"generated": "B1453", "cubes": {l: c for l, c in CUBES},
         "live_gates": list(LIVE_GATES), "demoted": list(DEMOTED),
         "selection_window": [str(IS_START), str(IS_END)],
         "grading_window": [str(HO_START), str(HO_END)],
         "fdr_q": FDR_Q, "fdr_threshold": thr, "jaccard": JACCARD,
         "n_cells": len(rows), "n_passed_fdr": len(passed), "n_roster": len(kept),
         "dup_of": dup_of,
         "mirrors": {"registered": mirrors_reg, "long_only_data": mirrors_asym,
                     "dual_self": mirrors_dual, "needs_creation": mirrors_new},
         "roster": [{k: v for k, v in r.items() if k != "trades"} for r in kept],
         "all_rows": rows}, indent=2, default=str), encoding="utf-8")

    print(f"\n[FUNNEL] cells {len(rows)} -> holdout-evaluable "
          f"{sum(1 for r in rows if r['holdout'])} -> all-gates "
          f"{sum(1 for r in rows if r['holdout'] and r['holdout']['all_live_gates'])} -> "
          f"BH-FDR {len(passed)} -> de-duped {len(kept)}")
    print(f"[MIRRORS] registered {len(mirrors_reg)} | dual-self {len(mirrors_dual)} | "
          f"long-only-excused {len(mirrors_asym)} | needs-creation {len(mirrors_new)}")
    # B1976: freshness stamp - sha256 of the generator sources this run
    # actually executed. The staleness gate accepts a matching stamp as
    # freshness, because an OUTPUT-PRESERVING generator change leaves the
    # artifact byte-identical and never re-committed, and a commit-timestamp
    # comparison then fires forever with no satisfying action except a
    # no-op commit.
    # B2078: READ-THEN-UPDATE, never overwrite - the stamp file is SHARED
    # (build_strategy_producer_map.py stamps itself here too, B2058), and
    # this writer's fresh-dict form silently DELETED the other generator's
    # entry on every roster run, resurrecting the timestamp gate for an
    # artifact that was provably fresh. Two writers for one artifact, one
    # of them lossy - the L603 class, inside the freshness machinery.
    import hashlib as _hl
    _sp = REPO / "output_audit" / "phase_1b_roster_freshness.json"
    _stamp = json.loads(_sp.read_text(encoding="utf-8")) if _sp.exists() else {}
    _stamp.update({f: _hl.sha256((REPO / f).read_bytes()).hexdigest()
                   for f in ("scripts/build_phase_1b_roster.py",
                             "scripts/roster_core.py",
                             "scripts/walk_forward_r5_cells.py")})
    _sp.write_text(json.dumps(_stamp, indent=1), encoding="utf-8")
    print(f"[OK] wrote {args.output} + {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
