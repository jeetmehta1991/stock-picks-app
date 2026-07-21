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


def analyze(out_dir, expected_sha=None) -> int:
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
        # code_sha parity (B1324 stale-code gap). B1336 (L212/B1334 fix):
        # frozen batch sequences compare against the SEQUENCE SHA via
        # --expected-sha, NOT git HEAD -- HEAD advances with doc/gate commits
        # while the frozen engine tar stays at the sequence SHA, so the old
        # HEAD-compare false-failed every frozen batch.
        if expected_sha:
            local_sha = expected_sha[:12]
        else:
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

    # --- B1330 addition 1: per-producer-FAMILY coverage (catches a whole
    # family silently dead - the B660 class). CORE families must fire on any
    # liquid sample; EVENT/rare families may legitimately be sparse (warn only).
    fired = set()
    if raw_files:
        for f in raw_files:
            try:
                d = pd.read_csv(f)
                if len(d):
                    fired |= set(d["strategy"].tolist())
            except Exception:
                pass
    if tl_p.exists():
        fired |= set(pd.read_parquet(tl_p)["strategy"].unique())
    CORE = {
        "oscillator": ("rsi", "macd", "stoch", "mfi", "ultimate", "cci"),
        "trend": ("ema", "sma", "adx", "supertrend", "ichimoku", "donchian", "hull"),
        "volatility": ("bollinger", "keltner", "atr", "squeeze", "vix"),
        "candle": ("hammer", "doji", "engulf", "star", "soldiers", "crows", "pin_bar", "shooting"),
        "avwap_vol": ("avwap", "vwap", "obv", "volume", "cmf"),
    }
    SPARSE = {
        "smc_ict": ("smc_", "turtle_soup", "judas", "mmbm", "mmsm", "po3", "_ote", "fvg", "order_block", "liquidity_sweep", "breaker", "mitigation"),
        "smart_money": ("insider", "congress", "institutional", "smart_money", "cluster", "13f"),
        "news_event": ("news_", "pead", "sentiment", "8k", "guidance", "buyback", "activist", "m_and_a"),
        "chart_pattern": ("cup_and_handle", "head_and_shoulders", "triangle", "flag_", "wedge", "double_", "pennant"),
        "index_calendar": ("rebalance", "inclusion", "deletion", "classification_change", "halloween", "january", "holiday", "fomc", "seasonal", "bias"),
        "cross_asset": ("xs_", "gold_silver", "dxy", "sector_rotation", "risk_off", "defensive"),
    }

    def _fam_count(subs):
        return sum(1 for s in fired if any(x in s for x in subs))
    print("[FAMILY] core coverage:", {f: _fam_count(sub) for f, sub in CORE.items()})
    print("[FAMILY] sparse coverage:", {f: _fam_count(sub) for f, sub in SPARSE.items()})
    if fired:  # only meaningful when strategies actually fired
        for fam, sub in CORE.items():
            if _fam_count(sub) == 0:
                fails.append(f"CORE producer family '{fam}' has ZERO firing "
                             "strategies (producer likely broken)")

    # --- addition 2: data-coverage (input tickers with zero activity = candidate
    # OHLCV gaps). Reported (warn) - zero trades can also be legit signal-sparsity.
    if tl_p.exists():
        active_tk = set(pd.read_parquet(tl_p)["ticker"].unique())
        print(f"[DATA] tickers with >=1 trade: {len(active_tk)}")

    # --- addition 3: log silent-failure / traceback scan (the SMC bug only
    # showed in the log). Scans the run log if present next to the output dir.
    for cand_log in [D.parent / (D.name + ".log"), D / "run.log",
                     D.parent / "r5chunk.log", D / "r5chunk.log"]:
        if cand_log.exists():
            txt = cand_log.read_text(encoding="utf-8", errors="replace")
            bad_markers = ["Traceback (most recent call last)", "ModuleNotFoundError",
                           "ImportError", "PREENGINE_GATE_FAIL", "SMC_VENDORED_INSTALL_FAILED"]
            hit = [m for m in bad_markers if m in txt]
            print(f"[LOG] {cand_log.name}: {'clean' if not hit else 'ERRORS ' + str(hit)}")
            if hit:
                fails.append(f"log {cand_log.name} has {hit}")
            break

    print("\n=== SMOKE " + ("PASS" if not fails else "FAIL") + " ===")
    for w in warns:
        print("  WARN:", w)
    for f in fails:
        print("  FAIL:", f)
    return 0 if not fails else 1


def determinism(dir1, dir2) -> int:
    """B1330 addition 4: two runs of the SAME sample must be bit-identical
    (same platform). A divergence = hidden nondeterminism (races/ordering)."""
    import pandas as pd
    a = pd.read_csv(Path(dir1) / "exit_strategy_comparison.csv").sort_values(
        ["strategy", "exit_method"]).reset_index(drop=True)
    b = pd.read_csv(Path(dir2) / "exit_strategy_comparison.csv").sort_values(
        ["strategy", "exit_method"]).reset_index(drop=True)
    if a.shape != b.shape:
        print(f"[DETERMINISM] FAIL shape {a.shape} != {b.shape}")
        return 1
    num = a.select_dtypes("number").columns
    diff = (a[num] - b[num]).abs().max().max()
    ok = a[["strategy", "exit_method"]].equals(b[["strategy", "exit_method"]]) and diff < 1e-9
    print(f"[DETERMINISM] cells={len(a)} max|numeric diff|={diff:.2e} -> {'IDENTICAL' if ok else 'DIVERGE'}")
    return 0 if ok else 1


def merge_check(dirs) -> int:
    """B1330 addition 5: validate the batch-APPEND mechanism the whole plan
    depends on - batches must be ticker-disjoint and merged trades == sum."""
    import pandas as pd
    tls, tickers, total = [], [], 0
    for d in dirs:
        tl = pd.read_parquet(Path(d) / "trade_log.parquet")
        tls.append(tl); total += len(tl); tickers.append(set(tl.ticker.unique()))
    overlap = set.intersection(*tickers) if len(tickers) > 1 else set()
    overlap.discard("SPY")  # SPY benchmark auto-added to each batch - dedup handles
    merged = pd.concat(tls, ignore_index=True)
    key = ["ticker", "entry_date", "strategy"]
    dupes = merged.duplicated(key & set(merged.columns) if False else
                              [k for k in key if k in merged.columns]).sum()
    ok = not overlap
    print(f"[MERGE-APPEND] batches={len(dirs)} sum_trades={total} merged={len(merged)} "
          f"non-SPY ticker-overlap={len(overlap)} dupes={dupes} -> {'OK' if ok else 'OVERLAP!'}")
    if overlap:
        print("  overlapping tickers (batches NOT disjoint):", sorted(overlap)[:10])
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="run the isolated engine first")
    ap.add_argument("--analyze", metavar="DIR", help="analyze an existing output dir")
    ap.add_argument("--expected-sha", default=None,
                    help="B1336: frozen-sequence SHA for the code_sha parity "
                         "check (default: current git HEAD)")
    ap.add_argument("--determinism", nargs=2, metavar=("DIR1", "DIR2"),
                    help="assert two runs are bit-identical")
    ap.add_argument("--merge-check", nargs="+", metavar="DIR",
                    help="validate ticker-disjoint batch append")
    ap.add_argument("--tickers", default="")
    ap.add_argument("--output-dir", default="output_coverage_smoke")
    ap.add_argument("--start", default="2022-05-05")
    ap.add_argument("--end", default="2026-05-05")
    ap.add_argument("--max-run-hours", type=float, default=4.0)
    args = ap.parse_args()

    if args.determinism:
        return determinism(*args.determinism)
    if args.merge_check:
        return merge_check(args.merge_check)
    if args.analyze:
        return analyze(args.analyze, expected_sha=args.expected_sha)
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
