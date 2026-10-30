#!/usr/bin/env python
# Source: output_r5_merged_1_7/{trade_log.csv,trade_exit_detail.csv} per CHECKLIST #77.
"""B2657 (S6-B2656, owner green-light 2026-09-09): the COMPANION-SIGNAL SCREEN.

THE QUESTION IT ANSWERS (owner, verbatim intent): the institutional family's
20 strategies did not qualify, yet institutional direction should be a strong
momentum indicator - so what OTHER persisted signals separate the family's
WINNING trades from its losers? Not knob-tuning: candidate companion
producers that eliminate noise.

DESIGN, stated before the data was read:
  - UNIT = unique (ticker, entry_date) ENTRY, deduplicated across the 20
    collinear family strategies (29,411 fires collapse to unique entries;
    using fires would pseudo-replicate each bar up to 20x).
  - OUTCOME = per-trade pnl_pct at a FIXED exit passed via --exit (no
    per-cell exit selection - selection would smuggle hindsight into the
    outcome). Run twice with different exits and keep only signals that
    discriminate under BOTH.
  - WINDOW = in-sample only by default (entries before 2025-05-05, the
    roster_core boundary), so any gate built from a finding can still be
    validated on data this screen never read. --window holdout exists for
    CONFIRMATION reads and stamps the artifact PEEKED (the family's holdout
    was spent at B2628).
  - FEATURES = every signals_at_entry key present on >= min-presence of
    entries, EXCLUDING the family's own gate keys (institutional_*) - a gate
    trivially "discriminates" its own fires.
      booleans: Welch t on pnl (True vs False), win-rate delta, min n per
                side --min-side (power floor).
      numerics: Spearman rho with pnl + top-vs-bottom quintile pnl spread,
                min non-null --min-n.
  - MULTIPLICITY: every test's p enters ONE Benjamini-Hochberg FDR at
    q=0.05 (walk_forward_r5_cells.bh_fdr, the same implementation the
    roster uses); the artifact records trials and survivors. This is a
    SCREEN - a ranked hypothesis list for producer design - never a gate:
    anything promoted from it must clear its own pre-registered campaign.

Artifact: JSON + a ranked markdown table beside it (the offline Table-D
convention, B2643).
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from walk_forward_r5_cells import bh_fdr  # noqa: E402  (canonical FDR)

CUBE = ROOT / "output_r5_merged_1_7" / "trade_exit_detail.csv"
TRADE_LOG = ROOT / "output_r5_merged_1_7" / "trade_log.csv"
# S6-B3335 (B3139q-r156): the R5 source, kept when --cube-dir rebinds TRADE_LOG
# and CUBE to a run's own directory - the survival filter and its guard
# describe R5 fires only (breadth_step1_grid's S6-B3321 convention)
R5_TRADE_LOG = TRADE_LOG
from roster_core import IS_END  # noqa: E402  (the one roster boundary, S6-B3139bc)
from breadth_step1_grid import BASES  # noqa: E402  (one basis vocabulary, S6-B3314)
FAMILY_PREFIX = "institutional_"


def _parse(s):
    if not isinstance(s, str) or not s.strip():
        return {}
    try:
        return json.loads(s)
    except Exception:
        try:
            return ast.literal_eval(s)
        except Exception:
            return {}


def _selector(names):
    """S6-B3291: the family is selected by EXACT NAME when --strategy is
    given, by prefix otherwise. The prefix form also takes every strategy
    whose name extends the subject's (squeeze_breakout takes
    squeeze_breakout_with_smart_money_long), so a single-strategy screen
    reads the wrong population - the exact form is what a campaign runs."""
    if names:
        want = set(names)
        return lambda s: s.isin(want)
    return lambda s: s.str.startswith(FAMILY_PREFIX)


def _read_selected(path, usecols, sel, chunksize: int = 250_000) -> pd.DataFrame:
    """S6-B3291: stream the merged file in chunks and keep the selected
    strategies' rows - the whole-file read (4.6 GB trade log, 1.6 GB cube)
    cannot run beside a chain on the owner's memory budget."""
    parts = [ch[sel(ch["strategy"])]
             for ch in pd.read_csv(path, low_memory=False, usecols=usecols,
                                   chunksize=chunksize)]
    parts = [p for p in parts if len(p)]
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=usecols)


def _surviving(ent: pd.DataFrame) -> tuple:
    """S6-B3320 (B3139q-r121): the T1 survival filter, per strategy - the
    fires the CURRENT gate keeps, build_table_a.surviving_fires on the status
    view's inputs (offline_level_sweep._survival_inputs): the one definition
    the depth sweep's --survival applies. Returns (kept, disclosure). The
    filter runs on every fire of the selection, BOTH legs - the leg is cut
    afterwards on the cube - so the per-leg counts sit in by_direction."""
    import build_table_a as bta
    from offline_level_sweep import _survival_inputs
    parts, by = [], {}
    for s, part in ent.groupby("strategy", sort=True):
        pct, unmeasured = _survival_inputs(s)
        kept, _sigs, _f = bta.surviving_fires(s, part, pct, unmeasured)
        by[s] = [int(len(part)), int(len(kept))]
        parts.append(kept)
    out = pd.concat(parts) if parts else ent.iloc[0:0]
    legs = sorted(set(ent["direction"].astype(str)))
    by_dir = {d: [int((ent["direction"].astype(str) == d).sum()),
                  int((out["direction"].astype(str) == d).sum())] for d in legs}
    return out, {"applied": True, "scope": "every fire of the selection, both legs",
                 "fires_before": int(len(ent)), "fires_after": int(len(out)),
                 "by_strategy": by, "by_direction": by_dir}


def load_entries(exit_method: str, window: str, names=None,
                 direction: str | None = None, survival: bool = False,
                 basis: str = "gross") -> pd.DataFrame:
    """S6-B3247 (B3139q-r117): `direction` keeps ONE leg of a dual strategy -
    a pooled screen ranks companions on long and short trades together,
    whose winners and losers have different drivers. None pools, as
    before (every artifact up to r116 is pooled).
    S6-B3320 (B3139q-r121): `survival` keeps the fires the CURRENT gate keeps
    (_surviving); without it a strategy whose gate changed since R5 is
    screened on fires the gate now removes, which main() refuses. The
    disclosure rides the returned frame's attrs['survival'].
    S6-B3382 (B3139q-r157): `basis` is 'gross' (the raw cube pnl, the
    default) or 'net' (roster_core.net_pnl, the grids' basis)."""
    if direction not in (None, "long", "short"):
        raise SystemExit(f"REFUSED: direction {direction!r} is not long or short")
    if basis not in BASES:
        raise SystemExit(f"REFUSED: basis {basis!r} not in {BASES} (S6-B3382)")
    sel = _selector(names)
    cols = ["strategy", "ticker", "entry_date", "signals_at_entry"]
    fam = _read_selected(TRADE_LOG, cols + (["direction"] if survival else []), sel)
    ent = fam.drop_duplicates(["ticker", "entry_date"]).copy()
    surv = {"applied": False}
    if survival:
        ent, surv = _surviving(ent)

    # the leg is decided by the CUBE's direction: the inner merge below drops
    # every entry with no pnl row on the kept leg, so a trade-log filter would
    # repeat it (a mutation probe found that copy unkillable). The pooled path
    # reads exactly the columns it always read (test_b3291's fixture has none)
    leg = ["direction"] if direction is not None else []
    cube = _read_selected(CUBE, ["strategy", "ticker", "entry_date",
                                 "exit_method", "pnl_pct"] + leg, sel)
    if direction is not None:
        cube = cube[cube["direction"] == direction]
    cc = cube[cube.exit_method == exit_method]
    pnl = cc.drop_duplicates(["ticker", "entry_date"])[["ticker", "entry_date", "pnl_pct"]]
    # S6-B3382 (B3139q-r157): the P&L the effects are scored on. 'net' is the
    # grids' basis - winsorized at +/-WINSORIZE, the round-trip cost charged -
    # through the ONE definition they call (roster_core.net_pnl, S6-B3139ag);
    # 'gross' is the raw cube pnl every screen before it scored
    if basis == "net":
        import roster_core as _rc
        pnl = pnl.assign(pnl_pct=_rc.net_pnl(pnl["pnl_pct"]))

    m = ent.merge(pnl, on=["ticker", "entry_date"], how="inner")
    m["entry_d"] = pd.to_datetime(m["entry_date"], errors="coerce").dt.date
    if window == "is":
        m = m[m.entry_d < IS_END]
    elif window == "holdout":
        m = m[m.entry_d >= IS_END]
    else:
        raise SystemExit(f"unknown --window {window!r}")
    m.attrs["survival"] = surv
    return m


def screen(m: pd.DataFrame, min_side: int, min_n: int) -> tuple[list, dict]:
    from scipy import stats as st
    dicts = [_parse(s) for s in m["signals_at_entry"]]
    pnl = m["pnl_pct"].to_numpy(dtype=float)
    n = len(dicts)

    presence: dict[str, int] = {}
    for d in dicts:
        for k in d:
            presence[k] = presence.get(k, 0) + 1
    keys = [k for k, c in presence.items()
            if c >= 0.8 * n and not k.startswith(FAMILY_PREFIX)]

    rows = []
    for k in sorted(keys):
        vals = [d.get(k) for d in dicts]
        bools = [v for v in vals if isinstance(v, bool)]
        if len(bools) >= 0.8 * n:                      # boolean signal
            mask_t = np.array([v is True for v in vals])
            mask_f = np.array([v is False for v in vals])
            nt, nf = int(mask_t.sum()), int(mask_f.sum())
            if nt < min_side or nf < min_side:
                continue
            pt, pf = pnl[mask_t], pnl[mask_f]
            tstat, p = st.ttest_ind(pt, pf, equal_var=False)
            rows.append({"key": k, "kind": "bool", "n_true": nt, "n_false": nf,
                         "mean_pnl_true": float(pt.mean()),
                         "mean_pnl_false": float(pf.mean()),
                         "pnl_lift": float(pt.mean() - pf.mean()),
                         "winrate_true": float((pt > 0).mean()),
                         "winrate_false": float((pf > 0).mean()),
                         "p": float(p)})
        else:                                          # numeric signal
            num = pd.to_numeric(pd.Series(vals), errors="coerce")
            ok = num.notna().to_numpy()
            if int(ok.sum()) < min_n or num[ok].nunique() < 5:
                continue
            x, y = num[ok].to_numpy(dtype=float), pnl[ok]
            rho, p = st.spearmanr(x, y)
            if not np.isfinite(rho):
                continue
            q = pd.qcut(pd.Series(x), 5, labels=False, duplicates="drop")
            if q.nunique() < 5:
                continue
            top, bot = y[(q == q.max()).to_numpy()], y[(q == 0).to_numpy()]
            rows.append({"key": k, "kind": "numeric", "n": int(ok.sum()),
                         "spearman_rho": float(rho),
                         "q5_mean_pnl": float(top.mean()),
                         "q1_mean_pnl": float(bot.mean()),
                         "q5_minus_q1": float(top.mean() - bot.mean()),
                         "p": float(p)})

    rej, thr = bh_fdr([r["p"] for r in rows], q=0.05)
    for r, keep in zip(rows, rej):
        r["fdr_survivor"] = bool(keep)
    meta = {"entries": n, "trials": len(rows), "fdr_threshold": thr,
            "survivors": int(sum(rej))}
    return rows, meta


def render(rows: list, meta: dict, args) -> str:
    surv = [r for r in rows if r["fdr_survivor"]]
    surv.sort(key=lambda r: -(abs(r.get("pnl_lift", 0)) + abs(r.get("q5_minus_q1", 0))))
    fam_label = (", ".join(args.strategy) + " (exact names)" if getattr(args, "strategy", None)
                 else f"{FAMILY_PREFIX}family")
    head = (f"# COMPANION-SIGNAL SCREEN - {fam_label}\n\n"
            f"exit {args.exit}; basis {getattr(args, 'basis', 'gross')}; window {args.window}"
            f"{' (PEEKED - spent holdout, confirmation only)' if args.window == 'holdout' else ''}; "
            f"{meta['entries']} unique entries; {meta['trials']} signals tested; "
            f"BH-FDR q=0.05 threshold p<={meta['fdr_threshold']:.5g}; "
            f"{meta['survivors']} survivors. A SCREEN, not a gate (hypothesis "
            f"list for producer design).\n\n")
    lines = ["| rank | signal | kind | effect (pnl) | detail | p |",
             "|---|---|---|---|---|---|"]
    for i, r in enumerate(surv[:40], 1):
        if r["kind"] == "bool":
            eff = f"{r['pnl_lift']:+.2f} (T {r['mean_pnl_true']:.2f} vs F {r['mean_pnl_false']:.2f})"
            det = (f"n {r['n_true']}/{r['n_false']}, WR "
                   f"{r['winrate_true']:.3f} vs {r['winrate_false']:.3f}")
        else:
            eff = f"Q5-Q1 {r['q5_minus_q1']:+.2f} (rho {r['spearman_rho']:+.3f})"
            det = f"n {r['n']}, Q5 {r['q5_mean_pnl']:.2f} vs Q1 {r['q1_mean_pnl']:.2f}"
        lines.append(f"| {i} | {r['key']} | {r['kind']} | {eff} | {det} | {r['p']:.2e} |")
    return head + "\n".join(lines) + "\n"


def main() -> int:
    global FAMILY_PREFIX, CUBE, TRADE_LOG
    ap = argparse.ArgumentParser()
    ap.add_argument("--exit", required=True)
    # B2672 (L754: second family extracts the contract): the family is a
    # parameter, not a constant. Default preserves institutional behaviour.
    ap.add_argument("--family", default=FAMILY_PREFIX)
    ap.add_argument("--strategy", action="append", default=None,
                    help="S6-B3291: select by EXACT strategy name (repeatable); "
                         "overrides the --family prefix selection")
    ap.add_argument("--window", default="is", choices=["is", "holdout"])
    ap.add_argument("--direction", default=None, choices=["long", "short"],
                    help="S6-B3247: screen ONE leg of a dual strategy (default: pooled)")
    ap.add_argument("--survival", action="store_true",
                    help="S6-B3320: screen only the fires the CURRENT gate keeps "
                         "(required when a strategy's gate changed since R5)")
    ap.add_argument("--cube-dir", default=None,
                    help="S6-B3335: screen a run DIRECTORY's own fires (its "
                         "trade_log.csv and trade_exit_detail.csv) in place of "
                         "R5 - breadth_step1_grid's --cube-dir (S6-B3112c); "
                         "--survival and its guard are R5-only")
    ap.add_argument("--basis", required=True, choices=BASES,
                    help="S6-B3382: the pnl basis the effects are scored on, "
                         "stated on every run and recorded on the artifact - "
                         "'net' is the grids' basis (roster_core.net_pnl); no "
                         "default, so a screen is never gross by omission")
    ap.add_argument("--min-side", type=int, default=100)
    ap.add_argument("--min-n", type=int, default=500)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    FAMILY_PREFIX = args.family
    if args.cube_dir:
        CUBE = ROOT / args.cube_dir / "trade_exit_detail.csv"
        TRADE_LOG = ROOT / args.cube_dir / "trade_log.csv"
        for _f in (CUBE, TRADE_LOG):
            if not _f.exists():
                raise SystemExit(f"REFUSED: --cube-dir file missing: {_f}")
        print(f"cube-dir override: {args.cube_dir} (S6-B3335)")
    # no --cube-dir reads the module's own source (R5, or a test's stand-in);
    # a --cube-dir that names R5 is R5 as well
    reads_r5 = (not args.cube_dir
                or Path(TRADE_LOG).resolve() == Path(R5_TRADE_LOG).resolve())
    if args.survival and not reads_r5:
        raise SystemExit("REFUSED (S6-B3335): --survival filters R5 fires to the "
                         f"current gate; {args.cube_dir} is a run's own cube, which "
                         "holds the gate it ran under")
    m = load_entries(args.exit, args.window, names=args.strategy,
                     direction=args.direction, survival=args.survival,
                     basis=args.basis)
    # S6-B3320: fail closed (L642) - a strategy whose current gate keeps fewer
    # than all of its R5 fires is screened on the fires it keeps; the ONE guard
    # every R5 instrument calls (step1_gates, S6-B3321)
    from step1_gates import require_surviving_or_unchanged
    if reads_r5:                 # S6-B3335: a run's own cube needs no guard
        for s in sorted(set(m["strategy"])):
            require_surviving_or_unchanged(s, args.survival)
    if len(m) < 500:
        raise SystemExit(f"REFUSED: only {len(m)} entries in window - underpowered")
    rows, meta = screen(m, args.min_side, args.min_n)
    rec = {"family": FAMILY_PREFIX, "strategies": args.strategy,
           "selection": "exact" if args.strategy else "prefix",
           "direction": args.direction,
           "survival": m.attrs.get("survival"),     # S6-B3320
           "cube_dir": args.cube_dir or "output_r5_merged_1_7 (default)",   # S6-B3335
           "basis": args.basis,                                            # S6-B3382
           "exit": args.exit, "window": args.window,
           "peeked": args.window == "holdout", **meta, "results": rows}
    out = Path(args.out)
    out.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    out.with_suffix(".md").write_text(render(rows, meta, args), encoding="utf-8")
    print(f"{meta['entries']} entries | {meta['trials']} signals | "
          f"{meta['survivors']} FDR survivors -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
