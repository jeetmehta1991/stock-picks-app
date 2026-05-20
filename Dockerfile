# Dockerfile for Stage 4 live trading container (Batch 247).
# Target: AWS Lightsail $5-15/mo deployment.
# Owner directive 2026-05-19: BUILT BUT NOT ACTIVATED until owner deploys.

FROM python:3.14-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir ib_async

# Copy application
COPY backtest/ ./backtest/
COPY scripts/ ./scripts/
COPY data_prefetch/derived/ ./data_prefetch/derived/

# Backtesting universe CSVs (read-only at runtime)
COPY "Backtesting universe/" "./Backtesting universe/"

# Output dir (mount as volume in production)
RUN mkdir -p /app/output_live /app/logs

# Entrypoint
ENV PYTHONUNBUFFERED=1
ENV TZ=America/New_York

# Stage 4 cron entrypoint - schedule via container orchestrator (Lightsail
# Container or cron inside container)
CMD ["python", "scripts/run_live_morning.py"]
