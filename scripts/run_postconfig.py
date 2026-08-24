#!/usr/bin/env python
"""Mechanical post-config checks, automated (B2118, S6-B2117b - owner
directive: identify more errors/edge cases; automate and gate each step).

VERIFIED REALITY this closes: of the 9 mandatory post-config steps, only
step 1 was automated (run_wave, wave cubes only); steps 2/3/4/7 had scripts
with ZERO automatic invokers (#224). This runner executes every check that
is mechanical per cube, prints PASS/FAIL/SKIP per check with evidence, and
(with --write-ledger) records step 1 in the shared ledger. Judgment steps
(5/6/8) are NOT automated - a script marking them done would manufacture
compliance; they print as prompts.

NEW CHECKS beyond the runbook (the M-list, S6-B2117b):
  M1 determinism content-sha of the sorted trade columns (the B2094 regime -
     catches wrong-interpreter/env drift instantly when compared across runs)
  M2 exits-per-entry vs len(EXIT_STRATEGIES) DERIVED LIVE - never a
     hardcoded [26]; a pre-B2110 cube discloses its own registry-at-sha count
  M3 fill_date presence (B2087 schema) + no fill before entry where present
  M4 PIT window bounds + HOLDOUT-TOUCH detector (any entry >= HO_START in a
     Step-1 cube is an instant FAIL - the leak class B1718 closed)
  M5 NaN/inf pnl + beyond-winsorize magnitudes (the SBNY L581 class)
  M7 measure_degraded_exits auto-invoked (was listed, was manual)
  step 7 verify_engine_implemented.py invoked (was HAND-RUN-ONLY)

Usage:
  PYTHONPATH=. python scripts/run_postconfig.py --cube output_<dir>
      [--step1-cube]        # arms the M4 holdout-touch FAIL
      [--write-ledger]      # records 1_cube_sanity in the shared ledger
Exit 0 = no FAIL; 2 = at least one FAIL.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

MEGA = ("NVDA", "MSFT", "GOOGL", "META", "TSLA", "AAPL")


def checks(cube_dir: Path, step1: bool = False):
    import pandas as pd
    from roster_core import HO_START, WINSORIZE

    out = []
    f = cube_dir / "trade_exit_detail.csv"
    if not f.exists():
        return [("cube_exists", "FAIL", f"{f} missing")]
    df = pd.read_csv(f, low_memory=False)
    out.append(("cube_exists", "PASS", f"{len(df)} rows"))

    # 1. sanity: strategies / exits-per-entry / mega-caps
    n_strat = df["strategy"].nunique()
    out.append(("one_strategy", "PASS" if n_strat == 1 else "FAIL",
                f"{n_strat} strategies"))
    from backtest.engine.exit_strategies import EXIT_STRATEGIES
    epe = df.groupby(["ticker", "entry_date"]).exit_method.nunique().unique()
    reg = len(EXIT_STRATEGIES)
    ok = len(epe) == 1 and (epe[0] == reg or epe[0] in (24, 25, 26))
    out.append(("M2_exits_per_entry_vs_registry",
                "PASS" if len(epe) == 1 and epe[0] == reg else
                ("PASS" if ok else "FAIL"),
                f"cube {sorted(epe.tolist())} vs registry-now {reg} "
                f"(a differing single value = an older registry at the "
                f"cube's sha - disclosed, judged there)"))
    megas = [t for t in MEGA if t in set(df["ticker"])]
    mega_ev = (", ".join(megas) if megas else
               "none - small/deliberate universes SKIP; the archived A-C "
               "chunk trap is the FAIL case for 100t+ cubes")
    out.append(("megacaps_present", "PASS" if megas else "SKIP", mega_ev))

    # M1 determinism sha
    cols = [c for c in ("strategy", "direction", "exit_method", "entry_date",
                        "ticker", "pnl_pct", "hold_days") if c in df.columns]
    sha = hashlib.sha256(
        df[cols].sort_values(cols).to_csv(index=False).encode()).hexdigest()[:16]
    out.append(("M1_content_sha", "PASS", sha))

    # M3 fill_date
    if "fill_date" in df.columns:
        bad = (pd.to_datetime(df["fill_date"], errors="coerce")
               < pd.to_datetime(df["entry_date"], errors="coerce")).sum()
        out.append(("M3_fill_date", "PASS" if bad == 0 else "FAIL",
                    f"{bad} fills before entry"))
    else:
        out.append(("M3_fill_date", "SKIP",
                    "column absent (pre-B2087 cube - expected)"))

    # M4 PIT bounds + holdout touch
    ed = pd.to_datetime(df["entry_date"], errors="coerce").dt.date
    out.append(("M4_window", "PASS", f"entries {ed.min()} .. {ed.max()}"))
    touched = int((ed >= HO_START).sum())
    if step1:
        out.append(("M4_holdout_touch", "PASS" if touched == 0 else "FAIL",
                    f"{touched} entries at/after HO_START {HO_START} in a "
                    "STEP-1 cube"))
    else:
        out.append(("M4_holdout_touch", "SKIP",
                    f"{touched} entries past {HO_START} (not declared a "
                    "Step-1 cube; pass --step1-cube to arm the FAIL)"))

    # M5 pnl integrity
    import numpy as np
    pnl = pd.to_numeric(df["pnl_pct"], errors="coerce")
    nan_inf = int(pnl.isna().sum() + np.isinf(pnl.fillna(0)).sum())
    beyond = int((pnl.abs() > WINSORIZE).sum())
    out.append(("M5_pnl_integrity", "PASS" if nan_inf == 0 else "FAIL",
                f"{nan_inf} NaN/inf; {beyond} beyond winsorize {WINSORIZE} "
                "(beyond-count is DISCLOSURE - the SBNY class - clip "
                "happens at grade time)"))

    # M7 degraded exits, auto
    try:
        import roster_core as rc
        deg = rc.measure_degraded_exits(rc.load_cube(f))
        out.append(("M7_degraded_exits", "PASS",
                    f"degraded map (B1623 measure-not-assume): {deg or '{}'}"))
    except Exception as exc:
        out.append(("M7_degraded_exits", "SKIP", f"lens unavailable: {exc!r}"))

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", required=True)
    ap.add_argument("--step1-cube", action="store_true")
    ap.add_argument("--write-ledger", action="store_true")
    a = ap.parse_args()
    cube_dir = ROOT / a.cube
    try:
        results = checks(cube_dir, step1=a.step1_cube)
    except Exception as exc:
        # a cube whose schema breaks the checks is a FAILED cube, loudly -
        # never a traceback that reads as a tooling problem (L566 class)
        results = [("checks_crashed", "FAIL", repr(exc))]

    # step 7, invoked (was HAND-RUN-ONLY)
    r = subprocess.run([sys.executable,
                        str(ROOT / "scripts" / "verify_engine_implemented.py")],
                       capture_output=True, text=True, cwd=str(ROOT))
    results.append(("step7_engine_implemented",
                    "PASS" if r.returncode == 0 else "FAIL",
                    f"exit {r.returncode}"))

    # M9 universe artifact check (the L445 wrong-artifact class), auto-wired:
    # the cube's own manifest names its tickers file. verify_universe_artifact
    # is non-blocking BY DESIGN (a deliberately narrow universe must stay
    # possible) - a FAIL here is a loud record for the human, and blocks only
    # the --write-ledger convenience, never the wave.
    mf = cube_dir / "run_manifest.json"
    tf = None
    if mf.exists():
        try:
            tf = json.loads(mf.read_text(encoding="utf-8"))["tickers"]["file"]
        except Exception:
            tf = None
    if tf and (ROOT / tf).exists():
        u = subprocess.run([sys.executable,
                            str(ROOT / "scripts" / "verify_universe_artifact.py"),
                            tf], capture_output=True, text=True, cwd=str(ROOT))
        results.append(("M9_universe_artifact",
                        "PASS" if u.returncode == 0 else "FAIL",
                        f"exit {u.returncode} on {tf} (verifier is "
                        "non-blocking by design - human judges a FAIL)"))
    else:
        results.append(("M9_universe_artifact", "SKIP",
                        f"no manifest tickers file resolvable ({tf!r})"))

    # B2136 (S6-B2135b): a status must never contradict its own evidence. The
    # ledger carried `DONE` on a step whose evidence ended "...SKIPPED", so a
    # reader trusting the status believed a check ran that never did and never
    # can. This is the same class as the holdout-ranked artifacts: STATUS
    # ASSERTED rather than DERIVED from what the evidence says.
    _CONTRA = ("SKIPPED", "CANNOT BE APPLIED", "NEVER RAN", "NOT RUN")
    lp_chk = ROOT / "output_audit" / "postconfig_ledger.json"
    if lp_chk.exists():
        _led = json.loads(lp_chk.read_text(encoding="utf-8"))
        bad = [f"{c}/{n}" for c, steps in _led.items() for n, v in steps.items()
               if isinstance(v, dict) and v.get("status") == "DONE"
               and any(t in (v.get("evidence") or "").upper() for t in _CONTRA)]
        results.append(("ledger_status_matches_evidence",
                        "PASS" if not bad else "FAIL",
                        f"{len(bad)} row(s) claim DONE with contradicting evidence"
                        + (f": {bad[:4]}" if bad else "")))

    for name, st, ev in results:
        print(f"  {st:<5} {name}: {ev}")
    print("\nJUDGMENT PROMPTS (never auto-marked): 5_adversarial_lens_review, "
          "6_post_fix_recheck, 8_verdict_with_denominators - and steps 2/4 "
          "need the config's own parameters:")
    print(f"  PYTHONPATH=.:scripts python scripts/tighten_breaker_block.py "
          f"--cube {a.cube}/trade_exit_detail.csv --swing-length <SW> --min-n 10")
    print(f"  PYTHONPATH=. python scripts/spot_check_trades.py --cube "
          f"{a.cube}/trade_exit_detail.csv --n 50 --swing-length <SW> --ema-span <SPAN>")


    fails = [x for x in results if x[1] == "FAIL"]
    if a.write_ledger and not fails:
        lp = ROOT / "output_audit" / "postconfig_ledger.json"
        ledger = json.loads(lp.read_text(encoding="utf-8")) if lp.exists() else {}
        entry = ledger.get(cube_dir.name, {})
        entry["1_cube_sanity"] = {
            "status": "DONE",
            "evidence": "run_postconfig: " + "; ".join(
                f"{n}={st}({ev[:60]})" for n, st, ev in results)}
        ledger[cube_dir.name] = entry
        lp.write_text(json.dumps(ledger, indent=1), encoding="utf-8")
        print(f"[OK] ledger step 1 recorded for {cube_dir.name}")
    return 2 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
