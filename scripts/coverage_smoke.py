"""scripts/coverage_smoke.py - #159 Part B (B1323 Council 355): coverage smoke
on the ISOLATED engine. Run BEFORE any full cube re-run (local free / cloud
~$1) to catch silent families + broken isolation BEFORE burning compute.

Asserts, on a small sample run with --cube-isolation:
  1. FANOUT  : cube rows == fired_strategies * n_exits (no partial fanout)
  2. ISOLATION: ZERO cross-strategy portfolio-gate skip reasons (portfolio_gate,
     cooldown, max_loss, factor_concentration, concurrent-ticker block) -- their
     presence means isolation did NOT bypass the gates (M2 regression)
  3. SMC     : env_fingerprint smc_active is True (else 22 SMC strategies silent)
  4. COVERAGE: report per-strategy raw-fire + trade counts (baseline)

Usage:
  python scripts/coverage_smoke.py --run --tickers AAPL,MSFT,.. --output-dir out_smoke \
      [--start 2022-05-05 --end 2026-05-05]
  python scripts/coverage_smoke.py --analyze out_smoke   # analyze an existing (e.g. cloud) dir
"""
from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Skip reasons that MUST be absent under isolation (cross-strategy portfolio
# gates M2 bypasses). Allowed: same-strategy dedup (bug61_mode_c), no_next_bar,
# required_macro_regime (strategy-intrinsic), avoid_tier (borrow, intrinsic).
FORBIDDEN_SKIP_SUBSTR = (
    "portfolio_gate_", "stopout_cooldown", "max_loss_cap",
    "factor_concentration", "concurrent_block_bug61",
)


def run_isolated(tickers, out_dir, start, end, max_hours=4.0):
    cmd = [
        sys.executable, "-m", "backtest.run_phase1a", "--phase", "1a-beta",
        "--tickers", tickers, "--start", start, "--end", end,
        "--no-news", "--no-walk-forward", "--no-agents", "--no-git",
        "--no-portfolio-cap", "--no-dd-halt", "--cube-isolation",
        "--max-run-hours", str(max_hours),   # 1a-beta requires this (run_phase1a:336)
        "--output-dir", out_dir,
    ]
    print("RUN:", " ".join(cmd))
    r = subprocess.run(cmd)
    # Emit the env fingerprint into the output dir so analyze() can check
    # smc_active + parity for this run (the same manifest the launcher emits).
    ef = Path(__file__).resolve().parents[1] / "scripts" / "env_fingerprint.py"
    subprocess.run([sys.executable, str(ef), "--emit",
                    str(Path(out_dir) / "env_fingerprint.json")])
    return r.returncode


def analyze(out_dir) -> int:
    import pandas as pd
    D = Path(out_dir)
    fails, warns = [], []

    # 1. FANOUT
    esc_p = D / "exit_strategy_comparison.csv"
    if esc_p.exists():
        esc = pd.read_csv(esc_p)
        nfired, nex = esc.strategy.nunique(), esc.exit_method.nunique()
        ok = len(esc) == nfired * nex
        print(f"[FANOUT] cube={len(esc)} = {nfired} strat x {nex} exits -> {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append("fanout != fired*exits")
    else:
        fails.append("no exit_strategy_comparison.csv")

    # 2. ISOLATION - forbidden skip reasons must be ABSENT
    sk_p = D / "skipped_trades.csv"
    if sk_p.exists():
        sk = pd.read_csv(sk_p)
        rc = sk["reason"].astype(str) if "reason" in sk.columns else pd.Series([], dtype=str)
        hits = {sub: int(rc.str.contains(sub).sum()) for sub in FORBIDDEN_SKIP_SUBSTR}
        bad = {k: v for k, v in hits.items() if v > 0}
        print(f"[ISOLATION] forbidden cross-strategy skips: {bad if bad else 'NONE (isolation OK)'}")
        if bad:
            fails.append(f"isolation leaked portfolio gates: {bad}")
    else:
        warns.append("no skipped_trades.csv (may be fine if 0 skips)")

    # 3. SMC active
    fp_p = D / "env_fingerprint.json"
    if fp_p.exists():
        fp = json.loads(fp_p.read_text(encoding="utf-8"))
        print(f"[SMC] smc_active={fp.get('smc_active')} lib={fp.get('smc_lib_importable')} "
              f"phase={fp.get('smc_phase')} blas={fp.get('numpy_blas')} os={fp.get('os')}")
        if not fp.get("smc_active"):
            fails.append("smc_active=False -> 22 SMC/ICT strategies silent")
        # code_sha parity: the cloud MUST run current code (B1324 stale-code
        # gap - cloud ran 07-17 code all session). This is the gate that would
        # have caught it before spending. Compared against local HEAD.
        try:
            local_sha = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True
            ).stdout.strip()[:12]
        except Exception:
            local_sha = ""
        cloud_sha = str(fp.get("code_sha", ""))[:12]
        if cloud_sha and local_sha:
            match = cloud_sha == local_sha
            print(f"[CODE_SHA] cloud={cloud_sha} local={local_sha} -> "
                  f"{'OK' if match else 'MISMATCH'}")
            if not match:
                fails.append(f"code_sha mismatch cloud={cloud_sha} "
                             f"local={local_sha} (STALE cloud code - rebuild "
                             "r5_code.tar)")
        else:
            warns.append(f"code_sha unavailable (cloud={cloud_sha!r} "
                         f"local={local_sha!r}) - cannot verify code parity")
    else:
        warns.append("no env_fingerprint.json in output dir")

    # 4. COVERAGE report
    raw_files = [f for f in glob.glob(str(D / "raw_signal_fires.*.csv"))]
    n_raw_strats = 0
    if raw_files:
        frames = [pd.read_csv(f) for f in raw_files if pd.read_csv(f).shape[0]]
        if frames:
            raw = pd.concat(frames, ignore_index=True)
            n_raw_strats = raw["strategy"].nunique()
    tl_p = D / "trade_log.parquet"
    n_traded = 0
    if tl_p.exists():
        n_traded = pd.read_parquet(tl_p)["strategy"].nunique()
    try:
        from backtest.signals.screener import ALL_STRATEGIES
        n_reg = len(ALL_STRATEGIES)
    except Exception:
        n_reg = -1
    print(f"[COVERAGE] registered={n_reg} raw-fired={n_raw_strats} traded={n_traded}")

    print("\n=== SMOKE " + ("PASS" if not fails else "FAIL") + " ===")
    for w in warns:
        print("  WARN:", w)
    for f in fails:
        print("  FAIL:", f)
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="run the isolated engine first")
    ap.add_argument("--analyze", metavar="DIR", help="analyze an existing output dir")
    ap.add_argument("--tickers", default="")
    ap.add_argument("--output-dir", default="output_coverage_smoke")
    ap.add_argument("--start", default="2022-05-05")
    ap.add_argument("--end", default="2026-05-05")
    ap.add_argument("--max-run-hours", type=float, default=4.0)
    args = ap.parse_args()

    if args.analyze:
        return analyze(args.analyze)
    if args.run:
        if not args.tickers:
            print("--run requires --tickers")
            return 2
        rc = run_isolated(args.tickers, args.output_dir, args.start, args.end,
                          args.max_run_hours)
        if rc != 0:
            print(f"engine run failed rc={rc}")
            return rc
        return analyze(args.output_dir)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
