"""S6-B2556a (B3139, council of 5): the ONE list of engine entry points.

Two gates read it and they ask DIFFERENT questions, so each reads its own name:
  RUN_PROCESSES        a process that IS an engine run while it is alive - the
                       pyramid gate's in-flight check (scripts/pyramid_gate.py);
  LAUNCH_ENTRY_POINTS  a command that STARTS one - the turn gate's launch
                       classifier (scripts/verify_turn_compliance.py
                       _segment_is_launch): every run process plus the spawner
                       that starts one and exits (launch_detached.py);
  SPEC_DRIVEN          entry points that read the pool setting from their SPEC,
                       so their command line has no --screen-pool-workers flag
                       for the pool-workers scan to demand.

MEASURED before this module: the turn gate's copy named run_phase1a.py and
run_phase1b.py - which exists nowhere - and missed run_wave.py,
run_serial_chain.py, launch_sweep.py and launch_detached.py, so a direct
run_wave launch escaped the launch-turn monitor gate (#185); the pyramid gate
kept a second, different copy (L593: two readings drift, one cannot).
"""
RUN_PROCESSES = ("run_phase1a.py", "run_wave.py", "run_serial_chain.py",
                 "launch_sweep.py")
LAUNCH_ENTRY_POINTS = RUN_PROCESSES + ("launch_detached.py",)
SPEC_DRIVEN = ("run_wave.py", "run_serial_chain.py", "launch_sweep.py",
               "launch_detached.py")

# S6-B3178: an entry point's MODES, in its OWN dispatch precedence - the first
# flag present decides whether the call starts an engine run; no flag present
# means it does. launch_detached.main tests a.selftest, then a.chain, then
# a.cleanup, then falls through to --spec (pinned against that if-chain by
# test_b3178_launch_dispatch_table_matches_launch_detached). MEASURED: the
# turn gate counted `launch_detached.py --cleanup <task>` - which only
# unregisters a finished task - as a launch. run_phase1a.py --dry-run is NOT
# here: it runs the engine on a two-month, ten-ticker window, a real run.
LAUNCH_DISPATCH = {
    "launch_detached.py": (("--selftest", False), ("--chain", True),
                           ("--cleanup", False)),
}


def starts_a_run(script: str, tokens) -> bool:
    """Does invoking `script` with these argv tokens start an engine run?"""
    toks = set(tokens)
    for flag, is_launch in LAUNCH_DISPATCH.get(script, ()):
        if flag in toks:
            return is_launch
    return True
