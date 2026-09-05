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
  3. CHUNKED-RESUME LEGS under the owner's local cap (OWNER_LOCAL_CAP_HOURS
     in prelaunch_gate.py, the one constant the gate enforces; B2613 stopped
     this file retyping the retired 3h figure): each leg runs
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
sys.path.insert(0, str(ROOT / "scripts"))
from producer_variant_table import launch_refusals  # noqa: E402  (B2578 launch gate)
from prelaunch_gate import OWNER_LOCAL_CAP_HOURS  # noqa: E402  (B2613 S6-B2612g)
RATE_S_PER_TICKER_DAY = 0.2613   # canonical, B2021-bracketed end to end


def project_from_leg(elapsed_s: float, sim_day: int, total_days: int,
                     leg_cap_hours: float, leg_start_day: int = 0) -> dict:
    """B2127 (S6-B2125b): re-project THIS arm from THIS arm's own first leg.

    The canonical 0.2613 s/ticker-day under-projected the B2118 pilot by
    1.6-2.4x, and the per-day cost varies with the parameter being swept
    (measured: swing 5 cost ~1.5x per sim-day what swing 10 did), so ONE
    projection cannot cover an arm set. After a leg checkpoints out, its
    own days-per-second is the only honest estimator for its remaining legs.
    """
    if sim_day <= 0 or elapsed_s <= 0:
        return {"measured": False,
                "note": "leg produced no sim-days; cannot re-project"}
    # S6-B2405: elapsed_s covers THIS LEG only, so the denominator must too.
    # It was the checkpoint's CUMULATIVE simulated_day, mixing a per-leg
    # numerator with an all-legs denominator - understating s/day by a factor
    # that GROWS with leg number. MEASURED on the config-1 wave: reported
    # 49.92/26.09/18.70 s/day across legs 1-3, reading as IMPROVING throughput,
    # against a true 49.92/54.54/66.02 which is DEGRADING - an error of
    # 1.00x/2.09x/3.53x. Leg 3's ETA read 0.69h against a true 2.42h, and every
    # leg had in fact run the same ~4.5h cap.
    leg_days = sim_day - max(0, leg_start_day)
    if leg_days <= 0:
        return {"measured": False,
                "note": "leg advanced no sim-days; cannot re-project"}
    s_per_day = elapsed_s / leg_days
    remaining = max(0, total_days - sim_day)
    remaining_h = s_per_day * remaining / 3600.0
    legs_needed = int(-(-remaining_h // leg_cap_hours)) if leg_cap_hours else 0
    return {"measured": True,
            "s_per_sim_day": round(s_per_day, 2),
            "days_done": sim_day, "days_this_leg": leg_days,
            "days_remaining": remaining,
            "projected_remaining_hours": round(remaining_h, 2),
            "legs_still_needed_at_cap": legs_needed}


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
            f"owner's {OWNER_LOCAL_CAP_HOURS:g}h local cap"),
        # B2174: spec passthrough for the drift waiver. Hourly owner updates
        # are commits, commits move HEAD, and the sha half of drift_check
        # would refuse every resume leg after the first report. The waiver is
        # explicit and recorded HERE, in the manifest the receipt hashes; the
        # no-engine-commits-mid-wave discipline carries the real safety.
        "allow_engine_drift": bool(spec.get("allow_engine_drift", False)),
        "obsolescence_risks": [
            {"risk": "open trades dropped at chunk boundaries (B1076)",
             "status": "DISCLOSED - leg count recorded per arm; the auction "
                       "box runs single-piece and will not carry this"},
            # B2613 (S6-B2612g): the cap is READ from the constant the gate
            # enforces (prelaunch_gate.py OWNER_LOCAL_CAP_HOURS), not retyped -
            # every manifest to date said '3h' against an enforced 5.0h.
            {"risk": f"{OWNER_LOCAL_CAP_HOURS:g}h local cap", "status": f"GATED - leg cap "
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
    boundary_carryover = []
    # S6-B2405: the sim-day each leg STARTS from, so a leg's rate is
    # measured over its own days rather than every leg's days.
    _prev_sim_day = 0
    rates = []   # B2127 per-leg measured rates
    t0 = time.time()
    while legs < int(spec.get("max_legs", 4)):
        legs += 1
        leg_t0 = time.time()
        leg_start_day = _prev_sim_day
        engine_args = [
            "--tickers-file", spec["tickers_file"], "--phase", "1a-beta",
            "--cube-isolation", "--no-agents", "--no-news", "--no-git",
            # B2142: the pool is SPEC-DRIVEN now. It was hardcoded to 0
            # (sequential), which is why every run to date used ONE core of ten
            # - and why the N=3 concurrency figure (2.04x/arm) was measured
            # pool-OFF. Those two speedups draw on the SAME ten cores and must
            # never be multiplied: 3 pooled arms get ~3.3 cores each and the
            # pool dividend that brings a config under the owner's local cap
            # collapses. Default stays 0 so no existing spec changes behaviour.
            "--no-walk-forward",
            "--screen-pool-workers", str(spec.get("pool_workers", 0)),
            "--start", spec["window"]["start"], "--end", spec["window"]["end"],
            "--max-run-hours", str(spec["leg_cap_hours"]),
        ]
        # B2181: a spec declaring "resume": true continues from the dir's
        # existing checkpoint ON LEG 1 - the owner-directed sw50 relaunch
        # path. Without it, leg 1 omits the flag and the engine RESTARTS
        # from day 0, clobbering the checkpoint it was meant to continue
        # (the exact hazard the B2179 costing exposed).
        if legs > 1 or (legs == 1 and spec.get("resume")
                        and (out_dir / "engine_state.json").exists()):
            engine_args += ["--resume-from-checkpoint", str(out_dir)]
        cmd = [sys.executable, str(ROOT / "scripts" / "launch_sweep.py"),
               "--manifest", str(manifest), "--output-dir", str(out_dir),
               "--tag", f"{arm['tag']}-leg{legs}",
               "--summary-log", str(summary)]
        if engine_cmd:
            cmd += ["--engine-cmd", engine_cmd]
        cmd += ["--"] + engine_args
        env = {**os.environ,
               # B2185: cap native thread pools per process. Windows Event
               # 2004 diagnosed 22 low-VIRTUAL-memory conditions in 30h with
               # python.exe at ~5.5GB virtual EACH - OpenBLAS/OMP per-thread
               # buffers multiplied across 12+ spawn processes exhaust
               # COMMIT, and failed native allocations are the 0xC0000005
               # crash mechanism. Parallelism here is the PROCESS pool;
               # BLAS threads buy nothing and reserve gigabytes.
               "OPENBLAS_NUM_THREADS": "1",
               "OMP_NUM_THREADS": "1",
               "MKL_NUM_THREADS": "1",
               "STRATEGY_SUBSET_FILE": spec["strategy_subset"],
               **{k: str(v) for k, v in arm.get("env", {}).items()}}
        # S6-B2250a (L680): PROVE THE POOL CAN SPAWN BEFORE SPENDING HOURS.
        # b2197_sw10sp20 ran to sim_day 230 - about 1.3 hours - and then died
        # on `PermissionError: [WinError 5]` raised by _winapi.DuplicateHandle
        # inside multiprocessing/reduction.py while spawning a worker. That
        # failure is DETERMINISTIC and available at second zero: the process
        # either has the privilege to duplicate a handle into a child or it
        # does not. Paying 1.3 hours to discover it is pure waste.
        #
        # Deliberately narrow: this proves ONE spawn worked ONCE, at launch. It
        # does NOT prove spawning survives 230 sim-days, since a failure driven
        # by handle exhaustion or a transient token state would pass here - so
        # the message says what it proved, not that the run is safe.
        if legs == 1:
            ok, why = probe_pool_spawn()
            if not ok:
                print(f"[B2250a REFUSED] pool spawn failed at launch: {why}")
                return {"arm": arm["tag"], "status": "SPAWN_REFUSED",
                        "legs": 0, "spawn_error": why}
            print("[B2250a] pool spawn probe OK (one worker, at launch - "
                  "does not prove spawning survives the whole run)")
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
            # S6-B2404: the open-trade count AT the boundary. The NEXT leg
            # RESTORES exactly these trades (measured: the launch log reports
            # the same counts as restored), so this is a CARRYOVER. It was
            # named *_drops, which said the opposite of what it counts.
            boundary_carryover.append({
                "leg": legs, "sim_date": st.get("sim_date"),
                "open_trades_carried": st.get("open_trades")})
            # B2127: re-project the rest of THIS arm from THIS leg.
            total_days = 251 * max(1, (int(spec["window"]["end"][:4])
                                       - int(spec["window"]["start"][:4])))
            _sd = int(st.get("simulated_day") or 0)
            rate = project_from_leg(
                time.time() - leg_t0, _sd, total_days,
                float(spec["leg_cap_hours"]), leg_start_day=leg_start_day)
            rates.append({"leg": legs, **rate})
            _prev_sim_day = _sd
            print(f"[B2127 rate] arm={arm['tag']} leg={legs}: {rate}")
            if rate.get("measured") and rate["legs_still_needed_at_cap"] > (
                    int(spec.get("max_legs", 4)) - legs):
                print(f"[B2127 WARN] arm={arm['tag']} needs "
                      f"{rate['legs_still_needed_at_cap']} more legs but only "
                      f"{int(spec.get('max_legs', 4)) - legs} remain under "
                      "max_legs - this arm will NOT finish as specced")
        except (OSError, ValueError) as exc:
            print(f"[WARN] M6: could not read {state_p} at leg {legs} "
                  f"boundary: {exc!r} - drop count UNMEASURED for this leg")
            boundary_carryover.append({
                "leg": legs, "sim_date": None, "open_trades_carried": None})
    if not cube.exists():
        return {"arm": arm["tag"], "status": "INCOMPLETE_MAX_LEGS",
                "legs": legs}
    with cube.open(encoding="utf-8", errors="replace") as f:
        rows = sum(1 for _ in f) - 1
    status = "COMPLETE" if rows > 1 else "FAILED_EMPTY_CUBE"
    # B2118 (S6-B2117b) -> B2520: the post-config LANDING SUPERVISOR runs
    # HERE as the second line of defence, BEFORE this orchestrator writes a
    # word to the ledger. The engine itself calls it the moment the cube is
    # written (run_phase1a._postconfig_landing_hook), so for a real engine
    # this call is a fingerprint no-op (--if-not-landed); for a substitute
    # engine (--engine-cmd, tests) it is THE landing, with git + toast off
    # because a fake cube must never be pushed or announced. A non-zero exit
    # is RECORDED on the arm result, never swallowed. Waves are Step-1 search
    # runs by the ruled shape unless the spec says step1_cube: false (a
    # Step-2 validation wave).
    pc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "postconfig_landing.py"),
         "--cube", out_dir.name, "--if-not-landed", "--source", "run_wave"]
        + (["--step1-cube"] if spec.get("step1_cube", True) else ["--step2-cube"])
        + (["--no-git", "--no-notify"] if engine_cmd else []),
        cwd=str(ROOT))
    # mechanical ledger entry: what the orchestrator ITSELF verified (legs +
    # M6 boundary drops - the battery cannot know these).
    # B2207 (S6-B2205a): the ledger write is LOCKED + atomic via
    # ledger_lock.locked_ledger_update - two configs landing simultaneously
    # serialize instead of losing an entry. The parallel-program prerequisite.
    # B2520: ADDITIVE, never authoritative. Until B2520 this block pre-wrote
    # all nine steps as SKIPPED "PENDING-WAVE-REVIEW" for a review batch that
    # never existed (L721) - the phantom deferral behind "why are some steps
    # skipped after each config?" - and its first B2520 shape wrote step 1 as
    # DONE before the battery had run, which would have turned a battery FAIL
    # into DONE. Now the battery's status STANDS and the wave's evidence is
    # appended to it; if the battery recorded nothing (supervisor crashed),
    # the row is OPEN - a row-count is not a sanity verdict (L642).
    _wave_ev = (f"run_wave verified {rows} cube rows across {legs} leg(s); "
                f"M6 boundary drops (B1076 caveat, measured): "
                f"{boundary_carryover if boundary_carryover else 'none - single leg'}")
    from ledger_lock import locked_ledger_update

    def _put(ledger: dict) -> dict:
        entry = dict(ledger.get(out_dir.name) or {})
        old = entry.get("1_cube_sanity") or {}
        if old.get("status") and old.get("evidence"):
            entry["1_cube_sanity"] = {
                "status": old["status"], "evidence": f"{old['evidence']} | {_wave_ev}"}
        else:
            entry["1_cube_sanity"] = {
                "status": "OPEN",
                "evidence": f"{_wave_ev} - the battery recorded nothing for this "
                            f"step (supervisor exit {pc.returncode}); OPEN until "
                            "it does (fail closed, L642)"}
        ledger[out_dir.name] = entry
        return ledger
    locked_ledger_update(_put)
    # B2198 (L651) + B2208 FIX: the battery's result is RENDERED, not only
    # written. B2198 placed this block AFTER the return - dead code, which is
    # why the owner saw nothing print for three landings. It now runs BEFORE
    # the return, and ALSO writes a durable per-config artifact so the result
    # is a file you can open rather than a needle in a 9,000-line engine log.
    try:
        # B2211: ONE document, regenerated whole (owner: "I want a single
        # document and not multiple"). Per-config cards are retired; this
        # doc carries every step's FINDINGS, not its status. Regenerated
        # AFTER the wave evidence lands so the report carries it.
        import postconfig_doc as _pcd
        _doc = ROOT / "output_audit" / "POSTCONFIG_REPORT.md"
        _doc.write_text(_pcd.build(), encoding="utf-8")
        print(f"[OK] {_doc.name} regenerated including this config")
    except Exception as _exc:               # never let reporting kill a landing
        print(f"[WARN] post-config report card unavailable: {_exc!r}")
    # S6-B2230 (L580 applied to a LIST): at legs=1 the append sites for BOTH
    # accumulators sit after the `if cube.exists(): break`, so neither is
    # reachable and an empty list is STRUCTURALLY GUARANTEED rather than
    # measured. Reporting `[]` invites a reader to take it for a clean result -
    # and I did exactly that for 15 configs, calling them "zero boundary drops"
    # when no boundary had existed. An unmeasured value renders as its own
    # token, never as the value that means "measured, and it was nothing".
    _na = "NOT-APPLICABLE-SINGLE-LEG"
    return {"arm": arm["tag"], "status": status, "legs": legs,
            "boundary_carryover": boundary_carryover if legs > 1 else _na,
            "measured_rates": rates if legs > 1 else _na,
            "cube_rows": rows, "elapsed_s": int(time.time() - t0),
            "postconfig_exit": pc.returncode}


def _spawn_probe_worker(x):
    """Module-level so it is picklable by the spawn start method."""
    return x * 2


def probe_pool_spawn(timeout_s: float = 60.0) -> tuple[bool, str]:
    """S6-B2250a: can this process actually spawn a pool worker?

    Returns (ok, reason). The failure this exists for is
    `PermissionError: [WinError 5] Access is denied` from
    `_winapi.DuplicateHandle(..., DUPLICATE_CLOSE_SOURCE)` during spawn, which
    killed b2197_sw10sp20 after ~1.3 hours of work. One worker is enough to
    settle it: the privilege is present or it is not.
    """
    import multiprocessing as _mp
    try:
        ctx = _mp.get_context("spawn")
        with ctx.Pool(processes=1) as pool:
            got = pool.apply_async(_spawn_probe_worker, (21,)).get(timeout_s)
        if got != 42:
            return False, f"worker returned {got!r}, expected 42"
        return True, "one worker spawned and returned"
    except Exception as exc:                      # noqa: BLE001 - report ANY
        # Deliberately broad: the point is to surface whatever spawn raises,
        # named, rather than to enumerate the failure modes in advance.
        return False, f"{type(exc).__name__}: {exc}"


def archive_stale_summary(wave: str):
    """B2193 (L649): a resume-in-place wave inherits its predecessor's TERMINAL
    wave summary, and any reader waiting on the NEW run's summary reads the old
    verdict instead (measured: the B2192 chain runner halted on sw50's
    parallel-era INCOMPLETE_MAX_LEGS summary while the live resumed run was at
    sim day 110). A summary on disk at launch time describes a PRIOR attempt by
    construction - archive it so no reader can see a summary older than the run
    it claims to describe. Returns the archive path, or None if none existed.
    """
    p = ROOT / "output_audit" / f"{wave}_wave_summary.json"
    if not p.exists():
        return None
    dest = p.with_name(f"{wave}_wave_summary_STALE_{int(time.time())}.json")
    p.rename(dest)
    return dest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--engine-cmd", default=None,
                    help="TEST SEAM ONLY - forwarded to launch_sweep.py")
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    stale = archive_stale_summary(spec["wave"])
    if stale:
        print(f"[STALE] prior wave summary archived -> {stale.name}")
    # B2578 (S6-B2573b): the launch gate runs BEFORE any arm. A refusal
    # writes a REFUSED summary (so run_serial_chain HALTs on it and an
    # idempotent restart does not relaunch the same spec) and exits 3.
    refusals = launch_refusals(spec, ROOT)
    if refusals:
        for r in refusals:
            print(f"LAUNCH REFUSED (S6-B2573b): {r}")
        out = ROOT / "output_audit" / f"{spec['wave']}_wave_summary.json"
        out.write_text(json.dumps({
            "spec": spec, "refusals": refusals,
            "results": [{"arm": arm.get("tag", "?"), "status": "REFUSED",
                         "legs": 0} for arm in spec["arms"]]},
            indent=1), encoding="utf-8")
        print(f"[REFUSED] wrote {out}")
        return 3
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
