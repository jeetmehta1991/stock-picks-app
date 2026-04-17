import os
import sys
import time
import requests
from datetime import datetime, timezone

API_KEY = os.environ.get("ALPHA_VANTAGE_KEY")
BASE_URL = "https://www.alphavantage.co/query"

# Major TSX-listed stocks (Alpha Vantage uses .TRT suffix for Toronto Stock Exchange)
TSX_CANDIDATES = [
    "SHOP.TRT", "RY.TRT", "TD.TRT", "ENB.TRT", "BNS.TRT",
    "BMO.TRT", "MFC.TRT", "SU.TRT", "CNR.TRT", "CP.TRT",
    "ABX.TRT", "CNQ.TRT", "TRP.TRT", "WPM.TRT", "ATD.TRT",
]


def _check_av_error(data: dict) -> str | None:
    """Return an error string if Alpha Vantage signalled a problem in the response body."""
    msg = data.get("Note") or data.get("Information") or data.get("Error Message")
    return msg if msg else None


def get_us_top_gainers() -> tuple[list, str | None]:
    """Return (top_5_gainers, error_message_or_None)."""
    try:
        resp = requests.get(
            BASE_URL,
            params={"function": "TOP_GAINERS_LOSERS", "apikey": API_KEY},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        return [], f"Network error fetching US gainers: {exc}"
    except ValueError as exc:
        return [], f"JSON parse error for US gainers: {exc}"

    av_err = _check_av_error(data)
    if av_err:
        return [], f"Alpha Vantage (US): {av_err}"

    gainers = data.get("top_gainers", [])[:5]
    return [
        {
            "ticker": g.get("ticker", ""),
            "price": g.get("price", "N/A"),
            "change_amount": g.get("change_amount", "N/A"),
            "change_percentage": g.get("change_percentage", "N/A"),
        }
        for g in gainers
    ], None


def get_tsx_top_performers() -> tuple[list, list[str]]:
    """Return (top_5_performers, list_of_error_strings)."""
    results = []
    errors = []

    for i, symbol in enumerate(TSX_CANDIDATES):
        # Always sleep between calls; the first call here also follows the US request
        # so we sleep unconditionally to stay within the 5-calls/min free-tier limit.
        if i > 0:
            time.sleep(13)

        try:
            resp = requests.get(
                BASE_URL,
                params={"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": API_KEY},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            errors.append(f"{symbol}: network error — {exc}")
            continue
        except ValueError as exc:
            errors.append(f"{symbol}: JSON parse error — {exc}")
            continue

        av_err = _check_av_error(data)
        if av_err:
            errors.append(f"{symbol}: {av_err}")
            continue

        quote = data.get("Global Quote", {})
        if not quote.get("05. price"):
            continue

        raw_pct = quote.get("10. change percent", "0%")
        try:
            change_pct = float(raw_pct.strip("%"))
        except ValueError:
            change_pct = 0.0

        results.append(
            {
                "ticker": symbol.replace(".TRT", ".TO"),
                "price": quote.get("05. price", "N/A"),
                "change_amount": quote.get("09. change", "N/A"),
                "change_percentage": raw_pct,
                "_sort_key": change_pct,
            }
        )

    results.sort(key=lambda x: x["_sort_key"], reverse=True)
    top5 = results[:5]
    for r in top5:
        del r["_sort_key"]
    return top5, errors


def fmt_change(change_pct_str):
    """Return (css_class, arrow, display_string) for a change-percent string."""
    try:
        val = float(change_pct_str.strip("%"))
    except ValueError:
        return "neutral", "—", change_pct_str
    if val > 0:
        return "positive", "▲", f"+{change_pct_str.strip()}"
    if val < 0:
        return "negative", "▼", change_pct_str.strip()
    return "neutral", "—", change_pct_str.strip()


def stock_row(stock):
    css, arrow, pct_label = fmt_change(stock["change_percentage"])
    try:
        price = f"${float(stock['price']):,.2f}"
    except ValueError:
        price = stock["price"]
    try:
        delta = float(stock["change_amount"])
        delta_label = f"{'+' if delta >= 0 else ''}{delta:.2f}"
    except ValueError:
        delta_label = stock["change_amount"]

    return f"""
        <tr>
          <td class="ticker">{stock['ticker']}</td>
          <td class="price">{price}</td>
          <td class="change {css}">{arrow} {delta_label}</td>
          <td class="pct {css}">{pct_label}</td>
        </tr>"""


EMPTY_ROW = (
    '<tr><td colspan="4" class="empty">Data unavailable — check workflow logs</td></tr>'
)


def build_html(us_stocks, tsx_stocks, generated_at, fetch_errors=None):
    us_rows = "".join(stock_row(s) for s in us_stocks) if us_stocks else EMPTY_ROW
    tsx_rows = "".join(stock_row(s) for s in tsx_stocks) if tsx_stocks else EMPTY_ROW

    error_banner = ""
    if fetch_errors:
        items = "".join(f"<li>{e}</li>" for e in fetch_errors)
        error_banner = f"""
  <div class="error-banner">
    <strong>⚠ Some data could not be fetched:</strong>
    <ul>{items}</ul>
  </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Top Stock Picks — {generated_at}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: #0d1117;
      color: #c9d1d9;
      min-height: 100vh;
      padding: 2rem 1rem;
    }}

    header {{
      text-align: center;
      margin-bottom: 2.5rem;
    }}

    header h1 {{
      font-size: 1.9rem;
      font-weight: 700;
      color: #f0f6fc;
      letter-spacing: 0.5px;
    }}

    header p {{
      margin-top: 0.4rem;
      font-size: 0.85rem;
      color: #8b949e;
    }}

    .badge {{
      display: inline-block;
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 999px;
      font-size: 0.75rem;
      padding: 0.2rem 0.7rem;
      margin-top: 0.6rem;
      color: #58a6ff;
    }}

    .error-banner {{
      max-width: 900px;
      margin: 0 auto 1.5rem;
      background: #1a0a0a;
      border: 1px solid #6e2020;
      border-radius: 8px;
      padding: 0.9rem 1.25rem;
      font-size: 0.8rem;
      color: #f85149;
    }}

    .error-banner ul {{
      margin-top: 0.4rem;
      padding-left: 1.2rem;
      color: #8b949e;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 1.5rem;
      max-width: 900px;
      margin: 0 auto;
    }}

    .card {{
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 12px;
      overflow: hidden;
    }}

    .card-header {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      padding: 1rem 1.25rem;
      border-bottom: 1px solid #30363d;
    }}

    .card-header .flag {{
      font-size: 1.4rem;
      line-height: 1;
    }}

    .card-header h2 {{
      font-size: 1rem;
      font-weight: 600;
      color: #f0f6fc;
    }}

    .card-header .sub {{
      font-size: 0.75rem;
      color: #8b949e;
      margin-left: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
    }}

    th, td {{
      padding: 0.65rem 1.25rem;
      font-size: 0.875rem;
      text-align: right;
    }}

    th {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #8b949e;
      border-bottom: 1px solid #21262d;
    }}

    th:first-child, td:first-child {{
      text-align: left;
    }}

    tr:not(:last-child) td {{
      border-bottom: 1px solid #21262d;
    }}

    tr:hover td {{
      background: #1c2128;
    }}

    .ticker {{
      font-weight: 700;
      color: #58a6ff;
      font-size: 0.9rem;
    }}

    .price {{
      color: #f0f6fc;
      font-variant-numeric: tabular-nums;
    }}

    .positive {{ color: #3fb950; }}
    .negative {{ color: #f85149; }}
    .neutral  {{ color: #8b949e; }}

    .change, .pct {{
      font-variant-numeric: tabular-nums;
    }}

    .empty {{
      text-align: center !important;
      color: #484f58;
      font-style: italic;
      padding: 1.2rem !important;
    }}

    footer {{
      text-align: center;
      margin-top: 2.5rem;
      font-size: 0.75rem;
      color: #484f58;
    }}

    footer a {{
      color: #58a6ff;
      text-decoration: none;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Top Performing Stocks</h1>
    <p>Today's top 5 gainers by exchange</p>
    <span class="badge">Updated {generated_at} UTC</span>
  </header>
{error_banner}
  <div class="grid">
    <div class="card">
      <div class="card-header">
        <span class="flag">🇺🇸</span>
        <h2>US Markets</h2>
        <span class="sub">NYSE · NASDAQ</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Price</th>
            <th>Change</th>
            <th>% Change</th>
          </tr>
        </thead>
        <tbody>{us_rows}
        </tbody>
      </table>
    </div>

    <div class="card">
      <div class="card-header">
        <span class="flag">🇨🇦</span>
        <h2>TSX Canada</h2>
        <span class="sub">Toronto Stock Exchange</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Price</th>
            <th>Change</th>
            <th>% Change</th>
          </tr>
        </thead>
        <tbody>{tsx_rows}
        </tbody>
      </table>
    </div>
  </div>

  <footer>
    <p>Data sourced from <a href="https://www.alphavantage.co" target="_blank" rel="noopener">Alpha Vantage</a> &mdash; updated daily at 06:00 UTC</p>
  </footer>
</body>
</html>
"""


def main():
    if not API_KEY:
        raise EnvironmentError("ALPHA_VANTAGE_KEY environment variable is not set.")

    all_errors = []

    print("Fetching US top gainers...")
    us_stocks, us_err = get_us_top_gainers()
    if us_err:
        print(f"  ERROR: {us_err}", file=sys.stderr)
        all_errors.append(us_err)
    else:
        print(f"  Got {len(us_stocks)} US stocks")

    # Sleep before the first TSX call — the US request just fired and shares the
    # same rate-limit bucket (5 calls/min on the free tier).
    print("Waiting before TSX requests...")
    time.sleep(13)

    print("Fetching TSX quotes (rate-limited — this takes ~3 min on the free tier)...")
    tsx_stocks, tsx_errors = get_tsx_top_performers()
    if tsx_errors:
        for e in tsx_errors:
            print(f"  WARN: {e}", file=sys.stderr)
        all_errors.extend(tsx_errors)
    print(f"  Got {len(tsx_stocks)} TSX stocks")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    html = build_html(us_stocks, tsx_stocks, generated_at, fetch_errors=all_errors or None)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {output_path}")

    if all_errors:
        # Exit non-zero so GitHub Actions marks the step as failed when data is missing
        sys.exit(1)


if __name__ == "__main__":
    main()
