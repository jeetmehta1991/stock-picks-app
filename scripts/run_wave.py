#!/usr/bin/env python
"""THE codified wave workflow (B2116, S6-B2115b - owner precondition B).

Owner ruling 2026-08-23: the Hetzner-auction venue unlocks ONLY after one
strategy completes locally AND "all workflows are established and codified in
an automated fashion". This orchestrator IS that codification for the
launch half: a wave SPEC in, graded-ready cubes out, with every rule that
was previously a habit enforced in code:

  1. MANIFEST per arm (the B2070 field set; frozen sha read from git;
     wall-clock projection from the canonical rate; obsolescence risks
     including the OPEN-TRADE-DROP caveat below).
  2. PRELAUNCH GATE per arm - non-zero = the arm never launches (the
     launch_sweep.py contract, reused not re-implemented).
  3. CHUNKED-RESUME LEGS under the owner's 3h local cap: each leg runs
     with --max-run-hours <leg_cap>; a leg that checkpoints out is
     resumed with --resume-from-checkpoint on the same output dir until
     the cube exists. COMPLETION = the cube file exists (written only
     after the full day loop), never an exit code (L566).
  4. VERIFICATION per arm: cube rows > 1, or the arm is FAILED loudly.
  5. POST-CONFIG LEDGER entries written mechanically for the steps the
     orchestrator itself performed (cube sanity); analysis steps are
     recorded PENDING-WAVE-REVIEW by name, never silently absent.
  6. WAVE SUMMARY artifact + a queue-ready text block printed at the end.

DISCLOSED FIDELITY CAVEAT (codified, not buried): the engine's resume
drops OPEN trades at each chunk boundary (B1076 acknowledged limitation,
run_phase1a.py --resume-from-checkpoint help). A chunked local run is
therefore NOT byte-identical to the same config run in one piece - the
pilot's graded numbers carry this boundary artifact and the auction box
(no cap, single-piece runs) will not. Every wave summary records the leg
count per arm so the artifact's size is visible to the grader.

SPEC (json):
  {"wave": "b2117_pilot", "tickers_file": "output_audit/_sweep_200.txt",
   "strategy_subset": "output_audit/_subset_one.txt",
   "window": {"start": "2024-05-05", "end": "2025-05-05"},
   "leg_cap_hours": 2.5, "max_legs": 4,
   "arms": [{"tag": "sw10", "env": {"SMC_SWING_LENGTH": "10",
                                    "STRAT_EMA_SPAN": "200"}}, ...]}

Usage: PYTHONPATH=. python scripts/run_wave.py --spec <spec.json>
       [--engine-cmd <fake> ]   # TEST SEAM ONLY (B1761), forwarded to
                                # launch_sweep.py; production never passes it
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RATE_S_PER_TICKER_DAY = 0.2613   # canonical, B2021-bracketed end to end


def build_manifest(spec: dict, arm: dict, out_dir: Path, sha: str) -> Path:
    tickers = (ROOT / spec["tickers_file"]).read_text().split()
    days = 251 * max(1, (int(spec["window"]["end"][:4])
                         - int(spec["window"]["start"][:4])))
    proj_h = round(RATE_S_PER_TICKER_DAY * len(tickers) * days / 3600, 2)
    m = {
        "sequence": f"{spec['wave']}_{arm['tag']}",
        "batch": spec["wave"].upper(), "execution": "LOCAL",
        "frozen_sha": sha, "isolation": True, "calendar": "nyse_mcal",
        "tickers": {"file": spec["tickers_file"], "n": len(tickers),
                    "sha256": hashlib.sha256(
                        "\n".join(tickers).encode()).hexdigest()},
        "strategy_subset": spec["strategy_subset"],
        "window": spec["window"], "arms": [arm],
        "concurrency": "orchestrated legs, solo per arm",
        "budget_cap_usd": 0, "spent_usd": 0, "projected_batch_usd": 0,
        "wall_clock_projection_hours": proj_h,
        "wall_clock_projection_basis": (
            f"{RATE_S_PER_TICKER_DAY} s/ticker-day x {len(tickers)}t x "
            f"{days}d; chunked at {spec['leg_cap_hours']}h legs under the "
            "owner's 3h local cap"),
        "obsolescence_risks": [
            {"risk": "open trades dropped at chunk boundaries (B1076)",
             "status": "DISCLOSED - leg count recorded per arm; the auction "
                       "box runs single-piece and will not carry this"},
            {"risk": "3h local cap", "status": f"GATED - leg cap "
             f"{spec['leg_cap_hours']}h enforced per leg"}],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    mp = out_dir / "run_manifest.json"
    mp.write_text(json.dumps(m, indent=1), encoding="utf-8")
    return mp


def run_arm(spec: dict, arm: dict, engine_cmd: str | None = None) -> dict:
    out_dir = ROOT / f"output_{spec['wave']}_{arm['tag']}"
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT),
                         capture_output=True, text=True).stdout.strip()
    manifest = build_manifest(spec, arm, out_dir, sha)
    summary = ROOT / "output_audit" / f"{spec['wave']}_summary.log"
    cube = out_dir / "trade_exit_detail.csv"
    legs = 0
    # M6 (B2121, S6-B2118b): quantify the B1076 open-trade-drop caveat -
    # each checkpoint boundary records how many open trades the resume
    # will drop, read from the engine's own state file. run_wave is the
    # only layer that sees leg boundaries, so the counter lives here.
    boundary_drops = []
    t0 = time.time()
    while legs < int(spec.get("max_legs", 4)):
        legs += 1
        engine_args = [
            "--tickers-file", spec["tickers_file"], "--phase", "1a-beta",
            "--cube-isolation", "--no-agents", "--no-news", "--no-git",
            "--no-walk-forward", "--screen-pool-workers", "0",
            "--start", spec["window"]["start"], "--end", spec["window"]["end"],
            "--max-run-hours", str(spec["leg_cap_hours"]),
        ]
        if legs > 1:
            engine_args += ["--resume-from-checkpoint", str(out_dir)]
        cmd = [sys.executable, str(ROOT / "scripts" / "launch_sweep.py"),
               "--manifest", str(manifest), "--output-dir", str(out_dir),
               "--tag", f"{arm['tag']}-leg{legs}",
               "--summary-log", str(summary)]
        if engine_cmd:
            cmd += ["--engine-cmd", engine_cmd]
        cmd += ["--"] + engine_args
        env = {**os.environ,
               "STRATEGY_SUBSET_FILE": spec["strategy_subset"],
               **{k: str(v) for k, v in arm.get("env", {}).items()}}
        rc = subprocess.run(cmd, cwd=str(ROOT), env=env).returncode
        if rc == 2:
            return {"arm": arm["tag"], "status": "GATE_REFUSED", "legs": legs}
        if cube.exists():
            break
        state_p = out_dir / "engine_state.json"
        if not state_p.exists():
            return {"arm": arm["tag"], "status": "FAILED_NO_CHECKPOINT",
                    "legs": legs, "exit": rc}
        try:
            st = json.loads(state_p.read_text(encoding="utf-8"))
            boundary_drops.append({
                "leg": legs, "sim_date": st.get("sim_date"),
                "open_trades_dropped": st.get("open_trades")})
        except (OSError, ValueError) as exc:
            print(f"[WARN] M6: could not read {state_p} at leg {legs} "
                  f"boundary: {exc!r} - drop count UNMEASURED for this leg")
            boundary_drops.append({
                "leg": legs, "sim_date": None, "open_trades_dropped": None})
    if not cube.exists():
        return {"arm": arm["tag"], "status": "INCOMPLETE_MAX_LEGS",
                "legs": legs}
    with cube.open(encoding="utf-8", errors="replace") as f:
        rows = sum(1 for _ in f) - 1
    status = "COMPLETE" if rows > 1 else "FAILED_EMPTY_CUBE"
    # mechanical ledger entries: what the orchestrator itself verified
    lp = ROOT / "output_audit" / "postconfig_ledger.json"
    ledger = json.loads(lp.read_text(encoding="utf-8")) if lp.exists() else {}
    steps = ["1_cube_sanity", "2_grade_with_config_params",
             "3_outlier_discrepancy_sweep", "4_three_leg_spot_check",
             "5_adversarial_lens_review", "6_post_fix_recheck",
             "6b_equivalence_class_check", "7_implement_in_engine",
             "8_verdict_with_denominators"]
    entry = {s: {"status": "SKIPPED",
                 "evidence": f"PENDING-WAVE-REVIEW ({spec['wave']}): the "
                             "wave-level review batch performs this step "
                             "across all arms together"} for s in steps}
    entry["1_cube_sanity"] = {
        "status": "DONE",
        "evidence": f"run_wave verified {rows} cube rows across {legs} "
                    f"leg(s); M6 boundary drops (B1076 caveat, measured): "
                    f"{boundary_drops if boundary_drops else 'none - single leg'}"}
    ledger[out_dir.name] = entry
    lp.write_text(json.dumps(ledger, indent=1), encoding="utf-8")
    # B2118 (S6-B2117b): the mechanical post-config battery runs HERE, at
    # wave completion, not by hand. --write-ledger upgrades 1_cube_sanity
    # with the M-check evidence when all checks pass; a non-zero exit is
    # RECORDED on the arm result, never swallowed. Waves are Step-1 search
    # runs by the ruled shape, so the holdout-touch FAIL is armed unless
    # the spec says step1_cube: false (a Step-2 validation wave).
    pc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_postconfig.py"),
         "--cube", out_dir.name, "--write-ledger"]
        + (["--step1-cube"] if spec.get("step1_cube", True) else []),
        cwd=str(ROOT))
    return {"arm": arm["tag"], "status": status, "legs": legs,
            "boundary_drops": boundary_drops,
            "cube_rows": rows, "elapsed_s": int(time.time() - t0),
            "postconfig_exit": pc.returncode}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--engine-cmd", default=None,
                    help="TEST SEAM ONLY - forwarded to launch_sweep.py")
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    results = [run_arm(spec, arm, engine_cmd=a.engine_cmd)
               for arm in spec["arms"]]
    out = ROOT / "output_audit" / f"{spec['wave']}_wave_summary.json"
    out.write_text(json.dumps({"spec": spec, "results": results}, indent=1),
                   encoding="utf-8")
    print(f"\nWAVE {spec['wave']}: "
          + " | ".join(f"{r['arm']}={r['status']}(legs={r['legs']})"
                       for r in results))
    print(f"[OK] wrote {out}")
    return 0 if all(r["status"] == "COMPLETE" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
