"""Diagnostic: parse Phase 1A-beta batch logs for per-day timing.

Source (per CHECKLIST #77): Owner directive Option D 2026-05-26.
Phase 1A-beta launched at 08:59; 2h17m in, only 50-63 of 1003 days
processed per batch. Projected wall 30-40h not 6.6h. This script
parses the existing run.log files to identify the slowness pattern
before relaunching.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

PAT = re.compile(
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?"
    r"screen_universe \[(\d{4}-\d{2}-\d{2})\] regime=(\w+): "
    r"(\d+)/(\d+) passed"
)


def main():
    for batch in [1, 2, 3]:
        p = Path(f"output_phase_1a_beta_cube_b{batch}/run.log")
        if not p.exists():
            print(f"=== batch {batch}: log not found ===")
            continue
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        days = []
        for line in lines:
            m = PAT.search(line)
            if m:
                days.append((
                    datetime.fromisoformat(m.group(1)),
                    m.group(2),
                    m.group(3),
                    int(m.group(4)),
                    int(m.group(5)),
                ))
        if len(days) < 2:
            print(f"=== batch {batch}: only {len(days)} days ===")
            continue
        deltas = sorted(
            [(days[i][0] - days[i-1][0]).total_seconds() for i in range(1, len(days))]
        )
        n = len(deltas)
        median = deltas[n // 2]
        p90 = deltas[int(n * 0.9)]
        max_d = deltas[-1]
        cand_counts = [d[3] for d in days]
        median_cand = sorted(cand_counts)[n // 2]
        max_cand = max(cand_counts)
        total = sum(deltas)
        rem = 1003 - len(days)
        print(f"=== batch {batch} ===")
        print(f"  days processed: {len(days)}")
        print(f"  total wall sec: {total:.0f} ({total/3600:.1f}h)")
        print(f"  per-day median: {median:.1f}s")
        print(f"  per-day p90:    {p90:.1f}s")
        print(f"  per-day max:    {max_d:.1f}s")
        print(f"  candidates median: {median_cand}")
        print(f"  candidates max:    {max_cand}")
        print(f"  remaining days: {rem}")
        print(f"  projected remaining at median: {rem * median / 3600:.1f}h")
        print(f"  projected remaining at p90:    {rem * p90 / 3600:.1f}h")
        # Trend: are early days faster than later days? (cache warmup)
        early_30 = deltas[:30] if len(deltas) >= 30 else deltas
        late_30 = deltas[-30:] if len(deltas) >= 30 else deltas
        print(f"  first-30 days avg: {sum(early_30)/len(early_30):.1f}s")
        print(f"  last-30 days avg:  {sum(late_30)/len(late_30):.1f}s")
        # Regime distribution observed
        from collections import Counter
        regimes = Counter(d[2] for d in days)
        print(f"  regimes processed: {dict(regimes)}")


if __name__ == "__main__":
    main()
