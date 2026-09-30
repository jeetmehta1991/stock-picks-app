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
