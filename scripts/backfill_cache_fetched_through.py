"""B1564 -- stamp `fetched_through` onto pre-existing OHLCV index entries.

WHY THIS EXISTS
The index records `end` = the last OBSERVED bar. The coverage check needs the
last date we ASKED for. Those differ for any DELISTED ticker: ABMD's final bar
is its acquisition date and will precede every future window end forever, so an
`end`-only check marks it uncovered on every run (260 of 2,122 entries).

WHY A BACKFILL IS DEFENSIBLE HERE
The requested end was never persisted, so it cannot be recovered per-ticker.
But it CAN be inferred from the population: 1,861 of 2,122 entries share the
exact end date 2026-05-05, which is only explicable as one bulk prefetch's
requested end. (The MODE, not the max -- max is 2026-05-06 with a single
outlier entry.)

WHY IT RECORDS ITS OWN PROVENANCE
This is an INFERENCE about how the cache was built, not an observation. Every
value written here is tagged `fetched_through_source: "backfill_B1564"` so a
later reader can tell inferred metadata from values recorded at fetch time by
get_ohlcv. Entries whose observed `end` already equals or exceeds the modal
date are stamped too, but for them the value is merely redundant.

CONSERVATISM
An entry is stamped ONLY when its observed `end` is <= the modal date. An entry
ending AFTER the modal date was written by some later run whose requested end
we cannot infer, so it is left alone rather than guessed at.

Run with --dry-run first; it prints the exact mutation counts and changes
nothing.
"""
from __future__ import annotations

import argparse
import collections
import json
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def modal_end(index: dict) -> tuple[str, int, int]:
    """Return (modal_end_date, count_at_mode, total_with_end)."""
    ends = collections.Counter(
        m["end"] for m in index.values() if isinstance(m, dict) and m.get("end"))
    if not ends:
        return "", 0, 0
    d, n = ends.most_common(1)[0]
    return d, n, sum(ends.values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=None, help="path to index.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--min-mode-share", type=float, default=0.50,
                    help="refuse to backfill if the modal end date is not at "
                         "least this share of entries -- a diffuse "
                         "distribution means there was no single prefetch and "
                         "the inference is unsafe")
    a = ap.parse_args()

    idx_path = Path(a.index) if a.index else (
        REPO / "backtest" / "data" / "cache" / "index.json")
    if not idx_path.exists():
        print(f"index not found: {idx_path}")
        return 1

    index = json.loads(idx_path.read_text())
    mode, n_mode, n_total = modal_end(index)
    if not mode:
        print("no entries carry an 'end' -- nothing to do")
        return 1
    share = n_mode / n_total
    print(f"index entries with 'end': {n_total}")
    print(f"modal end date: {mode}  x{n_mode}  ({share:.1%} of entries)")

    # HARD GATE: the whole inference rests on one prefetch dominating the
    # population. If it does not, refuse rather than stamp a guess.
    if share < a.min_mode_share:
        print(f"REFUSING: modal share {share:.1%} < {a.min_mode_share:.0%}. "
              f"The end dates are too diffuse to infer a single requested end; "
              f"backfilling would fabricate provenance.")
        return 2

    mode_d = date.fromisoformat(mode)
    stamp = skip_have = skip_after = 0
    for t, m in index.items():
        if not isinstance(m, dict) or not m.get("end"):
            continue
        if m.get("fetched_through"):
            skip_have += 1
            continue
        if date.fromisoformat(m["end"]) > mode_d:
            # written by a later run; its requested end is unknowable
            skip_after += 1
            continue
        if not a.dry_run:
            m["fetched_through"] = mode
            m["fetched_through_source"] = "backfill_B1564"
        stamp += 1

    print(f"\n  would stamp        : {stamp}")
    print(f"  already had value  : {skip_have}")
    print(f"  end > mode (skip)  : {skip_after}")

    if a.dry_run:
        print("\nDRY RUN -- index not modified")
        return 0

    backup = idx_path.with_suffix(".json.pre_b1564")
    if not backup.exists():
        backup.write_text(json.dumps(json.loads(idx_path.read_text()), indent=2))
        print(f"\nbackup written: {backup}")
    idx_path.write_text(json.dumps(index, default=str, indent=2))
    print(f"index updated: {idx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
