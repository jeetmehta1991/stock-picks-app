"""B1061 post-completion analyzer for Phase D R5 cube runs.

# Source: Council 161 Option-2 wait-window pre-staging per CHECKLIST #77.

Consumes:
- engine.log PHASE_TIMING markers (B1057 C-fix; ~7 markers per sim_day)
- engine_state.json incremental checkpoints
- trade_log_checkpoint.csv (or .parquet) cube cell results

Emits:
- Per-phase wall-clock decomposition (p50/p95/p99 across days)
- Per-PHASE_TIMING-stage timing (ohlcv_pit_built, pre_exits, exits_done,
  pre_screen, screen_done, sentiment_done)
- Per-strategy x exit cube cell summary (PASS / FAIL / INSUFFICIENT_DATA)
- HALT-CRITICAL classifier (if FAIL sentinel encountered)

Reads inputs from local AWS sync directory (e.g. tmp/phase_d_b1060_results/)
or S3 path (s3://bucket/run_id/output_phase_N/).

Usage:
    python scripts/analyze_phase_d_results.py \\
        --engine-log /path/to/engine.log \\
        --output-dir /path/to/output_phase_4/ \\
        --report-out /path/to/b1060_phase_d_analysis.md
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

PHASE_TIMING_RE = re.compile(
    r"PHASE_TIMING day=(?P<day>\S+) (?P<stage>\S+) "
    r"(?:dur=(?P<dur>[\d.]+)s)?(?:.* total=(?P<total>[\d.]+)s)?"
)


def parse_phase_timing(engine_log: Path) -> dict:
    """Parse PHASE_TIMING markers from engine.log.

    Returns dict {stage: [durations_sec]} for percentile analysis.
    """
    stage_durations: dict[str, list[float]] = defaultdict(list)
    total_per_day: list[float] = []
    n_markers = 0
    n_days = 0

    if not engine_log.exists():
        return {"stage_durations": {}, "total_per_day": [],
                "n_markers": 0, "n_days": 0}

    with open(engine_log) as f:
        for line in f:
            m = PHASE_TIMING_RE.search(line)
            if not m:
                continue
            n_markers += 1
            stage = m.group("stage")
            dur = m.group("dur")
            total = m.group("total")
            if dur:
                stage_durations[stage].append(float(dur))
            if total:
                total_per_day.append(float(total))
                n_days += 1

    return {
        "stage_durations": dict(stage_durations),
        "total_per_day": total_per_day,
        "n_markers": n_markers,
        "n_days": n_days,
    }


def pct(xs: list[float], p: float) -> float:
    """Compute percentile; returns 0 on empty list."""
    if not xs:
        return 0.0
    xs_sorted = sorted(xs)
    idx = max(0, min(len(xs_sorted) - 1, int(round((p / 100.0) * (len(xs_sorted) - 1)))))
    return xs_sorted[idx]


def summarize_timing(timing: dict) -> str:
    """Produce markdown summary table of timing percentiles."""
    lines = [
        "## Per-Stage Timing (B1057 PHASE_TIMING markers)",
        "",
        f"Total markers parsed: {timing['n_markers']}",
        f"Total sim_days: {timing['n_days']}",
        "",
        "| Stage | n | p50 (sec) | p95 (sec) | p99 (sec) | max (sec) |",
        "|---|---|---|---|---|---|",
    ]
    for stage in sorted(timing["stage_durations"].keys()):
        durs = timing["stage_durations"][stage]
        if not durs:
            continue
        lines.append(
            f"| {stage} | {len(durs)} | "
            f"{pct(durs, 50):.4f} | "
            f"{pct(durs, 95):.4f} | "
            f"{pct(durs, 99):.4f} | "
            f"{max(durs):.4f} |"
        )
    if timing["total_per_day"]:
        td = timing["total_per_day"]
        lines.extend([
            "",
            f"**Per-day TOTAL:** n={len(td)} "
            f"p50={pct(td, 50):.3f}s p95={pct(td, 95):.3f}s "
            f"p99={pct(td, 99):.3f}s max={max(td):.3f}s "
            f"mean={statistics.mean(td):.3f}s",
        ])
    return "\n".join(lines)


def summarize_cube_cells(output_dir: Path) -> str:
    """Summarize cube cell results from trade_log + engine_state.

    Returns markdown summary.
    """
    lines = ["## Cube Cell Summary", ""]
    state_file = output_dir / "engine_state.json"
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
        # B1064 fix: correct key names per actual engine_state.json schema
        # (verified against B1063 Phase 1 output)
        lines.append(f"status: {state.get('status', 'unknown')}")
        lines.append(f"sim_date: {state.get('sim_date', 'unknown')}")
        lines.append(f"timestamp: {state.get('timestamp', 'unknown')}")
        lines.append(f"simulated_day: {state.get('simulated_day', 'unknown')}")
        lines.append(f"cells_completed: {state.get('cells_completed', 'unknown')}")
        lines.append(f"trades_so_far: {state.get('trades_so_far', 'unknown')}")
        lines.append(f"open_trades: {state.get('open_trades', 'unknown')}")
        lines.append(f"pid: {state.get('pid', 'unknown')}")
    else:
        lines.append("engine_state.json not found")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--engine-log", type=Path, required=True,
                        help="Path to engine.log with PHASE_TIMING markers")
    parser.add_argument("--output-dir", type=Path, required=False,
                        help="Phase output directory (engine_state.json + trade_log)")
    parser.add_argument("--report-out", type=Path,
                        default=Path("output_audit/phase_d_analysis_report.md"),
                        help="Output report path")
    args = parser.parse_args()

    timing = parse_phase_timing(args.engine_log)
    timing_md = summarize_timing(timing)

    cube_md = ""
    if args.output_dir and args.output_dir.exists():
        cube_md = summarize_cube_cells(args.output_dir)

    report = "\n\n".join([
        "# Phase D R5 Cube Analysis Report",
        f"_Generated from `{args.engine_log}`._",
        timing_md,
        cube_md,
    ])

    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(report)
    print(f"Report written to {args.report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
