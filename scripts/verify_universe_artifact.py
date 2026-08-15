"""B1572 -- MECHANICAL guard against the wrong-artifact class (L445).

THE FAILURE THIS EXISTS TO PREVENT
The runbook rule said "derive the universe from the BASELINE ARTIFACT, not a
roster CSV" (L378). It was followed - to `output_audit/r5_universe_381.txt`,
which was derived from `output_r5_rung4_chunk1`: an ABANDONED, alphabetically
partitioned rung-4 chunk. 380 of its 381 tickers start with A, B or C. The real
R5 baseline is `output_r5_merged_1_7` with 544 tickers, 25pct A-C, containing
MSFT / NVDA / GOOGL / META / TSLA - none of which are in the 381. Overlap
between the two is 133; the 381 holds 248 tickers R5 never ran.

A rule that says "use the artifact" does not say "use the RIGHT artifact", and
381-vs-544 is not a discrepancy anyone notices by reading a filename.

WHAT THIS CHECKS (each is a real, separate way the class bites)
  1. ALPHABETICAL SKEW - a ticker-partitioned chunk masquerading as a universe.
  2. MEGA-CAP ABSENCE - a US equity universe without the largest names is a
     slice, whatever its size. This is the check that would have caught B1571
     in one second.
  3. LETTER COVERAGE - how much of A-Z is represented.
  4. PROVENANCE - the artifact must name the cube it came from.

Exit 0 = looks like a universe. Exit 1 = looks like a slice. Non-blocking by
design: it reports loudly and the human decides, because a legitimately narrow
universe (sector study, single-tier run) must stay possible.
"""
from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Largest US names by weight. Absence of nearly all of these from a broad-market
# universe is the single loudest signal that it is a slice.
MEGA_CAPS = ["MSFT", "NVDA", "AAPL", "GOOGL", "AMZN", "META", "AVGO", "TSLA",
             "LLY", "JPM", "V", "UNH", "XOM", "WMT", "JNJ", "PG", "MA", "HD"]

SKEW_MAX = 0.60      # >60pct of tickers in <=3 leading letters == partitioned
MEGA_MIN = 0.30      # <30pct of mega-caps present == slice
LETTERS_MIN = 12     # fewer than 12 distinct leading letters == narrow


def load(path: Path) -> list[str]:
    txt = path.read_text(encoding="utf-8", errors="ignore")
    return [t.strip().upper() for t in txt.split() if t.strip()]


def audit(tickers: list[str], label: str) -> list[str]:
    fails: list[str] = []
    n = len(tickers)
    if n == 0:
        return [f"{label}: EMPTY"]

    letters = collections.Counter(t[0] for t in tickers if t and t[0].isalpha())
    top3 = sum(c for _, c in letters.most_common(3))
    skew = top3 / n
    present = [m for m in MEGA_CAPS if m in set(tickers)]
    mega_share = len(present) / len(MEGA_CAPS)

    print(f"  tickers            : {n}")
    print(f"  distinct letters   : {len(letters)}")
    print(f"  top-3 letter share : {skew:.0%}  ({[l for l, _ in letters.most_common(3)]})")
    print(f"  mega-caps present  : {len(present)}/{len(MEGA_CAPS)} ({mega_share:.0%})")
    print(f"  missing mega-caps  : {[m for m in MEGA_CAPS if m not in set(tickers)][:8]}")

    if skew > SKEW_MAX:
        fails.append(
            f"ALPHABETICAL SKEW: {skew:.0%} of tickers share the top 3 leading "
            f"letters (limit {SKEW_MAX:.0%}). This looks like a ticker-"
            f"PARTITIONED CHUNK, not a universe.")
    if mega_share < MEGA_MIN:
        fails.append(
            f"MEGA-CAP ABSENCE: only {len(present)}/{len(MEGA_CAPS)} mega-caps "
            f"present ({mega_share:.0%}, limit {MEGA_MIN:.0%}). A US equity "
            f"universe without the largest names is a SLICE.")
    if len(letters) < LETTERS_MIN:
        fails.append(
            f"NARROW COVERAGE: only {len(letters)} distinct leading letters "
            f"(limit {LETTERS_MIN}).")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("universe", help="newline-separated ticker file")
    ap.add_argument("--compare-cube", default=None,
                    help="cube CSV whose ticker column is the TRUE baseline")
    a = ap.parse_args()

    path = Path(a.universe)
    if not path.is_absolute():
        path = REPO / path
    if not path.exists():
        print(f"universe file not found: {path}")
        return 2

    tickers = load(path)
    print(f"\nAUDIT: {path.name}")
    fails = audit(tickers, path.name)

    if a.compare_cube:
        import pandas as pd
        cp = Path(a.compare_cube)
        if not cp.is_absolute():
            cp = REPO / cp
        cube = set(pd.read_csv(cp, low_memory=False, usecols=["ticker"])
                   .ticker.astype(str).str.upper().unique())
        ts = set(tickers)
        print(f"\n  baseline cube      : {cp.parent.name} ({len(cube)} tickers)")
        print(f"  overlap            : {len(ts & cube)}")
        print(f"  in file, NOT cube  : {len(ts - cube)}")
        print(f"  in cube, NOT file  : {len(cube - ts)}")
        if ts - cube:
            fails.append(
                f"PROVENANCE MISMATCH: {len(ts - cube)} tickers are in the "
                f"universe file but were NEVER RUN in the baseline cube. The "
                f"file was derived from a DIFFERENT artifact.")

    print()
    if fails:
        print(f"VERDICT: SLICE / SUSPECT - {len(fails)} finding(s)")
        for f in fails:
            print(f"  ! {f}")
        print("\nIf a narrow universe is INTENTIONAL, say so explicitly in the "
              "doc that consumes it. Otherwise rebuild from the merged cube.")
        return 1
    print("VERDICT: looks like a broad universe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
