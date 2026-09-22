#!/usr/bin/env python
# Source: each run's own output_candle_*/run_heartbeat.json plus
# output_audit/serial_chain.log; per CHECKLIST #77 every figure here is
# derived from those at run time and none is stored in this file.
"""S6-B2978 / L840 correction: the landed-runtime table, terminality PROVEN.

WHY THIS EXISTS. I computed the campaign's landed-runtime mean by hand,
three times, from the elapsed_hours in each run's heartbeat - and twice I
included a run that had not finished, because its sim_day_index had reached
the last simulated day and that LOOKS terminal.

MEASURED 2026-09-22 on candle_tws_c07. At one reading its heartbeat showed
sim_day_index 249, the final day, and elapsed_hours 1.9291 - which I
published as the run's actual, and used to RETRACT an objection. The final
value in the same file is 1.9708. The run had reached its last sim-day and
was still working: open_trades was non-zero at the earlier reading and zero
at the last. The 0.0417 h between them inverted a conclusion.

THE DISCRIMINATOR, and it is cheap. A run is terminal when BOTH hold:

  open_trades == 0          in its heartbeat, and
  a "<wave> finished:" line  for it in output_audit/serial_chain.log

sim_day_index is NOT a terminal condition. It reaches its last value while
the run is still closing positions and writing its cube, which is exactly
the window where elapsed_hours is still moving.

THIS TOOL REFUSES rather than guesses: a run that fails either test is
reported as NOT-TERMINAL and excluded from the mean, by name, so the mean
can never quietly include a moving figure.

    python scripts/candle_runtime_table.py
"""
from __future__ import annotations

import argparse
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAIN_LOG = ROOT / "output_audit" / "serial_chain.log"


def _finished_waves() -> set[str]:
    """Wave names the chain log records as finished."""
    if not CHAIN_LOG.exists():
        return set()
    text = io.open(CHAIN_LOG, encoding="utf-8", errors="replace").read()
    return set(re.findall(r"(\S+) finished: run_wave exit 0", text))


def _wave_of(dirname: str) -> str:
    """output_candle_tws_c07_b0.3_s0.0_wNone -> candle_tws_c07."""
    m = re.match(r"output_(candle_[a-z]+_c\d+)", dirname)
    return m.group(1) if m else dirname


def collect(root: Path | None = None) -> dict:
    root = root or ROOT
    finished = _finished_waves()
    terminal, not_terminal = [], []

    for hb in sorted(root.glob("output_candle_*/run_heartbeat.json")):
        d = hb.parent.name
        h = json.loads(io.open(hb, encoding="utf-8").read())
        wave = _wave_of(d)
        reasons = []
        if h.get("open_trades") != 0:
            reasons.append("open_trades %r is not 0" % (h.get("open_trades"),))
        if wave not in finished:
            reasons.append("no finished line for %s in serial_chain.log" % wave)
        row = {"dir": d, "wave": wave,
               "elapsed_hours": h.get("elapsed_hours"),
               "sim_day_index": h.get("sim_day_index"),
               "open_trades": h.get("open_trades")}
        if reasons:
            row["refused"] = "; ".join(reasons)
            not_terminal.append(row)
        else:
            terminal.append(row)

    hours = [r["elapsed_hours"] for r in terminal]
    return {
        "ticket": "S6-B2978 (L840 correction)",
        "rule": ("a run at its last sim-day is NOT finished - terminality is "
                 "open_trades == 0 AND a finished line in the chain log"),
        "terminal": terminal,
        "not_terminal": not_terminal,
        "n_terminal": len(terminal),
        "sum_hours": round(sum(hours), 4) if hours else None,
        "mean_hours": round(sum(hours) / len(hours), 4) if hours else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    doc = collect()
    print("=== candle landed runtime, terminality proven ===")
    for r in doc["terminal"]:
        print("  TERMINAL     %-40s %s h" % (r["dir"], r["elapsed_hours"]))
    for r in doc["not_terminal"]:
        print("  NOT-TERMINAL %-40s %s h  REFUSED: %s"
              % (r["dir"], r["elapsed_hours"], r["refused"]))
    print("  n_terminal %s  sum %s  mean %s"
          % (doc["n_terminal"], doc["sum_hours"], doc["mean_hours"]))

    if a.out:
        p = Path(a.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        io.open(p, "w", encoding="utf-8").write(json.dumps(doc, indent=1))
        print("  -> %s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
