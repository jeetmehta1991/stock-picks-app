#!/usr/bin/env python
"""LENS 12 - EFFECTIVE PARAMETER: does a flag you passed actually BIND?

S6-B1705f, owner-approved. The eleven adversarial lenses in
`STRATEGY_OPTIMISATION_PLAN.md` all interrogate an OUTPUT. **None asks whether an
input that was ACCEPTED changed anything.**

The incident. The owner passed `--min-n 10`. It was accepted, it appeared in the
log, and it governed admission only - `OOS_MIN_N = 30`, a per-fold walk-forward
floor living in a different module, decided which cells received a Sharpe. So
`--min-n 10` and `--min-n 20` produced byte-identical results, and every report
built on them quoted a floor that was never in force. Fixed at B1714
(`roster_core.py:171` now threads the caller's floor into `_sharpe`).

**An inert flag is indistinguishable from an absent one, and strictly worse: the
absent flag would have raised.** The nearest existing lens, EXECUTABILITY, asks
whether the engine CAN apply a knob the search selected. This asks the mirror
question - a knob you did pass, does changing it change the answer?

The check is deliberately crude and says so: run the callable at two values and
compare. It proves BINDING, never CORRECTNESS - a flag that binds to the wrong
thing passes here and is the EXECUTABILITY lens's problem. It also cannot prove
inertness in general, only on the inputs given: a flag with no effect on THIS
fixture may bind on another, which is why `INERT` is reported as
`INERT ON THIS INPUT` and the fixture is named in the result.

Usage:
    from verify_flag_binds import binds
    binds(rc.evaluate, "min_n", 10, 30, pnl, hold)   -> {"verdict": "BINDS", ...}

CLI (subprocess flags):
    python scripts/verify_flag_binds.py --cmd "python x.py --min-n {v}" --values 10 30
"""
from __future__ import annotations

import argparse
import subprocess
import sys

BINDS = "BINDS"
INERT = "INERT ON THIS INPUT"
RAISED = "RAISED"


def _norm(x) -> str:
    """A comparable rendering of a result.

    `repr` is used deliberately rather than `==`: the results being compared are
    often dicts holding floats and None, and `==` on two dicts that differ only
    in a nested NaN is False for the wrong reason. A stable string keeps the
    comparison honest and, when it fails, SHOWS what differed.
    """
    try:
        import pandas as pd
        if isinstance(x, (pd.Series, pd.DataFrame)):
            return x.to_json()
    except Exception:
        pass
    if isinstance(x, dict):
        return repr(sorted((str(k), _norm(v)) for k, v in x.items()))
    if isinstance(x, (list, tuple)):
        return repr([_norm(v) for v in x])
    return repr(x)


def binds(fn, param: str, val_a, val_b, *args, **kwargs) -> dict:
    """Run `fn` with `param=val_a` and `param=val_b`; did the output change?

    Returns a dict carrying the verdict AND both renderings, so a caller that
    reports `BINDS` can show what moved rather than asserting that it did.
    """
    out = {"param": param, "values": [val_a, val_b],
           "callable": getattr(fn, "__qualname__", repr(fn))}
    try:
        a = _norm(fn(*args, **{**kwargs, param: val_a}))
        b = _norm(fn(*args, **{**kwargs, param: val_b}))
    except TypeError as e:
        # an unknown kwarg is the loudest possible form of "does not bind"
        out.update(verdict=RAISED, detail=f"{type(e).__name__}: {e}")
        return out
    out.update(verdict=BINDS if a != b else INERT, a=a[:400], b=b[:400])
    return out


def binds_cmd(cmd_template: str, val_a, val_b, timeout: int = 300) -> dict:
    """The subprocess form: `{v}` in the template is replaced by each value."""
    out = {"template": cmd_template, "values": [val_a, val_b]}
    res = []
    for v in (val_a, val_b):
        cmd = cmd_template.replace("{v}", str(v))
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True,
                               text=True, timeout=timeout)
            res.append(f"rc={r.returncode}\n{r.stdout}")
        except subprocess.TimeoutExpired:
            res.append(f"TIMEOUT after {timeout}s")
    out.update(verdict=BINDS if res[0] != res[1] else INERT,
               a=res[0][:400], b=res[1][:400])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cmd", required=True,
                    help="command template; {v} is replaced by each value")
    ap.add_argument("--values", nargs=2, required=True, metavar=("A", "B"))
    ap.add_argument("--timeout", type=int, default=300)
    a = ap.parse_args()

    r = binds_cmd(a.cmd, a.values[0], a.values[1], timeout=a.timeout)
    print(f"LENS 12 EFFECTIVE PARAMETER: {r['verdict']}")
    print(f"  template : {r['template']}")
    print(f"  values   : {r['values']}")
    if r["verdict"] != BINDS:
        print("\n  Both runs produced identical output. The flag was accepted "
              "and changed nothing on this input - which is what `--min-n 10` "
              "did while OOS_MIN_N=30 governed (S6-B1705b).")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
