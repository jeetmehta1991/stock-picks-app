"""Batch 496 (2026-05-30) -- P17a SEC EDGAR XML/HTML extractor scaffold.

Source: per CHECKLIST #77 + #99 (schema-verify before producer ships).
Queue row: EXECUTION_QUEUE.md item P17a.

Pre-req for P17b/c/d/e (SC 13D activist / 8-K Item 1.01 M&A / 8-K Item
5.02 officer change / SC 13G passive flow). The current SEC EDGAR cache
under `data_prefetch/sec_edgar/{SC_13D, SC_13G, 8_K, 4}/<TICKER>.parquet`
has only the filing INDEX (ticker, cik, form, filing_date, accession_
number, primary_doc filename). The actual filing CONTENT (SC 13D filer
identity + % owned, 8-K item codes, etc.) lives in HTML/XBRL primary_doc
files referenced by URL.

This module:

  1. Builds the EDGAR URL from (cik, accession_number, primary_doc).
  2. Defines per-form extraction stubs:
       - SC 13D / 13G:  extract filer_identity + percent_owned + item_4_purpose
       - 8-K:           extract item_codes (1.01, 2.01, 5.02, 8.01, ...)
  3. Provides consumer signal helpers reading the DECODED cache
     `data_prefetch/sec_edgar_decoded/<form>/<TICKER>.parquet`
     (gracefully empty until extractor runs).

The actual network extraction (downloading ~6,056 filings * 2,000
tickers * 4 forms = ~48M XML files) is owner-gated and runs as a
separate batch job. This module is the wiring scaffold + the consumer
side.

URL pattern (EDGAR public):
  https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_no_dashes_removed}/{primary_doc}
where:
  cik_int: cik with leading zeros stripped (e.g. "0000320193" -> 320193)
  acc_no_dashes_removed: accession_number with hyphens stripped
                         (e.g. "0001193125-15-258464" -> "000119312515258464")
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

REPO = Path(__file__).resolve().parent.parent.parent
_INDEX_CACHE_DIR = REPO / "data_prefetch" / "sec_edgar"
_DECODED_CACHE_DIR = REPO / "data_prefetch" / "sec_edgar_decoded"


# ---------------------------------------------------------------------------
# URL construction
# ---------------------------------------------------------------------------

EDGAR_BASE = "https://www.sec.gov/Archives/edgar/data"


def build_edgar_filing_url(
    cik: str | int,
    accession_number: str,
    primary_doc: str,
) -> str:
    """Build the canonical EDGAR URL for a filing's primary document.

    EDGAR strips leading zeros from CIK and dashes from accession_number
    when forming the URL path.

    Raises ValueError on missing accession_number or primary_doc.
    """
    if not accession_number:
        raise ValueError("accession_number is required")
    if not primary_doc:
        raise ValueError("primary_doc is required")
    cik_int = int(str(cik).lstrip("0") or "0")
    acc_no_clean = str(accession_number).replace("-", "")
    return f"{EDGAR_BASE}/{cik_int}/{acc_no_clean}/{primary_doc}"


# ---------------------------------------------------------------------------
# Per-form parsing stubs (operate on raw HTML text; network-fetched by
# the batch extractor script under scripts/, not by this module)
# ---------------------------------------------------------------------------

# 8-K item codes (subset of the commonly-traded ones)
_KNOWN_8K_ITEMS = (
    "1.01", "1.02", "1.03",          # Material agreements
    "2.01", "2.02", "2.03", "2.05",  # Material results / restructure
    "4.01", "4.02",                  # Auditor / restatement
    "5.02", "5.03",                  # Officer / charter changes
    "7.01", "8.01",                  # Reg FD / other events
)


def extract_8k_item_codes(html_text: str) -> list[str]:
    """Find 8-K item codes mentioned in the primary_doc body.

    Per SEC 8-K cover page convention, items are referenced as
    "Item X.YY" where X.YY is one of the codes in 17 CFR 249.308.
    Returns the sorted unique list found.

    Tolerant to whitespace, em-dash separators, and Unicode item-code
    formatting variations.
    """
    if not html_text:
        return []
    pattern = re.compile(r"\bItem\s+([0-9]+\.[0-9]+)\b", re.IGNORECASE)
    found = set()
    for match in pattern.finditer(html_text):
        code = match.group(1)
        if code in _KNOWN_8K_ITEMS:
            found.add(code)
    return sorted(found)


def extract_sc_13d_fields(html_text: str) -> dict:
    """Extract activist 13D fields: filer_identity, percent_owned,
    item_4_purpose_text.

    EDGAR 13D filings have semi-structured cover pages. Filer identity
    is on the cover page bullet "NAMES OF REPORTING PERSONS". Percent
    owned appears as "PERCENT OF CLASS REPRESENTED BY AMOUNT". Item 4
    is the free-text purpose-of-transaction section.

    Returns empty values on parse failure (degrade quietly).
    """
    out = {
        "filer_identity":     "",
        "percent_owned":      None,
        "item_4_purpose":     "",
    }
    if not html_text:
        return out
    text = re.sub(r"<[^>]+>", " ", html_text)  # strip HTML tags

    # Filer identity bullet
    m = re.search(
        r"NAMES?\s+OF\s+REPORTING\s+PERSONS?[^\n\r]*[\n\r]+\s*([A-Za-z0-9 \.,&'\-]+?)(?=[\n\r])",
        text, re.IGNORECASE,
    )
    if m:
        out["filer_identity"] = m.group(1).strip()[:200]

    # Percent of class
    pm = re.search(
        r"PERCENT\s+OF\s+CLASS[^\d]*([0-9]+\.?[0-9]*)\s*%",
        text, re.IGNORECASE,
    )
    if pm:
        try:
            out["percent_owned"] = float(pm.group(1))
        except (ValueError, TypeError):
            pass

    # Item 4 purpose section (truncate to first 1000 chars to keep cache small)
    im = re.search(
        r"ITEM\s*4[\.\s]+(?:PURPOSE\s+OF\s+TRANSACTION|PURPOSE)\b(.{50,1000}?)(?=ITEM\s*5|$)",
        text, re.IGNORECASE | re.DOTALL,
    )
    if im:
        out["item_4_purpose"] = im.group(1).strip()[:1000]

    return out


# ---------------------------------------------------------------------------
# Consumer signal helpers (read the decoded cache)
# ---------------------------------------------------------------------------

# Batch 534 (2026-06-01) perf fix: cache decoded DataFrames in-memory
# keyed by (form, ticker). Prior implementation read the parquet from
# disk on every producer call -- with 4 producer calls per
# `compute_sec_edgar_signals` * 388 tickers * 1044 bars per R4 batch
# = ~1.6M disk reads. Cache eliminates repeat reads (first-touch fills
# cache; subsequent calls O(1) dict lookup). Bounded memory: 3,782
# parquets total across 3 forms at ~30KB each = ~110MB peak.
_DECODED_DF_CACHE: dict[tuple[str, str], pd.DataFrame] = {}


def _load_decoded(form: str, ticker: str) -> pd.DataFrame:
    """Load decoded filings for (form, ticker). Empty DataFrame on miss.

    Batch 534: in-memory cache keyed by (form, ticker). First call reads
    the parquet + normalizes filing_date dtype; subsequent calls return
    the cached DataFrame directly (zero disk IO).
    """
    safe_ticker = ticker.replace(".", "-").upper()
    cache_key = (form, safe_ticker)
    cached = _DECODED_DF_CACHE.get(cache_key)
    if cached is not None:
        return cached
    path = _DECODED_CACHE_DIR / form / f"{safe_ticker}.parquet"
    if not path.exists():
        _DECODED_DF_CACHE[cache_key] = pd.DataFrame()
        return _DECODED_DF_CACHE[cache_key]
    try:
        df = pd.read_parquet(path)
        if "filing_date" in df.columns:
            df = df.copy()
            df["filing_date"] = pd.to_datetime(df["filing_date"]).dt.date
        _DECODED_DF_CACHE[cache_key] = df
        return df
    except Exception:
        _DECODED_DF_CACHE[cache_key] = pd.DataFrame()
        return _DECODED_DF_CACHE[cache_key]


def sc_13d_filed_within_days(
    ticker: str,
    as_of: date,
    lookback_days: int = 30,
    df: Optional[pd.DataFrame] = None,
) -> dict:
    """P17b consumer: did an SC 13D filing land in the last
    `lookback_days` ending at as_of?

    Returns dict with `sc_13d_filed_within_<N>d` boolean +
    `sc_13d_latest_filer_identity` + `sc_13d_latest_percent_owned`
    when present; empty dict on no data."""
    src = df if df is not None else _load_decoded("SC_13D", ticker)
    if src is None or src.empty or "filing_date" not in src.columns:
        return {}
    from datetime import timedelta
    cutoff = as_of - timedelta(days=lookback_days)
    window = src[(src["filing_date"] > cutoff) & (src["filing_date"] <= as_of)]
    if window.empty:
        return {
            f"sc_13d_filed_within_{lookback_days}d": False,
        }
    latest = window.iloc[-1]
    out = {
        f"sc_13d_filed_within_{lookback_days}d": True,
    }
    if "filer_identity" in latest.index and latest["filer_identity"]:
        out["sc_13d_latest_filer_identity"] = str(latest["filer_identity"])
    if "percent_owned" in latest.index and pd.notna(latest["percent_owned"]):
        out["sc_13d_latest_percent_owned"] = float(latest["percent_owned"])
    return out


def eight_k_item_filed_within_days(
    ticker: str,
    as_of: date,
    item_code: str,
    lookback_days: int = 30,
    df: Optional[pd.DataFrame] = None,
) -> dict:
    """P17c/d consumer: did the named 8-K item code land in the lookback?

    Returns dict with `8k_item_<code>_filed_within_<N>d` boolean.
    Empty when no data."""
    src = df if df is not None else _load_decoded("8_K", ticker)
    if src is None or src.empty:
        return {}
    if "item_codes" not in src.columns or "filing_date" not in src.columns:
        return {}
    from datetime import timedelta
    cutoff = as_of - timedelta(days=lookback_days)
    window = src[(src["filing_date"] > cutoff) & (src["filing_date"] <= as_of)]
    if window.empty:
        return {f"8k_item_{item_code.replace('.', '_')}_filed_within_"
                f"{lookback_days}d": False}
    # item_codes is stored as comma-separated string per row
    hits = window["item_codes"].astype(str).str.contains(
        item_code.replace(".", "\\."), regex=True, na=False
    )
    return {f"8k_item_{item_code.replace('.', '_')}_filed_within_"
            f"{lookback_days}d": bool(hits.any())}


def sc_13g_filed_within_days(
    ticker: str,
    as_of: date,
    lookback_days: int = 30,
    df: Optional[pd.DataFrame] = None,
) -> dict:
    """Batch 522 (2026-05-31, P17e SCAFFOLD) -- did an SC 13G passive
    filing land in the last `lookback_days` ending at as_of?

    Mirrors `sc_13d_filed_within_days` but reads from SC_13G decoded
    cache. Per EXECUTION_QUEUE P17e: passive 5%+ filing is moderate
    signal -- Vanguard/BlackRock crossing 5% predicts index reweighting;
    smart-passive concentration signals quality. Use case: low-priority
    add to `smart_money_score`.
    """
    src = df if df is not None else _load_decoded("SC_13G", ticker)
    if src is None or src.empty or "filing_date" not in src.columns:
        return {}
    from datetime import timedelta
    cutoff = as_of - timedelta(days=lookback_days)
    window = src[(src["filing_date"] > cutoff) & (src["filing_date"] <= as_of)]
    if window.empty:
        return {f"sc_13g_filed_within_{lookback_days}d": False}
    latest = window.iloc[-1]
    out = {f"sc_13g_filed_within_{lookback_days}d": True}
    if "filer_identity" in latest.index and latest["filer_identity"]:
        out["sc_13g_latest_filer_identity"] = str(latest["filer_identity"])
    if "percent_owned" in latest.index and pd.notna(latest["percent_owned"]):
        out["sc_13g_latest_percent_owned"] = float(latest["percent_owned"])
    return out


def compute_sec_edgar_signals(ticker: str, as_of: date) -> dict:
    """Batch 522 (2026-05-31, P17b/c/d/e producer bundle) -- compute the
    full SEC EDGAR signal pack consumed by the P17 sleeve strategies +
    modifiers. Returns a dict that screener.screen_instrument can
    `signals.update()` with.

    Bundle:
      sc_13d_filed_within_30d         (P17b primary trigger)
      sc_13d_latest_filer_identity    (P17b enrichment when present)
      sc_13d_latest_percent_owned     (P17b enrichment when present)
      8k_item_1_01_filed_within_30d   (P17c primary trigger)
      8k_item_5_02_filed_within_7d    (P17d primary trigger)
      sc_13g_filed_within_30d         (P17e primary trigger)
      sc_13g_latest_filer_identity    (P17e enrichment)
      sc_13g_latest_percent_owned     (P17e enrichment)

    Returns an empty dict on any failure (silent-failure pattern per
    Batch 458 logger; matches the convention used by
    compute_short_interest_signals etc.).

    NOT WIRED into screen_instrument in Batch 522 -- producer ships
    SCAFFOLD-ONLY; owner approves wire-in once P17a scoped extraction
    completes (~6h ETA per EXECUTION_QUEUE).
    """
    out: dict = {}
    try:
        out.update(sc_13d_filed_within_days(ticker, as_of, lookback_days=30))
    except Exception:
        pass
    try:
        out.update(eight_k_item_filed_within_days(
            ticker, as_of, item_code="1.01", lookback_days=30))
    except Exception:
        pass
    try:
        out.update(eight_k_item_filed_within_days(
            ticker, as_of, item_code="5.02", lookback_days=7))
    except Exception:
        pass
    try:
        out.update(sc_13g_filed_within_days(ticker, as_of, lookback_days=30))
    except Exception:
        pass
    return out


__all__ = [
    "EDGAR_BASE",
    "build_edgar_filing_url",
    "extract_8k_item_codes",
    "extract_sc_13d_fields",
    "sc_13d_filed_within_days",
    "eight_k_item_filed_within_days",
    "sc_13g_filed_within_days",
    "compute_sec_edgar_signals",
]
