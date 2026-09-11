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
IS_END = date(2025, 5, 5)          # roster_core.py:56-57 boundary
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


def load_entries(exit_method: str, window: str) -> pd.DataFrame:
    tl = pd.read_csv(TRADE_LOG, low_memory=False,
                     usecols=["strategy", "ticker", "entry_date", "signals_at_entry"])
    fam = tl[tl.strategy.str.startswith(FAMILY_PREFIX)]
    ent = fam.drop_duplicates(["ticker", "entry_date"]).copy()

    cube = pd.read_csv(CUBE, low_memory=False,
                       usecols=["strategy", "ticker", "entry_date", "exit_method", "pnl_pct"])
    cc = cube[(cube.strategy.str.startswith(FAMILY_PREFIX))
              & (cube.exit_method == exit_method)]
    pnl = cc.drop_duplicates(["ticker", "entry_date"])[["ticker", "entry_date", "pnl_pct"]]

    m = ent.merge(pnl, on=["ticker", "entry_date"], how="inner")
    m["entry_d"] = pd.to_datetime(m["entry_date"], errors="coerce").dt.date
    if window == "is":
        m = m[m.entry_d < IS_END]
    elif window == "holdout":
        m = m[m.entry_d >= IS_END]
    else:
        raise SystemExit(f"unknown --window {window!r}")
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
    head = (f"# COMPANION-SIGNAL SCREEN - {FAMILY_PREFIX}family\n\n"
            f"exit {args.exit}; window {args.window}"
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
    global FAMILY_PREFIX
    ap = argparse.ArgumentParser()
    ap.add_argument("--exit", required=True)
    # B2672 (L754: second family extracts the contract): the family is a
    # parameter, not a constant. Default preserves institutional behaviour.
    ap.add_argument("--family", default=FAMILY_PREFIX)
    ap.add_argument("--window", default="is", choices=["is", "holdout"])
    ap.add_argument("--min-side", type=int, default=100)
    ap.add_argument("--min-n", type=int, default=500)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    FAMILY_PREFIX = args.family
    m = load_entries(args.exit, args.window)
    if len(m) < 500:
        raise SystemExit(f"REFUSED: only {len(m)} entries in window - underpowered")
    rows, meta = screen(m, args.min_side, args.min_n)
    rec = {"family": FAMILY_PREFIX, "exit": args.exit, "window": args.window,
           "peeked": args.window == "holdout", **meta, "results": rows}
    out = Path(args.out)
    out.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    out.with_suffix(".md").write_text(render(rows, meta, args), encoding="utf-8")
    print(f"{meta['entries']} entries | {meta['trials']} signals | "
          f"{meta['survivors']} FDR survivors -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
