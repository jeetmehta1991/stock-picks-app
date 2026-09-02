#!/usr/bin/env python
"""Post-config battery: all nine runbook steps, recorded on EVERY landing.

B2520 (owner ruling 2026-09-01: "Once the config lands, i want it to run
automatically no exceptions and share results with me").

WHAT THIS REPLACES. B2118 automated the mechanical checks and recorded step 1;
B2177 added steps 2/4 for the ONE family whose parameters the manifest carried
(smc swing/span); B2192 recorded 3/6b from the same run. Steps 5/6/8 were
declared "JUDGMENT (never auto-marked)", every other family fell into the
else-branch as "pre-B2138 cube", and a single FAIL discarded the records of
every step that had run. Six owner asks, six instance fixes. This file is the
CLASS fix:

  * a FAMILY REGISTRY (FAMILIES) keyed by the cube's strategy column - an
    unregistered strategy FAILS closed (L642), it never "skips";
  * step-1 / step-2 derived from the manifest window (flags win; no window ->
    Step-1, the stricter arm, basis recorded);
  * a mechanical LENS battery for step 5 -> output_audit/<cube>_lenses.json;
    a WARN/FAIL lens makes step 6 OPEN (a finding must be rechecked), no lens
    finding makes step 6 N/A on evidence;
  * step 8 = the verdict WITH DENOMINATORS read from the grid artifact;
  * step 7 = the engine-implementation check, N/A on a Step-1 cube (nothing is
    admitted at Step 1), DONE/OPEN on a Step-2 cube;
  * EVERY step written to the ledger on EVERY run, FAIL included. Statuses are
    DONE / N/A (terminal) / OPEN / FAIL (block the gate) - never SKIPPED
    (L721; verify_postconfig_complete.py treats only DONE and N/A as terminal).
    Terminal rows are never downgraded automatically: the battery's finding
    rides along as " | battery re-run <ts>: ..." and the B2136 contradiction
    check flags a kept status the battery contradicts.

The mechanical checks (the M-list, S6-B2117b) are unchanged in checks():
  M1 determinism content-sha; M2 exits-per-entry vs len(EXIT_STRATEGIES);
  M3 fill_date; M4 PIT window + HOLDOUT-TOUCH (FAIL on a Step-1 cube);
  M5 NaN/inf pnl + beyond-winsorize; M7 measure_degraded_exits;
  M9 universe artifact; M10 gate receipt vs manifest sha.

Usage:
  PYTHONPATH=. python scripts/run_postconfig.py --cube output_<dir>
      [--step1-cube | --step2-cube]   # else derived from the manifest window
      [--write-ledger]                # records all nine steps in the ledger
Exit 0 = no FAIL; 2 = at least one FAIL (every step is recorded either way).
Invoked automatically by scripts/postconfig_landing.py, which the engine calls
from backtest/run_phase1a.py the moment a cube lands.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from verify_postconfig_complete import STEPS  # noqa: E402  (the gate's list)
from grid_population import grid_population  # noqa: E402  (B2521 S6-B2520m)

MEGA = ("NVDA", "MSFT", "GOOGL", "META", "TSLA", "AAPL")
TERMINAL = ("DONE", "N/A")
_GRADER_CHECKS = ("step2_grade_auto", "step4_spot_check_auto",
                  "step7_engine_implemented")
_LEDGER_WIDE = ("ledger_status_matches_evidence",)


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

    # M10 gate receipt (B2169, S6-B2159b): the cube's dir must carry the
    # receipt the gate wrote at launch, and its manifest hash must match the
    # manifest sitting beside the cube. A cube with no receipt was launched
    # around the gate; a hash mismatch means the manifest changed after the
    # gate read it. Legacy cubes (pre-B2169) SKIP with the reason stated.
    import hashlib as _hl10
    rp = cube_dir / "gate_receipt.json"
    mp10 = cube_dir / "run_manifest.json"
    if not rp.exists():
        out.append(("M10_gate_receipt", "SKIP",
                        "no gate_receipt.json - cube predates B2169 or was "
                        "launched AROUND the gate; post-B2169 launches always "
                        "write one, so treat SKIP on a NEW cube as a finding"))
    elif not mp10.exists():
        out.append(("M10_gate_receipt", "FAIL",
                        "receipt present but run_manifest.json missing - the "
                        "receipt cannot be verified against anything"))
    else:
        rec = json.loads(rp.read_text(encoding="utf-8"))
        actual = _hl10.sha256(mp10.read_bytes()).hexdigest()
        if rec.get("manifest_sha256") == actual:
            out.append(("M10_gate_receipt", "PASS",
                            f"receipt matches manifest sha {actual[:12]}"))
        else:
            out.append(("M10_gate_receipt", "FAIL",
                            "receipt manifest_sha256 != the manifest beside "
                            "the cube - the manifest CHANGED after the gate "
                            "read it (the rebind hole the council named)"))


    return out


# --------------------------------------------------------------------------
# helpers shared by the family runners
# --------------------------------------------------------------------------
def _run(cmd: list[str], env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = {**os.environ, **(env_extra or {})}
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT),
                          env=env)


def _tail(p: subprocess.CompletedProcess, n: int = 2) -> str:
    lines = ((p.stdout or "") + "\n" + (p.stderr or "")).strip().splitlines()
    return "; ".join(x.strip() for x in lines[-n:] if x.strip())


def spot_summary(spot_out: Path) -> str:
    """Step-4 evidence from the ARTIFACT, never from stdout - the smc checker
    prints a blank line before 'wrote ...', so a stdout tail lost the tally
    (measured on the first B2520 dry run)."""
    try:
        sd = json.loads(spot_out.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return f"artifact {spot_out.name} unreadable: {exc!r}"
    s = (f"n_sampled {sd.get('n_sampled')} seed {sd.get('seed')}: "
         f"{sd.get('agree')} agree / {sd.get('disagree')} DISAGREE / "
         f"{sd.get('skipped')} skipped; execution failures "
         f"{len(sd.get('execution_failures') or [])}")
    if "empty_records" in sd:
        s += (f"; empty records {sd.get('empty_records')}; legs A/B disagree "
              f"{sd.get('legs_ab_disagree')}")
    return s + f"; artifact {spot_out.name}"


def row_label(r: dict) -> str:
    """A ranked row's identity: the combination (smc grids rank OUTCOME
    CLASSES whose production-closest member sits in `admit`) plus its exit,
    or the exit alone on a per-exit grid."""
    adm = r.get("admit") or {}
    parts = [f"{k}={adm[k]}" for k in ("close_mitigation", "break_pct_max",
                                      "age_bars_max", "tail_n") if k in adm]
    return (" ".join(parts) + " -> " if parts else "") + str(r.get("exit"))


def read_manifest(cube_dir: Path) -> dict:
    mf = cube_dir / "run_manifest.json"
    if not mf.exists():
        return {}
    try:
        return json.loads(mf.read_text(encoding="utf-8")) or {}
    except (OSError, ValueError):
        return {}


def _arm0(manifest: dict) -> tuple[dict, dict]:
    arms = manifest.get("arms") or []
    arm = (arms[0] or {}) if arms else {}
    return arm, dict(arm.get("env") or {})


def cube_strategies(cube_dir: Path) -> list[str]:
    """The cube's strategy column, read alone (a 9k-row cube is cheap; a junk
    cube without the column returns [] and the family resolves to nothing)."""
    import pandas as pd
    try:
        s = pd.read_csv(cube_dir / "trade_exit_detail.csv", usecols=["strategy"],
                        low_memory=False)["strategy"]
    except (OSError, ValueError, KeyError):
        return []
    return sorted(str(x) for x in s.dropna().unique())


def derive_step(manifest: dict, *, step1_flag: bool, step2_flag: bool) -> tuple[int, str]:
    """1 or 2 plus the basis. Flags win; else the manifest window end against
    HO_START; else Step-1 - the arm that arms the holdout-touch FAIL (L642)."""
    from roster_core import HO_START
    if step1_flag:
        return 1, "declared --step1-cube"
    if step2_flag:
        return 2, "declared --step2-cube"
    end = (manifest.get("window") or {}).get("end")
    if end:
        try:
            d = _dt.date.fromisoformat(str(end)[:10])
        except ValueError:
            d = None
        if d is not None:
            if d <= HO_START:
                return 1, f"manifest window.end {d} <= HO_START {HO_START} -> Step-1 cube"
            return 2, f"manifest window.end {d} > HO_START {HO_START} -> Step-2 cube"
    return 1, ("UNDECLARED (no --step1-cube/--step2-cube flag, no manifest "
               "window) - treated as Step-1, the stricter arm (fail closed, L642)")


# --------------------------------------------------------------------------
# family registry - keyed by the cube's strategy column. An unregistered
# strategy FAILS closed; there is no else-branch that skips.
# --------------------------------------------------------------------------
def _smc_params(manifest: dict) -> tuple[dict | None, str]:
    _, env = _arm0(manifest)
    swing, span = env.get("SMC_SWING_LENGTH"), env.get("STRAT_EMA_SPAN")
    if swing and span:
        return ({"swing": str(swing), "span": str(span)},
                f"manifest arms[0].env swing={swing} span={span}")
    return None, ("manifest carries no arms env with SMC_SWING_LENGTH + "
                  "STRAT_EMA_SPAN (a pre-B2138 cube has this shape)")


def _institutional_params(manifest: dict) -> tuple[dict | None, str]:
    arm, env = _arm0(manifest)
    keys = (("INST_MIN_CONSECUTIVE_QUARTERS", "min_consecutive_quarters"),
            ("INST_GROWTH_LOOKBACK_QUARTERS", "growth_lookback_quarters"),
            ("INST_GROWTH_MULTIPLE", "growth_multiple"),
            ("STRAT_EMA_SPAN", "ema_span"))
    vals = {}
    for ek, pk in keys:
        v = env.get(ek)
        if v is None:
            v = arm.get(pk)
        vals[pk] = v
    missing = [k for k, v in vals.items() if v is None]
    if missing:
        return None, (f"manifest arms[0] lacks {missing} (neither the INST_*/"
                      f"STRAT_EMA_SPAN env keys nor the plain keys)")
    return vals, "manifest arms[0] " + " ".join(f"{k}={v}" for k, v in vals.items())


def run_smc(cube_dir: Path, p: dict, manifest: dict) -> tuple[list, dict, Path, Path]:
    swing2, span2 = p["swing"], p["span"]
    results, notes = [], {}
    grid_out = ROOT / "output_audit" / f"{cube_dir.name}_grid_auto.json"
    spot_out = ROOT / "output_audit" / f"{cube_dir.name}_spot_check.json"
    g = _run([sys.executable, str(ROOT / "scripts" / "tighten_breaker_block.py"),
              "--cube", str(cube_dir / "trade_exit_detail.csv"),
              "--swing-length", str(swing2), "--span", str(span2),
              "--min-n", "10", "--out", str(grid_out)],
             {"PYTHONPATH": ".;scripts"})
    ok2 = g.returncode == 0 and grid_out.exists()
    results.append(("step2_grade_auto", "PASS" if ok2 else "FAIL",
                    f"exit {g.returncode}; swing={swing2} span={span2} "
                    f"-> {grid_out.name}" + ("" if ok2 else f"; {_tail(g)[:160]}")))
    notes["2_grade_with_config_params"] = (
        ("DONE", f"AUTO (B2177): graded at manifest swing={swing2} "
                 f"span={span2} -> {grid_out.name}") if ok2 else
        ("FAIL", f"tighten_breaker_block exit {g.returncode} at swing={swing2} "
                 f"span={span2}: {_tail(g)[:200]}"))
    sc = _run([sys.executable, str(ROOT / "scripts" / "spot_check_trades.py"),
               "--cube", str(cube_dir / "trade_exit_detail.csv"),
               "--n", "50", "--swing-length", str(swing2),
               "--ema-span", str(span2), "--out", str(spot_out)],
              {"PYTHONPATH": "."})
    ok4 = sc.returncode == 0 and spot_out.exists()
    tail = spot_summary(spot_out) if ok4 else _tail(sc)
    results.append(("step4_spot_check_auto", "PASS" if ok4 else "FAIL",
                    f"exit {sc.returncode}; {tail[:180]}"))
    notes["4_three_leg_spot_check"] = (
        ("DONE", f"AUTO (B2177): spot_check_trades --n 50 at manifest "
                 f"swing={swing2} span={span2}; {tail[:200]}") if ok4 else
        ("FAIL", f"spot_check_trades exit {sc.returncode}: {tail[:200]}"))
    # step 7 engine implementation, invoked (was HAND-RUN-ONLY before B2118)
    r = _run([sys.executable, str(ROOT / "scripts" / "verify_engine_implemented.py")])
    results.append(("step7_engine_implemented",
                    "PASS" if r.returncode == 0 else "FAIL",
                    f"exit {r.returncode}; {_tail(r, 1)[:120]}"))
    return results, notes, grid_out, spot_out


def run_institutional(cube_dir: Path, p: dict, manifest: dict) -> tuple[list, dict, Path, Path]:
    results, notes = [], {}
    grid_out = ROOT / "output_audit" / f"{cube_dir.name}_grid_auto.json"
    spot_out = ROOT / "output_audit" / f"{cube_dir.name}_spot_check.json"
    label = (f"minq={p['min_consecutive_quarters']} lookback="
             f"{p['growth_lookback_quarters']} multiple={p['growth_multiple']} "
             f"span={p['ema_span']}")
    g = _run([sys.executable, str(ROOT / "scripts" / "grade_institutional_config.py"),
              "--cube", str(cube_dir),
              "--min-consecutive-quarters", str(p["min_consecutive_quarters"]),
              "--growth-lookback-quarters", str(p["growth_lookback_quarters"]),
              "--growth-multiple", str(p["growth_multiple"]),
              "--span", str(p["ema_span"]), "--min-n", "10",
              "--out", str(grid_out)])
    ok2 = g.returncode == 0 and grid_out.exists()
    results.append(("step2_grade_auto", "PASS" if ok2 else "FAIL",
                    f"exit {g.returncode}; {label} -> {grid_out.name}; "
                    f"{_tail(g)[:160]}"))
    notes["2_grade_with_config_params"] = (
        ("DONE", f"AUTO (B2520): grade_institutional_config at manifest {label} "
                 f"-> {grid_out.name}; {_tail(g, 2)[:160]}") if ok2 else
        ("FAIL", f"grade_institutional_config exit {g.returncode} at {label}: "
                 f"{_tail(g)[:200]}"))
    win = manifest.get("window") or {}
    cmd = [sys.executable, str(ROOT / "scripts" / "spot_check_institutional.py"),
           "--cube", str(cube_dir), "--n", "50", "--ema-span", str(p["ema_span"]),
           "--out", str(spot_out)]
    if win.get("start"):
        cmd += ["--start", str(win["start"])[:10]]
    if win.get("end"):
        cmd += ["--end", str(win["end"])[:10]]
    sc = _run(cmd)
    ok4 = sc.returncode == 0 and spot_out.exists()
    tail = spot_summary(spot_out) if ok4 else _tail(sc)
    results.append(("step4_spot_check_auto", "PASS" if ok4 else "FAIL",
                    f"exit {sc.returncode}; {tail[:180]}"))
    notes["4_three_leg_spot_check"] = (
        ("DONE", f"AUTO (B2520): spot_check_institutional --n 50 at manifest "
                 f"span={p['ema_span']}; {tail[:200]}") if ok4 else
        ("FAIL", f"spot_check_institutional exit {sc.returncode}: {tail[:200]}"))
    # step 7 anchors: the swept parameters reach the engine through env reads
    # in the precompute builder (INST_* x3) and the screener's EMA gate
    # (STRAT_EMA_SPAN). A code-presence check, named as such.
    try:
        pre = (ROOT / "scripts" / "build_institutional_persistence_precompute.py"
               ).read_text(encoding="utf-8", errors="replace")
        scr = (ROOT / "backtest" / "signals" / "screener.py"
               ).read_text(encoding="utf-8", errors="replace")
        need = (("INST_MIN_CONSECUTIVE_QUARTERS", pre),
                ("INST_GROWTH_LOOKBACK_QUARTERS", pre),
                ("INST_GROWTH_MULTIPLE", pre), ("STRAT_EMA_SPAN", scr))
        missing = [k for k, src in need if k not in src]
    except OSError as exc:
        missing = [f"unreadable: {exc!r}"]
    results.append(("step7_engine_implemented",
                    "PASS" if not missing else "FAIL",
                    "4 of 4 swept parameters anchored in the engine path "
                    "(precompute INST_* x3 + screener STRAT_EMA_SPAN; "
                    "code-presence check)" if not missing else
                    f"missing anchors {missing}"))
    return results, notes, grid_out, spot_out


FAMILIES = {
    "smc_breaker_block_long": {"params": _smc_params, "run": run_smc,
                               "single_combination": False},
    "institutional_committed_growth_long": {"params": _institutional_params,
                                            "run": run_institutional,
                                            "single_combination": True},
}


# --------------------------------------------------------------------------
# step 5: the mechanical lens battery. Each lens returns INFO / WARN / FAIL
# with its evidence; WARN or FAIL is a FINDING and makes step 6 OPEN.
# --------------------------------------------------------------------------
def lenses(cube_dir: Path, step: int, grid: dict, spot_out: Path | None) -> list:
    import pandas as pd
    from roster_core import HO_START
    out = []
    want = {"strategy", "direction", "entry_date", "ticker", "exit_method"}
    df = pd.read_csv(cube_dir / "trade_exit_detail.csv", low_memory=False,
                     usecols=lambda c: c in want)
    ent = df.drop_duplicates(subset=["ticker", "entry_date"])
    ed = pd.to_datetime(ent["entry_date"], errors="coerce")
    n = int(len(ent))

    touched = int((ed.dt.date >= HO_START).sum())
    if step == 1:
        out.append(("holdout_untouched", "FAIL" if touched else "INFO",
                    f"{touched} of {n} entries at/after HO_START {HO_START} "
                    "(Step-1 cube: any touch is a leak, B1718 class)"))
    else:
        out.append(("holdout_untouched", "INFO",
                    f"{touched} of {n} entries in the holdout (Step-2 cube: the "
                    "holdout is graded separately, never ranked on)"))

    span_days = int((ed.max() - ed.min()).days) if n else 0
    if span_days > 540:
        per, label, bar = ed.dt.year.astype(str), "year", 0.6
    else:
        per, label, bar = ed.dt.to_period("Q").astype(str), "quarter", 0.5
    shares = per.value_counts(normalize=True)
    top = float(shares.iloc[0]) if len(shares) else 0.0
    out.append(("period_concentration", "WARN" if top > bar else "INFO",
                f"max {label} share {top:.2f} ({shares.index[0] if len(shares) else '-'}) "
                f"over {len(shares)} {label}s of {n} entries; WARN > {bar}"))

    tick = ent["ticker"].value_counts(normalize=True)
    top5 = float(tick.head(5).sum())
    if len(tick) < 20:
        out.append(("ticker_concentration", "INFO",
                    f"{len(tick)} tickers (< 20: top-5 share {top5:.2f} is not a "
                    "concentration measure)"))
    else:
        out.append(("ticker_concentration", "WARN" if top5 > 0.3 else "INFO",
                    f"top-5 tickers carry {top5:.2f} of {n} entries across "
                    f"{len(tick)} tickers; WARN > 0.30"))

    # rank-1 vs rank-2 on the ranking key: the rows are OUTCOME CLASSES on a
    # multi-combination grid (two classes may share an exit) and EXITS on a
    # single-combination grid - row_label names whichever it is.
    rk = grid.get("step1_ranking") or []
    # B2521 (S6-B2520m): the population question has ONE owner now.
    _, _pop_field, _pop_unit = grid_population(grid)
    unit = "exits" if _pop_field == "per_exit" else "outcome classes"
    if (len(rk) >= 2 and rk[0].get("is_ci_lo") is not None
            and rk[1].get("is_ci_lo") is not None):
        margin = float(rk[0]["is_ci_lo"]) - float(rk[1]["is_ci_lo"])
        out.append(("selection_margin", "WARN" if margin < 0.05 else "INFO",
                    f"rank-1 [{row_label(rk[0])}] is_ci_lo {rk[0]['is_ci_lo']} vs "
                    f"rank-2 [{row_label(rk[1])}] {rk[1]['is_ci_lo']}: margin "
                    f"{margin:.3f} between {unit}; WARN < 0.05 (selection at "
                    "noise level)"))
    elif rk:
        out.append(("selection_margin", "INFO",
                    f"1 ranked row ({unit}) - no margin to measure"))
    else:
        out.append(("selection_margin", "INFO",
                    "no ranked row in the grid artifact"))

    tl = cube_dir / "trade_log.csv"
    if tl.exists():
        try:
            s = pd.read_csv(tl, usecols=["signals_at_entry"], low_memory=False
                            )["signals_at_entry"].fillna("").astype(str).str.strip()
            empty = int(((s == "") | (s == "{}")).sum())
            out.append(("empty_signals_share", "WARN" if empty else "INFO",
                        f"{empty} of {len(s)} trade_log rows carry an empty "
                        "signals_at_entry (S6-B2512 class)"))
        except (OSError, ValueError, KeyError) as exc:
            out.append(("empty_signals_share", "INFO",
                        f"trade_log.csv has no readable signals_at_entry: {exc!r}"))
    else:
        out.append(("empty_signals_share", "INFO", "no trade_log.csv beside the cube"))

    if "direction" in df.columns:
        dirs = sorted(str(x) for x in df["direction"].dropna().unique())
        out.append(("direction_consistency", "INFO" if len(dirs) == 1 else "FAIL",
                    f"directions {dirs} (one strategy, one direction expected)"))

    if spot_out is not None and spot_out.exists():
        try:
            sd = json.loads(spot_out.read_text(encoding="utf-8"))
            dis = int(sd.get("disagree") or 0)
            out.append(("spot_check_disagreements", "WARN" if dis else "INFO",
                        f"{sd.get('agree')} agree / {dis} DISAGREE / "
                        f"{sd.get('skipped')} skipped in {spot_out.name}"))
        except (OSError, ValueError) as exc:
            out.append(("spot_check_disagreements", "WARN",
                        f"spot-check artifact unreadable: {exc!r}"))
    else:
        out.append(("spot_check_disagreements", "WARN",
                    "no spot-check artifact - step 4 produced nothing to read"))

    try:
        from backtest.config import PASSING_CRITERIA as _pc
        ho, fp = _pc.get("min_trades_holdout"), _pc.get("min_trades_full_period")
    except Exception:  # pragma: no cover - config import failure is reported, not fatal
        ho = fp = "?"
    out.append(("min_trades_floor", "INFO",
                f"{n} distinct entries; the live gates need holdout >= {ho} and "
                f"full-period >= {fp} (applied by the grader, not here)"))
    return out


def verdict_from_grid(grid: dict, step: int) -> str:
    """Step 8: the verdict sentence names its denominators (CHECKLIST #182)."""
    res = grid.get("results") or []
    top = grid.get("step1_ranking") or []
    if "per_exit" in grid:                       # single-combination grid
        pe = grid["per_exit"]
        ranked = [r for r in pe if (r.get("admit") or {}).get("verdict") == "RANKED"]
        s = (f"{len(ranked)} of {len(pe)} exits RANKED at min-trades >= "
             f"{grid.get('min_n')} on {grid.get('is_rows')} IS rows "
             f"({grid.get('rows')} cube rows, {grid.get('holdout_rows')} holdout rows)")
    else:
        cnt = Counter(str(r.get("verdict")) for r in res)
        s = (f"{len(res)} combinations enumerated: "
             + ", ".join(f"{v} {k}" for k, v in cnt.most_common()))
        pq = grid.get("provisional_qualifiers")
        if isinstance(pq, (list, dict)):
            s += f"; provisional_qualifiers {len(pq)}"
    if top:
        t = top[0]
        s += (f"; rank-1 [{row_label(t)}] is_ci_lo {t.get('is_ci_lo')} "
              f"is_sharpe {t.get('is_sharpe')} fires {t.get('fires')}")
    else:
        s += "; NO ranked row (nothing cleared the power floor)"
    s += (" - Step-1: ranking only, no admission (B1608)" if step == 1 else
          " - Step-2: PASS rows are the admission candidates (S6-B2409: "
          "clearing the six live gates IS qualification)")
    return s


# --------------------------------------------------------------------------
# ledger merge: FAIL/OPEN/DONE/N/A written for every step; terminal rows are
# never downgraded automatically - the battery's finding rides along.
# --------------------------------------------------------------------------
def _old_evidence(row) -> str:
    if not isinstance(row, dict):
        return ""
    return " / ".join(str(row[k]) for k in ("evidence", "reason", "note")
                      if row.get(k))


def merge_row(entry: dict, step: str, status: str, evidence: str, ts: str) -> dict:
    old = entry.get(step)
    old_st = old.get("status") if isinstance(old, dict) else None
    old_ev = _old_evidence(old)
    # Never truncate the evidence (B2211: the truncation the owner saw came
    # from packing; the measured values sit at the END of a battery line, so a
    # [:200] cut removed exactly the numbers). Growth is bounded by KEEPING
    # ONE re-run tag and ONE level of prior history, not by cutting text.
    if old_st in TERMINAL:
        base = old_ev.split(" | battery re-run ")[0]
        if status == "FAIL":
            tag = (f" | battery re-run {ts}: FAIL (status kept - terminal rows "
                   f"are never downgraded automatically; disposition by hand) "
                   f"- {evidence}")
        else:
            tag = f" | battery re-run {ts}: {status} - {evidence}"
        entry[step] = {"status": old_st, "evidence": base + tag}
    else:
        prior = old_ev.split(" | prior: ")[0]
        entry[step] = {"status": status,
                       "evidence": evidence + (f" | prior: {prior}"
                                               if prior else "")}
    return entry


def _current_claim(ev: str) -> str:
    """The evidence text that IS the row's claim: history after ' | prior:'
    is excluded; a number followed by 'skipped' is a tally, not a status
    (B2136's detector matched '0 skipped' inside spot-check tallies - the
    false positive that flipped seven DONE rows, B2520)."""
    cur = ev.split(" | prior:")[0]
    return re.sub(r"\b\d+\s+skipped\b", "", cur, flags=re.I)


# B2136 (S6-B2135b): a status must never contradict its own evidence. The
# ledger carried `DONE` on a step whose evidence ended "...SKIPPED", so a
# reader trusting the status believed a check ran that never did and never
# can. "(STATUS KEPT" is the battery's own contradiction marker (B2520).
#
# A MENTION is not an ASSERTION (B2520, second false-positive class): a
# narrative row may quote a status ("wrote steps 2-8 as SKIPPED citing...")
# or contain the words inside another token ("run_phase1a direct, not
# run_wave" holds "NOT RUN"). A row asserts non-execution when its claim
# STARTS or ENDS with the status word - B2136's original shape - or carries
# a phrase no narrative quotes, or the battery's own kept-status marker.
_CONTRA_EDGE = ("SKIPPED", "NOT RUN")
_CONTRA_ANY = ("CANNOT BE APPLIED", "NEVER RAN", "(STATUS KEPT")


def asserts_non_execution(claim: str) -> bool:
    up = claim.upper().strip()
    if any(t in up for t in _CONTRA_ANY):
        return True
    return any(re.match(rf"^\W*{t}\b", up) or re.search(rf"\b{t}\W*$", up)
               for t in _CONTRA_EDGE)


def ledger_contradictions(ledger: dict) -> list[str]:
    return [f"{c}/{n}" for c, steps in ledger.items()
            if isinstance(steps, dict) for n, v in steps.items()
            if isinstance(v, dict) and v.get("status") == "DONE"
            and asserts_non_execution(_current_claim(_old_evidence(v)))]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cube", required=True)
    ap.add_argument("--step1-cube", action="store_true")
    ap.add_argument("--step2-cube", action="store_true")
    ap.add_argument("--write-ledger", action="store_true")
    a = ap.parse_args()
    cube_dir = Path(a.cube)
    if not cube_dir.is_absolute():
        cube_dir = ROOT / a.cube
    manifest = read_manifest(cube_dir)
    step, step_basis = derive_step(manifest, step1_flag=a.step1_cube,
                                   step2_flag=a.step2_cube)
    try:
        results = checks(cube_dir, step1=(step == 1))
    except Exception as exc:
        # a cube whose schema breaks the checks is a FAILED cube, loudly -
        # never a traceback that reads as a tooling problem (L566 class)
        results = [("checks_crashed", "FAIL", repr(exc))]
    results.append(("step_derivation", "PASS", f"Step-{step}: {step_basis}"))

    # M9 universe artifact check (the L445 wrong-artifact class), auto-wired:
    # the cube's own manifest names its tickers file. verify_universe_artifact
    # is non-blocking BY DESIGN (a deliberately narrow universe must stay
    # possible) - a FAIL here is a loud record for the human to judge.
    tf = None
    try:
        tf = (manifest.get("tickers") or {}).get("file")
    except AttributeError:
        tf = None
    if tf and (ROOT / tf).exists():
        u = _run([sys.executable, str(ROOT / "scripts" / "verify_universe_artifact.py"),
                  tf])
        results.append(("M9_universe_artifact",
                        "PASS" if u.returncode == 0 else "FAIL",
                        f"exit {u.returncode} on {tf} (verifier is "
                        "non-blocking by design - human judges a FAIL)"))
    else:
        results.append(("M9_universe_artifact", "SKIP",
                        f"no manifest tickers file resolvable ({tf!r})"))

    # family dispatch - the cube's own strategy column decides; nothing skips
    strategies = cube_strategies(cube_dir)
    fam_name = strategies[0] if len(strategies) == 1 else None
    fam = FAMILIES.get(fam_name) if fam_name else None
    notes: dict = {}
    grid_out = spot_out = None
    fam_fail = None
    if fam is None:
        fam_fail = (f"no registered post-config family for strategies "
                    f"{strategies or '[]'} - register it in run_postconfig."
                    f"FAMILIES (fail closed, L642; the old else-branch called "
                    f"this a pre-B2138 cube and skipped)")
        results.append(("family_dispatch", "FAIL", fam_fail))
    else:
        params, basis = fam["params"](manifest)
        if params is None:
            fam_fail = f"family {fam_name}: {basis} (fail closed, L642)"
            results.append(("family_dispatch", "FAIL", fam_fail))
        else:
            results.append(("family_dispatch", "PASS", f"{fam_name}: {basis}"))
            fr, notes, grid_out, spot_out = fam["run"](cube_dir, params, manifest)
            results.extend(fr)

    grid: dict = {}
    if grid_out is not None and grid_out.exists():
        try:
            grid = json.loads(grid_out.read_text(encoding="utf-8")) or {}
        except (OSError, ValueError):
            grid = {}

    # step 5 lenses -> artifact
    try:
        lens_rows = lenses(cube_dir, step, grid, spot_out)
    except Exception as exc:
        lens_rows = [("lenses_crashed", "FAIL", repr(exc))]
    lens_out = ROOT / "output_audit" / f"{cube_dir.name}_lenses.json"
    try:
        lens_out.parent.mkdir(parents=True, exist_ok=True)
        lens_out.write_text(json.dumps(
            {"cube": cube_dir.name, "step": step, "step_basis": step_basis,
             "family": fam_name, "ts": _dt.datetime.now().isoformat(timespec="seconds"),
             "lenses": [{"lens": ln, "level": lv, "evidence": ev}
                        for ln, lv, ev in lens_rows]}, indent=1), encoding="utf-8")
    except OSError as exc:
        lens_rows.append(("lenses_artifact", "FAIL", f"could not write {lens_out}: {exc!r}"))
    findings = [(ln, lv, ev) for ln, lv, ev in lens_rows if lv in ("WARN", "FAIL")]

    # ledger-wide contradiction check (B2136), read before this run writes
    lp_chk = ROOT / "output_audit" / "postconfig_ledger.json"
    if lp_chk.exists():
        try:
            bad = ledger_contradictions(json.loads(lp_chk.read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            bad = [f"ledger unreadable: {exc!r}"]
        results.append(("ledger_status_matches_evidence",
                        "PASS" if not bad else "FAIL",
                        f"{len(bad)} row(s) claim DONE with contradicting evidence"
                        + (f": {bad[:4]}" if bad else "")))

    # ---- assemble the nine steps ------------------------------------------
    by = {n: (st, ev) for n, st, ev in results}
    sanity_fails = [n for n, st, _ in results
                    if st == "FAIL" and n not in _GRADER_CHECKS + _LEDGER_WIDE
                    and n != "family_dispatch"]
    summary = "; ".join(f"{n}={st}({ev[:60]})" for n, st, ev in results)
    steps: dict[str, tuple[str, str]] = {}
    steps["1_cube_sanity"] = ("FAIL" if sanity_fails else "DONE",
                              "run_postconfig: " + summary)
    m_core = ("M2_exits_per_entry_vs_registry", "M3_fill_date", "M4_holdout_touch",
              "M5_pnl_integrity", "M7_degraded_exits")
    m_missing = [m for m in m_core if m not in by]
    m_fail = [m for m in m_core if by.get(m, ("", ""))[0] == "FAIL"]
    if m_missing:
        steps["3_outlier_discrepancy_sweep"] = (
            "FAIL", f"mechanical core did not run ({m_missing} absent - checks "
                    f"crashed: {by.get('checks_crashed', ('', ''))[1][:120]})")
    elif m_fail:
        steps["3_outlier_discrepancy_sweep"] = (
            "FAIL", "mechanical core FAILED: " + "; ".join(
                f"{m}: {by[m][1][:100]}" for m in m_fail))
    else:
        steps["3_outlier_discrepancy_sweep"] = (
            "DONE", "AUTO (B2192): mechanical core executed by the battery "
                    "(M2 exits-vs-registry, M5 NaN/inf/winsorize, M7 degraded "
                    "exits) + the grader's union diagnosis-loss gate and "
                    "ci_lo-led ranking; " + "; ".join(
                        f"{m}={by[m][0]}" for m in m_core))
    for s_name in ("2_grade_with_config_params", "4_three_leg_spot_check"):
        steps[s_name] = notes.get(s_name) or ("FAIL", fam_fail or
                                              "family runner recorded nothing")
    # step 5 / 6
    n_w = sum(1 for _, lv, _ in lens_rows if lv == "WARN")
    n_f = sum(1 for _, lv, _ in lens_rows if lv == "FAIL")
    n_i = sum(1 for _, lv, _ in lens_rows if lv == "INFO")
    crashed = any(ln == "lenses_crashed" for ln, _, _ in lens_rows)
    lens_txt = (f"AUTO (B2520): lenses {len(lens_rows)} run: {n_w} WARN / {n_f} "
                f"FAIL / {n_i} INFO -> {lens_out.name}")
    if findings:
        lens_txt += "; findings: " + "; ".join(f"{ln} {lv}: {ev[:90]}"
                                                for ln, lv, ev in findings)
    steps["5_adversarial_lens_review"] = ("FAIL" if crashed else "DONE", lens_txt)
    if crashed:
        steps["6_post_fix_recheck"] = ("OPEN", "lens battery crashed - nothing "
                                               "to recheck until step 5 runs")
    elif findings:
        steps["6_post_fix_recheck"] = (
            "OPEN", f"{len(findings)} lens finding(s) need a recheck with evidence "
                    f"(#196): " + "; ".join(f"{ln} {lv}" for ln, lv, _ in findings))
    else:
        steps["6_post_fix_recheck"] = (
            "N/A", f"no lens finding ({len(lens_rows)} lenses, 0 WARN / 0 FAIL) "
                   "-> nothing to recheck; N/A on evidence")
    # 6b
    if fam is None or fam_fail:
        steps["6b_equivalence_class_check"] = ("FAIL", fam_fail or "no family")
    elif fam["single_combination"]:
        steps["6b_equivalence_class_check"] = (
            "N/A", "1 combination per cube (the swept parameters live in the "
                   "precompute the engine consumed); equivalence collapse "
                   "requires >= 2 combinations - N/A on evidence")
    elif grid:
        # tighten_breaker_block.py:549-550: carried = members of the RANKED
        # classes; distinct = outcome classes among ALL enumerated combinations
        steps["6b_equivalence_class_check"] = (
            "DONE", f"AUTO (B2192): the grader collapses identical outcomes - "
                    f"{len(grid.get('step1_ranking') or [])} ranked outcome "
                    f"classes carry {grid.get('step1_combinations_carried')} "
                    f"parameter combinations; {grid.get('step1_distinct_outcomes')} "
                    f"distinct outcome classes among {len(grid.get('results') or [])} "
                    f"combinations enumerated in {grid_out.name}")
    else:
        steps["6b_equivalence_class_check"] = ("FAIL", "no grid artifact to read "
                                                       "equivalence classes from")
    # 7
    e7 = by.get("step7_engine_implemented")
    if e7 is None:
        steps["7_implement_in_engine"] = ("FAIL", fam_fail or "engine check did not run")
    elif step == 1:
        steps["7_implement_in_engine"] = (
            ("N/A", "Step-1 ranking cube; admission happens at Step 2; nothing "
                    f"to implement. Engine check {e7[0]}: {e7[1][:140]}")
            if e7[0] == "PASS" else
            ("OPEN", "engine check FAIL on a Step-1 cube - a swept parameter "
                     "does not reach the engine; resolve before any Step-2 "
                     f"admission: {e7[1][:140]}"))
    else:
        steps["7_implement_in_engine"] = (
            ("DONE", f"engine check PASS on a Step-2 cube: {e7[1][:160]}")
            if e7[0] == "PASS" else
            ("OPEN", f"engine check FAIL on a Step-2 cube: {e7[1][:160]}"))
    # 8
    if grid:
        steps["8_verdict_with_denominators"] = (
            "DONE", f"AUTO (B2520) VERDICT (denominators from {grid_out.name}): "
                    + verdict_from_grid(grid, step))
    else:
        steps["8_verdict_with_denominators"] = (
            "OPEN", "no grid artifact - step 2 produced nothing to derive a "
                    "verdict from" + (f" ({fam_fail})" if fam_fail else ""))
    assert set(steps) == set(STEPS), sorted(set(STEPS) ^ set(steps))

    for name, st, ev in results:
        print(f"  {st:<5} {name}: {ev}")
    print("\nSTEPS (every one recorded; DONE / N/A are terminal, OPEN / FAIL "
          "block the gate until dispositioned with evidence):")
    for s_name in STEPS:
        st, ev = steps[s_name]
        print(f"  {st:<5} {s_name}: {ev[:220]}")

    fails = [x for x in results if x[1] == "FAIL"]
    auto_notes = [(s_name, {"status": st, "evidence": ev})
                  for s_name, (st, ev) in steps.items()]
    if a.write_ledger:
        # B2207 (S6-B2205a): locked + atomic - see scripts/ledger_lock.py.
        from ledger_lock import locked_ledger_update
        ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")

        def _upgrade(ledger: dict) -> dict:
            entry = ledger.get(cube_dir.name) or {}
            for step_name, ev in auto_notes:
                entry = merge_row(entry, step_name, ev["status"], ev["evidence"], ts)
            ledger[cube_dir.name] = entry
            return ledger
        locked_ledger_update(_upgrade)
        print(f"[OK] ledger: all {len(STEPS)} steps recorded for {cube_dir.name}"
              f" ({'FAIL present' if fails else 'no FAIL'})")
    return 2 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
