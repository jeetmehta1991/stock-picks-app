"""Stage 3 email digest formatter (Batch 246).

Builds daily-picks email + EOD-PnL summary email. SMTP transport stub-only
in this skeleton (owner activates post-1B-alpha; jeetmehta1991@gmail.com
confirmed recipient 2026-05-19).
"""
from __future__ import annotations

import os
from datetime import date
from typing import Optional


def format_picks_email(picks: list[dict], as_of: date) -> tuple[str, str]:
    """Format daily picks email. Returns (subject, body)."""
    n = len(picks)
    subject = f"[Paper] {n} pick{'s' if n != 1 else ''} for {as_of}"
    if n == 0:
        body = f"No picks today ({as_of}). Either zero P1 combos fired or market closed."
        return subject, body
    lines = [
        f"# Paper Trading Daily Picks - {as_of}",
        "",
        f"{n} candidates from Phase 1B-alpha-validated P1 combos:",
        "",
    ]
    for i, pick in enumerate(picks, 1):
        lines.extend([
            f"## {i}. {pick['ticker']} ({pick['strategy']} / {pick['exit_method']})",
            f"- Confidence: **{pick['confidence_tier']}** -> size {pick['position_size_pct']}%",
            f"- Entry: ${pick['entry_price']:.2f} | Stop: ${pick['initial_stop']:.2f}",
            f"- Combo: `{pick['combo_id']}` | Regime at entry: {pick['regime_at_entry']}",
            "- Rationale:",
        ])
        for bullet in pick.get("rationale_bullets", []):
            lines.append(f"  - {bullet}")
        lines.append("")
    lines.append("---")
    lines.append("Stage 3 paper trading; Phase 1B-alpha validated.")
    return subject, "\n".join(lines)


def format_eod_summary_email(eod_summary: dict, journal_entry: str) -> tuple[str, str]:
    """Format end-of-day summary email."""
    as_of = eod_summary.get("as_of", "?")
    val = eod_summary.get("current_value", 0)
    pnl = eod_summary.get("daily_pnl_dollar", 0)
    n_open = eod_summary.get("n_open", 0)
    n_closed = eod_summary.get("n_closed_today", 0)
    dd = eod_summary.get("current_dd_pct", 0)
    subject = f"[Paper EOD] {as_of} | PnL ${pnl:+.0f} | Open {n_open} | DD {dd}%"
    body = f"""# Paper Trading EOD Summary - {as_of}

- Portfolio value:    ${val:,.2f}
- Daily PnL:          ${pnl:+,.2f}
- Cash:               ${eod_summary.get('cash', 0):,.2f}
- Open positions:     {n_open}
- Closed today:       {n_closed}
- Current drawdown:   {dd}%

---
## Journal entry
{journal_entry}

---
Stage 3 paper trading."""
    return subject, body


def send_email(subject: str, body: str,
                to: str = "jeetmehta1991@gmail.com",
                smtp_host: Optional[str] = None,
                smtp_user: Optional[str] = None,
                smtp_password: Optional[str] = None,
                dry_run: bool = True) -> bool:
    """Send email via SMTP. Default dry_run=True for skeleton.

    Owner activates with SMTP credentials when ready (smtp_host, smtp_user,
    smtp_password sourced from env vars EMAIL_SMTP_HOST / _USER / _PASSWORD).
    """
    smtp_host = smtp_host or os.environ.get("EMAIL_SMTP_HOST")
    smtp_user = smtp_user or os.environ.get("EMAIL_SMTP_USER")
    smtp_password = smtp_password or os.environ.get("EMAIL_SMTP_PASSWORD")

    if dry_run or not all([smtp_host, smtp_user, smtp_password]):
        print(f"[DRY RUN] Would send email to {to}")
        print(f"Subject: {subject}")
        print(f"Body length: {len(body)} chars")
        return True

    try:
        import smtplib
        from email.mime.text import MIMEText
        msg = MIMEText(body, "plain")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = to
        with smtplib.SMTP_SSL(smtp_host, 465) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as exc:
        print(f"[ERROR] SMTP send failed: {exc}")
        return False
