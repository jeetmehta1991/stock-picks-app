#!/usr/bin/env python
"""S6-B3155a (owner ruling 2026-10-14, verbatim "S6-B3155a b"): repair the
engine cache's final bar where a third source confirmed it was a partial
session - for runs launched after the repair; frozen results unchanged.

WHAT IT WRITES. For each CONFIRMED row of the evidence artifact written by
scripts/final_bar_third_source_check.py classify - or each row its
`provenance` subcommand writes on an owner ruling (S6-B3155b) - ONE row of one file under
backtest/data/cache/ohlcv: the bar dated the evidence's `date`, which must be
the file's LAST row. Its open/high/low/close/volume become the PREFETCH
cache's bar for that date (data_prefetch/polygon/ohlcv_daily - the cache's own
vendor, Polygon). The third source only adjudicates; its values are never
written. No row is added or removed, so backtest/data/cache/index.json
(start/end/rows) stays true and is not touched.

RULES
- DRY-RUN BY DEFAULT; --apply writes.
- FAIL CLOSED, ALL OR NOTHING: every precondition is checked for every row
  before the first write - the engine bar must still equal the evidence's
  engine_before EXACTLY (else the cache moved since the read) and the
  prefetch bar must still equal the evidence's prefetch values EXACTLY (else
  the repair source moved). Any refusal: nothing is written, exit 2.
- CONTINUITY, PER ROW (B3139q-r69n): the bar before the final bar must already equal
  the prefetch's bar for the evidence's `prior` date, or a one-row repair
  splices two price bases (CVNA's 5.0x scale became a fake -80% day before
  this check existed; it was restored from git and is recorded as reverted).
- AN INTEGER COLUMN gets the nearest whole share (target_value): pyarrow
  would otherwise truncate silently.
- ONE ROW CHANGES: each new file is read back and compared with the old one
  - every other row identical in every column, the schema and its metadata
  identical, the repaired row equal to the prefetch bar - before it replaces
  the old file (temp file + os.replace).
- IDEMPOTENT: a bar already holding its repaired value is skipped, and the log
  is merged across runs; a logged repair the evidence no longer supports is
  recorded as reverted only if its file is back to its pre-repair bytes.
- The old bars stay recoverable from git history (the cache is tracked); the
  log records both values and both file hashes per ticker.

usage:
  python scripts/repair_final_bar_partial_session.py            # dry run
  python scripts/repair_final_bar_partial_session.py --apply
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if not (ROOT / "EXECUTION_QUEUE.md").is_file():          # L846 marker rule
    raise SystemExit(f"repair_final_bar_partial_session: {ROOT} is not the repo root (L846)")

FIELDS = ("open", "high", "low", "close", "volume")
EVIDENCE = "output_audit/b3155a_final_bar_third_source.json"
LOG = "output_audit/b3155a_final_bar_repair_log.json"
RULING = "S6-B3155a b"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


SAME_REL = 1e-6   # one vendor's bar held in two files: float noise only - the
                  # classifier's IDENTICAL_REL (final_bar_third_source_check)


def _same(a: dict, b: dict) -> bool:
    return all((a[f] == b[f]) if b[f] == 0 else abs(a[f] / b[f] - 1.0) <= SAME_REL
               for f in FIELDS)


def _relpath(p: Path) -> str:
    """Repo-relative when under the repo (the evidence's own form), else the
    absolute path (the pin test's temp files)."""
    try:
        return str(p.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(p)


def _bar_of(table, i: int) -> dict:
    return {f: float(table.column(f)[i].as_py()) for f in FIELDS}


def _final_index(table, date: str) -> int:
    import pandas as pd
    dates = pd.to_datetime(table.column("date").to_pandas()).dt.normalize()
    hits = [int(k) for k in (dates == pd.Timestamp(date)).to_numpy().nonzero()[0]]
    if len(hits) != 1:
        raise ValueError(f"{len(hits)} rows dated {date}")
    if hits[0] != table.num_rows - 1:
        raise ValueError(f"the {date} row is row {hits[0]}, not the last row "
                         f"({table.num_rows - 1}) - this repair touches a FINAL bar only")
    return hits[0]


def _prefetch_bar(path: Path, date: str):
    import pandas as pd
    p = pd.read_parquet(path)
    p["date"] = pd.to_datetime(p["date"]).dt.normalize()
    r = p[p["date"] == pd.Timestamp(date)]
    if len(r) != 1:
        return None
    return {f: float(r[f].iloc[0]) for f in FIELDS}


def target_value(value: float, arrow_type) -> float:
    """The prefetch value as the target COLUMN stores it. An integer column
    (VXX's volume is int64, 1 of 494 files at B3139q-r69n) stores whole shares:
    the nearest integer, because pa.array would otherwise TRUNCATE silently
    (MEASURED: 6213415.903644 written as 6213415 - caught by the read-back,
    never by the schema check). A float column stores the value unchanged."""
    import pyarrow as pa
    if pa.types.is_integer(arrow_type):
        return float(round(value))
    return value


def plan(evidence: dict) -> tuple[list, list, list]:
    """(planned, already, refusals): every check, no writes. A bar that
    already holds its repaired value is ALREADY (idempotent re-run); one that
    holds neither the evidence's before nor the repaired value is refused."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    date = evidence["date"]
    planned, already, refusals = [], [], []
    for row in evidence["repair"]:
        t = row["ticker"]
        ef, pf = ROOT / row["engine_file"], ROOT / row["prefetch_file"]
        if not ef.is_file() or not pf.is_file():
            refusals.append(f"{t}: file missing ({ef.is_file()=}, {pf.is_file()=})")
            continue
        old = pq.read_table(ef)
        try:
            i = _final_index(old, date)
        except ValueError as exc:
            refusals.append(f"{t}: {exc}")
            continue
        now = _bar_of(old, i)
        src = _prefetch_bar(pf, date)
        if src != row["prefetch"]:
            refusals.append(f"{t}: prefetch bar moved since the evidence read - now {src}, "
                            f"evidence {row['prefetch']}")
            continue
        want = {f: target_value(src[f], old.column(f).type) for f in FIELDS}
        # Continuity (B3139q-r69n): the bar BEFORE the final bar must already be on
        # the prefetch's basis, or a one-row repair splices two price bases
        # (CVNA: a 5.0x scale on every earlier bar became a fake -80% day).
        prev = _prefetch_bar(pf, evidence["prior"])
        if i == 0 or prev is None or not _same(_bar_of(old, i - 1), prev):
            refusals.append(f"{t}: the {evidence['prior']} bar differs between the caches "
                            f"(engine {_bar_of(old, i - 1) if i else None}, prefetch {prev}) "
                            "- a one-row repair would splice two price bases")
            continue
        if now == want:
            already.append(t)
            continue
        if now != row["engine_before"]:
            refusals.append(f"{t}: engine bar moved since the evidence read - now {now}, "
                            f"evidence {row['engine_before']}")
            continue
        new = old
        for f in FIELDS:
            vals = new.column(f).to_pylist()
            vals[i] = (int(want[f]) if pa.types.is_integer(new.column(f).type) else want[f])
            k = new.schema.get_field_index(f)
            new = new.set_column(k, new.schema.field(f), pa.array(vals, type=new.column(f).type))
        if new.schema != old.schema or new.schema.metadata != old.schema.metadata:
            refusals.append(f"{t}: the rebuilt table's schema or metadata differs")
            continue
        if _bar_of(new, i) != want:
            refusals.append(f"{t}: the rebuilt row is {_bar_of(new, i)}, not {want}")
            continue
        codec = pq.ParquetFile(ef).metadata.row_group(0).column(0).compression.lower()
        planned.append({"ticker": t, "file": ef, "index": i, "old": old, "new": new,
                        "before": now, "after": want, "prefetch": src, "codec": codec,
                        "shape": row["shape"]})
    return planned, already, refusals


def verify(path: Path, p: dict) -> list:
    """Read a written file back and compare it with the old table."""
    import pandas as pd
    import pyarrow.parquet as pq
    got = pq.read_table(path)
    bad = []
    if got.schema != p["old"].schema or got.schema.metadata != p["old"].schema.metadata:
        bad.append("schema or metadata changed")
    if got.num_rows != p["old"].num_rows:
        bad.append(f"rows {got.num_rows} != {p['old'].num_rows}")
        return bad
    g, o = got.to_pandas(), p["old"].to_pandas()
    i = p["index"]
    keep = [k for k in range(len(o)) if k != i]
    if not g.iloc[keep].reset_index(drop=True).equals(o.iloc[keep].reset_index(drop=True)):
        bad.append("a row other than the final bar changed")
    if pd.Timestamp(g["date"].iloc[i]) != pd.Timestamp(o["date"].iloc[i]):
        bad.append("the final bar's date changed")
    if _bar_of(got, i) != p["after"]:
        bad.append(f"final bar {_bar_of(got, i)} != prefetch {p['after']}")
    return bad


def main(argv=None) -> int:
    import pyarrow.parquet as pq
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--evidence", default=EVIDENCE)
    ap.add_argument("--log", default=LOG)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    evidence = json.loads((ROOT / a.evidence).read_text(encoding="utf-8"))
    # S6-B3155b: the log records the authority the EVIDENCE carries. An
    # evidence for any other ticket must name its owner ruling, or the log
    # would credit S6-B3155a's ruling with a repair that ruling never covered.
    ticket = evidence.get("ticket", "S6-B3155a")
    auth = evidence.get("authority")
    if auth is None and ticket != "S6-B3155a":
        print(f"REFUSED: the {ticket} evidence names no owner authority; nothing written")
        return 2
    ruling = (auth or {}).get("ruling_verbatim", RULING)
    ruled = (auth or {}).get("ruled", "2026-10-14")
    planned, already, refusals = plan(evidence)
    print(f"evidence {a.evidence}: {len(evidence['repair'])} confirmed rows; "
          f"{len(planned)} planned, {len(already)} already repaired, "
          f"{len(refusals)} refused")
    for r in refusals[:20]:
        print("  REFUSED", r)
    if refusals:
        print("nothing written (all or nothing)")
        return 2
    if not a.apply:
        print("DRY RUN - pass --apply to write")
        return 0
    log_path = ROOT / a.log
    prior_log = (json.loads(log_path.read_text(encoding="utf-8"))
                 if log_path.is_file() else {})
    kept = {e["ticker"]: e for e in prior_log.get("entries", [])}
    # An applied repair the evidence no longer supports: recorded as REVERTED
    # when its file is back to the recorded pre-repair bytes, refused otherwise
    # (B3139q-r69n: CVNA was repaired, then dropped from the evidence by the
    # per-ticker prior-bar check and restored from git).
    in_evidence = {r["ticker"] for r in evidence["repair"]}
    reverted = list(prior_log.get("reverted") or [])
    for t in sorted(set(kept) - in_evidence):
        e = kept.pop(t)
        if _sha(ROOT / e["file"]) != e["sha256_before"]:
            print(f"REFUSED: {t} was repaired, is no longer in the evidence's repair "
                  "set, and its file is not back to its pre-repair bytes; nothing written")
            return 2
        reverted.append({**e, "reverted_check_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                                  time.gmtime()),
                         "reason": "no longer in the evidence's repair set; the file "
                                   "holds its pre-repair bytes again (sha256_before)"})
    missing_history = sorted(t for t in already if t not in kept)
    if missing_history:
        print(f"REFUSED: {len(missing_history)} bar(s) already hold their repaired "
              f"value but the log has no entry for them (first: {missing_history[:5]}) "
              "- a repair this log did not record; nothing written")
        return 2
    entries = []
    for p in planned:
        path = p["file"]
        sha_before = _sha(path)
        tmp = path.with_name(path.name + ".tmp_b3155a")
        pq.write_table(p["new"], tmp, compression=p["codec"])
        bad = verify(tmp, p)
        if bad:
            tmp.unlink()
            print(f"STOPPED at {p['ticker']}: {bad}; {len(entries)} file(s) already "
                  "replaced, listed in the log; the rest untouched")
            break
        os.replace(tmp, path)
        entry = {"ticker": p["ticker"],
                 "file": _relpath(path),
                 "shape": p["shape"], "before": p["before"], "after": p["after"],
                 "sha256_before": sha_before, "sha256_after": _sha(path)}
        if p["after"] != p["prefetch"]:
            entry["prefetch_value_as_read"] = p["prefetch"]
            entry["note"] = "integer column: the nearest whole share was written"
        entries.append(entry)
    run = {"applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "planned": len(planned), "already_repaired": len(already),
           "replaced": len(entries)}
    merged = dict(kept)
    merged.update({e["ticker"]: e for e in entries})
    log = {"ticket": ticket, "owner_ruling": ruling, "ruled": ruled,
           "evidence": a.evidence, "date": evidence["date"],
           "generator": "scripts/repair_final_bar_partial_session.py --apply",
           "runs": list(prior_log.get("runs") or (
               [{k: prior_log[k] for k in ("applied_at_utc", "planned", "replaced")
                 if k in prior_log}] if prior_log else [])) + [run],
           "replaced_total": len(merged),
           "entries": [merged[t] for t in sorted(merged)],
           "reverted": reverted}
    log_path.write_text(json.dumps(log, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"replaced {len(entries)} of {len(planned)} final bars this run; "
          f"{len(merged)} in the log -> {a.log}")
    return 0 if len(entries) == len(planned) else 3


if __name__ == "__main__":
    sys.exit(main())
