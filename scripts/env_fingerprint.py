"""scripts/env_fingerprint.py - pre-run environment-fingerprint parity gate.

# Source: per CHECKLIST #77 canonical-source; CHECKLIST #158 + L207/L208.
# Council 339 B1307 owner-directed 2026-07-18.

The chunk-1 calendar defect (B1305): chunk 1 ran the Mon-Fri fallback
grid (1043 days) while AWS chunks ran the correct NYSE grid (1002),
caught only at merge. This gate makes environment parity MECHANICAL and
PRE-RUN instead of a post-hoc discovery.

Fingerprint captures the things that silently change run SEMANTICS:
  - trading-day grid: total count + hash for the canonical R5 window
    (this is the calendar signal -- 1002 NYSE vs 1043 Mon-Fri)
  - calendar backend: whether pandas_market_calendars is importable
  - key package versions (pandas, numpy, pyarrow, pandas_market_calendars)
  - code commit SHA (HEAD)

Usage:
  python scripts/env_fingerprint.py --emit  out.json      # write fingerprint
  python scripts/env_fingerprint.py --check a.json b.json  # parity diff; exit 1 on mismatch
A per-chunk fingerprint is emitted at launch; before MERGING chunks, all
fingerprints must match on grid_total + grid_hash + calendar_backend.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

# Run-as-script puts scripts/ on sys.path[0], not the repo root -> import
# backtest.* fails and the grid silently reports error. Anchor to repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

WINDOW_START = date(2022, 5, 5)
WINDOW_END = date(2026, 5, 5)
# Fields that MUST match across any set of chunks that will be merged.
# B1322 (Council 354): added smc_active - the chunk-2 gap (B1317) was 22 SMC/ICT
# strategies silent on cloud because the vendored lib failed to import there
# while local had it. A chunk WITH SMC cannot be merged with a chunk WITHOUT it.
MERGE_CRITICAL = ("grid_total", "grid_hash", "calendar_backend", "smc_active")


def trading_day_grid():
    """Return (total, hash, backend) for the canonical window using the
    SAME path the engine uses (backtest.engine.improvements)."""
    try:
        from backtest.engine.improvements import (
            is_nyse_trading_day, get_nyse_calendar_helper)
        cal = get_nyse_calendar_helper()
        backend = "nyse_mcal" if cal is not None else "monfri_fallback"
        days, d = [], WINDOW_START
        while d <= WINDOW_END:
            if is_nyse_trading_day(d, calendar=cal):
                days.append(d.isoformat())
            d += timedelta(days=1)
    except Exception as exc:
        return 0, f"ERROR:{exc}", "error"
    h = hashlib.sha256("".join(days).encode()).hexdigest()[:16]
    return len(days), h, backend


def _pkg(name):
    try:
        import importlib.metadata as m
        return m.version(name)
    except Exception:
        return "absent"


def probe_smc():
    """Will SMC/ICT strategies actually EMIT? Requires the vendored
    smartmoneyconcepts library importable AND SMC_PHASE == 'PRODUCTION'.
    The chunk-2 gap (B1317): the lib imported LOCAL but FAILED on the cloud
    instance -> 22 strategies silent on cloud only. pip-freeze can't see a
    vendored *directory*, so we import-probe it directly.
    Returns (lib_importable, smc_phase, smc_active)."""
    lib_ok = False
    try:
        from vendored.smartmoneyconcepts.smartmoneyconcepts import smc  # noqa: F401
        lib_ok = True
    except Exception:
        lib_ok = False
    try:
        from backtest.config import SMC_PHASE as _phase
        phase = str(_phase)
    except Exception:
        phase = "unknown"
    return lib_ok, phase, bool(lib_ok and phase == "PRODUCTION")


def numpy_blas():
    """BLAS backend name (float-determinism awareness - Win/MKL vs Linux/
    OpenBLAS produce different threshold-boundary signals, L209)."""
    try:
        import io
        import contextlib
        import numpy as np
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                np.show_config()
            except Exception:
                pass
        txt = buf.getvalue().lower()
        for b in ("mkl", "openblas", "blis", "accelerate"):
            if b in txt:
                return b
        return "unknown"
    except Exception:
        return "error"


def pip_freeze_hash():
    """Hash + count of the FULL installed package set (not just 4 pins).
    Reported (not merge-critical: cross-platform wheels legitimately differ);
    a diff is a signal to inspect, not an automatic HALT."""
    try:
        import importlib.metadata as m
        pkgs = sorted(
            f"{d.metadata['Name']}=={d.version}" for d in m.distributions()
            if d.metadata and d.metadata["Name"])
        return hashlib.sha256("\n".join(pkgs).encode()).hexdigest()[:16], len(pkgs)
    except Exception:
        return "error", 0


def fingerprint() -> dict:
    import platform
    total, h, backend = trading_day_grid()
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True).stdout.strip()[:12]
    except Exception:
        sha = ""
    if not sha:
        # B1326: no .git on the instance (lean git-archive tar) -> read the
        # SHA baked into the tar by build_r5_code_tar.py.
        try:
            sha = Path("CODE_SHA").read_text(encoding="utf-8").strip()[:12]
        except Exception:
            sha = "unknown"
    smc_lib, smc_phase, smc_active = probe_smc()
    freeze_hash, n_pkgs = pip_freeze_hash()
    return {
        "grid_total": total, "grid_hash": h, "calendar_backend": backend,
        "smc_lib_importable": smc_lib, "smc_phase": smc_phase,
        "smc_active": smc_active,
        "numpy_blas": numpy_blas(),
        "os": platform.platform(), "python": platform.python_version(),
        "pip_freeze_hash": freeze_hash, "pip_n_packages": n_pkgs,
        "pkg_pandas_market_calendars": _pkg("pandas_market_calendars"),
        "pkg_pandas": _pkg("pandas"), "pkg_numpy": _pkg("numpy"),
        "pkg_pyarrow": _pkg("pyarrow"), "code_sha": sha,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", metavar="OUT")
    ap.add_argument("--check", nargs="+", metavar="FP")
    args = ap.parse_args()

    if args.emit:
        fp = fingerprint()
        with open(args.emit, "w", encoding="utf-8") as f:
            json.dump(fp, f, indent=2)
        print(f"env fingerprint -> {args.emit}: grid={fp['grid_total']} "
              f"backend={fp['calendar_backend']} sha={fp['code_sha']}")
        if fp["calendar_backend"] != "nyse_mcal":
            print("WARN: calendar backend is NOT the NYSE calendar "
                  "(pandas_market_calendars missing) -- run would use the "
                  "degraded Mon-Fri grid (L207/L208).")
        if not fp["smc_active"]:
            print(f"WARN: SMC NOT ACTIVE (lib_importable={fp['smc_lib_importable']}"
                  f" phase={fp['smc_phase']}) -- 22 SMC/ICT strategies will be "
                  "SILENT this run (B1317). If this env should have SMC, HALT "
                  "and fix the vendored import before spending compute.")
        return 0

    if args.check:
        fps = []
        for p in args.check:
            with open(p, encoding="utf-8") as f:
                fps.append((p, json.load(f)))
        base_name, base = fps[0]
        mismatches = []
        for name, fp in fps[1:]:
            for k in MERGE_CRITICAL:
                if fp.get(k) != base.get(k):
                    mismatches.append(f"{name}.{k}={fp.get(k)} != {base_name}.{k}={base.get(k)}")
        if mismatches:
            print("ENV-PARITY FAIL (CHECKLIST #158) - these runs are NOT "
                  "mergeable; re-run mismatched chunks on the correct grid:")
            for m in mismatches:
                print(f"  {m}")
            return 1
        print(f"ENV-PARITY PASS: {len(fps)} runs agree on {MERGE_CRITICAL} "
              f"(grid={base['grid_total']} backend={base['calendar_backend']})")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
