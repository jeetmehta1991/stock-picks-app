#!/usr/bin/env python
"""B2521 (S6-B2520m): what is a grid artifact's POPULATION, and what is it called?

A renderer that infers a denominator from a field NAME is right for the shape it
was written against and silently wrong for the next one. MEASURED: three
consumers each asked `"per_exit" in grid` or read `results` directly; on a
single-combination institutional grid two of them rendered "1 combination, 0
starved" - true, and uninformative, because the evidence-bearing denominator
there is the 24 EXITS, not the 1 combination.

The council's First Principles lens: have the artifact declare its own
population and have every consumer read the declaration. This helper IS that
declaration - one place to change when a third grid shape appears, and it
reports the FIELD NAME so a renderer can say what it counted (L717: a claim
must carry its own denominator).

HAND-RUN as a script prints the population of every grid on disk.
"""
from __future__ import annotations


def grid_population(grid: dict) -> tuple[list, str, str]:
    """Return (rows, field_name, unit) for a graded grid artifact.

    A grid whose combinations were consumed by a precompute carries ONE result
    row (the combination and its verdict) and ranks the EXITS inside it; a
    multi-combination grid ranks OUTCOME CLASSES over its enumerated rows.
    `per_exit` is the discriminator because only the single-combination grader
    emits it - checked here once instead of at every call site.
    """
    if not isinstance(grid, dict):
        return [], "results", "rows"
    if isinstance(grid.get("per_exit"), list) and grid["per_exit"]:
        return grid["per_exit"], "per_exit", "exits"
    return (grid.get("results") or []), "results", "combinations"


def population_note(grid: dict) -> str:
    """One clause naming the population and its source field, for a report."""
    rows, field, unit = grid_population(grid)
    return f"{len(rows)} {unit} (population field `{field}`)"


def main() -> int:
    import json
    from pathlib import Path as _P
    audit = _P(__file__).resolve().parents[1] / "output_audit"
    n = 0
    for p in sorted(audit.glob("output_*_grid_auto.json")):
        try:
            g = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"  {p.name}: UNREADABLE ({exc})")
            continue
        rows, field, unit = grid_population(g)
        n += 1
        print(f"  {p.name:52s} {len(rows):>5d} {unit:14s} <- {field}")
    print(f"{n} grid artifact(s)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
