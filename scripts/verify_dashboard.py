"""scripts/verify_dashboard.py (B1354, Council 373) -- the gate the dashboard
error-streak needed. The pyramid tests the ENGINE, not rendered deliverables;
8 dashboard bugs (missing app.js -> stuck loading, 404, empty tabs, wrong
labels) all sailed through because nothing verified the ARTIFACT. This checks a
dashboard dir the way a browser would:

  1. ASSET COMPLETENESS: every local (non-CDN) src/href in index.html exists in
     the dir (catches the missing-app.js class -> stuck "loading").
  2. DATA PRESENCE: data.js is a non-empty valid JS assignment; data.json parses
     and >=1 declared data section is non-empty (catches all-empty-tabs).
  3. (optional) LIVE RENDER: --url fetches the deployed page + each asset and
     asserts HTTP 200 (catches the Pages 404 / undeployed-asset class).

Usage:
  python scripts/verify_dashboard.py --dir dashboard_r5_cube
  python scripts/verify_dashboard.py --dir dashboard_r5_cube --url https://.../dashboard_r5_cube/
Exit 0 = ok; exit 3 = broken (do NOT tell the owner it's live).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def local_assets(index_html: str) -> list[str]:
    return sorted(set(re.findall(r'(?:src|href)="(?!https?://)([^"]+)"', index_html)))


def check_forbidden_tokens(index_html: str, forbid: list[str]) -> list[str]:
    """2026-07-24 (B1363): the STATIC-PROSE-STALENESS gate. The dashboard
    generator writes only data.js/data.json - it NEVER rewrites index.html.
    So a dashboard cloned from a prior round's template carries that round's
    hardcoded prose (ticker counts, strategy counts, exit counts, source dirs,
    OOS numbers) which survives every data regen AND passes the asset/data/
    banner checks. This gate scans the RENDERED index.html for caller-supplied
    forbidden substrings (prior-round tokens) and FAILS if any appear -- so a
    green from this script actually means content-current, not just structurally
    present. Class fix for the R4-prose-in-R5-dashboard miss."""
    fails = []
    for tok in forbid:
        tok = tok.strip()
        if tok and tok in index_html:
            fails.append(f"forbidden stale token in index.html: {tok!r} "
                         "(prior-round prose survived a data-only regen; "
                         "static index.html must be updated for this round)")
    return fails


def check_dir(d: Path, forbid: list[str] | None = None) -> list[str]:
    fails = []
    idx = d / "index.html"
    if not idx.exists():
        return [f"{d}/index.html missing"]
    idx_html = idx.read_text(encoding="utf-8")
    if forbid:
        fails += check_forbidden_tokens(idx_html, forbid)
    assets = local_assets(idx_html)
    for a in assets:
        if not (d / a).exists():
            fails.append(f"referenced local asset MISSING: {a} (page will not render)")
    dj = d / "data.js"
    if dj.exists():
        txt = dj.read_text(encoding="utf-8")
        if "=" not in txt or len(txt) < 50:
            fails.append("data.js present but not a valid non-empty JS assignment")
    djson = d / "data.json"
    if djson.exists():
        try:
            data = json.loads(djson.read_text(encoding="utf-8"))
            nonempty = [k for k, v in data.items()
                        if isinstance(v, (list, dict)) and len(v) > 0]
            if not nonempty:
                fails.append("data.json parses but EVERY section is empty (all tabs blank)")
            # B1355: content-correctness -- a data-driven header/round banner must
            # resolve to POPULATED metadata for the current round, else the page
            # shows a stale/empty banner (the R3-banner class: right data, wrong
            # round shown). Catches "shows the wrong dataset", not just "renders".
            cur = data.get("current_round")
            if cur is not None:
                ir = data.get("iteration_rounds", [])
                meta = next((r for r in ir if r.get("id") == cur), None)
                if meta is None:
                    fails.append(f"current_round={cur} but no matching iteration_rounds entry "
                                 "(banner will render empty/stale)")
                else:
                    blank = [f for f in ("label", "date_completed", "trades_total",
                                         "n_strategies_fired") if not meta.get(f)]
                    if blank:
                        fails.append(f"current_round={cur} banner metadata blank: {blank} "
                                     "(register the round in archive/cube_rounds/rounds.json)")
        except Exception as exc:
            fails.append(f"data.json does not parse: {exc}")
    return fails


def check_live(url: str, assets: list[str]) -> list[str]:
    import urllib.request
    fails = []
    base = url if url.endswith("/") else url + "/"
    for path in ["", *assets]:
        u = base + path
        try:
            req = urllib.request.Request(u, method="GET")
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status != 200:
                    fails.append(f"{u} -> HTTP {r.status}")
        except Exception as exc:
            fails.append(f"{u} -> {exc}")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--url", default=None, help="deployed base URL for a live render check")
    ap.add_argument("--forbid", default="",
                    help="SEMICOLON-separated prior-round tokens that must NOT appear "
                         "in index.html (B1363 static-prose-staleness gate); "
                         "semicolon delimiter so tokens may contain commas, e.g. '1,531 tickers'")
    args = ap.parse_args()
    d = Path(args.dir)
    forbid = [t for t in args.forbid.split(";") if t.strip()] if args.forbid else []
    fails = check_dir(d, forbid=forbid)
    if args.url:
        assets = local_assets((d / "index.html").read_text(encoding="utf-8")) if (d / "index.html").exists() else []
        fails += check_live(args.url, assets)
    if fails:
        print(f"DASHBOARD_VERIFY_FAIL ({d}):")
        for f in fails:
            print(f"  - {f}")
        return 3
    print(f"DASHBOARD_VERIFY_PASS: {d} has all local assets + non-empty data"
          + (" + live URL renders" if args.url else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
