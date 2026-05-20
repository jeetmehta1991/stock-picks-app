"""Stage 4 live trading module.

IB API order execution + real-time risk overlay + owner-approval workflow
for live trades. Built by May 29 per owner directive 2026-05-19; activation
deferred until owner deploys to AWS Lightsail with IB credentials.

Modules:
  risk_overlay       - DEC-515 Level 6 + circuit breakers + tier sizing
  ib_executor        - IB API order placement (ib_async wrapper)
  live_approval      - owner email approval workflow for trade signoff

Scripts (in scripts/ root):
  run_live_morning.py     - daily picks + approval email
  run_live_execution.py   - execute on owner-approved picks
  run_live_end_of_day.py  - reconciliation

Deployment:
  Dockerfile + scripts/deploy_live.sh - AWS Lightsail $5-15/mo target
  (BUILT BUT NOT ACTIVATED per owner directive)
"""
