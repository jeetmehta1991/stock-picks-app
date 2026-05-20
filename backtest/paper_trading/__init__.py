"""Stage 3 paper trading module.

Daily-cron-able paper portfolio management consuming Phase 1A-beta
winners.parquet (P1 combos) + day's market data.

Modules:
  daily_picks      - top-10 candidate selection from P1 winners
  paper_portfolio  - simulated position tracking + PnL
  journal          - auto-generated daily journal entries
  email_digest     - email formatter for daily picks + EOD PnL summary

Scripts:
  run_paper_morning.py     - daily 8 AM ET picks + email
  run_paper_end_of_day.py  - 4 PM ET PnL update + journal entry
  run_paper_dashboard.py   - refresh Stage 3 web dashboard

Owner-confirmed 2026-05-19: built by May 29; activates post-1B-alpha verdict.
"""
