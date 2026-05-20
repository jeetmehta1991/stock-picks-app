"""Stage 3 daily journal entries (Batch 246).

Auto-generated markdown journal entries per day. Saved to
dashboard_stage_3/journal/{YYYY-MM-DD}.md for public-website ingest.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path


def build_journal_entry(
    as_of: date,
    eod_summary: dict,
    picks_executed: list[dict],
    closed_today: list[dict],
) -> str:
    """Build markdown journal entry for a single day."""
    lines = [
        f"# Paper Trading Journal - {as_of}",
        "",
        "## Portfolio state",
        f"- Value:        ${eod_summary.get('current_value', 0):,.2f}",
        f"- Cash:         ${eod_summary.get('cash', 0):,.2f}",
        f"- Open:         {eod_summary.get('n_open', 0)} positions",
        f"- Daily PnL:    ${eod_summary.get('daily_pnl_dollar', 0):+,.2f}",
        f"- Drawdown:     {eod_summary.get('current_dd_pct', 0)}%",
        "",
    ]
    if picks_executed:
        lines.extend([
            "## Picks executed (opens)",
            "",
            "| # | Ticker | Strategy | Exit | Size | Entry | Stop | Tier |",
            "|---|--------|----------|------|------|-------|------|------|",
        ])
        for i, p in enumerate(picks_executed, 1):
            lines.append(
                f"| {i} | {p['ticker']} | {p['strategy']} | {p['exit_method']} "
                f"| {p['position_size_pct']}% | ${p['entry_price']:.2f} "
                f"| ${p['initial_stop']:.2f} | {p['confidence_tier']} |"
            )
        lines.append("")
    if closed_today:
        lines.extend([
            "## Closed today",
            "",
            "| # | Ticker | Entry | Exit | PnL % | PnL $ | Hold days | Reason |",
            "|---|--------|-------|------|-------|-------|-----------|--------|",
        ])
        for i, t in enumerate(closed_today, 1):
            lines.append(
                f"| {i} | {t['ticker']} | ${t['entry_price']:.2f} "
                f"| ${t['exit_price']:.2f} | {t['pnl_pct']:+.2f}% "
                f"| ${t['pnl_dollar']:+.2f} | {t['hold_days']} | {t['exit_reason']} |"
            )
        lines.append("")
    if not picks_executed and not closed_today:
        lines.append("No trades today (no picks fired and no exits triggered).")
        lines.append("")
    return "\n".join(lines)


def save_journal_entry(
    journal_text: str,
    as_of: date,
    output_dir: Path,
) -> Path:
    """Save journal entry as markdown file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{as_of.isoformat()}.md"
    path.write_text(journal_text, encoding="utf-8")
    return path
