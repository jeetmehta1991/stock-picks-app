"""scripts/build_dei_shares_store.py - S6-B3139bd (owner ruling 2026-10-06,
packet row 22 'source-dated'): the DATED share count short_interest_pct
divides by.

Builds data_prefetch/sec_xbrl/dei_shares_outstanding.parquet - one row per
SEC fact of dei:EntityCommonStockSharesOutstanding (the cover-page count a
10-K / 10-Q states), columns ticker / end (the count's as-of date) / filed
(the filing date, when the count became public) / val / form / accn - for
every ticker in the FINRA short-interest cache. The producer
(backtest/signals/short_interest.py dated_shares_outstanding) uses the
latest fact FILED on or before a settlement date; a ticker with no such
fact gets no short_interest_pct (excluded from the share-dependent layer,
never imputed from today's count).

SEC's companyconcept endpoint is read with the project's configured contact
(scripts/prefetch_sec_xbrl.HEADERS) at its rate limit, ONE call per ticker,
cached as raw JSON in --cache-dir so a rebuild re-fetches nothing. This is a
prefetch script: the backtest itself never calls SEC (DEC-497).

  python scripts/build_dei_shares_store.py --cache-dir <dir> [--fetch]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
SI_DIR = ROOT / "data_prefetch" / "finra" / "short_interest"
OUT = ROOT / "data_prefetch" / "sec_xbrl" / "dei_shares_outstanding.parquet"
URL = ("https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}"
       "/dei/EntityCommonStockSharesOutstanding.json")


def _facts(body: dict, ticker: str) -> list[dict]:
    out = []
    for f in ((body.get("units") or {}).get("shares")) or []:
        if f.get("end") and f.get("filed") and f.get("val") is not None:
            out.append({"ticker": ticker, "end": f["end"], "filed": f["filed"],
                        "val": float(f["val"]), "form": f.get("form"),
                        "accn": f.get("accn")})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--cache-dir", required=True, type=Path,
                    help="raw companyconcept JSON cache (one file per ticker)")
    ap.add_argument("--fetch", action="store_true",
                    help="fetch tickers missing from the cache from SEC")
    a = ap.parse_args(argv)
    a.cache_dir.mkdir(parents=True, exist_ok=True)
    tickers = sorted(p.stem for p in SI_DIR.glob("*.parquet"))
    status = {"cached": 0, "fetched": 0, "no_cik": 0, "http_not_200": 0}
    cik = None
    rows = []
    for t in tickers:
        cp = a.cache_dir / f"{t}.json"
        if not cp.exists():
            if not a.fetch:
                continue
            if cik is None:
                import prefetch_sec_xbrl as px
                import requests
                cik = px.load_cik_map()
            c = cik.get(t)
            if not c:
                status["no_cik"] += 1
                continue
            r = requests.get(URL.format(cik=str(c).zfill(10)), headers=px.HEADERS, timeout=30)
            time.sleep(px.RATE_LIMIT_SLEEP)
            body = r.json() if r.status_code == 200 else {}
            body["_status"] = r.status_code
            cp.write_text(json.dumps(body), encoding="utf-8")
            status["fetched"] += 1
        else:
            status["cached"] += 1
        body = json.loads(cp.read_text(encoding="utf-8"))
        if body.get("_status", 200) != 200:
            status["http_not_200"] += 1
            continue
        rows.extend(_facts(body, t))
    df = pd.DataFrame(rows, columns=["ticker", "end", "filed", "val", "form", "accn"])
    df = df.drop_duplicates().sort_values(["ticker", "end", "filed"]).reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT, index=False)
    print(f"SI tickers {len(tickers)} | {status} | tickers in store {df.ticker.nunique()} | "
          f"facts {len(df)} -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
