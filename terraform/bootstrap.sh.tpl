#!/bin/bash
# Stage 4 LIVE instance bootstrap (Batch 373 C-2 SKELETON)
#
# Runs as user_data on Lightsail instance launch. Installs deps + clones
# repo + sets cron jobs for daily morning + EOD runs.
#
# Placeholders use Terraform templatefile() interpolation: ${repo_url}, ${region}

set -euo pipefail

# Update system
apt-get update -y
apt-get install -y python3.12 python3.12-venv git awscli

# Clone repo (read-only; production fetches from main on each cron run)
git clone ${repo_url} /opt/stock-picks-app
cd /opt/stock-picks-app

# Python virtualenv
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Cron entries (Stage 4 daily jobs)
cat > /etc/cron.d/stock-picks <<'CRON'
# Stage 4 LIVE daily picks (8 AM ET = 13:00 UTC summer / 12:00 UTC winter)
0 13 * * 1-5 root cd /opt/stock-picks-app && /opt/stock-picks-app/.venv/bin/python scripts/run_live_morning.py --send-email >> /var/log/stock-picks-morning.log 2>&1
# Stage 4 LIVE EOD reconciliation (4:30 PM ET = 21:30 UTC summer / 20:30 UTC winter)
30 21 * * 1-5 root cd /opt/stock-picks-app && /opt/stock-picks-app/.venv/bin/python scripts/run_live_end_of_day.py --live --send-email >> /var/log/stock-picks-eod.log 2>&1
# Weekly OHLCV cache refresh (Saturday 2 AM UTC)
0 2 * * 6 root cd /opt/stock-picks-app && /opt/stock-picks-app/.venv/bin/python scripts/refresh_sp500_universe.py >> /var/log/stock-picks-weekly.log 2>&1
CRON

# Pull SSM parameters into env (Anthropic + IB credentials)
cat > /opt/stock-picks-app/.env <<EOF
ANTHROPIC_API_KEY=\$(aws ssm get-parameter --region ${region} --name /stock-picks/anthropic_api_key --with-decryption --query Parameter.Value --output text)
IB_ACCOUNT=\$(aws ssm get-parameter --region ${region} --name /stock-picks/ib_account --with-decryption --query Parameter.Value --output text)
EOF
chmod 600 /opt/stock-picks-app/.env
chown root:root /opt/stock-picks-app/.env

echo "[OK] Stage 4 LIVE bootstrap complete"
