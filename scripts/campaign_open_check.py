#!/usr/bin/env python
"""S6-B3402 (B3139q-r216, on the owner's 'Address and impletement all open
tickets' 2026-11-16; the ticket's trigger fired when 15 campaign-open records
were written under S6-B3435 (a)): the three campaign-open rules of S6-B3344's
M-OPEN cluster, run over EVERY record of output_audit/owner_campaign_opens.json
as a DISCLOSURE, never a refusal.

The rules (runbook census lines 535, 891, 1062): a family pre-gate (overlap,
band clustering, median-exit holdout beside the best) before a campaign opens;
a W-T entrant is NOT-STARTED or STALLED-CAMPAIGN with stream TIGHTEN or BOTH; a
W-L entrant the same with stream LOOSEN or BOTH. MEASURED at B3139q-r216 on the
24 records then on the register: 3 family pre-gate artifacts exist (pead, xs,
smc) and the smc one lists the register's 5 smc opens among its members, so
19 of 24 opens have none; 0 of 24 name a W-T or W-L lane in their role - band
and launch words under S6-B3249, S6-B3423 and the LEVER4 programme, and the
S6-B3232 shortlist opens - so the lane entry rules cannot be checked from
them. A pre-gate refusal would fire on 19 of 24 (L721: tightening over a
backlog), so this reports, per record and in summary; whether an open owes
a family pre-gate is the owner's question (S6-B3402a). Written by
build_strategy_status on every build, so the disclosure moves with the view.

Output: output_audit/campaign_open_check.json. `check` is pure (the test seam).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIEW = ROOT / "output_audit" / "strategy_optimisation_status.json"
OUT = ROOT / "output_audit" / "campaign_open_check.json"
# a family pre-gate artifact is found by STRUCTURE: an output_audit JSON whose name holds
# "pregate" and whose body carries a `members` dict - b2633_pead_pregate.json,
# b2667_xs_family_pregate.json and b2690_smc_pregate.json share it; a narrower name
# pattern found 1 of the 3 (L687)
PREGATE_GLOB = "*pregate*.json"
# the lane a record declares in its role, and the streams that lane admits
LANE_STREAMS = {"W-T": ("TIGHTEN", "BOTH"), "W-L": ("LOOSEN", "BOTH")}
ENTRY_STATUSES = ("NOT-STARTED", "STALLED-CAMPAIGN")
# an open makes its strategy IN-CAMPAIGN in the view, so an entrant read after its open
# carries that status; any other status was not an entrant (explicit, never a substring)
ENTERED_STATUSES = ENTRY_STATUSES + ("IN-CAMPAIGN",)
RULES = {
    "census_535": "a family pre-gate (overlap, band clustering, median-exit holdout beside the best) "
                  "runs before a campaign opens - read here as a *family_pregate*.json artifact "
                  "naming the family or the strategy",
    "census_891": "a W-T entrant is NOT-STARTED or STALLED-CAMPAIGN with stream TIGHTEN or BOTH",
    "census_1062": "a W-L entrant is NOT-STARTED or STALLED-CAMPAIGN with stream LOOSEN or BOTH",
}


def pregate_members(root=ROOT) -> dict:
    """{artifact name: the strategies its `members` dict names}, for every
    output_audit JSON matching PREGATE_GLOB whose body carries one; a file
    that does not parse, or carries no `members` dict, is not a pre-gate."""
    out = {}
    for f in sorted((Path(root) / "output_audit").glob(PREGATE_GLOB)):
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        mem = doc.get("members") if isinstance(doc, dict) else None
        if isinstance(mem, dict):
            out[f.name] = set(mem)
    return out


def pregate_artifacts(root=ROOT) -> list:
    """Every family pre-gate artifact under output_audit, by name."""
    return sorted(pregate_members(root))


def lane_of(role: str) -> str:
    """W-T / W-L when the record's role names a lane, else UNDECLARED - the
    record names no lane, so the lane entry rule cannot be checked from it."""
    r = str(role or "")
    if "W-T" in r:
        return "W-T"
    if "W-L" in r:
        return "W-L"
    return "UNDECLARED"


def check(opens: dict, rows_by_strategy: dict, artifacts: list, members=None) -> dict:
    """The disclosure over `opens` ({strategy: record}, load_campaign_opens's
    shape) against the view rows and the pre-gate artifacts: an artifact
    whose `members` (pregate_members) names the strategy counts first, else
    one whose file name names the strategy or its family. Pure."""
    members = members or {}
    records = []
    for s in sorted(opens):
        rec = opens[s]
        row = rows_by_strategy.get(s) or {}
        fam = row.get("family")
        by_member = [a for a in artifacts if s in members.get(a, ())]
        by_name = [a for a in artifacts if a not in by_member
                   and (s.lower() in a.lower() or (fam and f"_{str(fam).lower()}_" in a.lower()))]
        hits = by_member + by_name
        lane = lane_of(rec.get("role"))
        status, stream = row.get("status"), row.get("stream")
        if lane == "UNDECLARED":
            entry = None
        else:
            entry = status in ENTERED_STATUSES and stream in LANE_STREAMS[lane]
        findings = []
        if not hits:
            findings.append("no family pre-gate artifact names this family or strategy (census 535)")
        elif not by_member:
            findings.append("a pre-gate names the family but not this strategy among its members - "
                            "credited by name only; the pre-gate did not measure it (census 535)")
        if entry is False:
            findings.append(f"the {lane} entry rule is not met by status {status} / stream {stream} "
                            f"(census {'891' if lane == 'W-T' else '1062'})")
        if lane == "UNDECLARED":
            findings.append("the record names no W-T / W-L lane, so the lane entry rule "
                            "cannot be checked from it; whether such an open owes a family "
                            "pre-gate is the owner's question")
        records.append({"strategy": s, "opened": rec.get("opened"), "tickets": list(rec.get("tickets") or []),
                        "role": str(rec.get("role") or "")[:120], "family": fam,
                        "family_pregate_artifacts": hits, "pregate_by_membership": by_member,
                        "pregate_by_name_only": by_name, "status_now": status, "stream_now": stream,
                        "lane_declared": lane, "lane_entry_rule_met": entry, "findings": findings})
    summary = {
        "opens": len(records),
        "without_family_pregate": sum(1 for r in records if not r["family_pregate_artifacts"]),
        "pregate_by_name_only": sum(1 for r in records if r["pregate_by_name_only"]
                                    and not r["pregate_by_membership"]),
        "lane_entry_rule_unmet": sum(1 for r in records if r["lane_entry_rule_met"] is False),
        "lane_undeclared": sum(1 for r in records if r["lane_declared"] == "UNDECLARED"),
        "pregate_artifacts_in_repo": len(artifacts),
    }
    return {"ticket": "S6-B3402", "mode": "DISCLOSURE - never a refusal (L721)", "rules": RULES,
            "summary": summary, "pregate_artifacts": sorted(artifacts), "records": records}


def run(root=ROOT, view=None, out=None) -> dict:
    """Load the register and the view, write the disclosure, return it."""
    root = Path(root)
    from build_strategy_status import load_campaign_opens   # a sibling in scripts/
    opens = load_campaign_opens(root)
    view_p = Path(view) if view is not None else root / "output_audit" / "strategy_optimisation_status.json"
    sv = json.loads(view_p.read_text(encoding="utf-8"))
    rows = {r.get("strategy"): r for r in sv.get("rows") or []}
    members = pregate_members(root)
    doc = check(opens, rows, sorted(members), members)
    doc["view_build"] = sv.get("build")
    out_p = Path(out) if out is not None else root / "output_audit" / "campaign_open_check.json"
    out_p.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return doc


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="S6-B3402: disclose, per campaign-open record, the family pre-gate naming it and "
                    "its lane entry rule; writes output_audit/campaign_open_check.json")
    ap.add_argument("--view", default=None,
                    help="the status view (default output_audit/strategy_optimisation_status.json)")
    ap.add_argument("--out", default=None,
                    help="the disclosure to write (default output_audit/campaign_open_check.json)")
    a = ap.parse_args(argv)
    doc = run(view=a.view, out=a.out)
    s = doc["summary"]
    print(f"campaign_open_check (S6-B3402, disclosure): {s['opens']} opens; "
          f"{s['without_family_pregate']} without a family pre-gate artifact "
          f"({s['pregate_artifacts_in_repo']} such artifact(s) in the repo); "
          f"{s['lane_entry_rule_unmet']} W-T/W-L opens not meeting their entry rule; "
          f"{s['lane_undeclared']} naming no W-T / W-L lane -> {OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
